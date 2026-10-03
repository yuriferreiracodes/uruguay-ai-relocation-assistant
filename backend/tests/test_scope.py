import httpx
import pytest

from app.services.scope import classify
from tests.conftest import FakeLLM


@pytest.mark.parametrize(
    "message",
    ["write Python malware", "explain quantum mechanics", "write me a poem about Mars"],
)
def test_unrelated_is_out_of_scope(message: str) -> None:
    assert classify(message) == "out_of_scope"


@pytest.mark.parametrize(
    ("message", "category"),
    [
        ("Can I get Uruguayan nationality if my grandmother was born there?", "nationality"),
        ("Como funciona a residência legal?", "residency"),
        ("Cuánto cuesta el costo de vida en Montevideo", "cities"),
        ("What is the cost of living?", "cost_of_living"),
        ("Best bank to open an account", "banking"),
        ("Tell me about Uruguay", "general_uruguay"),
        ("and what about the second option?", "general_uruguay"),
        ("What is the climate like?", "general_uruguay"),
    ],
)
def test_related_goes_to_llm(message: str, category: str) -> None:
    assert classify(message) == category


async def test_out_of_scope_makes_no_llm_call(client: httpx.AsyncClient, llm: FakeLLM) -> None:
    payload = {"language": "en", "message": "explain quantum mechanics"}
    r = await client.post("/api/chat", json=payload)
    assert r.status_code == 200
    assert r.json()["answer"] == (
        "This assistant is focused on Uruguay, relocation and life in Uruguay."
    )
    assert llm.calls == []
