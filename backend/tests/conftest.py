from collections.abc import AsyncIterator

import httpx
import pytest

from app.api.chat import get_chat_service
from app.api.rate_limit import limiter
from app.config import get_settings
from app.knowledge.retriever import RetrievedContext
from app.llm.base import LLMResponse
from app.main import create_app
from app.schemas.chat import ChatMessage
from app.services.chat_service import ChatService


class FakeLLM:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.error: Exception | None = None

    async def answer(
        self,
        message: str,
        language: str,
        history: list[ChatMessage],
        context: str | None = None,
    ) -> LLMResponse:
        self.calls.append(
            {"message": message, "language": language, "history": history, "context": context}
        )
        if self.error:
            raise self.error
        return LLMResponse(text="fake answer")


class FakeRetriever:
    def __init__(self) -> None:
        self.result = RetrievedContext()
        self.categories: list[str] = []

    async def retrieve(self, category: str) -> RetrievedContext:
        self.categories.append(category)
        return self.result


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "secret-test-key")
    get_settings.cache_clear()
    limiter._hits.clear()  # pyright: ignore[reportPrivateUsage]


@pytest.fixture
def llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def retriever() -> FakeRetriever:
    return FakeRetriever()


@pytest.fixture
async def client(llm: FakeLLM, retriever: FakeRetriever) -> AsyncIterator[httpx.AsyncClient]:
    app = create_app()
    service = ChatService(get_settings(), llm, retriever)  # type: ignore[arg-type]
    app.dependency_overrides[get_chat_service] = lambda: service
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
