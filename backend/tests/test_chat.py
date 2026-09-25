import asyncio
from types import SimpleNamespace
from typing import Any, cast

import pytest
from anthropic import AsyncAnthropic
from fastapi.testclient import TestClient

from app import chat
from app.catalog import BY_SLUG
from app.core import settings
from app.main import app
from app.schemas import ChatMessage, Example

TWO_SUM = BY_SLUG["two-sum"]
CHAT_URL = "/api/sessions/000000000000000000000000/problems/two-sum/chat"
EXAMPLES = [
    Example(args=["[2, 7, 11, 15]", "9"], output="[0, 1]", note="nums[0] + nums[1] = 9."),
    Example(args=["[3, 2, 4]", "6"], output="[1, 2]"),
]


class FakeMessages:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return self.response


def fake_client(text: str, stop_reason: str = "end_turn") -> tuple[AsyncAnthropic, FakeMessages]:
    messages = FakeMessages(SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)]))
    return cast(AsyncAnthropic, SimpleNamespace(messages=messages)), messages


def test_system_prompt_carries_the_whole_problem() -> None:
    prompt = chat.build_system_prompt(TWO_SUM, EXAMPLES)
    assert TWO_SUM.statement.strip()[:60] in prompt
    assert "nums = [2, 7, 11, 15], target = 9 → [0, 1]" in prompt
    assert "nums = [3, 2, 4], target = 6 → [1, 2]" in prompt
    assert all(h in prompt for h in TWO_SUM.hints)
    assert TWO_SUM.reference.strip() in prompt


def test_user_turn_attaches_code() -> None:
    turn = chat.user_turn("why does this fail?", "def f():\n    return 1\n")
    assert "<my_current_code>" in turn and "return 1" in turn
    assert turn.endswith("why does this fail?")


def test_user_turn_without_code_is_just_the_message() -> None:
    assert chat.user_turn("hint please", "   \n") == "hint please"


def test_reply_sends_history_then_turn_and_returns_text() -> None:
    client, messages = fake_client("Try a hash map.")
    history = [ChatMessage(role="user", content="hi"), ChatMessage(role="assistant", content="hello")]
    out = asyncio.run(chat.reply(client, "claude-sonnet-5", "SYSTEM", history, "a hint?"))
    assert out == "Try a hash map."
    call = messages.calls[0]
    assert call["model"] == "claude-sonnet-5"
    assert call["system"] == "SYSTEM"
    assert call["messages"] == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
        {"role": "user", "content": "a hint?"},
    ]


def test_reply_caps_history() -> None:
    client, messages = fake_client("ok")
    history = [ChatMessage(role="user" if i % 2 == 0 else "assistant", content=str(i)) for i in range(100)]
    asyncio.run(chat.reply(client, "m", "S", history, "latest"))
    sent = messages.calls[0]["messages"]
    assert len(sent) == chat.HISTORY_LIMIT + 1
    assert sent[0] == {"role": "user", "content": "60"}
    assert sent[-1] == {"role": "user", "content": "latest"}


def test_reply_refusal_raises_chat_error() -> None:
    client, _ = fake_client("", stop_reason="refusal")
    with pytest.raises(chat.ChatError):
        asyncio.run(chat.reply(client, "m", "S", [], "x"))


def test_chat_without_key_returns_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "")
    resp = TestClient(app).post(CHAT_URL, json={"message": "hint?", "code": ""})
    assert resp.status_code == 503
    assert "ANTHROPIC_API_KEY" in resp.json()["detail"]


def test_blank_message_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    resp = TestClient(app).post(CHAT_URL, json={"message": "   ", "code": ""})
    assert resp.status_code == 422
