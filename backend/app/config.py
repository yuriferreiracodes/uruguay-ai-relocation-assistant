import os
from dataclasses import dataclass
from functools import lru_cache


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    return int(raw) if raw else default


def _bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    return raw.lower() in {"1", "true", "yes"} if raw else default


@dataclass(frozen=True)
class Settings:
    app_env: str
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    llm_timeout_seconds: int
    max_history_messages: int
    max_message_length: int
    max_output_tokens: int
    rate_limit_requests: int
    rate_limit_window_seconds: int
    trust_proxy_headers: bool
    retrieval_timeout_seconds: int
    retrieval_cache_ttl_seconds: int


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_env=os.environ.get("APP_ENV", "development"),
        llm_api_key=os.environ.get("LLM_API_KEY", ""),
        llm_base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
        llm_model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
        llm_timeout_seconds=_int("LLM_TIMEOUT_SECONDS", 30),
        max_history_messages=_int("MAX_HISTORY_MESSAGES", 6),
        max_message_length=_int("MAX_MESSAGE_LENGTH", 2000),
        max_output_tokens=_int("MAX_OUTPUT_TOKENS", 600),
        rate_limit_requests=_int("RATE_LIMIT_REQUESTS", 10),
        rate_limit_window_seconds=_int("RATE_LIMIT_WINDOW_SECONDS", 60),
        trust_proxy_headers=_bool("TRUST_PROXY_HEADERS"),
        retrieval_timeout_seconds=_int("RETRIEVAL_TIMEOUT_SECONDS", 5),
        retrieval_cache_ttl_seconds=_int("RETRIEVAL_CACHE_TTL_SECONDS", 21600),
    )
