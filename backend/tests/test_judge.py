import random
from typing import Any

import pytest

from app import judge
from app.catalog import BY_SLUG, PROBLEMS, Problem

TWO_SUM = BY_SLUG["two-sum"]
LRU = BY_SLUG["lru-cache"]


@pytest.mark.parametrize(
    ("res", "total", "expected"),
    [
        ({"status": "compile_error", "results": []}, 2, ("Compile Error", None)),
        ({"status": "ok", "results": [{"ok": True}, {"ok": True}]}, 2, ("Accepted", None)),
        ({"status": "ok", "results": [{"ok": True}, {"ok": False}]}, 2, ("Wrong Answer", 1)),
        ({"status": "ok", "results": [{"ok": False, "error_type": "memory"}]}, 1, ("Memory Limit Exceeded", 0)),
        ({"status": "ok", "results": [{"ok": False, "error_type": "runtime"}]}, 1, ("Runtime Error", 0)),
        ({"status": "timeout", "results": [{"ok": True}]}, 3, ("Time Limit Exceeded", 1)),
        ({"status": "crashed", "results": []}, 1, ("Runtime Error", 0)),
    ],
)
def test_verdict_of(res: dict[str, Any], total: int, expected: tuple[str, int | None]) -> None:
    assert judge.verdict_of(res, total) == expected


def test_preview_truncates_long_values() -> None:
    assert judge.preview([1, 2]) == "[1, 2]"
    long = judge.preview("x" * (judge.PREVIEW_CHARS + 50))
    assert long.startswith('"xxx')
    assert long.endswith("(52 more characters)")


def test_from_editor_rejects_wrong_arity() -> None:
    with pytest.raises(ValueError, match="expected 2 values, got 1"):
        judge.from_editor(TWO_SUM, [[1, 2]])


def test_design_cases_round_trip_through_editor() -> None:
    values = [["LRUCache", "put", "get"], [[2], [1, 1], [1]]]
    stored = judge.from_editor(LRU, values)
    assert stored == [{"ops": values[0], "args": values[1]}]
    assert judge.to_editor(LRU, stored) == values


@pytest.mark.parametrize(
    "values",
    [
        [["put"], [[1, 1]]],  # must start with the constructor
        [["LRUCache", "get"], [[2]]],  # one arg list per op
        [[], []],
    ],
)
def test_design_cases_reject_malformed_ops(values: list[Any]) -> None:
    with pytest.raises(ValueError, match="operations must start with"):
        judge.from_editor(LRU, values)


@pytest.mark.parametrize("problem", PROBLEMS, ids=lambda p: p.slug)
def test_hidden_tests_are_deterministic(problem: Problem) -> None:
    """Expected outputs are seeded once per fingerprint, so generators must be reproducible from the slug."""
    assert problem.gen(random.Random(problem.slug)) == problem.gen(random.Random(problem.slug))
