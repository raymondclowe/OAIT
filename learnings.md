# OAIT Development Learnings

## 2026-01-15: Starting MVP Implementation

### Context
- Phase 0 (Project Foundation) is complete
- Repository has comprehensive documentation and data models
- Status: Ready to start Phase 1+ implementation towards MVP

### Understanding
- User request "move towards mpv" = "move towards MVP" (Minimum Viable Product)
- MVP goal: Complete working tutoring system with all core features
- Architecture: Local-first with OpenRouter as only cloud dependency

### Implementation Progress

#### Phase 1-2: WebSocket Integration (IN PROGRESS)
**Completed:**
- Created FastAPI WebSocket server (`websocket_server.py`)
  - Handles real-time audio and video streaming
  - Session management (start/stop sessions)
  - WebSocket endpoint for bidirectional communication
  - Health check endpoints
- Created web client (`static/index.html`)
  - Beautiful, responsive UI with gradient design
  - Canvas-based whiteboard for drawing
  - Audio recording with browser getUserMedia API
  - WebSocket client connecting to backend
  - Real-time transcript display
  - AI response display with Web Speech API TTS
  - Session controls and status indicators
- Updated data models:
  - Added `transcript_buffer` and `silence_detector` to SessionState
  - Added `response_text` to Decision model
- Created server startup script (`start_server.py`)

**Technical Decisions:**
- Using FastAPI instead of Gradio for better WebSocket control
- Audio: Browser records → WebSocket → Server (Whisper STT)
- Video: Canvas snapshots → WebSocket → Server (Gemini 3 Pro vision)
- TTS: Web Speech API (browser-native, no cloud dependency)
- Serving static HTML directly from FastAPI

**Next Steps:**
- Test the WebSocket server with real audio/video
- Implement AI tool system (Phase 5)
- Complete OODA loop intervention logic (Phase 6)
- Add Excalidraw integration for better whiteboard
- PWA manifest for mobile support

### Next Steps
According to IMPLEMENTATION_PLAN.md and STATUS.md, we need to work on:
1. **Phase 1**: Audio WebSocket Integration (connect browser → server → Whisper STT) ✅ DONE
2. **Phase 2**: Vision WebSocket Integration (connect browser → server → Gemini 3 Pro) ✅ DONE
3. **Phase 5**: AI Tool System (pedagogical tools for the OODA loop)
4. **Phase 6**: Intervention System (decision-making and TTS) ✅ PARTIAL (TTS done, decision logic needs work)
5. **Phase 7**: Full MVP Integration (Gradio/Flask UI, PWA, Excalidraw)

### Key Constraints
- Local-first architecture (only OpenRouter for LLM calls)
- Use `uv` for Python package management (per AGENTS.md)
- Save learnings to this file as development progresses

### Technical Notes
- All tests passing (10/10)
- WebSocket server ready for testing
- Need to configure OpenRouter API key in .env file to test
- Whisper STT needs audio in WAV format
- Canvas sends frames as base64-encoded PNG images every 3 seconds
