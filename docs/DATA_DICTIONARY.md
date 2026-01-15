# OAIT Data Dictionary

This document defines the canonical naming conventions and data structures used throughout the OAIT codebase. All modules should adhere to these definitions.

## Naming Conventions

### General Rules
- Use `snake_case` for variables, functions, and file names
- Use `PascalCase` for class names
- Use `SCREAMING_SNAKE_CASE` for constants
- Prefix boolean variables with `is_`, `has_`, `should_`, `can_`
- Suffix duration values with `_duration` or `_seconds`
- Suffix timestamp values with `_time` or `_timestamp` or `_at`

### Module-Specific Prefixes
| Module | Prefix Example | Description |
|--------|----------------|-------------|
| Audio | `audio_`, `transcript_`, `speech_` | Audio processing |
| Vision | `image_`, `frame_`, `visual_` | Image processing |
| Cognitive | `ooda_`, `trigger_`, `decision_` | OODA loop |
| Models | `student_`, `session_` | Data models |

---

## Core Data Models

### StudentModel
**Location**: `src/oait/models/data_models.py`  
**Purpose**: Long-term student profile persisted across sessions

| Field | Type | Description |
|-------|------|-------------|
| `student_id` | `str` | Unique identifier for the student |
| `competencies` | `Dict[str, CompetencyLevel]` | Topic → competency mapping |
| `pedagogy_profile` | `PedagogyProfile` | Learning preferences |
| `session_history` | `List[SessionHistoryEntry]` | Past session summaries |
| `created_at` | `datetime` | When profile was created |
| `updated_at` | `datetime` | Last modification time |

### SessionState
**Location**: `src/oait/models/data_models.py`  
**Purpose**: Working memory for active tutoring session

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | `str` | Unique session identifier (UUID) |
| `student_id` | `str` | Reference to StudentModel |
| `current_problem_image` | `Optional[Image]` | Latest whiteboard capture |
| `last_significant_change` | `float` | Timestamp of last visual change |
| `student_speech_buffer` | `List[TranscriptEntry]` | Recent speech transcripts |
| `silence_duration` | `float` | Current silence in seconds |
| `ai_internal_monologue` | `List[InternalMonologue]` | AI thought history |
| `student_is_speaking` | `bool` | Currently speaking? |
| `student_is_writing` | `bool` | Currently writing? |
| `last_intervention_time` | `float` | When AI last spoke |
| `transcript_buffer` | `TranscriptBuffer` | Runtime transcript manager |
| `silence_detector` | `SilenceDetector` | Runtime silence tracker |

---

## OODA Loop Data Types

### The OODA Cycle
```
Observation → Analysis → Decision → Action
     ↓            ↓           ↓         ↓
 Observation   Analysis    Decision   (side effect)
     └──────────────┴───────────┘
                    ↓
            InternalMonologue
```

### Observation
**Purpose**: Raw aggregated data from sensors (audio + visual)

| Field | Type | Description |
|-------|------|-------------|
| `visual` | `str` | Description of whiteboard content |
| `audio` | `str` | Recent speech transcript text |
| `context` | `Dict[str, Any]` | Additional context (silence, activity) |
| `timestamp` | `datetime` | When observation was made |

### Analysis
**Purpose**: Interpretation of observation (student state assessment)

| Field | Type | Description |
|-------|------|-------------|
| `student_state` | `StudentState` | ENGAGED, CONFUSED, STUCK, MAKING_PROGRESS |
| `error_detected` | `bool` | Was an error detected? |
| `error_type` | `ErrorType` | NONE, CONCEPTUAL, COMPUTATIONAL, NOTATION |
| `error_severity` | `ErrorSeverity` | NONE, MINOR, MODERATE, CRITICAL |
| `explicit_question` | `bool` | Did student ask a question? |
| `confidence` | `float` | 0.0-1.0 confidence in analysis |

### Decision
**Purpose**: What action to take based on analysis

| Field | Type | Description |
|-------|------|-------------|
| `action` | `ActionDecision` | WAIT, SPEAK, UPDATE_DB |
| `reasoning` | `str` | Why this decision was made |
| `confidence` | `float` | 0.0-1.0 confidence in decision |
| `strategy` | `Optional[InterventionStrategy]` | SOCRATIC, DIRECT, HINT, EXAMPLE |
| `response_text` | `Optional[str]` | Text to speak if action=SPEAK |
| `estimated_duration` | `float` | Expected intervention duration |
| `fallback_plan` | `str` | Backup if primary fails |

### InternalMonologue
**Purpose**: Complete record of one OODA cycle

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | `datetime` | When cycle completed |
| `observation` | `Observation` | What was observed |
| `analysis` | `Analysis` | How it was interpreted |
| `decision` | `Decision` | What was decided |

**⚠️ IMPORTANT**: `OODALoop.run_cycle()` returns `InternalMonologue`, not `Decision`!

Access pattern:
```python
monologue = await ooda_loop.run_cycle(session_state, student_model)
if monologue.decision.action == ActionDecision.SPEAK:
    text = monologue.decision.response_text
```

---

## Enums

### StudentState
```python
ENGAGED = "engaged"           # Working productively
CONFUSED = "confused"         # Showing confusion signals
STUCK = "stuck"              # Not making progress
MAKING_PROGRESS = "making_progress"  # Actively improving
```

### ActionDecision
```python
WAIT = "WAIT"                # Continue observing
SPEAK = "SPEAK"              # Intervene verbally
UPDATE_DB = "UPDATE_DB"      # Update student model
```

### InterventionStrategy
```python
SOCRATIC = "socratic"        # Guide with questions
DIRECT = "direct"            # Provide direct answer
HINT = "hint"                # Give a hint
EXAMPLE = "example"          # Show worked example
```

### ErrorType
```python
NONE = "none"
CONCEPTUAL = "conceptual"    # Misunderstanding concept
COMPUTATIONAL = "computational"  # Arithmetic error
NOTATION = "notation"        # Writing/notation error
```

### CompetencyLevel
```python
UNKNOWN = "unknown"
STRUGGLING = "struggling"
MASTERED = "mastered"
```

---

## Audio Components

### TranscriptEntry
**Purpose**: Single timestamped transcript segment

| Field | Type | Description |
|-------|------|-------------|
| `text` | `str` | Transcribed text |
| `timestamp` | `float` | Unix timestamp when spoken |

### TranscriptBuffer
**Location**: `src/oait/audio/stream_handler.py`  
**Purpose**: Sliding window of recent transcripts

| Method | Returns | Description |
|--------|---------|-------------|
| `append(text, timestamp)` | `None` | Add transcript |
| `get_recent(duration)` | `List[dict]` | Get last N seconds |
| `get_all()` | `List[dict]` | Get entire buffer |
| `clear()` | `None` | Empty the buffer |

**Constructor**: `TranscriptBuffer(duration=30.0)`

### SilenceDetector
**Location**: `src/oait/audio/stream_handler.py`  
**Purpose**: Track silence duration

| Method | Returns | Description |
|--------|---------|-------------|
| `update(has_speech)` | `None` | Update with speech detection |
| `get_silence_duration()` | `float` | Current silence in seconds |
| `reset()` | `None` | Reset detector |

**Constructor**: `SilenceDetector(threshold=3.0)`

---

## WebSocket Message Types

### Client → Server

```json
// Audio chunk
{
  "type": "audio",
  "data": "<base64-encoded-wav>"
}

// Video frame
{
  "type": "video",
  "data": "<base64-encoded-png>"
}

// Heartbeat
{
  "type": "ping"
}
```

### Server → Client

```json
// Transcript update
{
  "type": "transcript",
  "text": "What is two plus two?",
  "timestamp": 1705320000.123
}

// AI intervention
{
  "type": "ai_response",
  "text": "That's a great question! What do you think happens when...",
  "strategy": "socratic"
}

// Heartbeat response
{
  "type": "pong"
}
```

---

## API Endpoints

| Method | Path | Description | Returns |
|--------|------|-------------|---------|
| GET | `/` | Serve web client | HTML |
| GET | `/health` | Health check | `{"status": "healthy"}` |
| POST | `/session/start?student_id=X` | Start session | `{"session_id": "...", "status": "active"}` |
| POST | `/session/{id}/stop` | Stop session | `{"session_id": "...", "status": "stopped"}` |
| WS | `/ws/{session_id}` | WebSocket connection | Bidirectional messages |

---

## Common Patterns

### Getting Recent Transcripts
```python
# From SessionState (returns TranscriptEntry objects)
entries = session_state.get_recent_transcripts(duration=10.0)
text = " ".join([e.text for e in entries])

# From TranscriptBuffer (returns dicts)
entries = session_state.transcript_buffer.get_recent(duration=10.0)
text = " ".join([e["text"] for e in entries])
```

### Checking Triggers
```python
# Returns (bool, List[str]) - (should_trigger, reasons)
should_trigger, reasons = trigger_detector.check_triggers(session_state)

# Convenience method - just returns bool
should_trigger = trigger_detector.should_trigger_analysis(session_state)
```

### Running OODA Cycle
```python
# Returns InternalMonologue (NOT Decision!)
monologue = await ooda_loop.run_cycle(session_state, student_model)

# Access the decision
if monologue and monologue.decision.action == ActionDecision.SPEAK:
    response = monologue.decision.response_text
    strategy = monologue.decision.strategy
```

---

## File Organization

```
src/oait/
├── config.py              # Settings (loaded from .env)
├── api/
│   └── openrouter.py      # LLM API client
├── audio/
│   ├── stream_handler.py  # TranscriptBuffer, SilenceDetector
│   └── whisper_stt.py     # WhisperSTT class
├── cognitive/
│   ├── loop.py            # OODALoop class
│   └── triggers.py        # TriggerDetector class
├── models/
│   ├── data_models.py     # All Pydantic models & enums
│   └── repository.py      # StudentModelRepository (SQLite)
├── server/
│   ├── websocket_server.py # FastAPI app
│   └── static/index.html   # Web client
├── tools/
│   └── pedagogical.py     # PedagogicalTools
└── vision/
    ├── analyzer.py        # VisionAnalyzer
    └── preprocessor.py    # ImagePreprocessor
```

---

*Last Updated: January 15, 2026*
