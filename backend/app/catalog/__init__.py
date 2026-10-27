"""Problem catalog. Problems are code (trusted); hidden tests are generated deterministically and
their expected outputs are computed by running the reference solution in the sandbox at seed time."""

import hashlib
import inspect
import json

from .base import Problem
from .problems_arrays import PROBLEMS as _A
from .problems_dp import PROBLEMS as _DP
from .problems_graphs import PROBLEMS as _GRAPHS
from .problems_hashing import PROBLEMS as _HASHING
from .problems_heap_design import PROBLEMS as _HEAP_DESIGN
from .problems_lists_trees import PROBLEMS as _LISTS_TREES
from .problems_math_bits import PROBLEMS as _MATH_BITS
from .problems_stack_search import PROBLEMS as _STACK_SEARCH
from .problems_structures import PROBLEMS as _B

PATTERNS = [
    "arrays-hashing",
    "two-pointers",
    "sliding-window",
    "prefix-sum",
    "stack",
    "binary-search",
    "linked-list",
    "trees",
    "heap",
    "graphs",
    "backtracking",
    "dynamic-programming",
    "intervals-greedy",
    "design",
    "trie",
    "math-geometry",
    "bit-manipulation",
]
__all__ = ["BY_SLUG", "PATTERNS", "PROBLEMS", "Problem", "problem_fingerprint"]

_DIFF = {"Easy": 0, "Medium": 1, "Hard": 2}

PROBLEMS: list[Problem] = sorted(
    _A + _B + _HASHING + _STACK_SEARCH + _LISTS_TREES + _GRAPHS + _HEAP_DESIGN + _DP + _MATH_BITS,
    key=lambda p: (PATTERNS.index(p.pattern), _DIFF[p.difficulty], p.title),
)
BY_SLUG: dict[str, Problem] = {p.slug: p for p in PROBLEMS}

assert len(BY_SLUG) == len(PROBLEMS), "duplicate problem slug"
for _p in PROBLEMS:
    assert _p.pattern in PATTERNS, f"{_p.slug}: unknown pattern {_p.pattern}"
    assert _p.kind == "function" or _p.starter, f"{_p.slug}: design problems need starter code"


def problem_fingerprint(p: Problem) -> str:
    """Changes whenever the reference, generator, examples, limits or compare mode change -> triggers reseed."""
    blob = json.dumps(
        {
            "ref": p.reference,
            "gen": inspect.getsource(p.gen) if callable(p.gen) else "",
            "ex": p.examples,
            "cmp": p.compare,
            "kind": p.kind,
            "params": p.params,
            "ret": p.returns,
            "tl": p.time_limit_ms,
            "v": p.seed_version,
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(blob.encode()).hexdigest()[:16]
