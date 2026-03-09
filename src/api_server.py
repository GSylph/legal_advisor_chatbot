from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .chat_service import ChatService
from .logger import log_error


app = FastAPI(title="Legal Advisor Chatbot API", version="0.1.0")

chat_service: Optional[ChatService] = None


class MessageItem(BaseModel):
    sender: str
    text: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    history: Optional[List[MessageItem]] = None


class ChatResponse(BaseModel):
    conversation_id: str
    raw_text: str
    formatted_text: str
    structured: Dict[str, Any]


@app.on_event("startup")
def startup_event() -> None:
    global chat_service
    chat_service = ChatService(kb_path="data/statutes")


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if chat_service is None:
        log_error("ChatService not initialized")
        raise HTTPException(status_code=500, detail="Service not initialized")

    # For now we ignore the incoming history and rely on server-side memory.
    try:
        structured, formatted = chat_service.run_turn(request.message)
    except Exception as exc:
        log_error(f"/api/chat failed: {exc}")
        raise HTTPException(status_code=500, detail="Failed to process message")

    conversation_id = request.conversation_id or "default"
    return ChatResponse(
        conversation_id=conversation_id,
        raw_text=formatted,
        formatted_text=formatted,
        structured=structured,
    )


def get_app() -> FastAPI:
    """Helper for ASGI servers."""
    return app

