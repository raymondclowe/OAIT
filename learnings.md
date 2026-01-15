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

### Next Steps
According to IMPLEMENTATION_PLAN.md and STATUS.md, we need to work on:
1. **Phase 1**: Audio WebSocket Integration (connect browser → server → Whisper STT)
2. **Phase 2**: Vision WebSocket Integration (connect browser → server → Gemini 3 Pro)
3. **Phase 5**: AI Tool System (pedagogical tools for the OODA loop)
4. **Phase 6**: Intervention System (decision-making and TTS)
5. **Phase 7**: Full MVP Integration (Gradio/Flask UI, PWA, Excalidraw)

### Key Constraints
- Local-first architecture (only OpenRouter for LLM calls)
- Use `uv` for Python package management (per AGENTS.md)
- Save learnings to this file as development progresses
