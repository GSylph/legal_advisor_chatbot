import asyncio
import json
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
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
    session_id: Optional[str] = None
    history: Optional[List[MessageItem]] = None
    retriever: Optional[str] = "hybrid"  # bm25 | dense | hybrid | none


class ChatResponse(BaseModel):
    conversation_id: str
    session_id: str
    raw_text: str
    formatted_text: str
    structured: Dict[str, Any]
    audit_hash: Optional[str] = None
    consistency_flag: Optional[bool] = None
    warning: Optional[str] = None


@app.on_event("startup")
def startup_event() -> None:
    global chat_service
    chat_service = ChatService(kb_path="corpus/raw")
    # Pre-build the semantic index so the first query doesn't wait
    try:
        chat_service.kb._build_semantic_index()
    except Exception as exc:
        log_error(f"Failed to pre-build semantic index: {exc}")


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
        structured, formatted = chat_service.run_turn(
            request.message,
            session_id=request.session_id,
            retriever=request.retriever or "hybrid",
        )
    except Exception as exc:
        log_error(f"/api/chat failed: {exc}")
        raise HTTPException(status_code=500, detail="Failed to process message")

    conversation_id = request.conversation_id or "default"
    session_id = structured.get("session_id", "unknown")
    
    return ChatResponse(
        conversation_id=conversation_id,
        session_id=session_id,
        raw_text=formatted,
        formatted_text=formatted,
        structured=structured,
        audit_hash=structured.get("audit_hash"),
        consistency_flag=structured.get("rule_result", {}).get("consistent"),
        warning=structured.get("warning")
    )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """SSE endpoint for token-by-token streaming.
    Events: token | done | refused | error — each as JSON on a data: line.
    """
    if chat_service is None:
        raise HTTPException(status_code=500, detail="Service not initialized")

    async def event_generator():
        loop = asyncio.get_event_loop()
        gen = chat_service.run_turn_streaming(
            request.message,
            session_id=request.session_id,
            retriever=request.retriever or "hybrid",
        )
        # run_turn_streaming is a sync generator; yield control between chunks
        for event in gen:
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


from .audit import get_session_log, verify_entry

@app.get("/api/audit/{session_id}")
async def get_audit_trail(session_id: str):
    """Returns the full reasoning trace and audit log for a session."""
    entries = get_session_log(session_id)
    if not entries:
        return {"session_id": session_id, "entries": [], "message": "No entries found"}
    
    return {
        "session_id": session_id,
        "entry_count": len(entries),
        "entries": entries,
        "integrity": [verify_entry(dict(e)) for e in entries]
    }


def get_app() -> FastAPI:
    """Helper for ASGI servers."""
    return app


# Serve the built React SPA in production.
# Registered last so it does not shadow any API routes above.
import os
from fastapi.staticfiles import StaticFiles

_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(_dist):
    app.mount("/", StaticFiles(directory=_dist, html=True), name="spa")

