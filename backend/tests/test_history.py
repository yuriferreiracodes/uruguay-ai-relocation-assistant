import httpx

from tests.conftest import FakeLLM


async def test_history_trimmed_to_last_n(client: httpx.AsyncClient, llm: FakeLLM) -> None:
    history = [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"m{i}"} for i in range(20)
    ]
    r = await client.post(
        "/api/chat", json={"language": "en", "message": "Uruguay cities?", "history": history}
    )
    assert r.status_code == 200
    sent = llm.calls[0]["history"]
    assert [m.content for m in sent] == [f"m{i}" for i in range(14, 20)]  # type: ignore[attr-defined]


async def test_history_too_large_rejected(client: httpx.AsyncClient) -> None:
    history = [{"role": "user", "content": "x"}] * 51
    r = await client.post(
        "/api/chat", json={"language": "en", "message": "Uruguay?", "history": history}
    )
    assert r.status_code == 422


async def test_history_invalid_role_rejected(client: httpx.AsyncClient) -> None:
    history = [{"role": "system", "content": "x"}]
    r = await client.post(
        "/api/chat", json={"language": "en", "message": "Uruguay?", "history": history}
    )
    assert r.status_code == 422
