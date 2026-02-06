# AI-Powered Todo Chatbot (Phase III)

## Overview
This project is an AI-powered conversational interface for task management. It allows users to add, list, complete, and delete tasks using natural language.
It follows a stateless Agentic architecture where the conversational state is persisted in a database, and the Backend API orchestrates the Agent and MCP Tools.

## Project Structure
- **/backend**: FastAPI application with OpenAI Agent logic and MCP Tools (local functions).
- **/frontend**: Next.js application using OpenAI ChatKit for the chat interface.
- **/specs**: Project specifications and tool definitions.

## Setup Instructions

### Backend
1. Navigate to `backend/`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables (create `.env`):
   ```
   DATABASE_URL=postgresql://user:password@host/dbname
   OPENAI_API_KEY=your_key
   # If using Gemini
   AI_MODEL=gemini-1.5-pro
   OPENAI_BASE_URL=...
   ```
4. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend
1. Navigate to `frontend/`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set environment variables (`.env.local`):
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key
   ```
4. Run the dev server:
   ```bash
   npm run dev
   ```

## Architecture
- **API**: `POST /api/{user_id}/chat`
- **Agent**: Uses `openai` SDK to effectively call Gemini models (or generic OpenAI models).
- **Tools**: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`.

## Author
Implementation by Antigravity Agent.
