# OAIT Technical Specification

## 1. System Overview

OAIT (Observational AI Tutor) is a proactive, observational AI system designed for educational contexts. Unlike reactive chatbots, OAIT continuously monitors a student's work and speech, maintaining an internal mental model and only intervening when pedagogically appropriate.

### 1.1 Core Principle: The OODA Loop

The system operates on a continuous **Observe-Orient-Decide-Act** cycle:

1. **Observe**: Ingest multimodal data (audio + video)
2. **Orient**: Update internal state and mental models
3. **Decide**: Evaluate intervention necessity against thresholds
4. **Act**: Either remain silent, update database, or speak

### 1.2 Key Differentiator

**Standard Chatbot**: `User Input → Bot Output`  
**OAIT**: `Continuous Input → Analysis → Decision → Conditional Action/Inaction`

## 2. Data Structures

### 2.1 Student Model (Long-Term Memory)

Persistent storage tracking student capabilities across sessions.

```json
{
  "student_id": "string",
  "competencies": {
    "topic_name": "mastered | struggling | unknown"
  },
  "pedagogy_profile": {
    "patience_level": "low | medium | high",
    "preferred_learning_style": "visual | verbal | kinesthetic",
    "preferred_analogies": "string",
    "response_to_correction": "string",
    "optimal_intervention_delay": "float (seconds)"
  },
  "session_history": [
    {
      "date": "ISO8601",
      "topics_covered": ["string"],
      "breakthroughs": ["string"],
      "persistent_errors": ["string"]
    }
  ]
}
```

### 2.2 Session Context (Short-Term Memory)

Working memory for current tutoring session.

```python
class SessionState:
    # Visual context
    current_problem_image: Image
    last_significant_change: float  # timestamp
    
    # Audio context
    student_speech_buffer: List[str]  # Last N seconds
    silence_duration: float
    
    # Cognitive context
    ai_internal_monologue: List[Dict]
    current_problem_analysis: Dict
    intervention_candidates: List[str]
    
    # State tracking
    student_is_speaking: bool
    student_is_writing: bool
    last_intervention_time: float
```

## 3. System Architecture

### 3.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STUDENT DEVICE (Browser)                          │
│  (Android Phone / Mac Mini / Windows Laptop)                        │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ getUserMedia │  │  Whiteboard  │  │ Web Speech API (TTS)     │  │
│  │   (Audio)    │  │  (Canvas)    │  │ (Browser-native, free)   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────────────┘  │
└─────────┼─────────────────┼─────────────────────────────────────────┘
          │                 │
          │    WebSocket    │
          ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│              HOUSEHOLD SERVER (Ubuntu/Windows + Python)              │
│                                                                      │
│  ┌─────────────────────────┐  ┌─────────────────────────────────┐  │
│  │   Gradio/Flask Web UI   │  │   Local Whisper STT             │  │
│  │   (Port 7860)           │  │   (faster-whisper, no API key)  │  │
│  └───────────┬─────────────┘  └────────────────┬────────────────┘  │
│              │                                  │                    │
│       ┌──────▼──────────────────────────────────▼──────┐            │
│       │            Event Aggregator                     │            │
│       │          (Trigger Detection)                    │            │
│       └──────────────────┬──────────────────────────────┘            │
│                          │                                           │
│       ┌──────────────────▼──────────────────────────────┐            │
│       │              Cognitive Loop                      │            │
│       │            (OODA Implementation)                 │            │
│       │  ┌────────────────────────────────────────────┐ │            │
│       │  │ Observe → Orient → Decide → Act            │ │            │
│       │  └────────────────────────────────────────────┘ │            │
│       └──────────────────┬──────────────────────────────┘            │
│                          │                                           │
│       ┌──────────────────▼──────────────────────────────┐            │
│       │              OpenRouter Client                   │            │
│       │  (All LLM calls routed here - geo-free)         │            │
│       └──────────────────┬──────────────────────────────┘            │
└──────────────────────────┼──────────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         OpenRouter.ai                                │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Gemini 3 Pro (Preferred)                                    │    │
│  │  ✓ Image input/output   ✓ Tool calling   ✓ High reasoning   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ⚠️ Note: OpenAI/Anthropic are geo-blocked - must use OpenRouter    │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Asynchronous Event Loop

The system runs multiple concurrent tasks:

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        # Parallel streams
        tg.create_task(audio_stream_handler())
        tg.create_task(video_stream_handler())
        tg.create_task(cognitive_loop())
        
        # State management
        tg.create_task(buffer_manager())
        tg.create_task(database_sync())
```

## 4. Core Algorithms

### 4.1 Trigger Detection

The cognitive loop activates based on specific triggers:

```python
def should_trigger_analysis() -> bool:
    triggers = [
        silence_duration > threshold,
        significant_whiteboard_change(),
        explicit_question_detected(),
        error_pattern_matches(),
        stuck_indicator_present()
    ]
    return any(triggers)
```

### 4.2 Internal Monologue Format

The AI's thought process follows a structured format:

```json
{
  "timestamp": "ISO8601",
  "observation": {
    "visual": "Description of what's on whiteboard",
    "audio": "Summary of recent speech",
    "context": "Relevant student model data"
  },
  "analysis": {
    "student_state": "engaged | confused | stuck | making_progress",
    "error_detected": "bool",
    "error_type": "conceptual | computational | notation",
    "error_severity": "critical | moderate | minor"
  },
  "decision": {
    "action": "WAIT | UPDATE_DB | SPEAK",
    "reasoning": "Why this action was chosen",
    "confidence": "0.0 to 1.0"
  },
  "strategy": {
    "approach": "socratic | direct | hint | example",
    "estimated_duration": "seconds",
    "fallback_plan": "What to do if student doesn't respond"
  }
}
```

### 4.3 Intervention Decision Algorithm

```python
def decide_intervention(
    analysis: Dict,
    student_model: StudentModel,
    session_state: SessionState
) -> ActionDecision:
    
    # Priority 1: Explicit request
    if analysis['explicit_question']:
        return ActionDecision.SPEAK
    
    # Priority 2: Critical error propagation
    if analysis['error_severity'] == 'critical' and \
       analysis['student_state'] == 'making_progress':
        # Student is continuing with wrong foundation
        return ActionDecision.SPEAK
    
    # Priority 3: Extended stuck state
    if session_state.silence_duration > \
       student_model.optimal_intervention_delay * 2:
        return ActionDecision.SPEAK
    
    # Default: Observe more
    if analysis['confidence'] < 0.7:
        return ActionDecision.WAIT
    
    # Minor issue: Just record it
    if analysis['error_severity'] == 'minor':
        return ActionDecision.UPDATE_DB
    
    return ActionDecision.WAIT
```

## 5. AI Model Integration

### 5.1 Vision Processing

The system periodically (every 2-5 seconds) captures and analyzes whiteboard frames:

```python
async def vision_processor():
    while session_active:
        frame = await video_stream.capture()
        
        # Preprocess
        clean_frame = preprocess_whiteboard(frame)
        
        # Vision LLM analysis
        analysis = await vision_llm.analyze(
            image=clean_frame,
            prompt=VISION_ANALYSIS_PROMPT,
            context=session_state.current_problem_analysis
        )
        
        # Update session state
        session_state.current_problem_image = clean_frame
        session_state.last_significant_change = time.time()
        
        await asyncio.sleep(VISION_POLLING_INTERVAL)
```

### 5.2 Audio Processing

Continuous speech-to-text with buffer management:

```python
async def audio_processor():
    async for audio_chunk in audio_stream:
        # STT
        text = await stt_service.transcribe(audio_chunk)
        
        if text:
            session_state.student_speech_buffer.append({
                'text': text,
                'timestamp': time.time()
            })
            
            # Maintain sliding window
            cutoff = time.time() - BUFFER_DURATION
            session_state.student_speech_buffer = [
                item for item in session_state.student_speech_buffer
                if item['timestamp'] > cutoff
            ]
```

### 5.3 LLM Tool System

The AI uses function calling to "think" before acting:

```python
INTERNAL_TOOLS = [
    {
        "name": "update_student_model",
        "description": "Record observation about student capability",
        "parameters": {
            "topic": "str",
            "observation": "str",
            "severity": "info | warning | critical"
        }
    },
    {
        "name": "consult_pedagogy_db",
        "description": "Retrieve teaching strategies for this student",
        "parameters": {
            "query": "str"
        }
    },
    {
        "name": "verify_calculation",
        "description": "Verify mathematical calculation programmatically",
        "parameters": {
            "expression": "str",
            "student_answer": "str"
        }
    },
    {
        "name": "assess_confusion_level",
        "description": "Analyze speech patterns for confusion indicators",
        "parameters": {
            "transcript": "str"
        }
    }
]
```

## 6. Pedagogical Intelligence

### 6.1 Intervention Strategies

Based on student model and current situation:

- **Socratic Questioning**: Guide with questions rather than answers
- **Scaffolding**: Break down problem into smaller steps
- **Direct Instruction**: Explicitly teach missing concept
- **Worked Example**: Demonstrate similar problem
- **Analogical Reasoning**: Connect to known concepts

### 6.2 Adaptive Timing

The system learns optimal intervention timing per student:

```python
def calculate_optimal_delay(student_model, context):
    base_delay = 3.0  # seconds
    
    # Adjust based on student profile
    if student_model.patience_level == 'high':
        base_delay *= 2.0
    elif student_model.patience_level == 'low':
        base_delay *= 0.5
    
    # Adjust based on context
    if context.topic in student_model.known_struggles:
        base_delay *= 0.7  # Intervene sooner
    
    return base_delay
```

## 7. Privacy and Security

### 7.1 Data Storage

- Student models stored locally or in encrypted database
- Video frames not persisted unless explicitly requested
- Audio transcripts retained only for session duration
- All PII encrypted at rest

### 7.2 Consent and Control

- Students can pause observation at any time
- Clear indicators when AI is "watching" vs. "thinking" vs. "speaking"
- Option to review AI's internal monologue (for metacognitive learning)

## 8. Performance Requirements

### 8.1 Latency Targets

- Audio transcription: < 300ms
- Vision analysis: < 2s (acceptable since periodic)
- Intervention decision: < 500ms
- Speech synthesis: < 1s

### 8.2 Accuracy Targets

- Transcription accuracy: > 95%
- Error detection accuracy: > 90%
- False positive intervention rate: < 10%

## 9. Testing Strategy

### 9.1 Unit Tests

- Individual tool functions
- Data structure validation
- Trigger detection logic

### 9.2 Integration Tests

- Audio/video stream handling
- LLM integration
- Database operations

### 9.3 End-to-End Tests

- Simulated tutoring sessions
- Intervention timing validation
- Student model updates

### 9.4 User Testing

- Real student sessions with feedback
- Intervention appropriateness ratings
- Learning outcome measurements

## 10. Deployment Architecture

### 10.1 Household Server Setup

The system runs on a household server (Ubuntu or Windows) accessible via LAN:

```
┌─────────────────────────────────────────────────────────────┐
│                    HOUSEHOLD LAN                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────────────────────────┐  │
│  │ Android Phone │    │     Household Server             │  │
│  │ Mac Mini      │───▶│  (Ubuntu/Windows + Python)       │  │
│  │ Windows Laptop│    │                                  │  │
│  └──────────────┘    │  ┌─────────────┐ ┌────────────┐  │  │
│      (Clients)       │  │ Gradio/Flask│ │  Whisper   │  │  │
│                      │  │  Frontend   │ │ (Local STT)│  │  │
│                      │  └─────────────┘ └────────────┘  │  │
│                      └──────────────┬───────────────────┘  │
└─────────────────────────────────────│───────────────────────┘
                                      │
                           ┌──────────▼──────────┐
                           │   OpenRouter.ai     │
                           │  (Geo-free routing) │
                           │                     │
                           │  ┌───────────────┐  │
                           │  │ Gemini 3 Pro  │  │
                           │  │ (Preferred)   │  │
                           │  └───────────────┘  │
                           └─────────────────────┘
```

### 10.2 API Constraints

> ⚠️ **CRITICAL**: OpenAI and Anthropic APIs are geo-blocked. All LLM calls MUST route through OpenRouter.ai.

**OpenRouter Tool Support**: Not all models support function calling. Verify model capabilities before use.

**Preferred Model**: Gemini 3 Pro (via OpenRouter)
- ✅ High-quality reasoning and understanding
- ✅ Image input support
- ✅ Image output support  
- ✅ Tool/function calling support

### 10.3 Cost Optimization (MVP)

| Service | MVP (Local/Free) | Post-MVP (Paid) |
|---------|------------------|------------------|
| STT | Whisper (local server) | Deepgram |
| TTS | Web Speech API (browser) | ElevenLabs |
| LLM | Gemini 3 Pro (OpenRouter) | Same |
| Vision | Gemini 3 Pro (OpenRouter) | Same |

## 11. Extensibility

### 11.1 Subject Domains

Initial focus: Mathematics  
Future: Physics, Chemistry, Programming, Writing

### 11.2 Interface Modalities

Current: Digital whiteboard + voice  
Future: Physical whiteboard via camera, gesture recognition, multiple students

### 11.3 AI Models

Designed to be model-agnostic with adapter pattern (all via OpenRouter):
- Vision/Reasoning: Gemini 3 Pro (preferred), Claude 3 Opus, GPT-4o
- STT: Faster-Whisper (local), Deepgram (future)
- TTS: Web Speech API (MVP), ElevenLabs (future)

## 12. Open Questions

1. How to handle multiple students in one session?
2. Optimal buffer sizes for different age groups?
3. Should the AI ever show its "internal monologue" to students?
4. How to balance intervention frequency across student diversity?
5. What metrics best indicate successful tutoring?
6. Which OpenRouter models support tool calling reliably?
7. Fallback strategy when OpenRouter is unavailable?
8. How to handle Whisper latency on lower-powered servers?
