from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.config import get_settings

LanguageCode = Literal["pt-BR", "es", "en", "fr", "de", "it"]

Category = Literal[
    "nationality",
    "citizenship",
    "residency",
    "immigration",
    "documents",
    "cities",
    "cost_of_living",
    "banking",
    "education",
    "employment",
    "healthcare",
    "taxes",
    "culture",
    "transport",
    "housing",
    "general_uruguay",
    "out_of_scope",
]

MAX_HISTORY_INPUT = 50
MAX_HISTORY_CONTENT = 8000


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=MAX_HISTORY_CONTENT)


class ChatRequest(BaseModel):
    language: LanguageCode
    message: str
    history: list[ChatMessage] = Field(
        default_factory=lambda: list[ChatMessage](), max_length=MAX_HISTORY_INPUT
    )

    @field_validator("message")
    @classmethod
    def _validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message must not be empty")
        if len(value) > get_settings().max_message_length:
            raise ValueError("message is too long")
        return value


class Source(BaseModel):
    title: str
    url: str
    retrieved_at: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=lambda: list[Source]())
    category: Category
