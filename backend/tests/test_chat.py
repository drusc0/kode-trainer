import asyncio

import pytest
from fastapi.testclient import TestClient

from app import chat, judge, llm
from app.catalog import BY_SLUG, PROBLEMS
from app.catalog.base import Problem
from app.core import settings
from app.designs import BY_SLUG as DESIGNS_BY_SLUG
from app.main import app
from app.schemas import ChatMessage, Example

TWO_SUM = BY_SLUG["two-sum"]
CHAT_URL = "/api/sessions/000000000000000000000000/problems/two-sum/chat"
EXAMPLES = [
    Example(args=["[2, 7, 11, 15]", "9"], output="[0, 1]", note="nums[0] + nums[1] = 9."),
    Example(args=["[3, 2, 4]", "6"], output="[1, 2]"),
]


class FakeProvider:
    def __init__(self, text: str) -> None:
        self.text = text
        self.calls: list[tuple[str, list[llm.Message]]] = []

    async def complete(self, system: str, messages: list[llm.Message]) -> str:
        self.calls.append((system, messages))
        return self.text


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
    provider = FakeProvider("Try a hash map.")
    history = [ChatMessage(role="user", content="hi"), ChatMessage(role="assistant", content="hello")]
    out = asyncio.run(chat.reply(provider, "SYSTEM", history, "a hint?"))
    assert out == "Try a hash map."
    system, messages = provider.calls[0]
    assert system == "SYSTEM"
    assert messages == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
        {"role": "user", "content": "a hint?"},
    ]


def test_reply_caps_history() -> None:
    provider = FakeProvider("ok")
    history = [ChatMessage(role="user" if i % 2 == 0 else "assistant", content=str(i)) for i in range(100)]
    asyncio.run(chat.reply(provider, "S", history, "latest"))
    _, sent = provider.calls[0]
    assert len(sent) == chat.HISTORY_LIMIT + 1
    assert sent[0] == {"role": "user", "content": "60"}
    assert sent[-1] == {"role": "user", "content": "latest"}


def test_chat_without_key_returns_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "")
    resp = TestClient(app, base_url="http://localhost").post(CHAT_URL, json={"message": "hint?", "code": ""})
    assert resp.status_code == 503
    assert "LLM_API_KEY" in resp.json()["detail"]


def test_blank_message_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "sk-ant-test")
    resp = TestClient(app, base_url="http://localhost").post(CHAT_URL, json={"message": "   ", "code": ""})
    assert resp.status_code == 422


def test_reply_without_text_raises_chat_error() -> None:
    with pytest.raises(llm.ChatError):
        asyncio.run(chat.reply(FakeProvider("  \n"), "S", [], "x"))


@pytest.mark.parametrize("p", PROBLEMS, ids=lambda p: p.slug)
def test_system_prompt_builds_for_every_problem(p: Problem) -> None:
    examples = [
        Example(args=[judge.preview(v) for v in judge.to_editor(p, ex["args"])], output="x") for ex in p.examples
    ]
    prompt = chat.build_system_prompt(p, examples)
    assert f"Example {len(examples)}:" in prompt


PATTERN_CHAT_URL = "/api/sessions/000000000000000000000000/patterns/sliding-window/chat"


def test_pattern_prompt_is_a_mentor_without_reference_solutions() -> None:
    problems = [p for p in PROBLEMS if p.pattern == "sliding-window"]
    prompt = chat.build_pattern_prompt("sliding-window", problems)
    assert prompt.startswith(chat.MENTOR)
    assert 'name="sliding window"' in prompt
    assert all(f"- {p.title} ({p.difficulty})" in prompt for p in problems)
    assert not any(p.reference.strip() in prompt for p in problems)


def test_pattern_chat_without_key_returns_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "")
    resp = TestClient(app, base_url="http://localhost").post(PATTERN_CHAT_URL, json={"message": "why O(n)?"})
    assert resp.status_code == 503


def test_unknown_pattern_chat_returns_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "sk-ant-test")
    url = PATTERN_CHAT_URL.replace("sliding-window", "nope")
    resp = TestClient(app, base_url="http://localhost").post(url, json={"message": "hi"})
    assert resp.status_code == 404


DESIGN_CHAT_URL = "/api/sessions/000000000000000000000000/designs/url-shortener/chat"


def test_design_prompt_carries_question_and_hidden_rubric() -> None:
    d = DESIGNS_BY_SLUG["url-shortener"]
    prompt = chat.build_design_prompt(d)
    assert prompt.startswith(chat.INTERVIEWER)
    assert d.prompt in prompt
    assert all(r in prompt for r in d.functional + d.non_functional + d.scale + d.rubric)
    assert '<deep_dive_topics hidden="true">' in prompt


def test_design_turn_puts_notes_before_the_message() -> None:
    assert (
        chat.design_turn("review my design", "QPS ~ 40k\n") == "<my_notes>\nQPS ~ 40k\n</my_notes>\n\nreview my design"
    )
    assert chat.design_turn("hi", "  ") == "hi"


def test_reply_attaches_the_diagram_to_the_current_turn_only() -> None:
    provider = FakeProvider("Looks good.")
    history = [ChatMessage(role="user", content="earlier"), ChatMessage(role="assistant", content="ok")]
    asyncio.run(chat.reply(provider, "S", history, "review", "iVBORw0KGgo="))
    _, messages = provider.calls[0]
    assert messages[:2] == [{"role": "user", "content": "earlier"}, {"role": "assistant", "content": "ok"}]
    assert messages[2] == {"role": "user", "content": "review", "image": "iVBORw0KGgo="}


def test_design_chat_without_key_returns_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "")
    resp = TestClient(app, base_url="http://localhost").post(DESIGN_CHAT_URL, json={"message": "review"})
    assert resp.status_code == 503


@pytest.mark.parametrize("diagram", ["not base64!", "<svg/>"])
def test_design_chat_rejects_non_base64_diagram(monkeypatch: pytest.MonkeyPatch, diagram: str) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "sk-ant-test")
    body = {"message": "review", "diagram": diagram}
    assert TestClient(app, base_url="http://localhost").post(DESIGN_CHAT_URL, json=body).status_code == 422


def test_unknown_design_chat_returns_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_api_key", "sk-ant-test")
    url = DESIGN_CHAT_URL.replace("url-shortener", "nope")
    assert TestClient(app, base_url="http://localhost").post(url, json={"message": "hi"}).status_code == 404
