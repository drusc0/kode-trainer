"""
KodeTrain judge harness.

Runs INSIDE the sandbox as an unprivileged, resource-limited process:
  1. reads one job (JSON) from stdin
  2. locks itself down with seccomp (no sockets, no exec, no ptrace, ...)
  3. executes the untrusted solution and each test case with a per-test time limit
  4. streams one JSON line per test on a private file descriptor

The harness never trusts user output: user prints are captured per test and truncated.
A determined user can still tamper with their *own* results (same process), which only
affects their own practice score; they cannot reach the network, other jobs, or the host.
"""

import io
import json
import math
import os
import signal
import sys
import time
import traceback
from collections import deque
from itertools import pairwise
from types import FrameType
from typing import Any, NoReturn, TextIO, cast

MAX_STDOUT = 16_000  # chars of print() output kept per test
MAX_OUTPUT_REPR = 2_000_000  # chars of serialized return value kept


# ---------------------------------------------------------------- lockdown
DENY_SYSCALLS = [
    "socket",
    "socketpair",
    "connect",
    "bind",
    "listen",
    "accept",
    "accept4",
    "sendto",
    "sendmsg",
    "sendmmsg",
    "recvfrom",
    "recvmsg",
    "recvmmsg",
    "execve",
    "execveat",
    "ptrace",
    "process_vm_readv",
    "process_vm_writev",
    "mount",
    "umount2",
    "pivot_root",
    "chroot",
    "unshare",
    "setns",
    "keyctl",
    "add_key",
    "request_key",
    "bpf",
    "perf_event_open",
    "userfaultfd",
    "io_uring_setup",
    "io_uring_enter",
    "io_uring_register",
    "personality",
    "open_by_handle_at",
    "name_to_handle_at",
    "kexec_load",
    "reboot",
    "swapon",
    "swapoff",
    "init_module",
    "finit_module",
    "delete_module",
    "acct",
    "quotactl",
    "setrlimit",
    "prlimit64",
]


def lockdown(required: bool) -> None:
    """Install a seccomp filter via libseccomp (ctypes, no extra Python packages).
    Denied syscalls fail with EPERM, so user code sees a normal PermissionError."""
    import ctypes
    import ctypes.util
    import errno

    path = ctypes.util.find_library("seccomp") or "libseccomp.so.2"
    try:
        lib = ctypes.CDLL(path, use_errno=True)
    except OSError:
        if required:
            raise SystemExit("libseccomp not available but required") from None
        return
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_release.argtypes = [ctypes.c_void_p]

    SCMP_ACT_ALLOW = 0x7FFF0000
    SCMP_ACT_ERRNO = 0x00050000 | (errno.EPERM & 0xFFFF)
    ctx = lib.seccomp_init(SCMP_ACT_ALLOW)
    if not ctx:
        raise SystemExit("seccomp_init failed")
    for name in DENY_SYSCALLS:
        nr = lib.seccomp_syscall_resolve_name(name.encode())
        if nr < 0:
            continue  # not on this architecture
        if lib.seccomp_rule_add(ctx, SCMP_ACT_ERRNO, nr, 0) != 0:
            raise SystemExit(f"seccomp rule for {name} failed")
    rc = lib.seccomp_load(ctx)  # also sets no_new_privs
    lib.seccomp_release(ctx)
    if rc != 0:
        raise SystemExit(f"seccomp_load failed ({rc})")


# ---------------------------------------------------------------- data structures
class ListNode:
    def __init__(self, val: Any = 0, next: "ListNode | None" = None) -> None:
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.val})"


class TreeNode:
    def __init__(self, val: Any = 0, left: "TreeNode | None" = None, right: "TreeNode | None" = None) -> None:
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"TreeNode({self.val})"


class GraphNode:
    """Clone Graph's `Node`."""

    def __init__(self, val: Any = 0, neighbors: "list[GraphNode] | None" = None) -> None:
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

    def __repr__(self) -> str:
        return f"Node({self.val})"


class RandomNode:
    """Copy List with Random Pointer's `Node`."""

    def __init__(self, x: Any, next: "RandomNode | None" = None, random: "RandomNode | None" = None) -> None:
        self.val = x
        self.next = next
        self.random = random

    def __repr__(self) -> str:
        return f"Node({self.val})"


def build_list(vals: list[Any] | None) -> ListNode | None:
    head = cur = ListNode()
    for v in vals or []:
        cur.next = ListNode(v)
        cur = cur.next
    return head.next


def list_to_array(node: ListNode | None, limit: int = 200_000) -> list[Any]:
    out: list[Any] = []
    while node is not None:
        if len(out) >= limit:
            raise ValueError("returned linked list is too long (cycle?)")
        out.append(node.val)
        node = node.next
    return out


def build_tree(vals: list[Any] | None) -> TreeNode | None:
    if not vals or vals[0] is None:
        return None
    root = TreeNode(vals[0])
    q, i = deque([root]), 1
    while q and i < len(vals):
        node = q.popleft()
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            q.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            q.append(node.right)
        i += 1
    return root


def tree_to_array(root: TreeNode | None, limit: int = 200_000) -> list[Any]:
    if root is None:
        return []
    out: list[Any] = []
    q: deque[TreeNode | None] = deque([root])
    seen = 0
    while q:
        node = q.popleft()
        seen += 1
        if seen > limit:
            raise ValueError("returned tree is too large (cycle?)")
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        q.append(node.left)
        q.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def find_node(root: TreeNode | None, val: Any) -> TreeNode | None:
    stack = [root]
    while stack:
        n = stack.pop()
        if n is None:
            continue
        if n.val == val:
            return n
        stack.append(n.left)
        stack.append(n.right)
    return None


def build_graph(adj: list[list[int]]) -> GraphNode | None:
    """LeetCode adjacency list: node i + 1 has neighbours adj[i]."""
    nodes = [GraphNode(i + 1) for i in range(len(adj))]
    for node, nbrs in zip(nodes, adj, strict=True):
        node.neighbors = [nodes[j - 1] for j in nbrs]
    return nodes[0] if nodes else None


def graph_to_adj(node: GraphNode | None, limit: int = 200_000) -> list[list[Any]]:
    seen: dict[int, GraphNode] = {}
    stack = [node] if node is not None else []
    while stack:
        n = stack.pop()
        if id(n) in seen:
            continue
        if len(seen) >= limit:
            raise ValueError("returned graph is too large")
        seen[id(n)] = n
        stack.extend(n.neighbors)
    return [[m.val for m in n.neighbors] for n in sorted(seen.values(), key=lambda n: n.val)]


def build_random_list(pairs: list[list[Any]]) -> RandomNode | None:
    """[[val, random_index or None], ...] -> linked nodes."""
    nodes = [RandomNode(v) for v, _ in pairs]
    for i, (node, (_, j)) in enumerate(zip(nodes, pairs, strict=True)):
        node.next = nodes[i + 1] if i + 1 < len(nodes) else None
        node.random = nodes[j] if j is not None else None
    return nodes[0] if nodes else None


def random_list_to_pairs(head: RandomNode | None, limit: int = 200_000) -> list[list[Any]]:
    nodes: list[RandomNode] = []
    while head is not None:
        if len(nodes) >= limit:
            raise ValueError("returned linked list is too long (cycle?)")
        nodes.append(head)
        head = head.next
    index = {id(n): i for i, n in enumerate(nodes)}
    return [[n.val, None if n.random is None else index.get(id(n.random), "outside the list")] for n in nodes]


def index_in_list(node: Any, head: ListNode | None, limit: int = 200_000) -> Any:
    """Position of `node` in the (possibly cyclic) list `head`; -1 for None."""
    if node is None:
        return -1
    seen: set[int] = set()
    i = 0
    while head is not None and id(head) not in seen and i < limit:
        if head is node:
            return i
        seen.add(id(head))
        head, i = head.next, i + 1
    return "a node that isn't in the input list"


LINKS = ("left", "right", "next", "random", "neighbors")


def node_ids(*roots: Any, limit: int = 200_000) -> set[int]:
    """ids of every node reachable from the roots through tree, list or graph links."""
    seen: set[int] = set()
    stack = list(roots)
    while stack and len(seen) < limit:
        n = stack.pop()
        if n is None or id(n) in seen or not any(hasattr(n, a) for a in LINKS):
            continue
        seen.add(id(n))
        for a in LINKS:
            link = getattr(n, a, None)
            stack.extend(link if isinstance(link, list) else [link])
    return seen


def base_type(t: str) -> str:
    t = t.replace(" ", "")
    if t.startswith("Optional[") and t.endswith("]"):
        t = t[9:-1]
    return t


def convert_args(raw_args: list[Any], param_types: list[str]) -> list[Any]:
    """JSON args -> Python objects the solution expects."""
    out: list[Any] = []
    for raw, t in zip(raw_args, param_types, strict=False):
        bt = base_type(t)
        if bt == "ListNode":
            out.append(build_list(raw))
        elif bt == "TreeNode":
            out.append(build_tree(raw))
        elif bt in ("List[ListNode]", "List[Optional[ListNode]]"):
            out.append([build_list(x) for x in raw])
        elif bt.startswith("TreeNode@"):  # a reference to a node inside another tree argument
            ref_index = int(bt.split("@")[1])
            out.append(find_node(out[ref_index], raw))
        elif bt.startswith("CyclePos@"):  # links that list's tail to node `raw`; not passed to the solution
            nodes, cur = [], out[int(bt.split("@")[1])]
            while cur is not None:
                nodes.append(cur)
                cur = cur.next
            if raw >= 0:
                nodes[-1].next = nodes[raw]
        elif bt == "GraphNode":
            out.append(build_graph(raw))
        elif bt == "RandomList":
            out.append(build_random_list(raw))
        else:
            out.append(raw)
    return out


def normalize(value: Any, return_type: str | None, args: list[Any]) -> Any:
    """Python return value -> JSON-able value."""
    bt = base_type(return_type or "")
    if bt.startswith("ListNode@"):
        return index_in_list(value, args[int(bt.split("@")[1])])
    if bt == "GraphNode":
        return graph_to_adj(value)
    if bt == "RandomList":
        return random_list_to_pairs(value)
    if bt == "ListNode":
        return list_to_array(value) if value is not None else []
    if bt == "TreeNode":
        return tree_to_array(value)
    return to_jsonable(value)


def to_jsonable(v: Any, depth: int = 0) -> Any:
    if depth > 200:
        return repr(v)
    if v is None or isinstance(v, (bool, int, str)):
        return v
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return repr(v)
        return v
    if isinstance(v, (list, tuple, deque)):
        return [to_jsonable(x, depth + 1) for x in v]
    if isinstance(v, (set, frozenset)):
        items = [to_jsonable(x, depth + 1) for x in v]
        try:
            return sorted(items)
        except TypeError:
            return items
    if isinstance(v, dict):
        return {str(k): to_jsonable(x, depth + 1) for k, x in v.items()}
    if isinstance(v, ListNode):
        return list_to_array(v)
    if isinstance(v, TreeNode):
        return tree_to_array(v)
    return repr(v)


# ---------------------------------------------------------------- comparison
def strict_equal(a: Any, b: Any) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(strict_equal(x, y) for x, y in zip(a, b, strict=True))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(strict_equal(a[k], b[k]) for k in a)
    return type(a) is type(b) and a == b


def _sort_key(x: Any) -> str:
    return json.dumps(x, sort_keys=True)


def _nested_sorted(groups: list[list[Any]]) -> list[list[Any]]:
    return sorted((sorted(x, key=_sort_key) for x in groups), key=_sort_key)


def is_valid_parens(s: str) -> bool:
    bal = 0
    for c in s:
        if c == "(":
            bal += 1
        elif c == ")":
            bal -= 1
            if bal < 0:
                return False
    return bal == 0


def is_subsequence(small: str, big: str) -> bool:
    it = iter(big)
    return all(c in it for c in small)


def check(mode: str, out: Any, exp: Any, args: Any) -> bool:
    try:
        if exp is None and mode != "exact":
            return out is None  # custom input with no valid answer
        if mode == "exact":
            return strict_equal(out, exp)
        if mode == "sorted":
            return isinstance(out, list) and strict_equal(sorted(out, key=_sort_key), sorted(exp, key=_sort_key))
        if mode == "nested_sorted":
            if not isinstance(out, list) or not all(isinstance(x, list) for x in out):
                return False
            return strict_equal(_nested_sorted(out), _nested_sorted(exp))
        if mode == "float":
            return isinstance(out, (int, float)) and not isinstance(out, bool) and abs(out - exp) < 1e-5
        if mode == "two_sum":
            nums, target = args
            return (
                isinstance(out, list)
                and len(out) == 2
                and all(isinstance(i, int) and not isinstance(i, bool) and 0 <= i < len(nums) for i in out)
                and out[0] != out[1]
                and nums[out[0]] + nums[out[1]] == target
            )
        if mode == "peak":
            nums = args[0]
            if not isinstance(out, int) or isinstance(out, bool) or not 0 <= out < len(nums):
                return False
            left = nums[out - 1] if out > 0 else -math.inf
            right = nums[out + 1] if out + 1 < len(nums) else -math.inf
            return bool(nums[out] > left and nums[out] > right)
        if mode == "min_window":
            s, t = args
            if not isinstance(out, str) or len(out) != len(exp):
                return False
            if exp == "":
                return out == ""
            if out not in s:
                return False
            need: dict[str, int] = {}
            for c in t:
                need[c] = need.get(c, 0) + 1
            for c in out:
                if c in need:
                    need[c] -= 1
            return all(v <= 0 for v in need.values())
        if mode == "palindrome":
            s = args[0]
            return isinstance(out, str) and len(out) == len(exp) and out == out[::-1] and out in s
        if mode == "min_remove_parens":
            s = args[0]
            return isinstance(out, str) and len(out) == len(exp) and is_valid_parens(out) and is_subsequence(out, s)
        if mode == "alien_order":
            words = args[0]
            if exp == "":
                return isinstance(out, str) and not out
            if not isinstance(out, str) or len(set(out)) != len(out) or set(out) != set("".join(words)):
                return False
            rank = {c: i for i, c in enumerate(out)}
            for a, b in pairwise(words):
                diff = next(((x, y) for x, y in zip(a, b, strict=False) if x != y), None)
                if diff and rank[diff[0]] > rank[diff[1]]:
                    return False
            return True
        if mode == "topo_order":
            n, prereqs = args
            if exp == []:
                return isinstance(out, list) and not out
            if not isinstance(out, list) or not all(type(c) is int for c in out) or sorted(out) != list(range(n)):
                return False
            pos = {c: i for i, c in enumerate(out)}
            return all(pos[before] < pos[after] for after, before in prereqs)
        return strict_equal(out, exp)
    except Exception:
        return False


# ---------------------------------------------------------------- execution
class TimeLimitExceeded(BaseException):
    pass


def _on_alarm(signum: int, frame: FrameType | None) -> NoReturn:
    raise TimeLimitExceeded()


class CappedIO(io.TextIOBase):
    def __init__(self, cap: int) -> None:
        self.cap = cap
        self.parts: list[str] = []
        self.size = 0
        self.truncated = False

    def write(self, s: Any) -> int:
        s = str(s)
        room = self.cap - self.size
        if room > 0:
            self.parts.append(s[:room])
            self.size += min(len(s), room)
        if len(s) > room:
            self.truncated = True
        return len(s)

    def getvalue(self) -> str:
        return "".join(self.parts) + ("\n… output truncated" if self.truncated else "")


def user_traceback(exc: BaseException) -> str:
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename == "<solution>"]
    lines = [f"Line {f.lineno} in {f.name}" + (f": {f.line}" if f.line else "") for f in frames[-3:]]
    head = f"{type(exc).__name__}: {exc}"
    return "\n".join([head, *lines])


PRELUDE = """
from typing import *
import collections, heapq, math, bisect, itertools, functools, string, re, random, operator
from collections import *
from heapq import *
from bisect import *
from itertools import *
from functools import *
from math import inf
"""


def main() -> None:
    real_stdout, real_stderr = sys.stdout, sys.stderr
    job = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    out_fd = os.dup(1)
    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, 0)
    os.dup2(devnull, 1)
    os.dup2(devnull, 2)
    chan = os.fdopen(out_fd, "w", buffering=1, encoding="utf-8")

    def emit(obj: dict[str, Any]) -> None:
        chan.write(json.dumps(obj, default=repr) + "\n")
        chan.flush()

    lockdown(job.get("_sandbox", {}).get("seccomp_required", False))
    sys.setrecursionlimit(20_000)
    signal.signal(signal.SIGALRM, _on_alarm)

    code = job["code"]
    kind = job.get("kind", "function")
    entry = job["entry"]
    param_types = job.get("param_types", [])
    return_type = job.get("return_type", "")
    tests = job["tests"]
    expected = job.get("expected")
    mode = job.get("compare", "exact")
    tl = max(0.05, job.get("time_limit_ms", 2000) / 1000)

    codec = job.get("codec")
    node_cls = RandomNode if "RandomList" in param_types else GraphNode
    ns: dict[str, Any] = {"__name__": "__main__", "ListNode": ListNode, "TreeNode": TreeNode, "Node": node_cls}
    exec(compile(PRELUDE, "<prelude>", "exec"), ns)

    # compile + load
    try:
        compiled = compile(code, "<solution>", "exec")
    except SyntaxError as e:
        emit(
            {
                "type": "compile_error",
                "error": f"Line {e.lineno}: {e.msg}" + (f"\n    {e.text.rstrip()}" if e.text else ""),
            }
        )
        return
    load_out = CappedIO(MAX_STDOUT)
    sys.stdout = sys.stderr = cast(TextIO, load_out)
    try:
        signal.setitimer(signal.ITIMER_REAL, tl)
        exec(compiled, ns)
        signal.setitimer(signal.ITIMER_REAL, 0)
    except TimeLimitExceeded:
        emit(
            {
                "type": "compile_error",
                "error": "Time limit exceeded while loading your code (check for top-level loops).",
            }
        )
        return
    except BaseException as e:  # anything the user raises at import time
        signal.setitimer(signal.ITIMER_REAL, 0)
        emit({"type": "compile_error", "error": user_traceback(e)})
        return
    finally:
        sys.stdout, sys.stderr = real_stdout, real_stderr

    if kind == "design" or codec:
        target: Any = ns.get(entry)
        if not isinstance(target, type):
            emit(
                {
                    "type": "compile_error",
                    "error": f"Couldn't find class {entry}. Keep the class name from the starter code.",
                }
            )
            return
    else:
        sol_cls: Any = ns.get("Solution")
        if not isinstance(sol_cls, type) or not callable(getattr(sol_cls, entry, None)):
            emit(
                {
                    "type": "compile_error",
                    "error": f"Couldn't find Solution.{entry}. Keep the class and method names from the starter code.",
                }
            )
            return

    emit({"type": "ready"})

    for i, raw in enumerate(tests):
        buf = CappedIO(MAX_STDOUT)
        sys.stdout = sys.stderr = cast(TextIO, buf)
        result: dict[str, Any] = {"type": "result", "index": i}
        t0 = time.perf_counter()
        try:
            signal.setitimer(signal.ITIMER_REAL, tl)
            if kind == "design":
                spec = raw[0] if isinstance(raw, list) else raw
                ops, op_args = spec["ops"], spec["args"]
                obj = target(*op_args[0])
                value: Any = [None]
                for op, a in zip(ops[1:], op_args[1:], strict=False):
                    value.append(getattr(obj, op)(*a))
                args = []
            elif codec:  # encode with one instance, decode with a fresh one
                args = convert_args(raw, param_types)
                data = getattr(target(), codec[0])(*args)
                if not isinstance(data, str):
                    raise TypeError(f"{codec[0]} must return a str, not {type(data).__name__}")
                value = getattr(target(), codec[1])(data)
            else:
                args = convert_args(raw, param_types)
                value = getattr(sol_cls(), entry)(*args)
            signal.setitimer(signal.ITIMER_REAL, 0)
            result["ms"] = round((time.perf_counter() - t0) * 1000, 3)
            needs_copy = codec or base_type(return_type) in ("GraphNode", "RandomList")
            if needs_copy and node_ids(value) & node_ids(*args):
                out = "returned original input nodes instead of building new ones"
            else:
                out = normalize(value, return_type, args)
            text = json.dumps(out)
            if len(text) > MAX_OUTPUT_REPR:
                out = text[:MAX_OUTPUT_REPR] + "…"
                result["truncated"] = True
            result["output"] = out
            if expected is not None:
                result["ok"] = check(mode, out, expected[i], raw)
        except TimeLimitExceeded:
            result.update(ok=False, error_type="timeout", error=f"Time limit exceeded ({int(tl * 1000)} ms per test)")
        except MemoryError:
            signal.setitimer(signal.ITIMER_REAL, 0)
            result.update(ok=False, error_type="memory", error="Memory limit exceeded")
        except RecursionError as e:
            signal.setitimer(signal.ITIMER_REAL, 0)
            result.update(ok=False, error_type="runtime", error=user_traceback(e))
        except BaseException as e:
            signal.setitimer(signal.ITIMER_REAL, 0)
            result.update(ok=False, error_type="runtime", error=user_traceback(e))
        finally:
            sys.stdout, sys.stderr = real_stdout, real_stderr
        result["stdout"] = buf.getvalue()
        emit(result)
        if result.get("error_type") in ("timeout", "memory"):
            break  # process state is unreliable after these

    emit({"type": "done"})


if __name__ == "__main__":
    main()
