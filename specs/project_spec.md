# AI-Powered Todo Chatbot Specification

## 1. Project Overview
**Objective**: Create an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture.
**Stack**:
- **Frontend**: OpenAI ChatKit (Next.js/React)
- **Backend**: Python FastAPI
- **AI Engine**: OpenAI Agents SDK (configured with Gemini models)
- **MCP Server**: Official MCP SDK
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel
- **Auth**: Better Auth

## 2. Architecture
- **Stateless API**: `POST /api/chat` receives message -> fetches history -> runs Agent -> Agent calls MCP Tools -> Updates DB -> Returns response.
- **MCP Server**: Internal or external server exposing `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`.
- **Database**: Stores `Task`, `Conversation`, `Message`.

## 3. Database Schema (SQLModel)

### Task
- `user_id`: str (Required)
- `id`: int (Primary Key)
- `title`: str
- `description`: str (Optional)
- `completed`: bool (Default false)
- `created_at`: datetime
- `updated_at`: datetime

### Conversation
- `user_id`: str
- `id`: int (Primary Key)
- `created_at`: datetime
- `updated_at`: datetime

### Message
- `user_id`: str
- `id`: int (Primary Key)
- `conversation_id`: int (Foreign Key to Conversation)
- `role`: str ("user" or "assistant")
- `content`: str
- `created_at`: datetime

## 4. MCP Tools Specification
The AI agent uses these tools to interact with the database.

- `add_task(user_id, title, description)`: Creates a task.
- `list_tasks(user_id, status="all")`: Lists tasks. Status: "all"|"pending"|"completed".
- `complete_task(user_id, task_id)`: Marks task as complete.
- `delete_task(user_id, task_id)`: Deletes a task.
- `update_task(user_id, task_id, title, description)`: Updates task details.

## 5. API Endpoints

### POST /api/{user_id}/chat
- **Request**: `{ "conversation_id": Optional[int], "message": str }`
- **Response**: `{ "conversation_id": int, "response": str, "tool_calls": List[dict] }`
- **Logic**:
    1. Retrieve or create conversation.
    2. Load history (limited window).
    3. Initialize Agent with MCP tools.
    4. Run Agent with user message.
    5. Save User Message and Assistant Response to DB.
    6. Return response.

## 6. Frontend (ChatKit)
- **Framework**: Next.js 14+ (App Router).
- **UI Component**: OpenAI ChatKit.
- **Styling**: TailwindCSS & Standard CSS for premium aesthetics.
- **Features**:
    - Chat interface.
    - Markdown rendering.
    - Optimistic UI updates (if possible).
    - Visual feedback for tool calls (e.g., "Adding task...").

## 7. AI Agent Configuration
- **Model**: Gemini 1.5 Pro (via OpenAI SDK compatible endpoint or Google Gen AI SDK adapted).
- **System Prompt**:
    - "You are a helpful Todo Assistant."
    - "Manage tasks using the provided tools."
    - "Be concise and friendly."
    - "Output Markdown."
