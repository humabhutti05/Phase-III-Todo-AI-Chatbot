from mcp.server.fastmcp import FastMCP
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional, List, Dict, Any
from .models import Task
from .database import engine

# Create the MCP server
mcp_server = FastMCP("Todo Task Manager")

@mcp_server.tool()
def add_task(user_id: str, title: str, description: str = "") -> str:
    """Create a new task for the given user"""
    with Session(engine) as session:
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        session.commit()
        session.refresh(task)
        return f"Task '{task.title}' created with ID {task.id}"

@mcp_server.tool()
def list_tasks(user_id: str, status: str = "all") -> str:
    """Retrieve tasks for a user. status can be 'all', 'pending', or 'completed'"""
    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)
        if status == "pending":
            statement = statement.where(Task.completed == False)
        elif status == "completed":
            statement = statement.where(Task.completed == True)
        
        results = session.exec(statement).all()
        if not results:
            return "No tasks found."
        
        output = []
        for task in results:
            status_str = "✅" if task.completed else "⏳"
            output.append(f"[{task.id}] {status_str} {task.title}: {task.description or 'No description'}")
        
        return "\n".join(output)

@mcp_server.tool()
def complete_task(user_id: str, task_id: int) -> str:
    """Mark a specific task as complete for the given user"""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            return f"Error: Task with ID {task_id} not found for user {user_id}"
        
        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        return f"Task '{task.title}' marked as complete"

@mcp_server.tool()
def delete_task(user_id: str, task_id: int) -> str:
    """Delete a task for the given user"""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            return f"Error: Task with ID {task_id} not found"
        
        title = task.title
        session.delete(task)
        session.commit()
        return f"Task '{title}' (ID {task_id}) deleted successfully"

@mcp_server.tool()
def update_task(user_id: str, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> str:
    """Update title or description of an existing task"""
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            return f"Error: Task {task_id} not found"
        
        if title: task.title = title
        if description: task.description = description
        task.updated_at = datetime.utcnow()
        
        session.add(task)
        session.commit()
        return f"Task {task_id} updated successfully"

# Helper to provide tool schemas to OpenAI/Gemini
def get_mcp_tool_schemas():
    # FastMCP tools can be exported to OpenAI function format
    # This is a bit manual depending on the SDK version, 
    # but here we'll define the mapping manually to ensure correctness
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Retrieve tasks from the list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "status": {"type": "string", "enum": ["all", "pending", "completed"]}
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "task_id": {"type": "integer"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Remove a task from the list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "task_id": {"type": "integer"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Modify task title or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "task_id": {"type": "integer"},
                        "title": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        }
    ]

def get_mcp_tool_callable(name: str):
    # Mapping tool names to their FastMCP decorated functions
    # Note: FastMCP makes it easy to run, but here we call them directly
    tools_map = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
        "delete_task": delete_task,
        "update_task": update_task
    }
    return tools_map.get(name)
