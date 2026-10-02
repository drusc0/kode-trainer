import asyncio
import json
from types import SimpleNamespace
from typing import Any, cast

import httpx
import pytest
from anthropic import AsyncAnthropic

from app import llm

MESSAGES: list[llm.Message] = [{"role": "user", "content": "a hint?"}]


@pytest.mark.parametrize(
    ("key", "kind", "model", "base_url"),
    [
        ("sk-ant-api03-x", llm.AnthropicProvider, "claude-sonnet-5", None),
        ("sk-or-v1-x", llm.OpenAICompatibleProvider, "openai/gpt-5", "https://openrouter.ai/api/v1/"),
        ("sk-proj-x", llm.OpenAICompatibleProvider, "gpt-5", "https://api.openai.com/v1/"),
        ("sk-x", llm.OpenAICompatibleProvider, "gpt-5", "https://api.openai.com/v1/"),
        (
            "AIzaSy-x",
            llm.OpenAICompatibleProvider,
            "gemini-2.5-flash",
            "https://generativelanguage.googleapis.com/v1beta/openai/",
        ),
    ],
)
def test_key_prefix_picks_the_provider(key: str, kind: type, model: str, base_url: str | None) -> None:
    provider = llm.create_provider(key)
    assert isinstance(provider, kind)
    assert cast(Any, provider).model == model
    if base_url:
        assert str(cast(llm.OpenAICompatibleProvider, provider).http.base_url) == base_url


def test_chat_model_overrides_the_default() -> None:
    assert cast(llm.AnthropicProvider, llm.create_provider("sk-ant-x", "claude-opus-5-5")).model == "claude-opus-5-5"


@pytest.mark.parametrize("key", ["", "gsk_unknown", "ant-sk-x"])
def test_unknown_or_missing_key_is_not_configured(key: str) -> None:
    with pytest.raises(ValueError, match="LLM_API_KEY"):
        llm.create_provider(key)


def anthropic_provider(stop_reason: str, text: str) -> tuple[llm.AnthropicProvider, list[dict[str, Any]]]:
    calls: list[dict[str, Any]] = []

    async def create(**kwargs: Any) -> Any:
        calls.append(kwargs)
        return SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)])

    provider = llm.AnthropicProvider("sk-ant-x", "claude-sonnet-5")
    provider.client = cast(AsyncAnthropic, SimpleNamespace(messages=SimpleNamespace(create=create)))
    return provider, calls


def test_anthropic_sends_system_and_messages() -> None:
    provider, calls = anthropic_provider("end_turn", "Try a hash map.")
    assert asyncio.run(provider.complete("SYSTEM", MESSAGES)) == "Try a hash map."
    assert calls[0]["model"] == "claude-sonnet-5"
    assert calls[0]["system"] == "SYSTEM"
    assert calls[0]["messages"] == MESSAGES


def test_anthropic_refusal_raises_chat_error() -> None:
    provider, _ = anthropic_provider("refusal", "")
    with pytest.raises(llm.ChatError, match="declined"):
        asyncio.run(provider.complete("S", MESSAGES))


def openai_provider(handler: Any) -> llm.OpenAICompatibleProvider:
    provider = llm.OpenAICompatibleProvider("sk-x", "gpt-5", "https://api.example.com/v1")
    provider.http = httpx.AsyncClient(base_url="https://api.example.com/v1", transport=httpx.MockTransport(handler))
    return provider


def completion(content: str | None, finish_reason: str = "stop", refusal: str | None = None) -> httpx.Response:
    message = {"role": "assistant", "content": content, "refusal": refusal}
    return httpx.Response(200, json={"choices": [{"message": message, "finish_reason": finish_reason}]})


def test_openai_compatible_puts_system_first_and_returns_content() -> None:
    sent: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return completion("Try a hash map.")

    assert asyncio.run(openai_provider(handler).complete("SYSTEM", MESSAGES)) == "Try a hash map."
    assert str(sent[0].url) == "https://api.example.com/v1/chat/completions"
    body = json.loads(sent[0].content)
    assert body["model"] == "gpt-5"
    assert body["messages"] == [{"role": "system", "content": "SYSTEM"}, *MESSAGES]


@pytest.mark.parametrize(
    ("response", "error"),
    [
        (httpx.Response(429), "busy"),
        (httpx.Response(401), r"error \(401\)"),
        (completion(None, finish_reason="content_filter"), "declined"),
        (completion(None, refusal="I can't help with that."), "declined"),
    ],
)
def test_openai_compatible_failures_raise_chat_error(response: httpx.Response, error: str) -> None:
    with pytest.raises(llm.ChatError, match=error):
        asyncio.run(openai_provider(lambda _: response).complete("S", MESSAGES))


def test_openai_compatible_connection_failure_raises_chat_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    with pytest.raises(llm.ChatError, match="reach"):
        asyncio.run(openai_provider(handler).complete("S", MESSAGES))
