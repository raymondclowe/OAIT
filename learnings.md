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

#### Phase 1-2: WebSocket Integration (COMPLETE ✅)
**Completed:**
- Created FastAPI WebSocket server (`websocket_server.py`)
  - Handles real-time audio and video streaming
  - Session management (start/stop sessions)
  - WebSocket endpoint for bidirectional communication
  - Health check endpoints
  - **SECURITY FIX**: Replaced hardcoded /tmp paths with tempfile module for secure temporary file handling
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
  - **TYPE SAFETY FIX**: Added proper type hints using TYPE_CHECKING to avoid circular imports
- Created server startup script (`start_server.py`)

**Technical Decisions:**
- Using FastAPI instead of Gradio for better WebSocket control
- Audio: Browser records → WebSocket → Server (Whisper STT)
- Video: Canvas snapshots → WebSocket → Server (Gemini 3 Pro vision)
- TTS: Web Speech API (browser-native, no cloud dependency)
- Serving static HTML directly from FastAPI
- **SECURITY**: Using tempfile.NamedTemporaryFile to avoid race conditions and TOCTOU vulnerabilities

#### Phase 5: AI Tool System (COMPLETE ✅)
**Completed:**
- Implemented `PedagogicalTools` class with 6 core tools:
  1. `verify_calculation`: Verify mathematical calculations
     - **SECURITY FIX**: Replaced eval() with AST-based safe evaluation to prevent arbitrary code execution
  2. `assess_confusion_level`: Analyze speech for confusion indicators
  3. `detect_question`: Detect if student asked a question
  4. `detect_stuck_pattern`: Detect if student is stuck
  5. `suggest_intervention_strategy`: Recommend best intervention approach
- Created `get_tool_definitions()` for OpenAI function calling format
- Comprehensive test suite (27 tests, 100% passing)
- Tools use heuristics and pattern matching for real-time analysis

**Technical Decisions:**
- Simple pattern matching for MVP (no ML models needed)
- Tools return structured dictionaries with confidence scores
- Confusion detection based on keywords and hesitations
- Stuck detection combines silence, whiteboard activity, and speech patterns
- Strategy suggestions based on combination of student state indicators
- **SECURITY**: AST-based math evaluation using ast.parse() with whitelisted operators (no eval(), no arbitrary code execution)

**Tool Capabilities:**
- Verify calculations with ~0.0001 tolerance for floating point
- Safely evaluate math expressions with +, -, *, /, ^ operators
- Detect 13+ confusion indicators (e.g., "I don't understand", "um", "?")
- Detect 11+ question patterns (e.g., "how do I", "what is", "?")
- Detect stuck with 5 explicit indicators + behavioral patterns
- Suggest 6 intervention strategies (socratic, direct, scaffolding, hint, example, analogical)

#### Security & Code Quality Fixes (2026-01-15)
**Addressed code review feedback:**

1. **CRITICAL - eval() Security Vulnerability** ✅ FIXED
   - **Issue**: Using eval() for math expressions allows arbitrary code execution
   - **Fix**: Replaced with AST-based safe evaluation
   - **Implementation**: Parse with ast.parse(), whitelist safe operators, recursive evaluation
   - **Result**: No arbitrary code execution possible, maintains full math functionality

2. **HIGH - Temporary File Security** ✅ FIXED
   - **Issue**: Hardcoded /tmp paths vulnerable to TOCTOU race conditions
   - **Fix**: Use tempfile.NamedTemporaryFile with automatic cleanup
   - **Result**: Secure, cross-platform, no race conditions

3. **MEDIUM - Student Model Loading** ✅ FIXED
   - **Issue**: OODA loop called with student_model=None
   - **Fix**: Load student model from repository before OODA loop execution
   - **Result**: OODA loop receives actual student data for better decisions

4. **MEDIUM - Type Safety** ✅ FIXED
   - **Issue**: Using Any for transcript_buffer and silence_detector
   - **Fix**: Added proper type hints using TYPE_CHECKING and forward references
   - **Result**: Better IDE support, type checking, and maintainability

5. **MEDIUM - Documentation** ✅ FIXED
   - **Issue**: README listed AI tools as TODO when already implemented
   - **Fix**: Updated Next Steps section to remove completed items
   - **Result**: Documentation accurately reflects current implementation state

**Next Steps:**
- Integrate tools with OODA loop decision-making
- Test the WebSocket server with real audio/video
- Complete OODA loop intervention logic (Phase 6)
- Add Excalidraw integration for better whiteboard
- PWA manifest for mobile support

### Next Steps
According to IMPLEMENTATION_PLAN.md and STATUS.md, we need to work on:
1. **Phase 1**: Audio WebSocket Integration ✅ DONE
2. **Phase 2**: Vision WebSocket Integration ✅ DONE
3. **Phase 5**: AI Tool System ✅ DONE
4. **Phase 6**: Intervention System (decision-making and TTS) - PARTIAL (TTS done, decision logic needs integration)
5. **Phase 7**: Full MVP Integration (Gradio/Flask UI, PWA, Excalidraw)

### Key Constraints
- Local-first architecture (only OpenRouter for LLM calls)
- Use `uv` for Python package management (per AGENTS.md)
- Save learnings to this file as development progresses

### Technical Notes
- All tests passing (37/37)
- WebSocket server ready for testing
- Pedagogical tools ready for OODA loop integration
- **SECURITY**: AST-based math eval (no eval(), no arbitrary code execution)
- **SECURITY**: tempfile module for secure temporary files (no race conditions)
- **CODE QUALITY**: Proper type hints with TYPE_CHECKING for better IDE support
- Need to configure OpenRouter API key in .env file to test
- Whisper STT needs audio in WAV format
- Canvas sends frames as base64-encoded PNG images every 3 seconds
- Tools use simple heuristics - can be enhanced with ML later if needed
- Student model now loaded from repository before OODA loop execution
