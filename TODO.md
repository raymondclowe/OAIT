# OAIT Development TODO

Fine-grained task checklist for OAIT implementation. Items are organized by phase and priority.

**Legend:**
- `[ ]` Not started
- `[~]` In progress
- `[x]` Complete
- `[?]` Blocked/needs discussion

---

## Phase 0: Project Foundation

### Repository Setup
- [x] Create README.md
- [x] Create SPECIFICATION.md
- [x] Create IMPLEMENTATION_PLAN.md
- [x] Create TODO.md (this file)
- [ ] Create directory structure
  - [ ] `/src/oait/server`
  - [ ] `/src/oait/api`
  - [ ] `/src/oait/audio`
  - [ ] `/src/oait/vision`
  - [ ] `/src/oait/cognitive`
  - [ ] `/src/oait/models`
  - [ ] `/src/oait/tools`
  - [ ] `/src/oait/utils`
  - [ ] `/tests/unit`
  - [ ] `/tests/integration`
  - [ ] `/tests/e2e`
  - [ ] `/config`
  - [ ] `/memory`
- [ ] Create `__init__.py` files for all packages

### Configuration
- [ ] Create `requirements.txt` with dependencies
  - [ ] openai (OpenRouter uses OpenAI-compatible API)
  - [ ] faster-whisper (local STT)
  - [ ] gradio (web frontend)
  - [ ] flask (alternative frontend)
  - [ ] pillow
  - [ ] pydantic
  - [ ] python-dotenv
  - [ ] pytest
  - [ ] pytest-asyncio
  - [ ] pytest-mock
  - [ ] httpx (async HTTP client)
- [ ] Create `.env.example` template
  - [ ] OPENROUTER_API_KEY (REQUIRED)
  - [ ] OPENROUTER_MODEL (default: google/gemini-3.0-pro)
  - [ ] WHISPER_MODEL_SIZE (default: base)
  - [ ] SERVER_HOST (default: 0.0.0.0)
  - [ ] SERVER_PORT (default: 7860)
  - [ ] LIVEKIT_URL (optional, future)
  - [ ] LIVEKIT_API_KEY (optional, future)
  - [ ] LIVEKIT_API_SECRET (optional, future)
- [ ] Create `.gitignore`
  - [ ] .env
  - [ ] __pycache__
  - [ ] *.pyc
  - [ ] .pytest_cache
  - [ ] /memory/*.json (exclude student data)
  - [ ] /tmp
- [ ] Create `pytest.ini`
- [ ] Create `pyproject.toml` or `setup.py`

### CI/CD
- [ ] Setup GitHub Actions
  - [ ] Linting workflow (black, flake8, mypy)
  - [ ] Testing workflow (pytest)
  - [ ] Coverage reporting
- [ ] Setup pre-commit hooks
  - [ ] Code formatting
  - [ ] Type checking

### Documentation
- [ ] Add architecture diagrams to /docs
- [ ] Create CONTRIBUTING.md
- [ ] Create LICENSE file
- [ ] Add setup instructions to README

---

## Phase 1: Basic Audio Pipeline

### Audio Stream Handler
- [ ] Implement `AudioStreamHandler` class
  - [ ] `__init__` with browser WebSocket connection
  - [ ] `capture_audio()` async method
  - [ ] `start()` method to begin capture
  - [ ] `stop()` method to end capture
  - [ ] Error handling for connection issues
- [ ] Add logging for audio events

### Speech-to-Text Integration (Local Whisper)
- [ ] Create STT service abstraction
  - [ ] Abstract base class `STTService`
  - [ ] **Whisper implementation (MVP - local, free)**
  - [ ] Deepgram implementation (future, paid)
- [ ] Implement transcription pipeline
  - [ ] Audio chunk processing
  - [ ] Batch transcription (Whisper doesn't stream)
  - [ ] Configure model size (base/small/medium/large)
  - [ ] Error recovery
- [ ] Add transcription quality metrics

### Transcript Buffer
- [ ] Implement `TranscriptBuffer` class
  - [ ] `append(text, timestamp)` method
  - [ ] `get_recent(duration)` method
  - [ ] `get_all()` method
  - [ ] `clear()` method
  - [ ] Automatic cleanup of old entries
- [ ] Add buffer size limits and warnings

### Silence Detection
- [ ] Implement `SilenceDetector` class
  - [ ] Track speech activity
  - [ ] Calculate silence duration
  - [ ] Configurable threshold
  - [ ] Callback for silence events
- [ ] Add VAD (Voice Activity Detection) integration

### Testing
- [ ] Unit tests for `TranscriptBuffer`
  - [ ] Test window size maintenance
  - [ ] Test timestamp ordering
  - [ ] Test edge cases (empty, overflow)
- [ ] Unit tests for `SilenceDetector`
  - [ ] Test threshold detection
  - [ ] Test timing accuracy
- [ ] Integration test: Audio to transcript
  - [ ] Test with sample audio file
  - [ ] Verify transcript accuracy
- [ ] Manual test: Real microphone
  - [ ] Test latency
  - [ ] Test continuous transcription
  - [ ] Test noise handling

---

## Phase 2: Basic Vision Pipeline

### Video Stream Handler
- [ ] Implement `VideoStreamHandler` class
  - [ ] `__init__` with LiveKit video track
  - [ ] `capture_frame()` async method
  - [ ] Frame rate management
  - [ ] Quality settings
- [ ] Add frame buffering for stability

### Image Preprocessing
- [ ] Implement `ImagePreprocessor` class
  - [ ] Crop to whiteboard region
  - [ ] Denoise/sharpen
  - [ ] Contrast adjustment
  - [ ] Resize for optimal LLM input
- [ ] Add image validation

### Vision LLM Integration
- [ ] Create vision service abstraction
  - [ ] Abstract base class `VisionService`
  - [ ] GPT-4o implementation
  - [ ] Moondream implementation (future)
- [ ] Implement `VisionAnalyzer` class
  - [ ] `analyze_whiteboard(image)` method
  - [ ] Parse LLM response to structured format
  - [ ] Error handling for API failures
  - [ ] Retry logic with backoff

### Change Detection
- [ ] Implement `ChangeDetector` class
  - [ ] Image difference calculation
  - [ ] Threshold for "significant" change
  - [ ] Ignore minor variations (lighting)
- [ ] Add configurable sensitivity

### Testing
- [ ] Unit tests for `ImagePreprocessor`
  - [ ] Test crop accuracy
  - [ ] Test image quality improvements
- [ ] Unit tests for `ChangeDetector`
  - [ ] Test with identical images
  - [ ] Test with similar images
  - [ ] Test with different images
- [ ] Integration test: Vision LLM
  - [ ] Test with sample whiteboard images
  - [ ] Verify response structure
- [ ] Manual test: Live whiteboard
  - [ ] Test with Excalidraw
  - [ ] Test with physical whiteboard via camera

---

## Phase 3: Data Models and State Management

### Student Model
- [ ] Define `StudentModel` Pydantic model
  - [ ] student_id field
  - [ ] competencies field
  - [ ] pedagogy_profile field
  - [ ] session_history field
  - [ ] Validation rules
- [ ] Implement `StudentModelRepository`
  - [ ] `load(student_id)` method
  - [ ] `save(model)` method
  - [ ] `list_all()` method
  - [ ] `delete(student_id)` method
- [ ] Add JSON serialization
- [ ] Add database migration system

### Session State
- [ ] Define `SessionState` Pydantic model
  - [ ] current_problem_image field
  - [ ] student_speech_buffer field
  - [ ] ai_internal_monologue field
  - [ ] silence_duration field
  - [ ] State tracking fields
- [ ] Implement state persistence
  - [ ] `snapshot()` method
  - [ ] `restore(snapshot)` method
  - [ ] Auto-save mechanism
- [ ] Add state validation

### Pedagogy Profile
- [ ] Define `PedagogyProfile` Pydantic model
  - [ ] patience_level
  - [ ] preferred_learning_style
  - [ ] optimal_intervention_delay
  - [ ] response_to_correction
- [ ] Add profile templates (default profiles)

### Database Layer
- [ ] Implement storage abstraction
  - [ ] `StorageBackend` interface
  - [ ] JSON file implementation
  - [ ] SQLite implementation (future)
- [ ] Add data encryption for PII
- [ ] Implement backup/restore functionality

### Testing
- [ ] Unit tests for model validation
  - [ ] Test valid data
  - [ ] Test invalid data
  - [ ] Test edge cases
- [ ] Unit tests for serialization
  - [ ] JSON round-trip
  - [ ] Backward compatibility
- [ ] Integration test: Persistence
  - [ ] Create, save, load model
  - [ ] Update model
  - [ ] Handle missing files
- [ ] Manual test: Multiple profiles
  - [ ] Create several student profiles
  - [ ] Switch between profiles
  - [ ] Verify data isolation

---

## Phase 4: Basic OODA Loop

### Event Trigger System
- [ ] Implement `TriggerDetector` class
  - [ ] `check_triggers(state)` method
  - [ ] Silence trigger
  - [ ] Whiteboard change trigger
  - [ ] Explicit question trigger
  - [ ] Error pattern trigger
  - [ ] Stuck indicator trigger
- [ ] Add trigger priority system
- [ ] Add trigger rate limiting

### Observation Phase
- [ ] Implement `Observer` class
  - [ ] Aggregate audio data
  - [ ] Aggregate visual data
  - [ ] Create structured observation
  - [ ] Timestamp management
- [ ] Add observation validation

### Orientation Phase
- [ ] Implement `Orientator` class
  - [ ] Generate internal monologue
  - [ ] Analyze student state
  - [ ] Detect errors
  - [ ] Assess confusion level
- [ ] Create orientation prompt templates
- [ ] Add context injection

### OODA Loop Controller
- [ ] Implement `OODALoop` class
  - [ ] Main loop with asyncio
  - [ ] Trigger-based activation
  - [ ] Phase orchestration
  - [ ] Error recovery
- [ ] Add loop state management
- [ ] Add performance monitoring

### Internal Monologue
- [ ] Define monologue structure
- [ ] Implement monologue storage
- [ ] Add monologue retrieval for debugging

### Testing
- [ ] Unit tests for triggers
  - [ ] Test each trigger type
  - [ ] Test priority logic
  - [ ] Test rate limiting
- [ ] Unit tests for Observer
  - [ ] Test data aggregation
  - [ ] Test observation structure
- [ ] Integration test: Observe-Orient
  - [ ] Mock audio/video inputs
  - [ ] Verify monologue generation
- [ ] Manual test: Log monitoring
  - [ ] Run loop with real inputs
  - [ ] Review internal monologue
  - [ ] Verify no speaking occurs

---

## Phase 5: AI Tool System

### Tool Framework
- [ ] Create tool definition schema
- [ ] Implement `ToolRegistry` class
  - [ ] Register tools
  - [ ] List available tools
  - [ ] Get tool by name
- [ ] Implement `ToolExecutor` class
  - [ ] Execute tool by name
  - [ ] Parameter validation
  - [ ] Error handling
  - [ ] Return value processing

### Pedagogical Tools
- [ ] `update_student_model` tool
  - [ ] Implementation
  - [ ] Parameter validation
  - [ ] Database integration
  - [ ] Unit tests
- [ ] `consult_pedagogy_db` tool
  - [ ] Implementation
  - [ ] Query logic
  - [ ] Unit tests
- [ ] `verify_calculation` tool
  - [ ] Mathematical expression parser
  - [ ] Calculation engine (sympy)
  - [ ] Answer comparison
  - [ ] Unit tests
- [ ] `assess_confusion_level` tool
  - [ ] Transcript analysis
  - [ ] Confusion indicators
  - [ ] Confidence score
  - [ ] Unit tests

### LLM Integration
- [ ] Add function calling to LLM requests
- [ ] Implement tool call parsing
- [ ] Add tool result injection back to LLM
- [ ] Handle multi-turn tool usage

### Testing
- [ ] Unit tests for each tool
  - [ ] Happy path
  - [ ] Error cases
  - [ ] Edge cases
- [ ] Integration test: Tool execution
  - [ ] LLM calls tool
  - [ ] Tool executes
  - [ ] Result returned to LLM
- [ ] Manual test: Tool chain
  - [ ] Multiple tools in sequence
  - [ ] Verify state updates

---

## Phase 6: Intervention System

### Decision Phase
- [ ] Implement `InterventionDecider` class
  - [ ] `decide(analysis, model, state)` method
  - [ ] Priority-based decision logic
  - [ ] Confidence threshold checks
  - [ ] Timing calculations
- [ ] Add decision logging

### Action Types
- [ ] Implement `ActionDecision` enum
  - [ ] WAIT
  - [ ] UPDATE_DB
  - [ ] SPEAK
- [ ] Define action metadata structure

### Speech Synthesis
- [ ] Create TTS service abstraction
  - [ ] Abstract base class `TTSService`
  - [ ] ElevenLabs implementation
  - [ ] Cartesia implementation (future)
  - [ ] Local TTS implementation (future)
- [ ] Implement speech queue
- [ ] Add interrupt handling

### Action Router
- [ ] Implement `ActionRouter` class
  - [ ] `route(decision)` method
  - [ ] `speak(text)` handler
  - [ ] `update_db(data)` handler
  - [ ] `wait()` handler
- [ ] Add action history logging

### Complete OODA Loop
- [ ] Add Decide phase to loop
- [ ] Add Act phase to loop
- [ ] Integrate action router
- [ ] Add loop metrics

### Testing
- [ ] Unit tests for decision logic
  - [ ] Test each priority path
  - [ ] Test threshold calculations
  - [ ] Test timing logic
- [ ] Unit tests for action routing
  - [ ] Test each action type
  - [ ] Test error handling
- [ ] Integration test: Full OODA
  - [ ] Mock scenario
  - [ ] Trigger intervention
  - [ ] Verify speech output
- [ ] Manual test: Real scenario
  - [ ] Setup tutoring session
  - [ ] Make deliberate error
  - [ ] Verify intervention

---

## Phase 7: MVP Integration

### LiveKit Agent
- [ ] Implement main agent class
  - [ ] Room connection
  - [ ] Track subscriptions
  - [ ] Event handlers
- [ ] Integrate all components
  - [ ] Audio pipeline
  - [ ] Vision pipeline
  - [ ] OODA loop
  - [ ] State management
- [ ] Add graceful shutdown
- [ ] Add health checks

### Configuration Management
- [ ] Create configuration loader
- [ ] Add environment-specific configs
  - [ ] Development
  - [ ] Testing
  - [ ] Production
- [ ] Validate all required settings

### Logging and Monitoring
- [ ] Setup structured logging
  - [ ] Component-level loggers
  - [ ] Log levels per environment
  - [ ] Sensitive data filtering
- [ ] Add performance metrics
  - [ ] Latency tracking
  - [ ] Error rate tracking
  - [ ] Resource usage tracking
- [ ] Create monitoring dashboard (optional)

### Error Handling
- [ ] Add global error handlers
- [ ] Implement retry logic
- [ ] Add fallback behaviors
- [ ] Create error recovery procedures

### Web Frontend (Optional)
- [ ] Simple React app
  - [ ] LiveKit room connection
  - [ ] Excalidraw whiteboard
  - [ ] Audio controls
  - [ ] Session controls
- [ ] Student profile selector
- [ ] Session history viewer

### End-to-End Testing
- [ ] E2E test: Complete session
  - [ ] Start agent
  - [ ] Connect to room
  - [ ] Simulate student
  - [ ] Verify intervention
  - [ ] End session
- [ ] Performance test: Latency
  - [ ] Measure audio latency
  - [ ] Measure vision latency
  - [ ] Measure decision latency
- [ ] Load test: Multiple sessions
  - [ ] Run concurrent sessions
  - [ ] Monitor resource usage

### User Acceptance Testing
- [ ] Create UAT plan
- [ ] Recruit test users (3-5)
- [ ] Prepare test scenarios
  - [ ] Math problem solving
  - [ ] Intentional errors
  - [ ] Stuck scenarios
- [ ] Collect feedback
  - [ ] Intervention quality
  - [ ] Speech naturalness
  - [ ] Overall helpfulness
- [ ] Analyze results

### Documentation
- [ ] Update README with setup instructions
- [ ] Add API documentation
- [ ] Create user guide
- [ ] Add troubleshooting guide
- [ ] Record demo video

---

## Phase 8: Refinement and Optimization

### Performance Optimization
- [ ] Profile code for bottlenecks
- [ ] Optimize image processing
- [ ] Optimize buffer management
- [ ] Reduce API calls where possible
- [ ] Implement caching strategies

### Intervention Quality
- [ ] Analyze false positive interventions
- [ ] Tune decision thresholds
- [ ] Improve trigger detection
- [ ] Enhance context understanding
- [ ] Refine timing calculations

### Speech Quality
- [ ] Test different TTS voices
- [ ] Adjust speech rate and tone
- [ ] Add emphasis/emotion where appropriate
- [ ] Test with different age groups

### Reliability
- [ ] Improve error recovery
- [ ] Add automatic reconnection
- [ ] Handle network interruptions
- [ ] Test edge cases extensively

### Resource Management
- [ ] Optimize memory usage
- [ ] Manage API rate limits
- [ ] Implement connection pooling
- [ ] Add resource cleanup

### Logging Improvements
- [ ] Add more detailed metrics
- [ ] Create log analysis tools
- [ ] Setup log aggregation
- [ ] Add alerting for errors

### Extended Testing
- [ ] Load test: Extended duration
  - [ ] 1+ hour sessions
  - [ ] Multiple consecutive sessions
- [ ] Edge case testing
  - [ ] Network failures
  - [ ] API errors
  - [ ] Invalid inputs
- [ ] User testing: Extended
  - [ ] 10+ hours of usage
  - [ ] Diverse student profiles
  - [ ] Multiple subject areas

### Documentation Updates
- [ ] Update docs based on feedback
- [ ] Add FAQs
- [ ] Document known issues
- [ ] Create migration guides

---

## Phase 9: Advanced Features

### Multiple Students
- [ ] Design multi-student architecture
- [ ] Implement student tracking
- [ ] Handle concurrent interactions
- [ ] Test group tutoring scenarios

### Enhanced Pedagogy
- [ ] Research additional strategies
- [ ] Implement strategy selection
- [ ] Add domain-specific strategies
- [ ] Create strategy effectiveness metrics

### Session Analytics
- [ ] Record session data
- [ ] Create analytics dashboard
- [ ] Generate progress reports
- [ ] Export data for analysis

### Visualization
- [ ] Show AI internal state (debug mode)
- [ ] Visualize student model
- [ ] Show intervention history
- [ ] Create attention heatmaps

### LMS Integration
- [ ] Define integration points
- [ ] Implement grade sync
- [ ] Add assignment tracking
- [ ] Support SSO

### Subject Expansion
- [ ] Physics tutoring
- [ ] Chemistry tutoring
- [ ] Programming tutoring
- [ ] Writing tutoring

### Privacy Features
- [ ] Local-only mode
- [ ] On-device models
- [ ] Data retention policies
- [ ] Export/delete user data

---

## Ongoing Tasks

### Code Quality
- [ ] Regular code reviews
- [ ] Refactoring as needed
- [ ] Type hint coverage > 90%
- [ ] Code coverage > 80%
- [ ] Documentation coverage 100%

### Security
- [ ] Regular dependency updates
- [ ] Security audit
- [ ] API key rotation
- [ ] Access control review

### Performance Monitoring
- [ ] Weekly metric review
- [ ] User feedback collection
- [ ] Bug triage and fixing
- [ ] Performance regression testing

---

## Blockers and Questions

### Technical Questions
- [?] Which vision model provides best accuracy/cost tradeoff?
- [?] What's optimal frame capture rate?
- [?] How to handle multi-language support?
- [?] Best approach for on-premise deployment?

### Product Questions
- [?] What age groups to target first?
- [?] Should AI show its reasoning to students?
- [?] How to measure learning outcomes?
- [?] Pricing model for API usage?

### Research Needed
- [?] Literature review on AI tutoring effectiveness
- [?] Best practices for intervention timing
- [?] Student model structure from pedagogy research
- [?] Privacy regulations for ed-tech

---

## Maintenance Checklist

### Weekly
- [ ] Review and triage new issues
- [ ] Update TODO based on progress
- [ ] Run full test suite
- [ ] Check system metrics

### Monthly
- [ ] Dependency updates
- [ ] Security patch review
- [ ] Performance review
- [ ] User feedback review

### Quarterly
- [ ] Roadmap review
- [ ] Architecture review
- [ ] User research
- [ ] Competition analysis

---

**Last Updated:** 2026-01-15
