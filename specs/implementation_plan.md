# Implementation Plan - AI Todo Chatbot (Phase III)

## Phase 1: Backend Foundation (Python/FastAPI)
- [ ] **Setup**: Create virtualenv, `pyproject.toml`, install dependencies (`fastapi`, `uvicorn`, `sqlmodel`, `psycopg2-binary`, `mcp`, `openai`).
- [ ] **Database**: Define `Task`, `Conversation`, `Message` models in `backend/models.py`. Setup connection in `backend/database.py`.
- [ ] **MCP Tools**: Implement task operations (`add_task`, etc.) in `backend/tools.py` using MCP SDK.
- [ ] **Agent Service**: Create `backend/agent.py` to handle the interaction between LLM (Gemini), History, and MCP Tools.
- [ ] **API**: Implement `backend/main.py` with `POST /api/{user_id}/chat`.

## Phase 2: Frontend (Next.js + ChatKit)
- [ ] **Setup**: Initialize Next.js project in `frontend/`.
- [ ] **Dependencies**: Install ChatKit and UI libraries.
- [ ] **Styles**: Configure `globals.css` for "Premium Aesthetics" (Glassmorphism, Neon/Dark mode).
- [ ] **Integration**: Connect ChatKit to `POST /api/.../chat`.

## Phase 3: Integration & Polish
- [ ] **Testing**: Verify flow: User -> UI -> API -> Agent -> MCP -> DB -> Response.
- [ ] **Refinement**: Improve prompts, fix UI bugs, ensure smooth animations.
