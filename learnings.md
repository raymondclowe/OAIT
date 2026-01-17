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
- Tests: 34/37 passing (3 failures to fix)
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

## 2026-01-15: uv Setup Complete

### Environment Setup
- ✅ Installed uv package manager via curl
- ✅ Created virtual environment with `uv venv`
- ✅ Installed all dependencies (100 packages)
- ✅ Package installed in editable mode with `uv pip install -e .`

### Test Status
**37/37 tests passing (100%)**

### Fixes Applied
1. **test_config.py**: Updated to accept both model names
2. **data_models.py**: Changed forward refs to `Any` type (no model_rebuild needed)
3. **triggers.py**: Added `should_trigger_analysis()` wrapper method
4. **websocket_server.py**: Fixed `TranscriptBuffer(duration=...)`, `silence_detector.update(has_speech=True)`
5. **whisper_stt.py**: Added file path support with soundfile
6. **loop.py**: Added `_generate_response()` method for LLM-based response generation
7. **requirements.txt**: Added soundfile dependency
8. **setup.sh**: Created comprehensive setup script

### Audio Trigger Design
- Continuous transcription happens via Whisper
- After each transcript, trigger detector checks if OODA should run
- Triggers include: explicit questions ("?", "how do", "help"), silence threshold, initial analysis
- When triggered, OODA decides if AI should SPEAK, WAIT, or UPDATE_DB
- If SPEAK, generates response via OpenRouter LLM

**Note**: ✅ Fixed deprecation warning for `ast.Num` in pedagogical.py - removed Python 3.7 compatibility code

## 2026-01-17: Testing and Quality Improvements

### Integration Tests Added
Created comprehensive integration tests (`tests/integration/test_component_integration.py`) covering:
- Calculation verification workflow
- Confusion detection at different levels
- Question detection accuracy  
- Stuck pattern detection
- Intervention strategy selection
- Trigger detection on silence
- Tool definitions format validation
- Complete analysis workflows (end-to-end)

**Test Status: 46/46 passing (100%)**
- 37 unit tests
- 9 integration tests
- Zero warnings
- All deprecation warnings fixed

### Code Quality
- Fixed Python 3.14 deprecation warning (ast.Num → ast.Constant)
- All pedagogical tools properly tested in integration scenarios
- Complete workflows validated (transcript → analysis → strategy)
- Tool definitions validated for OpenRouter compatibility

### PWA Support Added
Created Progressive Web App support for mobile and desktop installation:
- **manifest.json**: App metadata, icons, display mode
- **sw.js**: Service worker for offline caching
- **Icons**: 192x192 and 512x512 SVG-based app icons
- **Documentation**: Complete PWA guide in docs/PWA.md

**PWA Features:**
- Install on Android, iOS, Windows, Mac, Linux
- Offline UI access (cached static assets)
- Standalone app experience (no browser chrome)
- Network-first caching strategy
- Automatic cache updates

## 2026-01-15: Semaphore Leak Fix

### Issue
When stopping the uvicorn reloader, Python's multiprocessing resource tracker warned about 2 leaked semaphore objects. This is caused by the `faster-whisper` library which uses CTranslate2/OpenMP internally.

### Fixes Applied
1. **websocket_server.py**: Added `@app.on_event("shutdown")` handler to:
   - Unload Whisper model (releases semaphores)
   - Close active WebSocket connections
   - Clear session state and server components
   
2. **whisper_stt.py**: Enhanced `unload_model()` to force garbage collection after deleting model

3. **start_server.py**: Set multiprocessing start method to 'spawn' to improve resource cleanup

### Result
Clean shutdown without semaphore leak warnings

## 2026-01-15: Pull-Based Architecture Refactor

### Problem
Original push-based architecture flooded server with constant audio/video data, making logs unusable and wasting resources.

### Solution: AI-Pull Model
Changed to pull-based architecture where AI (OODA loop) is in control:

1. **Client buffers locally** - Audio with VAD, whiteboard changes tracked
2. **Server polls periodically** - OODA loop runs every 5 seconds
3. **Server requests data** - Sends `{type: 'request', resource: 'audio'}` 
4. **Client responds on demand** - Only sends data when AI asks for it

### Implementation
- `index.html`: Client buffers audio segments with Voice Activity Detection
- `websocket_server.py`: Added `request_from_client()` and polling loop
- WebSocket protocol: `request` → `response` pattern with `request_id`

## 2026-01-15: OpenRouter Tool Calling

### Key Points (from OpenRouter docs)
OpenRouter uses **standard OpenAI function calling format** but has specific requirements:

1. **Three-step flow**:
   - Step 1: Send request with `tools` array → model returns `tool_calls`
   - Step 2: Execute tool locally (client-side)
   - Step 3: Send result back with `role: "tool"` and `tool_call_id`

2. **Critical**: `tools` must be included in EVERY request (even step 3) for router validation

3. **Tool result format**:
```python
{
    "role": "tool",
    "tool_call_id": "call_abc123",  # Must match the request
    "content": '{"result": "..."}'   # JSON string
}
```

4. **Tool definition format** (same as OpenAI):
```python
{
    "type": "function",
    "function": {
        "name": "get_audio",
        "description": "Get recent audio from student",
        "parameters": {
            "type": "object",
            "properties": {
                "duration_seconds": {"type": "number"}
            },
            "required": ["duration_seconds"]
        }
    }
}
```

### Implementation
Added `chat_with_tools()` method to `OpenRouterClient` that:
- Handles the full tool calling loop automatically
- Takes `tool_handlers` dict mapping names to async functions
- Manages message history with proper `tool_call_id` matching
- Includes iteration limit to prevent infinite loops

## 2026-01-15: Comprehensive AI Tool System

### Architecture Change
Implemented a **tool-based OODA loop** where the AI controls everything via function calling.

**New Files:**
- `src/oait/tools/ai_tools.py`: Tool definitions and handlers
- `src/oait/cognitive/tool_loop.py`: New ToolOODALoop class

### Tool Categories (12 tools total)

**Observation Tools (5):**
1. `get_audio_transcript` - Get recent speech from student via Whisper STT
2. `get_whiteboard` - Get current whiteboard image, optionally analyze it
3. `get_camera_feed` - Get camera feed for emotion analysis
4. `get_student_profile` - Get pedagogical profile (learning style, patience)
5. `get_session_status` - Get session state (silence duration, activity)

**Action Tools (4):**
1. `speak` - Say something aloud to student via TTS
2. `update_student_model` - Update understanding/frustration/engagement levels
3. `send_visual_hint` - Display hints (highlight, diagram, formula, example)
4. `log_observation` - Internal logging for debugging

**Control Tools (3):**
1. `wait_for_event` - Wait until speech/silence/whiteboard_change or timeout
2. `set_observation_mode` - Change polling frequency (active/passive/intervention)
3. `end_observation_cycle` - End cycle with decision (wait/speak/observe_again)

### Key Design Decisions

1. **AI is fully in control**: Unlike the old polling-based approach, the AI decides:
   - What to observe (audio? whiteboard? camera?)
   - When to act (speak? update model?)
   - How long to wait (wait_for_event with timeout)

2. **Pull-based WebSocket**: Tools request data from client on-demand
   - Client buffers audio/whiteboard locally
   - Server sends `{type: "request", request_id, resource}` 
   - Client responds `{type: "response", request_id, data}`

3. **System prompt guides behavior**: AI tutor follows pedagogical principles:
   - Don't interrupt if student is making progress
   - Wait for struggle before helping (builds problem-solving)
   - Use Socratic questioning
   - Adapt to student's learning style

4. **ToolContext** bundles all dependencies:
   - session_state, student_model, websocket
   - repository, whisper_stt, vision_analyzer
   - pending_requests dict for async request/response

### Usage Pattern
```python
# Create context with all dependencies
tool_context = ToolContext(
    session_state=session_state,
    student_model=student_model,
    websocket=websocket,
    ...
)

# Create tool-based OODA loop
tool_ooda = ToolOODALoop(
    openrouter_client=openrouter,
    context=tool_context,
)

# Run continuously
await tool_ooda.start()
```

### Typical AI Cycle
1. Call `get_session_status()` to understand state
2. Call `get_audio_transcript()` to hear student
3. If working on visual: call `get_whiteboard()`
4. Decide: `speak()` if needs help, else `wait_for_event()`
5. Call `end_observation_cycle()` with decision

