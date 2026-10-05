import importlib.util
from pathlib import Path
from typing import Any

import pytest

_spec = importlib.util.spec_from_file_location("harness", Path(__file__).resolve().parents[2] / "runner" / "harness.py")
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
