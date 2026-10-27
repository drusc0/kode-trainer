from __future__ import annotations

import random
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Problem:
    slug: str
    title: str
    difficulty: str  # Easy | Medium | Hard
    pattern: str  # slug of a pattern guide page
    topics: list[str]
    companies: list[str]  # google | meta
    statement: str  # markdown
    entry: str  # method name (function) or class name (design)
    params: list[tuple[str, str]]  # (name, python type); "TreeNode@0" = node of arg 0 by value
    returns: str
    examples: list[dict[str, Any]]  # {"args": [...], "note": "..."}
    constraints: list[str]
    hints: list[str]
    reference: str  # trusted Python solution, run in the sandbox to compute expected outputs
    gen: Callable[[random.Random], list[Any]]
    compare: str = "exact"
    kind: str = "function"  # function | design
    time_limit_ms: int = 2000
    starter: str | None = None  # required for design problems
    seed_version: int = 1  # bump to regenerate this problem's hidden tests

    def display_type(self, t: str) -> str:
        return "TreeNode" if t.startswith("TreeNode@") else t

    def starter_code(self) -> str:
        if self.starter:
            return self.starter.strip("\n") + "\n"
        sig = ", ".join(f"{n}: {self.display_type(t)}" for n, t in self.params)
        pre = ""
        types = " ".join(t for _, t in self.params) + " " + self.returns
        if "ListNode" in types:
            pre += (
                "# Definition for singly-linked list.\n# class ListNode:\n#     def __init__(self, val=0, next=None):\n"
                "#         self.val = val\n#         self.next = next\n"
            )
        if "TreeNode" in types:
            pre += (
                "# Definition for a binary tree node.\n# class TreeNode:\n#     def __init__(self, val=0, left=None, right=None):\n"
                "#         self.val = val\n#         self.left = left\n#         self.right = right\n"
            )
        return f"{pre}class Solution:\n    def {self.entry}(self, {sig}) -> {self.returns}:\n        \n"

    def param_types(self) -> list[str]:
        return [t for _, t in self.params]


# ---------------------------------------------------------------- generator helpers
def ints(r: random.Random, n: int, lo: int, hi: int) -> list[int]:
    return [r.randint(lo, hi) for _ in range(n)]


def distinct(r: random.Random, n: int, lo: int, hi: int) -> list[int]:
    return r.sample(range(lo, hi + 1), n)


def word(r: random.Random, n: int, alpha: str) -> str:
    return "".join(r.choice(alpha) for _ in range(n))


def random_tree(r: random.Random, values: list[int]) -> list[int | None]:
    """Random binary tree shape filled with `values` in insertion order, as a LeetCode level-order list."""
    if not values:
        return []
    nodes: list[dict[str, Any]] = [{"v": values[0], "l": None, "r": None}]
    for v in values[1:]:
        while True:
            parent = r.choice(nodes)
            side = r.choice("lr")
            if parent[side] is None:
                child = {"v": v, "l": None, "r": None}
                parent[side] = child
                nodes.append(child)
                break
    return level_order(nodes[0])


def random_bst(r: random.Random, n: int, lo: int, hi: int) -> list[int | None]:
    """Random shape, values assigned in-order so it is a valid BST."""
    vals = sorted(r.sample(range(lo, hi + 1), n))
    shape = {"n": 0}

    def build(k: int) -> dict[str, Any] | None:
        if k == 0:
            return None
        left = r.randint(0, k - 1)
        node: dict[str, Any] = {"l": build(left)}
        node["v"] = vals[shape["n"]]
        shape["n"] += 1
        node["r"] = build(k - 1 - left)
        return node

    return level_order(build(n)) if n else []


def level_order(root: dict[str, Any] | None) -> list[int | None]:
    if root is None:
        return []
    out: list[int | None] = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node["v"])
        q.append(node["l"])
        q.append(node["r"])
    while out and out[-1] is None:
        out.pop()
    return out


def ops_case(
    r: random.Random, cls: str, ctor_args: list[Any], n: int, make: Callable[[], tuple[str, list[Any]]]
) -> list[Any]:
    ops, args = [cls], [ctor_args]
    for _ in range(n):
        op, a = make()
        ops.append(op)
        args.append(a)
    return [{"ops": ops, "args": args}]


def course_case(r: random.Random, n: int, cyclic: bool) -> list[Any]:
    order = list(range(n))
    r.shuffle(order)
    pos = {c: i for i, c in enumerate(order)}
    pairs: set[tuple[int, int]] = set()
    for _ in range(min(5000, n * 2)):
        a, b = r.sample(range(n), 2)
        if pos[a] < pos[b]:
            a, b = b, a
        pairs.add((a, b))  # b before a: consistent with order, so acyclic
    if cyclic and pairs:
        a, b = next(iter(pairs))
        pairs.add((b, a))
    return [n, [list(p) for p in pairs]]
