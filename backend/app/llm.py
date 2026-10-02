"""LLM providers for the chat assistant, chosen from the shape of the API key (bring your own key)."""

from collections.abc import Callable
from dataclasses import dataclass
from functools import cache, partial
from typing import Literal, Protocol, TypedDict

import anthropic
import httpx
from anthropic import AsyncAnthropic

from .core import settings

BUSY = "The assistant is busy right now. Try again in a moment."
UNREACHABLE = "Couldn't reach the assistant. Check your internet connection."
REFUSED = "The assistant declined to answer that. Try rephrasing."


class ChatError(RuntimeError):
    pass


class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class LLMProvider(Protocol):
    async def complete(self, system: str, messages: list[Message]) -> str: ...


class AnthropicProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def complete(self, system: str, messages: list[Message]) -> str:
        try:
            resp = await self.client.messages.create(
                model=self.model,
                max_tokens=16000,
                system=system,
                messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                cache_control={"type": "ephemeral"},
            )
        except anthropic.RateLimitError as e:
            raise ChatError(BUSY) from e
        except anthropic.APIStatusError as e:
            raise ChatError(f"The assistant returned an error ({e.status_code}).") from e
        except anthropic.APIConnectionError as e:
            raise ChatError(UNREACHABLE) from e
        if resp.stop_reason == "refusal":
            raise ChatError(REFUSED)
        return "".join(b.text for b in resp.content if b.type == "text")


class OpenAICompatibleProvider:
    """Any `/chat/completions` endpoint: OpenAI, OpenRouter, Gemini's OpenAI layer."""

    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self.http = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(120.0, connect=5.0),
        )
        self.model = model

    async def complete(self, system: str, messages: list[Message]) -> str:
        body = {"model": self.model, "messages": [{"role": "system", "content": system}, *messages]}
        try:
            resp = await self.http.post("/chat/completions", json=body)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            code = e.response.status_code
            raise ChatError(BUSY if code == 429 else f"The assistant returned an error ({code}).") from e
        except httpx.TransportError as e:
            raise ChatError(UNREACHABLE) from e
        choice = resp.json()["choices"][0]
        if choice.get("finish_reason") == "content_filter" or choice["message"].get("refusal"):
            raise ChatError(REFUSED)
        return str(choice["message"].get("content") or "")


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    key_prefix: str
    default_model: str
    build: Callable[[str, str], LLMProvider]


def openai_compatible(base_url: str) -> Callable[[str, str], LLMProvider]:
    return partial(OpenAICompatibleProvider, base_url=base_url)


# Adding a provider is one line. Matching takes the longest prefix, so order doesn't matter.
PROVIDERS: tuple[ProviderSpec, ...] = (
    ProviderSpec("Anthropic", "sk-ant-", "claude-sonnet-5", AnthropicProvider),
    ProviderSpec("OpenRouter", "sk-or-", "openai/gpt-5", openai_compatible("https://openrouter.ai/api/v1")),
    ProviderSpec("OpenAI", "sk-", "gpt-5", openai_compatible("https://api.openai.com/v1")),
    ProviderSpec(
        "Gemini",
        "AIza",
        "gemini-2.5-flash",
        openai_compatible("https://generativelanguage.googleapis.com/v1beta/openai"),
    ),
)
NOT_CONFIGURED = (
    "Chat is not configured: set LLM_API_KEY in .env to an "
    + ", ".join(s.name for s in PROVIDERS[:-1])
    + f" or {PROVIDERS[-1].name} key"
)


def create_provider(api_key: str, model: str = "") -> LLMProvider:
    matches = [s for s in PROVIDERS if api_key.startswith(s.key_prefix)]
    if not matches:
        raise ValueError(NOT_CONFIGURED)
    spec = max(matches, key=lambda s: len(s.key_prefix))
    return spec.build(api_key, model or spec.default_model)


@cache
def provider() -> LLMProvider:
    return create_provider(settings.llm_api_key, settings.chat_model)
