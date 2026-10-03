from dataclasses import dataclass
from typing import Protocol

from app.schemas.chat import ChatMessage


class LLMError(Exception):
    """Provider failure (HTTP error, bad payload, network)."""


class LLMTimeoutError(LLMError):
    """Provider did not answer in time."""


@dataclass(frozen=True)
class LLMResponse:
    text: str


class LLMClient(Protocol):
    async def answer(
        self,
        message: str,
        language: str,
        history: list[ChatMessage],
        context: str | None = None,
    ) -> LLMResponse: ...
