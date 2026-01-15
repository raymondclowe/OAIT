"""WebSocket server for real-time audio and video streaming."""

import logging
import asyncio
import json
from typing import Dict, Set, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import base64
from PIL import Image
import io
import time

from ..config import get_settings
from ..models.repository import StudentModelRepository
from ..api.openrouter import OpenRouterClient
from ..audio.whisper_stt import WhisperSTT
from ..audio.stream_handler import TranscriptBuffer, SilenceDetector
from ..vision.analyzer import VisionAnalyzer
from ..vision.preprocessor import ImagePreprocessor
from ..cognitive.loop import OODALoop
from ..cognitive.triggers import TriggerDetector
from ..models.data_models import SessionState, StudentModel
import uuid

logger = logging.getLogger(__name__)

app = FastAPI(title="OAIT Server", description="Observational AI Tutor WebSocket Server")

# Global state
active_sessions: Dict[str, SessionState] = {}
active_connections: Dict[str, WebSocket] = {}
server_components: Dict[str, Any] = {}


async def initialize_server() -> None:
    """Initialize all server components."""
    logger.info("Initializing OAIT WebSocket server...")
    
    settings = get_settings()
    
    # Ensure directories exist
    Path("./memory").mkdir(exist_ok=True)
    Path("./logs").mkdir(exist_ok=True)
    
    # Initialize repository
    repository = StudentModelRepository(settings.sqlite_db_path)
    await repository.initialize()
    server_components['repository'] = repository
    
    # Initialize OpenRouter client
    openrouter_client = OpenRouterClient(
        api_key=settings.openrouter_api_key.get_secret_value(),
        model=settings.openrouter_model,
    )
    server_components['openrouter'] = openrouter_client
    
    # Initialize Whisper STT
    whisper_stt = WhisperSTT(
        model_size=settings.whisper_model_size,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
    )
    server_components['whisper'] = whisper_stt
    
    # Initialize vision components
    image_preprocessor = ImagePreprocessor()
    server_components['preprocessor'] = image_preprocessor
    
    vision_analyzer = VisionAnalyzer(openrouter_client)
    server_components['vision'] = vision_analyzer
    
    # Initialize OODA loop components
    trigger_detector = TriggerDetector(
        silence_threshold=settings.silence_threshold,
        change_threshold=settings.vision_change_threshold,
    )
    server_components['trigger_detector'] = trigger_detector
    
    logger.info("OAIT WebSocket server initialized successfully")


@app.on_event("startup")
async def startup_event() -> None:
    """Startup event handler."""
    await initialize_server()


@app.get("/")
async def root() -> FileResponse:
    """Serve the main HTML page."""
    static_dir = Path(__file__).parent / "static"
    return FileResponse(static_dir / "index.html")


@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/session/start")
async def start_session(student_id: str) -> Dict[str, str]:
    """Start a new tutoring session.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Session information including session_id
    """
    repository = server_components.get('repository')
    if not repository:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    logger.info(f"Starting session for student: {student_id}")
    
    # Load or create student model
    student_model = await repository.load(student_id)
    if not student_model:
        logger.info(f"Creating new student model for: {student_id}")
        student_model = await repository.create_default_model(student_id)
    
    # Create session state
    session_id = str(uuid.uuid4())
    session_state = SessionState(
        session_id=session_id,
        student_id=student_id,
    )
    
    # Initialize session components
    session_state.transcript_buffer = TranscriptBuffer(max_duration=30.0)
    session_state.silence_detector = SilenceDetector(threshold=3.0)
    
    active_sessions[session_id] = session_state
    
    logger.info(f"Session started: {session_id}")
    
    return {
        "session_id": session_id,
        "student_id": student_id,
        "status": "active"
    }


@app.post("/session/{session_id}/stop")
async def stop_session(session_id: str) -> Dict[str, str]:
    """Stop a tutoring session.
    
    Args:
        session_id: ID of the session
        
    Returns:
        Status message
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Clean up session
    del active_sessions[session_id]
    if session_id in active_connections:
        del active_connections[session_id]
    
    logger.info(f"Session stopped: {session_id}")
    
    return {
        "session_id": session_id,
        "status": "stopped"
    }


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
    """WebSocket endpoint for audio and video streaming.
    
    Handles bidirectional communication:
    - Receives audio chunks and video frames from client
    - Sends transcripts and AI responses back to client
    
    Args:
        websocket: WebSocket connection
        session_id: Session ID
    """
    # Verify session exists
    if session_id not in active_sessions:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    await websocket.accept()
    active_connections[session_id] = websocket
    
    logger.info(f"WebSocket connected for session: {session_id}")
    
    session_state = active_sessions[session_id]
    whisper_stt = server_components.get('whisper')
    vision_analyzer = server_components.get('vision')
    preprocessor = server_components.get('preprocessor')
    openrouter = server_components.get('openrouter')
    trigger_detector = server_components.get('trigger_detector')
    
    # Initialize OODA loop for this session
    ooda_loop = OODALoop(
        openrouter_client=openrouter,
        trigger_detector=trigger_detector,
    )
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get('type')
            
            if message_type == 'audio':
                # Handle audio chunk
                audio_data = base64.b64decode(data.get('data', ''))
                
                # Transcribe audio using Whisper
                if whisper_stt and len(audio_data) > 0:
                    try:
                        # Save audio chunk temporarily
                        temp_audio_path = f"/tmp/audio_{session_id}.wav"
                        with open(temp_audio_path, 'wb') as f:
                            f.write(audio_data)
                        
                        # Transcribe
                        text = await whisper_stt.transcribe(temp_audio_path)
                        
                        if text:
                            # Add to transcript buffer
                            timestamp = time.time()
                            session_state.transcript_buffer.append(text, timestamp)
                            
                            # Update silence detector
                            session_state.silence_detector.on_speech()
                            
                            # Send transcript back to client
                            await websocket.send_json({
                                'type': 'transcript',
                                'text': text,
                                'timestamp': timestamp
                            })
                            
                            logger.debug(f"Transcribed: {text}")
                    except Exception as e:
                        logger.error(f"Error transcribing audio: {e}")
                else:
                    # Update silence detector even if no audio
                    silence_duration = session_state.silence_detector.get_silence_duration()
                    session_state.silence_duration = silence_duration
            
            elif message_type == 'video':
                # Handle video frame
                frame_data = base64.b64decode(data.get('data', ''))
                
                if vision_analyzer and preprocessor and len(frame_data) > 0:
                    try:
                        # Convert to PIL Image
                        image = Image.open(io.BytesIO(frame_data))
                        
                        # Preprocess image
                        processed_image = await preprocessor.preprocess(image)
                        
                        # Store in session state
                        session_state.current_problem_image = processed_image
                        
                        # Check if we should trigger analysis
                        if trigger_detector.should_trigger_analysis(session_state):
                            logger.info("Triggering OODA loop analysis...")
                            
                            # Run OODA loop
                            decision = await ooda_loop.run_cycle(
                                session_state=session_state,
                                student_model=None  # TODO: Load from repository
                            )
                            
                            # If AI decides to speak, send response to client
                            if decision.action.value == "SPEAK" and decision.response_text:
                                await websocket.send_json({
                                    'type': 'ai_response',
                                    'text': decision.response_text,
                                    'strategy': decision.strategy.value if decision.strategy else None
                                })
                                
                                logger.info(f"AI Response: {decision.response_text}")
                    except Exception as e:
                        logger.error(f"Error processing video frame: {e}")
            
            elif message_type == 'ping':
                # Heartbeat
                await websocket.send_json({'type': 'pong'})
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
        if session_id in active_connections:
            del active_connections[session_id]
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if session_id in active_connections:
            del active_connections[session_id]


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        log_level="info"
    )
