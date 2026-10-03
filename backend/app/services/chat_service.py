import logging

from app.config import Settings
from app.knowledge.retriever import Retriever
from app.llm.base import LLMClient
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.scope import OUT_OF_SCOPE_REPLY, classify

logger = logging.getLogger(__name__)


class ChatService:
    """scope check -> optional retrieval -> one LLM call."""

    def __init__(self, settings: Settings, llm: LLMClient, retriever: Retriever) -> None:
        self._settings = settings
        self._llm = llm
        self._retriever = retriever

    async def handle(self, request: ChatRequest) -> ChatResponse:
        category = classify(request.message)
        if category == "out_of_scope":
            return ChatResponse(answer=OUT_OF_SCOPE_REPLY[request.language], category=category)

        history = request.history[-self._settings.max_history_messages :]
        context = await self._retriever.retrieve(category)
        result = await self._llm.answer(
            message=request.message,
            language=request.language,
            history=history,
            context=context.text,
        )
        return ChatResponse(answer=result.text, sources=context.sources, category=category)
