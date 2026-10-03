import httpx

from app.config import Settings
from app.llm.base import LLMError, LLMResponse, LLMTimeoutError
from app.llm.prompts import build_system_prompt
from app.schemas.chat import ChatMessage


class OpenAICompatibleClient:
    """Talks to any OpenAI-compatible /chat/completions endpoint."""

    def __init__(self, settings: Settings, http: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._http = http

    async def answer(
        self,
        message: str,
        language: str,
        history: list[ChatMessage],
        context: str | None = None,
    ) -> LLMResponse:
        s = self._settings
        if not s.llm_api_key:
            raise LLMError("LLM_API_KEY is not configured")

        messages: list[dict[str, str]] = [
            {"role": "system", "content": build_system_prompt(language, context)},
            *({"role": m.role, "content": m.content} for m in history),
            {"role": "user", "content": message},
        ]
        payload = {
            "model": s.llm_model,
            "messages": messages,
            "max_tokens": s.max_output_tokens,
            "temperature": 0.3,
        }
        url = f"{s.llm_base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {s.llm_api_key}"}

        try:
            if self._http is not None:
                resp = await self._http.post(url, json=payload, headers=headers)
            else:
                async with httpx.AsyncClient(timeout=s.llm_timeout_seconds) as http:
                    resp = await http.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"]
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError("LLM request timed out") from exc
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise LLMError("LLM request failed") from exc

        if not isinstance(text, str) or not text.strip():
            raise LLMError("LLM returned an empty answer")
        return LLMResponse(text=text.strip())
