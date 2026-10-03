import json
from typing import Any, cast

import httpx
import pytest

from app.config import get_settings
from app.llm.base import LLMError, LLMTimeoutError
from app.llm.client import OpenAICompatibleClient
from app.schemas.chat import ChatMessage


def make(handler: httpx.MockTransport) -> OpenAICompatibleClient:
    return OpenAICompatibleClient(get_settings(), httpx.AsyncClient(transport=handler))


async def test_request_shape_and_language() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": " hola "}}]})

    client = make(httpx.MockTransport(handler))
    res = await client.answer(
        "hi", "pt-BR", [ChatMessage(role="user", content="before")], context="CTX"
    )
    assert res.text == "hola"
    body = cast(dict[str, Any], seen["body"])
    assert body["max_tokens"] == 600
    msgs = cast(list[dict[str, str]], body["messages"])
    assert "Portuguese (Brazil)" in msgs[0]["content"]
    assert "CTX" in msgs[0]["content"]
    assert [m["role"] for m in msgs] == ["system", "user", "user"]
    assert seen["auth"] == "Bearer secret-test-key"


async def test_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("t", request=request)

    with pytest.raises(LLMTimeoutError):
        await make(httpx.MockTransport(handler)).answer("hi", "en", [])


@pytest.mark.parametrize("status", [429, 500])
async def test_provider_error(status: int) -> None:
    client = make(httpx.MockTransport(lambda r: httpx.Response(status)))
    with pytest.raises(LLMError):
        await client.answer("hi", "en", [])


async def test_malformed_payload() -> None:
    client = make(httpx.MockTransport(lambda r: httpx.Response(200, json={"nope": 1})))
    with pytest.raises(LLMError):
        await client.answer("hi", "en", [])


async def test_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(LLMError):
        await OpenAICompatibleClient(get_settings()).answer("hi", "en", [])
