import logging
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException

from app.api.rate_limit import enforce_rate_limit
from app.config import get_settings
from app.knowledge.retriever import Retriever
from app.llm.base import LLMError, LLMTimeoutError
from app.llm.client import OpenAICompatibleClient
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)
router = APIRouter()


@lru_cache
def get_chat_service() -> ChatService:
    settings = get_settings()
    return ChatService(settings, OpenAICompatibleClient(settings), Retriever(settings))


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(enforce_rate_limit)])
async def chat(
    request: ChatRequest, service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    try:
        return await service.handle(request)
    except LLMTimeoutError as exc:
        logger.warning("LLM timeout")
        raise HTTPException(504, "The AI service took too long to respond.") from exc
    except LLMError as exc:
        logger.error("LLM error: %s", exc)
        raise HTTPException(503, "The AI service is temporarily unavailable.") from exc
