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

### Recommended (Cloud-based)
- **LiveKit Agents**: Real-time multimodal agent framework
- **Pipecat AI**: Pipeline framework for audio/video processing
- **GPT-4o**: Multimodal LLM for vision and language understanding
- **Deepgram**: Ultra-low latency speech-to-text
- **ElevenLabs/Cartesia**: Natural text-to-speech

### Open Source Alternatives (Local)
- **Ollama + Moondream**: Local vision model
- **Faster-Whisper**: On-device transcription
- **Excalidraw**: Web-based whiteboard component

## Project Status

🚧 **In Development** - Currently in planning and specification phase

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed roadmap and [TODO.md](TODO.md) for current task list.

## Getting Started

*(To be added as implementation progresses)*

### Prerequisites

- Python 3.9+
- LiveKit account (or self-hosted server)
- API keys for chosen services (OpenAI, Deepgram, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/raymondclowe/OAIT.git
cd OAIT

# Install dependencies (to be defined)
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys
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
