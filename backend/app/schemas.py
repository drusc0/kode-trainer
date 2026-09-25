"""Request and response models: the API contract. The frontend's types are generated from these."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from .core import settings

Target = Literal["google", "meta", "general"]
Difficulty = Literal["Easy", "Medium", "Hard"]


# ---------------------------------------------------------------- requests
class SessionIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    target: Target = "general"
    notes: str = Field(default="", max_length=2000)


class SessionPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    target: Target | None = None
    notes: str | None = Field(default=None, max_length=2000)


class CodeIn(BaseModel):
    code: str = Field(max_length=settings.max_code_bytes)


class RunIn(CodeIn):
    cases: list[list[Any]] = Field(min_length=1, max_length=settings.max_custom_cases)


# ---------------------------------------------------------------- responses
class SeedState(BaseModel):
    status: str
    done: int
    total: int
    errors: list[str]


class Health(BaseModel):
    ok: bool
    seeding: SeedState


class Session(BaseModel):
    id: str
    name: str
    target: Target
    notes: str
    created_at: datetime
    last_active_at: datetime | None
    solved: int
    attempted: int


class ProblemSummary(BaseModel):
    slug: str
    title: str
    difficulty: Difficulty
    pattern: str
    topics: list[str]
    companies: list[str]
    status: Literal["solved", "attempted"] | None
    attempts: int


class ProblemList(BaseModel):
    patterns: list[str]
    problems: list[ProblemSummary]


class EditorField(BaseModel):
    name: str
    type: str


class Example(BaseModel):
    args: list[str]
    output: str | None
    note: str | None = None


class ProblemDetail(ProblemSummary):
    statement: str
    constraints: list[str]
    hints: list[str]
    kind: Literal["function", "design"]
    fields: list[EditorField]
    examples: list[Example]
    default_cases: list[list[str]]
    starter_code: str
    draft: str | None


class CaseResult(BaseModel):
    args: list[str]
    ok: bool | None = None
    output: str | None = None
    expected: str | None = None
    stdout: str | None = None
    error: str | None = None
    ms: float | None = None
    input_error: str | None = None


class RunResult(BaseModel):
    verdict: str
    compile_error: str | None
    cases: list[CaseResult]
    passed: int
    runtime_ms: float | None


class FailingCase(CaseResult):
    index: int
    is_example: bool


class SubmitResult(BaseModel):
    submission_id: str
    verdict: str
    passed: int
    total: int
    compile_error: str | None
    runtime_ms: float | None
    failing: FailingCase | None


class Submission(BaseModel):
    id: str
    verdict: str
    passed: int
    total: int
    runtime_ms: float | None
    created_at: datetime
    code: str


class Bucket(BaseModel):
    solved: int
    total: int


class DifficultyBuckets(BaseModel):
    Easy: Bucket
    Medium: Bucket
    Hard: Bucket


class RecentSubmission(BaseModel):
    id: str
    problem: str
    title: str
    verdict: str
    created_at: datetime
    runtime_ms: float | None


class SessionStats(BaseModel):
    by_difficulty: DifficultyBuckets
    by_pattern: dict[str, Bucket]
    submissions: int
    accepted: int
    recent: list[RecentSubmission]


# ---------------------------------------------------------------- chat
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
