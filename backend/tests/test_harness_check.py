import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from app import judge
from app.catalog import BY_SLUG

HARNESS = Path(__file__).resolve().parents[2] / "runner" / "harness.py"
_spec = importlib.util.spec_from_file_location("harness", HARNESS)
assert _spec is not None and _spec.loader is not None
harness = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(harness)

COURSES = [4, [[1, 0], [2, 0], [3, 1], [3, 2]]]


@pytest.mark.parametrize(
    ("out", "ok"),
    [
        ([0, 1, 2, 3], True),
        ([0, 2, 1, 3], True),
        ([1, 0, 2, 3], False),  # 1 before its prerequisite 0
        ([0, 1, 2], False),  # a course is missing
        ([0, 1, 2, 3, 3], False),
        ([0, True, 2, 3], False),
        ([], False),
        ("0123", False),
    ],
)
def test_topo_order_accepts_any_valid_order(out: Any, ok: bool) -> None:
    assert harness.check("topo_order", out, [0, 1, 2, 3], COURSES) is ok


@pytest.mark.parametrize(("out", "ok"), [([], True), ([0, 1], False), (None, False)])
def test_topo_order_requires_empty_list_when_impossible(out: Any, ok: bool) -> None:
    assert harness.check("topo_order", out, [], [2, [[0, 1], [1, 0]]]) is ok


def _run(slug: str, code: str, tests: list[Any]) -> list[dict[str, Any]]:
    """Run code through the real harness (no sandbox), with expected outputs from the reference."""
    p = BY_SLUG[slug]

    def go(source: str, expected: list[Any] | None) -> list[dict[str, Any]]:
        job = json.dumps(judge.make_job(p, source, tests, expected))
        proc = subprocess.run([sys.executable, str(HARNESS)], input=job.encode(), capture_output=True, check=True)
        return [r for r in map(json.loads, proc.stdout.decode().splitlines()) if r.get("type") == "result"]

    return go(code, [r["output"] for r in go(p.reference, None)])


def test_cycle_pos_builds_a_cycle_and_is_not_passed_to_the_solution() -> None:
    code = "class Solution:\n    def detectCycle(self, head):\n        return head"
    results = _run("linked-list-cycle-ii", code, [[[3, 2, 0, -4], 1], [[3, 2, 0, -4], 0], [[1], -1]])
    assert [r["output"] for r in results] == [0, 0, 0]
    assert [r["ok"] for r in results] == [False, True, False]


@pytest.mark.parametrize(
    ("slug", "code", "tests"),
    [
        ("clone-graph", "class Solution:\n    def cloneGraph(self, node):\n        return node", [[[[2], [1]]]]),
        (
            "copy-list-with-random-pointer",
            "class Solution:\n    def copyRandomList(self, head):\n        return head",
            [[[[1, 0]]]],
        ),
        (
            "serialize-and-deserialize-binary-tree",
            "class Codec:\n    keep = None\n    def serialize(self, root):\n        Codec.keep = root\n        return ''\n"
            "    def deserialize(self, data):\n        return Codec.keep",
            [[[1, 2, 3]]],
        ),
    ],
)
def test_returning_the_original_nodes_is_wrong(slug: str, code: str, tests: list[Any]) -> None:
    (result,) = _run(slug, code, tests)
    assert result["ok"] is False
    assert "original input nodes" in result["output"]


def test_codec_encode_must_return_a_string() -> None:
    code = "class Codec:\n    def encode(self, strs):\n        return strs\n    def decode(self, s):\n        return s"
    (result,) = _run("encode-and-decode-strings", code, [[["a", "b"]]])
    assert result["error_type"] == "runtime"
    assert "encode must return a str" in result["error"]


WORDS = [["ab", "ac", "bc"]]  # a < b, b < c; nothing else is known


@pytest.mark.parametrize(("out", "ok"), [("abc", True), ("acb", False), ("ab", False), ("abcc", False), ("", False)])
def test_alien_order_accepts_any_consistent_order(out: str, ok: bool) -> None:
    assert harness.check("alien_order", out, "abc", WORDS) is ok


def test_alien_order_requires_empty_string_when_impossible() -> None:
    assert harness.check("alien_order", "", "", [["b", "a", "b"]]) is True
    assert harness.check("alien_order", "ab", "", [["b", "a", "b"]]) is False
