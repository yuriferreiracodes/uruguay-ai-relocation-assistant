import httpx
import pytest

from app.config import get_settings
from app.knowledge.retriever import RetrievedContext
from app.llm.base import LLMError, LLMTimeoutError
from app.schemas.chat import Source
from tests.conftest import FakeLLM, FakeRetriever


def body(message: str = "Can I get residency in Uruguay?", **extra: object) -> dict[str, object]:
    return {"language": "en", "message": message, "history": [], **extra}


async def test_chat_ok(client: httpx.AsyncClient, llm: FakeLLM) -> None:
    r = await client.post("/api/chat", json=body())
    assert r.status_code == 200
    assert r.json() == {"answer": "fake answer", "sources": [], "category": "residency"}
    assert len(llm.calls) == 1


async def test_empty_message(client: httpx.AsyncClient) -> None:
    r = await client.post("/api/chat", json=body("   "))
    assert r.status_code == 422
    assert r.json() == {"detail": "Invalid request."}


async def test_oversized_message(client: httpx.AsyncClient, llm: FakeLLM) -> None:
    r = await client.post("/api/chat", json=body("a" * 2001))
    assert r.status_code == 422
    assert llm.calls == []


async def test_sources_returned_with_retrieval(
    client: httpx.AsyncClient, llm: FakeLLM, retriever: FakeRetriever
) -> None:
    retriever.result = RetrievedContext(
        text="official text",
        sources=[Source(title="IMPO", url="https://www.impo.com.uy", retrieved_at="2026-10-03")],
    )
    r = await client.post("/api/chat", json=body())
    assert r.json()["sources"][0]["title"] == "IMPO"
    assert llm.calls[0]["context"] == "official text"
    assert retriever.categories == ["residency"]


async def test_llm_timeout(client: httpx.AsyncClient, llm: FakeLLM) -> None:
    llm.error = LLMTimeoutError("slow")
    r = await client.post("/api/chat", json=body())
    assert r.status_code == 504
    assert "slow" not in r.text


async def test_llm_provider_error_hides_details(client: httpx.AsyncClient, llm: FakeLLM) -> None:
    llm.error = LLMError("boom secret-test-key Traceback")
    r = await client.post("/api/chat", json=body())
    assert r.status_code == 503
    assert r.json() == {"detail": "The AI service is temporarily unavailable."}


async def test_rate_limit(client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "2")
    get_settings.cache_clear()
    codes = [(await client.post("/api/chat", json=body())).status_code for _ in range(3)]
    assert codes == [200, 200, 429]


async def test_api_key_never_in_responses(client: httpx.AsyncClient) -> None:
    for r in (
        await client.get("/api/health"),
        await client.post("/api/chat", json=body()),
        await client.post("/api/chat", json={"bad": 1}),
    ):
        assert "secret-test-key" not in r.text
