# OAIT - Observational AI Tutor

A multimodal AI tutoring system that continuously observes a student's whiteboard and listens to their speech, providing intelligent, context-aware guidance when needed.

## Overview

OAIT (Observational AI Tutor) is not a traditional chatbot. Instead of reacting to every input, it runs a continuous **OODA loop** (Observe-Orient-Decide-Act), constantly analyzing the student's work and speech, but only intervening when appropriate. The AI maintains an internal monologue and mental model of the student, ensuring pedagogically sound interactions.

## Key Features

- **Continuous Observation**: Monitors both audio (student speech) and video (whiteboard/screen) streams simultaneously
- **Intelligent Silence**: The AI "thinks" continuously but only speaks when necessary
- **Student Modeling**: Maintains both long-term (across sessions) and short-term (within session) mental models of student capabilities
- **Pedagogical Awareness**: Adapts teaching strategies based on student response patterns
- **Non-Intrusive**: Designed to avoid interrupting student flow unless critical

## Architecture

OAIT operates on an event-driven architecture with three parallel streams:

1. **Audio Stream (The Ears)**: Continuous speech-to-text using Deepgram or Faster-Whisper
2. **Video Stream (The Eyes)**: Periodic whiteboard snapshots analyzed by Vision LLM
3. **Cognitive Loop (The Brain)**: OODA loop that synthesizes observations and makes intervention decisions

### Core Components

- **Observation Layer**: Captures audio and visual input
- **Orientation Layer**: Updates the mental model of student state
- **Decision Layer**: Evaluates whether intervention is needed
- **Action Layer**: Speaks to student or silently updates internal state

## Technology Stack

### Architecture Overview
**Household Server** (Ubuntu or Windows) running Python with Gradio or Flask frontend, accessible from LAN devices (Android phone, Mac Mini, Windows laptop).

### API Routing (Required)
- **OpenRouter.ai**: All cloud LLM calls routed through OpenRouter (OpenAI/Anthropic are geo-blocked)
- **Gemini 3 Pro** (via OpenRouter): Preferred model for high-quality reasoning, understanding, and image work (supports image input/output)

> ⚠️ **Note**: OpenRouter supports tool calling with *some* models only - verify model capabilities before implementation.

### MVP Stack (Local-First)
- **Whisper** (local): Speech-to-text on household server
- **Web Speech API**: Browser-based TTS for MVP (upgrade to paid services later)
- **Gradio/Flask**: Web frontend served from household server
- **SQLite/JSON**: Local student model storage

### Future Enhancements (Post-MVP)
- **ElevenLabs/Cartesia**: Premium TTS (via OpenRouter where available)
- **Deepgram**: Low-latency cloud STT
- **LiveKit**: Real-time streaming (if needed)

### Open Source Components
- **Faster-Whisper**: Optimized local transcription
- **Excalidraw**: Web-based whiteboard component

## Project Status

🚧 **In Development** - Currently in planning and specification phase

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed roadmap and [TODO.md](TODO.md) for current task list.

## Getting Started

*(To be added as implementation progresses)*

### Prerequisites

- Python 3.9+
- Household server (Ubuntu or Windows) on LAN
- OpenRouter.ai API key (required - geo-free routing)
- Client device: Android phone, Mac Mini, or Windows laptop

### Installation

```bash
# Clone the repository
git clone https://github.com/raymondclowe/OAIT.git
cd OAIT

# Install dependencies
pip install -r requirements.txt

# Install Whisper for local STT
pip install faster-whisper

# Configure API keys
cp .env.example .env
# Edit .env with your OpenRouter API key
```

### Running the Server

```bash
# Start the household server (accessible on LAN)
python src/oait/server.py --host 0.0.0.0 --port 7860
```

### Usage

*(To be added as implementation progresses)*

## Documentation

- [SPECIFICATION.md](SPECIFICATION.md) - Detailed technical specification
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Phased development plan
- [TODO.md](TODO.md) - Fine-grained task checklist
- [discussion.txt](discussion.txt) - Original design discussion

## Contributing

*(To be defined)*

## License

*(To be defined)*

## Acknowledgments

Based on architectural concepts using LiveKit Agents and modern multimodal AI approaches for creating observational, human-in-the-loop AI systems.
