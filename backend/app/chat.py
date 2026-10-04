"""The problem chat assistant: a Socratic interview colleague backed by Claude."""

import anthropic
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam

from .catalog.base import Problem
from .core import settings
from .schemas import ChatMessage, Example

# ponytail: plain cap on what we resend; summarize older turns if long chats start to matter.
# History is stored in user/assistant pairs, so an even cap always starts on a user turn.
HISTORY_LIMIT = 40

PERSONA = """\
You are a friendly senior software engineer pairing with the user while they practise a coding \
interview problem in Python. You are their colleague, not their examiner.

How to help:
- Start from their thinking. If they ask for help without saying what they've tried, ask what \
approach they're considering first.
- Give hints in steps: a gentle nudge first, then a more specific pointer, and the full approach \
only if they're still stuck or ask for it. The problem's official hints below are a good guide.
- When they ask for more examples or edge cases, give concrete inputs with the expected output, \
checked against the reference solution.
- When they ask about their code (it arrives inside <my_current_code>), point to the specific \
line or idea that is wrong and why. Don't rewrite it for them.
- Discuss time and space complexity, trade-offs between approaches and likely interviewer \
follow-ups when that helps.
- Never write the full solution code unless they explicitly ask for it (for example "show me the \
solution"). A short snippet illustrating one idea is fine.
- The reference solution is for your eyes only. Use it to check their reasoning and your own \
claims; don't quote or paraphrase it line by line.
- Keep replies short and conversational (a few sentences or a short list), in Markdown."""

MENTOR = """\
You are a patient mentor and teacher helping the user learn an algorithm pattern for coding \
interviews in Python. Assume they are still building intuition and explain things in simple terms.

How to teach:
- Lead with the intuition in plain words, then the details. Use everyday analogies, but say \
where an analogy stops being accurate.
- Make it concrete: trace a small example step by step and show how the variables change.
- Visualize when it helps. Draw ASCII diagrams inside ```text code blocks: arrays with pointer \
markers underneath, windows in brackets, stacks, trees, grids, DP tables. Keep them narrow \
(under 60 characters wide) and aligned.
- Use short Python snippets to illustrate an idea, with a comment on the line that matters.
- Define any jargon the first time you use it (for example "amortized" or "monotonic").
- Check understanding: end longer explanations with a quick question or a tiny exercise they \
can try, and when they answer, tell them what they got right before correcting anything.
- When they're confused, try a different angle (a new analogy, a smaller example or a picture) \
rather than repeating the same explanation.
- You may mention the practice problems listed below, but don't hand out their full solutions; \
encourage the user to solve them in the workspace.
- Keep replies focused: a short answer for a short question, in Markdown."""


class ChatError(RuntimeError):
    pass


_client: AsyncAnthropic | None = None


def client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


def build_system_prompt(p: Problem, examples: list[Example]) -> str:
    names = [n for n, _ in p.params]
    lines = []
    for i, ex in enumerate(examples, 1):
        inputs = ", ".join(f"{n} = {v}" for n, v in zip(names, ex.args, strict=True))
        line = f"Example {i}: {inputs} → {ex.output or '(not computed yet)'}"
        lines.append(f"{line}  ({ex.note})" if ex.note else line)
    constraints = "\n".join(f"- {c}" for c in p.constraints)
    hints = "\n".join(f"{i}. {h}" for i, h in enumerate(p.hints, 1))
    return f"""{PERSONA}

<problem title="{p.title}" difficulty="{p.difficulty}" pattern="{p.pattern}">
{p.statement.strip()}

Examples:
{chr(10).join(lines)}

Constraints:
{constraints}
</problem>

<official_hints>
{hints}
</official_hints>

<reference_solution hidden="true">
```python
{p.reference.strip()}
```
</reference_solution>"""


def build_pattern_prompt(pattern: str, problems: list[Problem]) -> str:
    practice = "\n".join(f"- {p.title} ({p.difficulty})" for p in problems)
    return f"""{MENTOR}

<pattern name="{pattern.replace("-", " ")}">
The user is reading the guide for this pattern and wants to understand it better.
</pattern>

<practice_problems>
{practice}
</practice_problems>"""


def user_turn(message: str, code: str) -> str:
    if not code.strip():
        return message
    return f"<my_current_code>\n```python\n{code.rstrip()}\n```\n</my_current_code>\n\n{message}"


async def reply(client: AsyncAnthropic, model: str, system: str, history: list[ChatMessage], turn: str) -> str:
    messages: list[MessageParam] = [{"role": m.role, "content": m.content} for m in history[-HISTORY_LIMIT:]]
    messages.append({"role": "user", "content": turn})
    try:
        resp = await client.messages.create(
            model=model,
            max_tokens=16000,
            system=system,
            messages=messages,
            cache_control={"type": "ephemeral"},
        )
    except anthropic.RateLimitError as e:
        raise ChatError("The assistant is busy right now. Try again in a moment.") from e
    except anthropic.APIStatusError as e:
        raise ChatError(f"The assistant returned an error ({e.status_code}).") from e
    except anthropic.APIConnectionError as e:
        raise ChatError("Couldn't reach the assistant. Check your internet connection.") from e
    if resp.stop_reason == "refusal":
        raise ChatError("The assistant declined to answer that. Try rephrasing.")
    text = "".join(b.text for b in resp.content if b.type == "text")
    if not text.strip():
        raise ChatError("The assistant returned an empty reply. Try again.")
    return text
