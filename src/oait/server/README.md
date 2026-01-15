# OAIT WebSocket Server

This is the real-time WebSocket server for the OAIT (Observational AI Tutor) MVP.

## Features

- **Real-time Audio Streaming**: Browser → WebSocket → Faster-Whisper STT (local)
- **Real-time Video Streaming**: Canvas frames → WebSocket → Gemini 3 Pro vision (via OpenRouter)
- **Session Management**: Start/stop tutoring sessions with student tracking
- **AI Intervention**: OODA loop analyzes student work and provides intelligent guidance
- **Browser TTS**: Web Speech API for natural-sounding AI responses (no cloud TTS)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your OpenRouter API key:

```bash
cp .env.example .env
# Edit .env and set:
# OPENROUTER_API_KEY=your_key_here
```

### 3. Start the Server

```bash
python start_server.py
```

Or directly with uvicorn:

```bash
uvicorn oait.server.websocket_server:app --host 0.0.0.0 --port 7860 --reload
```

### 4. Open in Browser

Navigate to: `http://localhost:7860`

## Usage

1. **Enter Student ID**: Type a unique identifier for the student
2. **Start Session**: Click "Start Session" to begin
3. **Start Audio**: Click "Start Audio" to enable microphone (you'll be prompted for permission)
4. **Draw on Whiteboard**: Use your mouse to draw math problems or notes
5. **Speak**: The AI will transcribe your speech in real-time
6. **Listen**: When the AI decides to intervene, it will speak back to you

## API Endpoints

### HTTP Endpoints

- `GET /`: Serve the main HTML interface
- `GET /health`: Health check endpoint
- `POST /session/start?student_id={id}`: Start a new session
- `POST /session/{session_id}/stop`: Stop a session

### WebSocket Endpoint

- `WS /ws/{session_id}`: Real-time bidirectional communication

## WebSocket Message Types

### Client → Server

**Audio Message:**
```json
{
  "type": "audio",
  "data": "base64_encoded_wav_data"
}
```

**Video Message:**
```json
{
  "type": "video",
  "data": "base64_encoded_png_data"
}
```

**Ping Message:**
```json
{
  "type": "ping"
}
```

### Server → Client

**Transcript Message:**
```json
{
  "type": "transcript",
  "text": "What is 2 plus 2?",
  "timestamp": 1234567890.123
}
```

**AI Response Message:**
```json
{
  "type": "ai_response",
  "text": "That's a good question! Let's work through it together.",
  "strategy": "socratic"
}
```

**Pong Message:**
```json
{
  "type": "pong"
}
```

## Architecture

```
Browser Client
    ├─ getUserMedia() → Audio Stream → WebSocket
    ├─ Canvas Drawing → PNG Frames → WebSocket
    └─ Web Speech API ← AI Responses ← WebSocket

WebSocket Server (FastAPI)
    ├─ Session Management
    ├─ Audio Processing → Faster-Whisper STT (local)
    ├─ Vision Processing → Gemini 3 Pro (OpenRouter)
    ├─ OODA Loop → Decision Making
    └─ SQLite Database → Student Models

Components:
    ├─ Faster-Whisper: Local speech-to-text (GPU recommended)
    ├─ OpenRouter: Gemini 3 Pro for vision + reasoning (only cloud service)
    ├─ SQLite: Local student model storage
    └─ Web Speech API: Browser-native TTS (no cloud dependency)
```

## Configuration

Key environment variables in `.env`:

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-...

# Optional (with defaults)
OPENROUTER_MODEL=google/gemini-3.0-pro
WHISPER_MODEL_SIZE=base  # base, small, medium, large
WHISPER_DEVICE=auto  # auto, cpu, cuda
SERVER_HOST=0.0.0.0
SERVER_PORT=7860
SQLITE_DB_PATH=./memory/oait.db
SILENCE_THRESHOLD=3.0  # seconds
VISION_CHANGE_THRESHOLD=0.3  # 0.0-1.0
```

## Development

### Running Tests

```bash
pytest -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/
```

## Troubleshooting

### Audio Not Working

- Ensure browser has microphone permissions
- Check that Faster-Whisper is installed: `pip show faster-whisper`
- For better performance, install with GPU support

### Vision Not Processing

- Verify OpenRouter API key is set correctly
- Check server logs for API errors
- Ensure canvas frames are being sent (check browser console)

### WebSocket Disconnects

- Check server logs for errors
- Verify session was started successfully
- Try refreshing the browser page

## Next Steps

- [ ] Add Excalidraw for advanced whiteboard features
- [ ] Implement PWA manifest for mobile support
- [ ] Add AI pedagogical tools (verify_calculation, etc.)
- [ ] Enhanced OODA loop decision logic
- [ ] Session history and replay
- [ ] Multi-student support

## License

See LICENSE file in repository root.
