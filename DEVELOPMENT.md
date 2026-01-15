# OAIT Development Guide

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/raymondclowe/OAIT.git
cd OAIT
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### Running Tests

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src/oait --cov-report=html
```

### Code Quality

Format code:
```bash
black src/ tests/
```

Type checking:
```bash
mypy src/
```

Linting:
```bash
flake8 src/ tests/
```

## Project Structure

```
/OAIT
  /src/oait           # Main application code
    /server           # Web server and application entry point
    /api              # OpenRouter API client
    /audio            # Audio processing (Whisper STT)
    /vision           # Vision processing (image analysis)
    /cognitive        # OODA loop and decision making
    /models           # Data models and storage
    /tools            # AI tool functions
    /utils            # Shared utilities
  /tests              # Test suite
    /unit             # Unit tests
    /integration      # Integration tests
    /e2e              # End-to-end tests
  /config             # Configuration files
  /memory             # Student model storage (local SQLite)
  /docs               # Additional documentation
```

## Development Workflow

1. Create a feature branch
2. Write tests first (TDD)
3. Implement the feature
4. Run tests and quality checks
5. Create a pull request

## Architecture Notes

### Local-First Design
- **Only Cloud Service**: OpenRouter.ai for Gemini 3 Pro LLM
- **All Processing Local**: Faster-Whisper STT on self-hosted server
- **Storage**: SQLite database (local file)
- **TTS**: Web Speech API (browser-native, no cloud)

### Key Components

1. **Audio Pipeline**: Captures audio from browser, transcribes locally with Faster-Whisper
2. **Vision Pipeline**: Captures whiteboard images, analyzes with Gemini 3 Pro via OpenRouter
3. **OODA Loop**: Continuous cognitive cycle (Observe-Orient-Decide-Act)
4. **Student Model**: Persistent learning profile stored in SQLite
5. **Session State**: Working memory for current tutoring session

## MVP Status

**Phase 0: Project Foundation** ✅
- [x] Directory structure created
- [x] Configuration management implemented
- [x] Data models defined
- [x] Basic tests written

**Phase 1: Basic Audio Pipeline** 🚧
- [x] Whisper STT integration
- [x] Transcript buffer implementation
- [x] Silence detection
- [ ] Audio stream handler (WebSocket integration)
- [ ] Complete unit tests

**Phase 2: Basic Vision Pipeline** 🚧
- [x] OpenRouter API client
- [x] Vision analyzer
- [x] Image preprocessor
- [x] Change detection
- [ ] Video stream handler (WebSocket integration)
- [ ] Complete unit tests

**Phase 3: Data Models & State** 🚧
- [x] Student model defined
- [x] Session state defined
- [x] SQLite repository implementation
- [ ] Complete integration tests

**Phase 4: Basic OODA Loop** 🚧
- [x] Trigger detection
- [x] OODA loop structure
- [x] Basic decision logic
- [ ] Enhanced analysis with LLM
- [ ] Complete integration tests

**Remaining Phases**
- [ ] Phase 5: AI Tool System
- [ ] Phase 6: Intervention System
- [ ] Phase 7: MVP Integration (Gradio UI, WebSocket, PWA)
- [ ] Phase 8: Refinement
- [ ] Phase 9: Advanced Features

## Next Steps

1. Complete audio stream handler with WebSocket support
2. Complete vision stream handler with WebSocket support
3. Create Gradio web interface with PWA support
4. Integrate Excalidraw whiteboard
5. Add comprehensive integration tests
6. User acceptance testing

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

See [LICENSE](LICENSE) for details.
