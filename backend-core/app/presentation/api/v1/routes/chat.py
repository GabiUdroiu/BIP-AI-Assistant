"""
Chat routes.
Send messages and receive AI responses using the chat application service.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.presentation.deps import get_chat_service, log_request_start, log_request_error
from app.application.services.chat_service import ChatApplicationService
from app.domain.exceptions import ChatError, ContextRetrievalError, DatabaseError
from app.presentation.api.v1.schemas import ChatRequest, ChatResponse, ApiResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ApiResponse[ChatResponse])
def chat(
    request: ChatRequest,
    chat_service: ChatApplicationService = Depends(get_chat_service),
):
    """
    Send a message and receive AI response.

    Processes the user message through RAG context retrieval, conversation history,
    and the configured LLM to generate a contextual response.
    """
    log_request_start("POST /chat", {"message": request.message[:50] + "..." if len(request.message) > 50 else request.message})

    try:
        reply = chat_service.send_message(
            message=request.message,
            session_id=request.session_id,
        )
        return ApiResponse(data=ChatResponse(reply=reply, session_id=request.session_id))
    except ChatError as e:
        log_request_error("POST /chat", str(e))
        raise HTTPException(status_code=503, detail=str(e)) from e
    except ContextRetrievalError as e:
        log_request_error("POST /chat", str(e))
        raise HTTPException(status_code=503, detail="Failed to retrieve context") from e
    except DatabaseError as e:
        log_request_error("POST /chat", str(e))
        raise HTTPException(status_code=503, detail="Database error") from e
    except Exception as e:
        log_request_error("POST /chat", str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/chat/history", response_model=ApiResponse[dict])
def get_conversation_history(
    session_id: str = "default",
    chat_service: ChatApplicationService = Depends(get_chat_service),
):
    """Get conversation history for a session."""
    log_request_start("GET /chat/history", {"session_id": session_id})

    try:
        history = chat_service.get_conversation_history(session_id)
        return ApiResponse(data={"session_id": session_id, "messages": history})
    except DatabaseError as e:
        log_request_error("GET /chat/history", str(e))
        raise HTTPException(status_code=503, detail="Database error") from e
    except Exception as e:
        log_request_error("GET /chat/history", str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e
