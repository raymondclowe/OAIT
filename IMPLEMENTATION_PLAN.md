# OAIT Implementation Plan

## Phased Development Strategy

This plan breaks down the OAIT implementation into testable phases, with each phase building toward a functional MVP. Each phase includes specific deliverables, acceptance criteria, and testing strategies.

---

## Phase 0: Project Foundation (Week 1)

**Goal**: Establish project infrastructure and development environment

### Deliverables
- [x] Project documentation (README, SPECIFICATION, TODO)
- [ ] Repository structure
- [ ] Development environment setup
- [ ] Dependency management (requirements.txt)
- [ ] Configuration management (.env.example)
- [ ] CI/CD pipeline basics

### Directory Structure
```
/OAIT
  /docs              # Additional documentation
  /src
    /oait
      /agents        # LiveKit agent implementation
      /audio         # Audio processing
      /vision        # Vision processing
      /cognitive     # OODA loop and decision making
      /models        # Data models and state
      /tools         # AI tool functions
      /utils         # Shared utilities
  /tests
    /unit
    /integration
    /e2e
  /config            # Configuration files
  /memory            # Student model storage
  README.md
  SPECIFICATION.md
  IMPLEMENTATION_PLAN.md
  TODO.md
  requirements.txt
  .env.example
```

### Testing
- [ ] Verify all directories created
- [ ] Confirm dependencies install cleanly
- [ ] Validate configuration loading

### Success Criteria
- Clean repository structure
- Documentation in place
- Development environment reproducible

---

## Phase 1: Basic Audio Pipeline (Week 2)

**Goal**: Implement audio capture, transcription, and buffer management

### Deliverables
- [ ] Audio stream ingestion from LiveKit
- [ ] Speech-to-text integration (Deepgram or Whisper)
- [ ] Transcript buffer with sliding window
- [ ] Basic silence detection
- [ ] Audio pipeline unit tests

### Core Components

```python
# src/oait/audio/stream_handler.py
class AudioStreamHandler:
    async def capture_audio() -> AudioChunk
    async def transcribe(audio: AudioChunk) -> str
    
# src/oait/audio/buffer.py
class TranscriptBuffer:
    def append(text: str, timestamp: float)
    def get_recent(duration: float) -> List[str]
    def clear()
```

### Testing
- [ ] Unit test: Buffer maintains correct window size
- [ ] Unit test: Silence detection accuracy
- [ ] Integration test: End-to-end audio capture to transcript
- [ ] Manual test: Real microphone input transcription

### Success Criteria
- Audio consistently transcribed with < 500ms latency
- Buffer correctly maintains 30-second sliding window
- Silence detection triggers within 1 second accuracy

---

## Phase 2: Basic Vision Pipeline (Week 3)

**Goal**: Implement video capture and basic image analysis

### Deliverables
- [ ] Video stream ingestion from LiveKit
- [ ] Frame capture at configurable intervals
- [ ] Basic image preprocessing (crop, denoise)
- [ ] Vision LLM integration (GPT-4o or Moondream)
- [ ] Vision pipeline unit tests

### Core Components

```python
# src/oait/vision/stream_handler.py
class VideoStreamHandler:
    async def capture_frame() -> Image
    async def preprocess(image: Image) -> Image
    
# src/oait/vision/analyzer.py
class VisionAnalyzer:
    async def analyze_whiteboard(image: Image) -> Dict
    async def detect_changes(prev: Image, curr: Image) -> bool
```

### Testing
- [ ] Unit test: Frame capture at specified intervals
- [ ] Unit test: Image preprocessing consistency
- [ ] Integration test: Vision LLM returns valid analysis
- [ ] Manual test: Analyze actual whiteboard images

### Success Criteria
- Frames captured reliably every 2-5 seconds
- Vision LLM correctly describes whiteboard content
- Change detection identifies significant updates

---

## Phase 3: Data Models and State Management (Week 4)

**Goal**: Implement student model and session state persistence

### Deliverables
- [ ] Student model data structure
- [ ] Session state data structure
- [ ] Database abstraction layer (JSON or SQLite)
- [ ] State management unit tests
- [ ] Model migration system

### Core Components

```python
# src/oait/models/student_model.py
class StudentModel:
    student_id: str
    competencies: Dict[str, str]
    pedagogy_profile: PedagogyProfile
    
    def load(student_id: str) -> StudentModel
    def save()
    def update_competency(topic: str, level: str)

# src/oait/models/session_state.py
class SessionState:
    current_problem_image: Optional[Image]
    student_speech_buffer: List[Dict]
    ai_internal_monologue: List[Dict]
    
    def snapshot() -> Dict
    def restore(snapshot: Dict)
```

### Testing
- [ ] Unit test: Model serialization/deserialization
- [ ] Unit test: State updates maintain consistency
- [ ] Integration test: Persist and reload student model
- [ ] Manual test: Create multiple student profiles

### Success Criteria
- Student models persist correctly
- Session state can be saved and restored
- No data loss during normal operations

---

## Phase 4: Basic OODA Loop (Week 5-6)

**Goal**: Implement minimal cognitive loop without intervention

### Deliverables
- [ ] Event trigger detection system
- [ ] Basic cognitive loop (Observe-Orient only)
- [ ] Internal monologue generation
- [ ] Loop integration tests

### Core Components

```python
# src/oait/cognitive/loop.py
class OODALoop:
    async def observe() -> Observation
    async def orient(obs: Observation) -> Analysis
    async def decide(analysis: Analysis) -> Decision
    async def act(decision: Decision)
    
# src/oait/cognitive/triggers.py
class TriggerDetector:
    def should_analyze(state: SessionState) -> bool
    def get_trigger_reasons() -> List[str]
```

### Testing
- [ ] Unit test: Trigger detection logic
- [ ] Unit test: Observation aggregation
- [ ] Integration test: Complete Observe-Orient cycle
- [ ] Manual test: Log internal monologue during session

### Success Criteria
- Loop triggers appropriately based on events
- Internal monologue follows specified format
- System can "think" without speaking

---

## Phase 5: AI Tool System (Week 7)

**Goal**: Implement tool calling for internal AI reasoning

### Deliverables
- [ ] Tool definition framework
- [ ] Core pedagogical tools
- [ ] Tool execution engine
- [ ] Tool integration tests

### Core Tools

```python
# src/oait/tools/pedagogy.py
def update_student_model(topic: str, observation: str, severity: str)
def consult_pedagogy_db(query: str) -> str
def verify_calculation(expression: str, student_answer: str) -> bool
def assess_confusion_level(transcript: str) -> float
```

### Testing
- [ ] Unit test: Each tool function
- [ ] Unit test: Tool parameter validation
- [ ] Integration test: LLM tool calling
- [ ] Manual test: Tools update state correctly

### Success Criteria
- All tools execute without errors
- LLM correctly calls appropriate tools
- Tool results inform decision making

---

## Phase 6: Intervention System (Week 8)

**Goal**: Complete OODA loop with decision-making and actions

### Deliverables
- [ ] Intervention decision algorithm
- [ ] Text-to-speech integration
- [ ] Action routing system
- [ ] Full OODA loop tests

### Core Components

```python
# src/oait/cognitive/decision.py
class InterventionDecider:
    def decide_intervention(
        analysis: Dict,
        student_model: StudentModel,
        session_state: SessionState
    ) -> ActionDecision
    
# src/oait/agents/actions.py
class ActionRouter:
    async def speak(text: str)
    async def update_db(data: Dict)
    async def wait()
```

### Testing
- [ ] Unit test: Decision algorithm logic
- [ ] Unit test: Intervention threshold calculations
- [ ] Integration test: End-to-end intervention flow
- [ ] Manual test: Real tutoring scenario

### Success Criteria
- Decisions made within 500ms
- Interventions feel natural and timely
- False positive rate < 10%

---

## Phase 7: MVP Integration (Week 9-10)

**Goal**: Integrate all components into working MVP

### Deliverables
- [ ] Complete agent implementation
- [ ] LiveKit room integration
- [ ] Basic web frontend (optional)
- [ ] End-to-end tests
- [ ] User acceptance testing plan

### MVP Features
✅ Audio capture and transcription  
✅ Video capture and analysis  
✅ Student model persistence  
✅ Internal monologue generation  
✅ Basic intervention decisions  
✅ Text-to-speech output  

### Testing
- [ ] E2E test: Complete tutoring session simulation
- [ ] Performance test: Latency measurements
- [ ] User test: Real student sessions (3-5 users)

### Success Criteria
- All components work together
- System meets latency requirements
- Users find interventions helpful

---

## Phase 8: Refinement and Optimization (Week 11-12)

**Goal**: Polish MVP based on feedback

### Deliverables
- [ ] Performance optimizations
- [ ] Error handling improvements
- [ ] Logging and monitoring
- [ ] User feedback integration
- [ ] Documentation updates

### Focus Areas
- Reduce false positive interventions
- Improve speech naturalness
- Optimize resource usage
- Enhanced error recovery

### Testing
- [ ] Load testing with multiple concurrent sessions
- [ ] Edge case testing
- [ ] Extended user testing (10+ hours)

### Success Criteria
- System stable for 1+ hour sessions
- Resource usage acceptable
- Positive user feedback

---

## Phase 9: Advanced Features (Week 13+)

**Goal**: Implement enhancements beyond MVP

### Potential Features
- [ ] Multiple student support
- [ ] Enhanced pedagogy strategies
- [ ] Session replay and analysis
- [ ] Advanced visualization
- [ ] Integration with learning management systems
- [ ] Support for additional subjects
- [ ] Local-only mode (privacy-focused)

---

## Testing Philosophy

Each phase follows this testing pyramid:

```
       /\
      /  \
     / E2E\     ← Few, high-value scenarios
    /------\
   /  Intg. \   ← Component interactions
  /----------\
 /    Unit    \  ← Most tests, fast feedback
/--------------\
```

### Testing Guidelines
1. **Write tests first** for new functionality
2. **Test in isolation** before integration
3. **Use mocks** for external services during development
4. **Run manual tests** for subjective quality (e.g., speech naturalness)
5. **Record test sessions** for regression testing

---

## Risk Management

### Technical Risks
- **Latency**: Multimodal AI can be slow
  - *Mitigation*: Use streaming APIs, optimize polling intervals
  
- **API Costs**: Cloud services can be expensive
  - *Mitigation*: Implement rate limiting, support local models
  
- **Model Accuracy**: AI might misunderstand context
  - *Mitigation*: Extensive testing, confidence thresholds

### Product Risks
- **Over-intervention**: AI interrupts too much
  - *Mitigation*: Conservative thresholds, user feedback loops
  
- **Privacy Concerns**: Recording students
  - *Mitigation*: Clear consent, local-first options, data minimization

---

## Success Metrics

### Technical Metrics
- Audio-to-text latency < 500ms
- Vision analysis latency < 2s
- Decision latency < 500ms
- False positive rate < 10%
- System uptime > 99%

### User Metrics
- Intervention helpfulness rating > 4/5
- Perceived intrusiveness < 2/5
- Session completion rate > 90%
- User return rate > 70%

### Learning Metrics
- Problem completion rate
- Error correction time
- Student confidence scores
- Learning velocity

---

## Dependencies and Prerequisites

### Required Accounts/Keys
- LiveKit account (cloud or self-hosted)
- OpenAI API key (or local Ollama setup)
- Deepgram API key (or local Whisper setup)
- ElevenLabs API key (or local TTS setup)

### Development Tools
- Python 3.9+
- Git
- Docker (optional, for containerization)
- VS Code or similar IDE

### Knowledge Requirements
- Async Python programming
- Real-time audio/video processing
- LLM integration
- Basic pedagogy principles

---

## Iteration Strategy

Each phase follows this cycle:

1. **Plan**: Review requirements, create task breakdown
2. **Implement**: Write code with tests
3. **Verify**: Run all relevant tests
4. **Demo**: Demonstrate to stakeholders
5. **Reflect**: Gather feedback, update plan
6. **Document**: Update docs with learnings

---

## Definition of Done

A phase is complete when:
- ✅ All deliverables implemented
- ✅ All tests passing
- ✅ Code reviewed
- ✅ Documentation updated
- ✅ Demo successful
- ✅ Success criteria met
