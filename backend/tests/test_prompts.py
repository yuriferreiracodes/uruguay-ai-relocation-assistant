from datetime import UTC, datetime

from app.llm.prompts import build_system_prompt


def test_prompt_states_the_current_date() -> None:
    prompt = build_system_prompt("en", None, today="2026-10-04")
    assert "Today is 2026-10-04" in prompt


def test_prompt_defaults_to_today() -> None:
    assert datetime.now(UTC).strftime("%Y-%m-%d") in build_system_prompt("en", None)


def test_context_is_appended_as_official_context() -> None:
    prompt = build_system_prompt("es", "Residencia legal: requisitos")
    assert prompt.endswith("Official context:\nResidencia legal: requisitos")
    assert "Spanish" in prompt
