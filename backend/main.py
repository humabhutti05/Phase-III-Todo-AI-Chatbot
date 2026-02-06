from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from contextlib import asynccontextmanager
from sqlmodel import Session, select

from .database import create_db_and_tables, engine
from .models import Conversation
from .agent import AgentRunner

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="AI Todo Chatbot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[Dict[str, Any]] = []

@app.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(user_id: str, request: ChatRequest):
    conversation_id = request.conversation_id
    
    with Session(engine) as session:
        # Create conversation if not exists
        if not conversation_id:
            conv = Conversation(user_id=user_id)
            session.add(conv)
            session.commit()
            session.refresh(conv)
            conversation_id = conv.id
        else:
            # Verify exists
            conv = session.get(Conversation, conversation_id)
            if not conv:
                # If provided ID is invalid, make a new one or error. 
                # Let's clean up and make a new one for robustness
                conv = Conversation(user_id=user_id)
                session.add(conv)
                session.commit()
                session.refresh(conv)
                conversation_id = conv.id

    # Run Agent
    runner = AgentRunner(user_id=user_id, conversation_id=conversation_id)
    result = runner.run(request.message)
    
    return ChatResponse(
        conversation_id=conversation_id,
        response=result["response"],
        tool_calls=result.get("tool_calls", [])
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}
