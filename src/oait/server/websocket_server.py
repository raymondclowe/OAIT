"""WebSocket server for real-time audio and video streaming."""

import logging
import asyncio
import json
import tempfile
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
from ..cognitive.tool_loop import ToolOODALoop
from ..cognitive.triggers import TriggerDetector
from ..models.data_models import SessionState, StudentModel
from ..tools.ai_tools import ToolContext, AIToolHandlers
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


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Shutdown event handler - cleanup resources to prevent leaks."""
    logger.info("Shutting down OAIT WebSocket server...")
    
    # Unload Whisper model to release semaphores
    whisper_stt = server_components.get('whisper')
    if whisper_stt:
        whisper_stt.unload_model()
        logger.info("Whisper model unloaded")
    
    # Close any active WebSocket connections
    for session_id, ws in list(active_connections.items()):
        try:
            await ws.close()
        except Exception:
            pass
    active_connections.clear()
    
    # Clear active sessions
    active_sessions.clear()
    
    # Clear server components
    server_components.clear()
    
    logger.info("OAIT WebSocket server shutdown complete")


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
    session_state.transcript_buffer = TranscriptBuffer(duration=30.0)
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
    """WebSocket endpoint for AI-driven tool-based communication.
    
    Architecture: AI controls everything via tools
    - AI uses tools to request data (audio, whiteboard, camera)
    - AI uses tools to take actions (speak, update model, visual hints)
    - AI uses tools to control flow (wait_for_event, set_observation_mode)
    
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
    repository = server_components.get('repository')
    
    # Load student model
    student_model = None
    if repository:
        try:
            student_model = await repository.load(session_state.student_id)
        except Exception as e:
            logger.error(f"Error loading student model: {e}")
    
    if not student_model:
        logger.warning("[AI] No student model - creating default")
        student_model = await repository.create_default_model(session_state.student_id)
    
    # Pending requests waiting for client response
    pending_requests: Dict[str, asyncio.Future] = {}
    request_counter = [0]  # Use list for mutability in nested function
    
    async def send_debug(msg: str) -> None:
        """Send debug message to client."""
        try:
            await websocket.send_json({'type': 'debug', 'message': msg, 'timestamp': time.time()})
        except Exception:
            pass
    
    # Create tool context with all dependencies
    tool_context = ToolContext(
        session_state=session_state,
        student_model=student_model,
        websocket=websocket,
        repository=repository,
        whisper_stt=whisper_stt,
        vision_analyzer=vision_analyzer,
        openrouter=openrouter,
        pending_requests=pending_requests,
        request_counter=0,
    )
    
    # Create tool-based OODA loop
    tool_ooda = ToolOODALoop(
        openrouter_client=openrouter,
        context=tool_context,
    )
    
    async def process_client_response(data: dict) -> None:
        """Process response from client to a tool request."""
        request_id = data.get('request_id')
        if request_id and request_id in pending_requests:
            # Resolve the pending future
            pending_requests[request_id].set_result(data)
            logger.debug(f"[WS] Resolved request: {request_id}")
        else:
            logger.warning(f"[WS] Unknown request_id: {request_id}")
    
    async def ai_loop():
        """Background task that runs the AI's tool-based observation loop."""
        await asyncio.sleep(2.0)  # Initial delay to let client set up
        logger.info("[AI] Tool-based OODA loop starting")
        await send_debug("🤖 AI tool-based control starting...")
        
        try:
            await tool_ooda.start()
        except asyncio.CancelledError:
            logger.info("[AI] Loop cancelled")
        except Exception as e:
            logger.error(f"[AI] Loop error: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    # Start the AI loop
    ai_task = asyncio.create_task(ai_loop())
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            message_type = data.get('type')
            
            if message_type == 'response':
                # Client responding to a tool request
                await process_client_response(data)
            
            elif message_type == 'ping':
                await websocket.send_json({'type': 'pong'})
            
            elif message_type == 'client_event':
                # Client can send events like "speech_started", "whiteboard_changed"
                event = data.get('event')
                logger.debug(f"[WS] Client event: {event}")
                
                # Update context for wait_for_event tool
                if event == 'speech_started':
                    tool_context.last_speech_time = time.time()
                elif event == 'whiteboard_changed':
                    tool_context.last_whiteboard_change = time.time()
            
            else:
                logger.debug(f"[WS] Received: type={message_type}")
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Clean up
        await tool_ooda.stop()
        ai_task.cancel()
        try:
            await ai_task
        except asyncio.CancelledError:
            pass
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
