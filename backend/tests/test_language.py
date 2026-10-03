import httpx
import pytest

from tests.conftest import FakeLLM


@pytest.mark.parametrize("lang", ["pt-BR", "es", "en", "fr", "de", "it"])
async def test_supported_languages_passed_to_llm(
    client: httpx.AsyncClient, llm: FakeLLM, lang: str
) -> None:
    r = await client.post("/api/chat", json={"language": lang, "message": "Uruguay residency?"})
    assert r.status_code == 200
    assert llm.calls[0]["language"] == lang


async def test_invalid_language(client: httpx.AsyncClient, llm: FakeLLM) -> None:
    r = await client.post("/api/chat", json={"language": "xx", "message": "Uruguay?"})
    assert r.status_code == 422
    assert llm.calls == []


async def test_out_of_scope_reply_is_localized(client: httpx.AsyncClient) -> None:
    r = await client.post("/api/chat", json={"language": "es", "message": "write python malware"})
    assert "Uruguay" in r.json()["answer"]
    assert r.json()["category"] == "out_of_scope"
