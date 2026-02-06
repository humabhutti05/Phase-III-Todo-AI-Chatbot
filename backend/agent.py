import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from .mcp_server import get_mcp_tool_schemas, get_mcp_tool_callable
from .models import Message
from .database import engine
from sqlmodel import Session, select

# Gemini / OpenAI Client configuration
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL") 
if api_key and not base_url and "gemini" in os.getenv("AI_MODEL", "").lower():
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)
MODEL_NAME = os.getenv("AI_MODEL", "gpt-4-turbo")

TOOLS_SCHEMA = get_mcp_tool_schemas()

class AgentRunner:
    def __init__(self, user_id: str, conversation_id: int):
        self.user_id = user_id
        self.conversation_id = conversation_id

    def run(self, new_message: str) -> Dict[str, Any]:
        with Session(engine) as session:
            # 1. Store User Message
            user_msg = Message(
                user_id=self.user_id,
                conversation_id=self.conversation_id,
                role="user",
                content=new_message
            )
            session.add(user_msg)
            session.commit()
            
            # 2. Fetch History
            statement = select(Message).where(
                Message.conversation_id == self.conversation_id
            ).order_by(Message.created_at.desc()).limit(15)
            history_objs = session.exec(statement).all()
            history_objs = history_objs[::-1]
            
        messages = [
            {"role": "system", "content": f"You are a helpful Todo AI assistant powered by MCP. The current user is '{self.user_id}'. You must use tools for all task operations. Always confirm what you've done. Be concise."}
        ]
        
        for msg in history_objs:
            if msg.content:
                messages.append({"role": msg.role, "content": msg.content})

        # 3. Call AI
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )
        except Exception as e:
            return {"conversation_id": self.conversation_id, "response": f"AI Error: {str(e)}", "tool_calls": []}
        
        assistant_msg = response.choices[0].message
        tool_outputs = []
        
        # 4. Handle Tool Calls
        if assistant_msg.tool_calls:
            messages.append({
                "role": "assistant",
                "content": assistant_msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in assistant_msg.tool_calls
                ]
            })
            
            for tool_call in assistant_msg.tool_calls:
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except:
                    function_args = {}
                
                tool_func = get_mcp_tool_callable(function_name)
                if tool_func:
                    function_args["user_id"] = self.user_id
                    try:
                        result = tool_func(**function_args)
                        tool_outputs.append({"tool": function_name, "args": function_args, "result": result})
                        
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(result)
                        })
                    except Exception as e:
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"Error: {str(e)}"
                        })

            # 5. Final Response
            try:
                second_response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages
                )
                final_content = second_response.choices[0].message.content
            except Exception as e:
                final_content = f"Tools executed but final response failed: {str(e)}"
        else:
            final_content = assistant_msg.content

        # 6. Store Assistant Response
        if final_content:
            with Session(engine) as session:
                 db_msg = Message(
                     user_id=self.user_id,
                     conversation_id=self.conversation_id,
                     role="assistant",
                     content=final_content
                 )
                 session.add(db_msg)
                 session.commit()

        return {
            "conversation_id": self.conversation_id,
            "response": final_content,
            "tool_calls": tool_outputs
        }
