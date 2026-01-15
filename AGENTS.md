# Agent instructions

Be clear and precise, record learnings to avoid duplicated effort.

# Data Dictionary

Consult `docs/DATA_DICTIONARY.md` for:
- Naming conventions (snake_case, PascalCase, prefixes)
- Data model schemas (StudentModel, SessionState, OODA types)
- API contracts (WebSocket messages, REST endpoints)
- Common code patterns

**Critical**: `OODALoop.run_cycle()` returns `InternalMonologue`, not `Decision`!
Access via: `monologue.decision.action`, `monologue.decision.response_text`

# Tavily search

- Use the tavily search and extract MCP as needed to research

# Python environment

- Prefer uv - e.g. 'uv run', 'uv add'

# Learnings

Save learnings into 'learnings.md'.

# Openrouter keys

- COPILOT_OPENROUTER_API_KEY
- OPENROUTER_API_KEY
