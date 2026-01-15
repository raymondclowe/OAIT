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

1. **Audio Stream (The Ears)**: Continuous speech-to-text using local Faster-Whisper
2. **Video Stream (The Eyes)**: Periodic whiteboard snapshots analyzed by Gemini 3 Pro (via OpenRouter)
3. **Cognitive Loop (The Brain)**: OODA loop that synthesizes observations and makes intervention decisions

### Core Components

- **Observation Layer**: Captures audio and visual input
- **Orientation Layer**: Updates the mental model of student state
- **Decision Layer**: Evaluates whether intervention is needed
- **Action Layer**: Speaks to student or silently updates internal state

## Technology Stack

### Local-First Architecture
**Household/Building Server** (Ubuntu or Windows) running Python with Gradio or Flask frontend, accessible from LAN/subnet devices. Progressive Web App (PWA) for local phone and desktop access.

### Essential Cloud (LLM Only)
- **OpenRouter.ai**: Only external dependency - routes to Gemini 3 Pro for deep thinking and image analysis
- **Gemini 3 Pro** (via OpenRouter): Preferred model for reasoning, understanding, and image work

> ⚠️ **Note**: OpenRouter is the ONLY required cloud service. All other processing is local or on-premises.

### MVP Stack (100% Local Processing)
- **Faster-Whisper**: Local speech-to-text on self-hosted server
- **Web Speech API**: Browser-native TTS (no cloud TTS)
- **Gradio/Flask**: Web frontend served from local server
- **SQLite**: Local student model and session storage
- **Excalidraw**: Browser-based whiteboard (runs locally)
- **PWA**: Progressive Web App for phone/desktop (works offline for UI)

### Self-Hosted Infrastructure
- **Local Server**: Linux or Windows machine on building subnet
- **Nearby Processing**: Python code running on-premises
- **Local Storage**: SQLite database, JSON files

### Open Source Components
- **Faster-Whisper**: Optimized local transcription (OSS)
- **Excalidraw**: Web-based whiteboard component (OSS)
- **Gradio**: Web UI framework (OSS)

## Project Status

🚧 **In Development** - Currently in planning and specification phase

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed roadmap and [TODO.md](TODO.md) for current task list.

## Getting Started

*(To be added as implementation progresses)*

### Prerequisites

- Python 3.9+
- Self-hosted server (Ubuntu or Windows) on building LAN/subnet
- OpenRouter.ai API key (required - only cloud dependency)
- Client device with browser: Android phone (PWA), Mac Mini, Windows laptop
- GPU recommended for faster Whisper inference (optional)

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

Based on architectural concepts from modern multimodal AI approaches for creating observational, human-in-the-loop AI systems. Uses open-source components including Faster-Whisper and Excalidraw.
