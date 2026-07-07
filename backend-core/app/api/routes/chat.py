from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_chat_provider, get_conversation_service, get_prompt_service, get_rag_service
from app.models.api_response import ApiResponse
from app.services.conversation_service import ConversationService
from app.services.prompt_service import PromptService
from app.services.rag_service import RagService

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    provider: str | None = None


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ApiResponse[ChatResponse])
def chat(
    request: ChatRequest,
    rag_service: RagService = Depends(get_rag_service),
    prompt_service: PromptService = Depends(get_prompt_service),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    chat_provider = get_chat_provider(request.provider)
    if not chat_provider.api_key:
        raise HTTPException(status_code=503, detail=f"No API key configured for provider '{request.provider or 'default'}'")

    facts = rag_service.retrieve(request.message)
    system_prompt = prompt_service.get_system_prompt()
    if facts:
        system_prompt += "\n\nRelevant facts:\n" + "\n".join(facts)

    history = conversation_service.get_history(request.session_id)

    messages = [{"role": "system", "content": system_prompt}, *history, {"role": "user", "content": request.message}]
    reply = chat_provider.reply(messages)

    conversation_service.save_message(request.session_id, "user", request.message)
    conversation_service.save_message(request.session_id, "assistant", reply)

    return ApiResponse.ok(ChatResponse(reply=reply))
