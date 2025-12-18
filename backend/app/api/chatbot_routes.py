"""
Chatbot API routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from app.services.chatbot import get_chatbot

router = APIRouter()

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str
    success: bool = True

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the environmental chatbot
    """
    try:
        chatbot = get_chatbot()
        
        # Convert history to dict format
        history_dict = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        # Get response
        response = chatbot.chat(request.message, history_dict)
        
        return ChatResponse(response=response, success=True)
    
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")

@router.get("/quick-tip")
async def get_quick_tip():
    """
    Get a quick environmental tip
    """
    try:
        chatbot = get_chatbot()
        tip = chatbot.get_quick_tip()
        
        return {"tip": tip, "success": True}
    
    except Exception as e:
        print(f"Quick tip error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quick tip")

@router.get("/health")
async def chatbot_health():
    """
    Check if chatbot is available
    """
    try:
        chatbot = get_chatbot()
        return {"status": "available", "model": "gemini-1.5-flash"}
    except ValueError:
        return {"status": "unavailable", "error": "API key not configured"}
    except Exception as e:
        return {"status": "error", "error": str(e)}