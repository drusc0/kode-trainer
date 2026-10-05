import random
from typing import Any

from .base import Problem, distinct, ints, ops_case, word

G, M = "google", "meta"

PROBLEMS = [
    # ---------------------------------------------------------------- stack
    Problem(
        slug="min-stack",
        title="Min Stack",
        difficulty="Medium",
        pattern="stack",
        kind="design",
        topics=["Stack", "Design"],
        companies=[G, M],
        statement="Design a stack that also returns its minimum element, with every operation in O(1):\n\n- `push(val)`, `pop()`, `top()` behave like a normal stack.\n- `getMin()` returns the smallest value currently in the stack.\n\n`pop`, `top` and `getMin` are only called on a non-empty stack.",
        entry="MinStack",
        params=[("operations", "List[str]"), ("arguments", "List[List[int]]")],
        returns="List",
        starter="""
class MinStack:

    def __init__(self):


    def push(self, val: int) -> None:


    def pop(self) -> None:


    def top(self) -> int:


    def getMin(self) -> int:

""",
        examples=[
            {
                "args": [
                    {
                        "ops": ["MinStack", "push", "push", "push", "getMin", "pop", "top", "getMin"],
                        "args": [[], [-2], [0], [-3], [], [], [], []],
                    }
                ]
            }
        ],
        constraints=["−2³¹ ≤ val ≤ 2³¹ − 1", "At most 3 × 10⁴ calls"],
        hints=["Push pairs (value, min so far). The minimum is always stored on top."],
        reference="""
class MinStack:
    def __init__(self):
        self.st = []
    def push(self, val):
        self.st.append(val)
    def pop(self):
        self.st.pop()
    def top(self):
        return self.st[-1]
    def getMin(self):
        return min(self.st)
""",
        gen=lambda r: (
            [_stack_ops(r, "MinStack", r.randint(1, 30), ["top", "getMin", "pop"]) for _ in range(14)]
            + [_stack_ops(r, "MinStack", 3000, ["top", "getMin", "pop"])]
        ),
    ),
    Problem(
        slug="implement-queue-using-stacks",
        title="Implement Queue using Stacks",
        difficulty="Easy",
        pattern="stack",
        kind="design",
        topics=["Stack", "Queue", "Design"],
        companies=[G, M],
        statement="Implement a first-in-first-out queue using only two stacks (Python lists used with `append`, `pop()` and `[-1]`):\n\n- `push(x)` adds to the back.\n- `pop()` removes and returns the front.\n- `peek()` returns the front.\n- `empty()` returns whether the queue is empty.\n\n`pop` and `peek` are only called on a non-empty queue. Aim for amortised O(1) per operation.",
        entry="MyQueue",
        params=[("operations", "List[str]"), ("arguments", "List[List[int]]")],
        returns="List",
        starter="""
class MyQueue:

    def __init__(self):


    def push(self, x: int) -> None:


    def pop(self) -> int:


    def peek(self) -> int:


    def empty(self) -> bool:

""",
        examples=[
            {"args": [{"ops": ["MyQueue", "push", "push", "peek", "pop", "empty"], "args": [[], [1], [2], [], [], []]}]}
        ],
        constraints=["1 ≤ x ≤ 9", "At most 100 calls"],
        hints=["Push onto an `in` stack. To pop or peek, refill an `out` stack from `in` only when `out` is empty."],
        reference="""
class MyQueue:
    def __init__(self):
        self.q = deque()
    def push(self, x):
        self.q.append(x)
    def pop(self):
        return self.q.popleft()
    def peek(self):
        return self.q[0]
    def empty(self):
        return not self.q
""",
        gen=lambda r: [_stack_ops(r, "MyQueue", r.randint(1, 40), ["peek", "pop", "empty"]) for _ in range(15)],
    ),
    Problem(
        slug="online-stock-span",
        title="Online Stock Span",
        difficulty="Medium",
        pattern="stack",
        kind="design",
        topics=["Stack", "Design", "Monotonic Stack"],
        companies=[G, M],
        statement="Design `StockSpanner`. `next(price)` receives today's price and returns its span: the number of consecutive days, ending today and going backwards, on which the price was less than or equal to today's price.\n\nFor prices `[7, 2, 1, 2]` the spans are `[1, 1, 1, 3]`.",
        entry="StockSpanner",
        params=[("operations", "List[str]"), ("arguments", "List[List[int]]")],
        returns="List",
        starter="""
class StockSpanner:

    def __init__(self):


    def next(self, price: int) -> int:

""",
        examples=[
            {
                "args": [
                    {
                        "ops": ["StockSpanner", "next", "next", "next", "next", "next", "next", "next"],
                        "args": [[], [100], [80], [60], [70], [60], [75], [85]],
                    }
                ]
            }
        ],
        constraints=["1 ≤ price ≤ 10⁵", "At most 10⁴ calls"],
        hints=["Keep a stack of (price, span) with decreasing prices. Pop and absorb every span ≤ today's price."],
        reference="""
class StockSpanner:
    def __init__(self):
        self.st = []
    def next(self, price):
        span = 1
        while self.st and self.st[-1][0] <= price:
            span += self.st.pop()[1]
        self.st.append((price, span))
        return span
""",
        gen=lambda r: (
            [ops_case(r, "StockSpanner", [], r.randint(1, 30), lambda: ("next", [r.randint(1, 20)])) for _ in range(14)]
            + [ops_case(r, "StockSpanner", [], 10_000, lambda: ("next", [r.randint(1, 10**5)]))]
        ),
    ),
    Problem(
        slug="evaluate-reverse-polish-notation",
        title="Evaluate Reverse Polish Notation",
        difficulty="Medium",
        pattern="stack",
        topics=["Array", "Math", "Stack"],
        companies=[G, M],
        statement="Evaluate an arithmetic expression in Reverse Polish Notation, where every operator follows its two operands (`2 1 + 3 *` means `(2 + 1) * 3`). `tokens` holds integers and the operators `+ - * /`.\n\nDivision truncates toward zero. The expression is valid, there is no division by zero, and all results fit in 32 bits.",
        entry="evalRPN",
        params=[("tokens", "List[str]")],
        returns="int",
        examples=[
            {"args": [["2", "1", "+", "3", "*"]]},
            {"args": [["4", "13", "5", "/", "+"]]},
            {"args": [["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]]},
        ],
        constraints=["1 ≤ len(tokens) ≤ 10⁴"],
        hints=[
            "Push numbers. On an operator, pop b then a and push a op b.",
            "`int(a / b)` truncates toward zero; `a // b` floors, which differs for negatives.",
        ],
        reference="""
class Solution:
    def evalRPN(self, tokens):
        st = []
        for t in tokens:
            if t in '+-*/':
                b = st.pop(); a = st.pop()
                if t == '+': st.append(a + b)
                elif t == '-': st.append(a - b)
                elif t == '*': st.append(a * b)
                else: st.append(abs(a) // abs(b) * (1 if (a >= 0) == (b > 0) else -1))
            else:
                st.append(int(t))
        return st[0]
""",
        gen=lambda r: [[["42"]], [["-7"]]] + [[_rpn(r, r.randint(2, 12))] for _ in range(20)] + [[_rpn(r, 4000)]],
    ),
    Problem(
        slug="next-greater-element-i",
        title="Next Greater Element I",
        difficulty="Easy",
        pattern="stack",
        topics=["Array", "Hash Table", "Stack", "Monotonic Stack"],
        companies=[G, M],
        statement="`nums1` is a subset of `nums2`, and all values are distinct. For each `x` in `nums1`, find `x` in `nums2` and return the first value to its right that is greater than `x`, or `-1` if there is none.",
        entry="nextGreaterElement",
        params=[("nums1", "List[int]"), ("nums2", "List[int]")],
        returns="List[int]",
        examples=[{"args": [[4, 1, 2], [1, 3, 4, 2]]}, {"args": [[2, 4], [1, 2, 3, 4]]}],
        constraints=["1 ≤ len(nums1) ≤ len(nums2) ≤ 1000", "All values distinct"],
        hints=["One monotonic-stack pass over nums2 records every value's next greater element in a dict."],
        reference="""
class Solution:
    def nextGreaterElement(self, nums1, nums2):
        nxt = {}; st = []
        for x in nums2:
            while st and st[-1] < x: nxt[st.pop()] = x
            st.append(x)
        return [nxt.get(x, -1) for x in nums1]
""",
        gen=lambda r: [
            (lambda b: [r.sample(b, r.randint(1, len(b))), b])(distinct(r, n, 0, 10_000))
            for n in [r.randint(1, 20) for _ in range(18)] + [1000]
        ],
    ),
    Problem(
        slug="simplify-path",
        title="Simplify Path",
        difficulty="Medium",
        pattern="stack",
        topics=["String", "Stack"],
        companies=[M, G],
        statement="Convert an absolute Unix-style `path` to its simplified canonical form:\n\n- `.` means the current directory and `..` the parent (the parent of `/` is `/`).\n- Repeated slashes count as one.\n- Any other name, including `...`, is a directory name.\n\nThe result starts with a single `/`, separates names with single slashes and has no trailing slash.",
        entry="simplifyPath",
        params=[("path", "str")],
        returns="str",
        examples=[
            {"args": ["/home/"]},
            {"args": ["/home//foo/"]},
            {"args": ["/home/user/Documents/../Pictures"]},
            {"args": ["/../"]},
            {"args": ["/.../a/../b/c/../d/./"]},
        ],
        constraints=["1 ≤ len(path) ≤ 3000", "path starts with '/'"],
        hints=["Split on '/'. Push names onto a stack, pop on '..', ignore '' and '.'."],
        reference="""
class Solution:
    def simplifyPath(self, path):
        st = []
        for part in path.split('/'):
            if part == '..':
                if st: st.pop()
            elif part and part != '.':
                st.append(part)
        return '/' + '/'.join(st)
""",
        gen=lambda r: (
            [["/"], ["//"], ["/a/./b/../../c/"], ["/a//b////c/d//././/.."], ["/..hidden"]]
            + [
                ["/" + "/".join(r.choice(["a", "bc", ".", "..", "...", "", "x.y"]) for _ in range(r.randint(1, 10)))]
                for _ in range(18)
            ]
            + [["/" + "/".join(r.choice(["a", ".", "..", ""]) for _ in range(1000))]]
        ),
    ),
    Problem(
        slug="decode-string",
        title="Decode String",
        difficulty="Medium",
        pattern="stack",
        topics=["String", "Stack", "Recursion"],
        companies=[G, M],
        statement="Decode a string encoded with the rule `k[encoded]`, meaning `encoded` repeated `k` times. Brackets can be nested. Digits only appear as repeat counts, and the input is always valid.\n\n`3[a2[c]]` → `accaccacc`.",
        entry="decodeString",
        params=[("s", "str")],
        returns="str",
        examples=[{"args": ["3[a]2[bc]"]}, {"args": ["3[a2[c]]"]}, {"args": ["2[abc]3[cd]ef"]}],
        constraints=["1 ≤ len(s) ≤ 30", "1 ≤ k ≤ 300", "Output length ≤ 10⁵"],
        hints=[
            "On `[` push (current string, k) and start fresh; on `]` pop and set current = previous + k × current.",
            "Counts can have several digits.",
        ],
        reference="""
class Solution:
    def decodeString(self, s):
        st = []; cur = ''; k = 0
        for c in s:
            if c.isdigit(): k = k * 10 + int(c)
            elif c == '[':
                st.append((cur, k)); cur = ''; k = 0
            elif c == ']':
                prev, n = st.pop(); cur = prev + cur * n
            else:
                cur += c
        return cur
""",
        gen=lambda r: [["abc"], ["10[a]"], ["2[2[2[b]]]"], ["100[leetcode]"]] + [[_encoded(r, 3)] for _ in range(20)],
    ),
    Problem(
        slug="asteroid-collision",
        title="Asteroid Collision",
        difficulty="Medium",
        pattern="stack",
        topics=["Array", "Stack", "Simulation"],
        companies=[G, M],
        statement="Asteroids move along a line at the same speed. The absolute value is the size; the sign is the direction (positive → right, negative → left). When two meet, the smaller explodes; equal sizes both explode. Asteroids moving the same way never meet.\n\nReturn the asteroids left after all collisions.",
        entry="asteroidCollision",
        params=[("asteroids", "List[int]")],
        returns="List[int]",
        examples=[{"args": [[5, 10, -5]]}, {"args": [[8, -8]]}, {"args": [[10, 2, -5]]}, {"args": [[-2, -1, 1, 2]]}],
        constraints=["2 ≤ len(asteroids) ≤ 10⁴", "−1000 ≤ asteroids[i] ≤ 1000", "asteroids[i] ≠ 0"],
        hints=[
            "Only a left-mover hitting right-movers on top of the stack collides. Keep popping smaller right-movers."
        ],
        reference="""
class Solution:
    def asteroidCollision(self, asteroids):
        st = []
        for a in asteroids:
            alive = True
            while alive and a < 0 and st and st[-1] > 0:
                if st[-1] < -a: st.pop()
                elif st[-1] == -a: st.pop(); alive = False
                else: alive = False
            if alive: st.append(a)
        return st
""",
        gen=lambda r: (
            [[[r.choice([-1, 1]) * r.randint(1, 6) for _ in range(r.randint(2, 20))]] for _ in range(18)]
            + [[[r.choice([-1, 1]) * r.randint(1, 1000) for _ in range(10_000)]]]
        ),
    ),
    Problem(
        slug="remove-all-adjacent-duplicates-in-string-ii",
        title="Remove All Adjacent Duplicates in String II",
        difficulty="Medium",
        pattern="stack",
        topics=["String", "Stack"],
        companies=[M, G],
        statement="Repeatedly remove `k` adjacent equal letters from `s` (the pieces on either side then join up) until no more removals are possible. Return the final string; it is unique.",
        entry="removeDuplicates",
        params=[("s", "str"), ("k", "int")],
        returns="str",
        examples=[{"args": ["abcd", 2]}, {"args": ["deeedbbcccbdaa", 3]}, {"args": ["pbbcggttciiippooaais", 2]}],
        constraints=["1 ≤ len(s) ≤ 10⁵", "2 ≤ k ≤ 10⁴"],
        hints=["Stack of [char, run length]. When a run reaches k, pop it."],
        reference="""
class Solution:
    def removeDuplicates(self, s, k):
        st = []
        for c in s:
            if st and st[-1][0] == c:
                st[-1][1] += 1
                if st[-1][1] == k: st.pop()
            else:
                st.append([c, 1])
        return ''.join(c * n for c, n in st)
""",
        gen=lambda r: (
            [[word(r, r.randint(1, 30), "ab"), r.randint(2, 3)] for _ in range(18)]
            + [[word(r, 100_000, "abc"), 2], ["a" * 99_999, 3]]
        ),
    ),
    Problem(
        slug="remove-k-digits",
        title="Remove K Digits",
        difficulty="Medium",
        pattern="stack",
        topics=["String", "Stack", "Greedy", "Monotonic Stack"],
        companies=[G, M],
        statement='`num` is a non-negative integer as a string. Remove exactly `k` digits so the remaining number is as small as possible, and return it without leading zeros (`"0"` if nothing is left).',
        entry="removeKdigits",
        params=[("num", "str"), ("k", "int")],
        returns="str",
        examples=[
            {"args": ["1432219", 3], "note": '"1219"'},
            {"args": ["10200", 1], "note": '"200"'},
            {"args": ["10", 2]},
        ],
        constraints=["1 ≤ k ≤ len(num) ≤ 10⁵", "num has no leading zeros except '0' itself"],
        hints=["Keep the digits increasing on a stack: while k > 0 and the top is bigger than the next digit, pop it."],
        reference="""
class Solution:
    def removeKdigits(self, num, k):
        st = []
        for c in num:
            while k and st and st[-1] > c:
                st.pop(); k -= 1
            st.append(c)
        if k: st = st[:-k]
        return ''.join(st).lstrip('0') or '0'
""",
        gen=lambda r: (
            [["9", 1], ["112", 1], ["100", 1]]
            + [(lambda n: [n, r.randint(1, len(n))])(str(r.randint(1, 10 ** r.randint(1, 12)))) for _ in range(18)]
            + [[str(r.randint(1, 9)) + word(r, 99_999, "0123456789"), 50_000]]
        ),
    ),
    Problem(
        slug="car-fleet",
        title="Car Fleet",
        difficulty="Medium",
        pattern="stack",
        topics=["Array", "Stack", "Sorting", "Monotonic Stack"],
        companies=[G],
        statement="`n` cars drive toward `target` on a one-lane road. Car `i` starts at `position[i]` with speed `speed[i]`. A car can't pass the one ahead; when it catches up it slows down and they move together as a fleet. A car that catches up exactly at `target` joins the fleet.\n\nReturn how many fleets arrive at the target.",
        entry="carFleet",
        params=[("target", "int"), ("position", "List[int]"), ("speed", "List[int]")],
        returns="int",
        examples=[
            {"args": [12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]]},
            {"args": [10, [3], [3]]},
            {"args": [100, [0, 2, 4], [4, 2, 1]]},
        ],
        constraints=["1 ≤ n ≤ 10⁵", "0 < target ≤ 10⁶", "Positions are distinct and < target", "1 ≤ speed[i] ≤ 10⁶"],
        hints=[
            "Sort by position, closest to target first. Compute each car's arrival time alone.",
            "A car whose time is ≤ the fleet ahead's time joins it; a slower one starts a new fleet.",
        ],
        reference="""
class Solution:
    def carFleet(self, target, position, speed):
        fleets = 0; ld, ls = -1, 1  # arrival time of the fleet ahead, as the fraction ld / ls
        for p, s in sorted(zip(position, speed), reverse=True):
            d = target - p
            if d * ls > ld * s:
                fleets += 1; ld, ls = d, s
        return fleets
""",
        gen=lambda r: [_fleet(r, r.randint(1, 15), 30) for _ in range(18)] + [_fleet(r, 100_000, 10**6)],
    ),
    Problem(
        slug="largest-rectangle-in-histogram",
        title="Largest Rectangle in Histogram",
        difficulty="Hard",
        pattern="stack",
        topics=["Array", "Stack", "Monotonic Stack"],
        companies=[G, M],
        statement="`heights[i]` is the height of a bar of width 1. Return the area of the largest rectangle that fits inside the histogram.",
        entry="largestRectangleArea",
        params=[("heights", "List[int]")],
        returns="int",
        examples=[{"args": [[2, 1, 5, 6, 2, 3]], "note": "The bars 5 and 6 give 5 × 2 = 10."}, {"args": [[2, 4]]}],
        constraints=["1 ≤ len(heights) ≤ 10⁵", "0 ≤ heights[i] ≤ 10⁴"],
        hints=[
            "For each bar, the widest rectangle of its height stretches to the nearest shorter bar on each side.",
            "A stack of increasing heights finds both: when a shorter bar arrives, pop and compute the popped bar's area.",
        ],
        reference="""
class Solution:
    def largestRectangleArea(self, heights):
        st = []; best = 0
        for i, h in enumerate(heights + [0]):
            start = i
            while st and st[-1][1] >= h:
                j, hh = st.pop()
                best = max(best, hh * (i - j)); start = j
            st.append((start, h))
        return best
""",
        gen=lambda r: (
            [[[0]], [[1]], [[2, 2, 2]], [[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]]]
            + [[ints(r, r.randint(1, 30), 0, 10)] for _ in range(16)]
            + [[ints(r, 100_000, 0, 10**4)], [list(range(1, 100_001))]]
        ),
    ),
    Problem(
        slug="basic-calculator",
        title="Basic Calculator",
        difficulty="Hard",
        pattern="stack",
        topics=["Math", "String", "Stack", "Recursion"],
        companies=[G, M],
        statement="Evaluate the expression string `s`, which contains non-negative integers, `+`, `-`, parentheses and spaces. `-` can also be unary (`-1`, `-(2 + 3)`), but `+` is never unary. Don't use `eval`.\n\nThe expression is valid and every intermediate result fits in 32 bits.",
        entry="calculate",
        params=[("s", "str")],
        returns="int",
        examples=[
            {"args": ["1 + 1"]},
            {"args": [" 2-1 + 2 "]},
            {"args": ["(1+(4+5+2)-3)+(6+8)"]},
            {"args": ["-(3-(2+1))"]},
        ],
        constraints=["1 ≤ len(s) ≤ 3 × 10⁵"],
        hints=[
            "Keep a running result and a sign. On `(`, push (result, sign) and start a new result; on `)`, pop and combine.",
        ],
        reference="""
class Solution:
    def calculate(self, s):
        st = []; res = 0; num = 0; sign = 1
        for c in s:
            if c.isdigit():
                num = num * 10 + int(c)
            elif c in '+-':
                res += sign * num; num = 0
                sign = 1 if c == '+' else -1
            elif c == '(':
                st.append((res, sign)); res = 0; sign = 1
            elif c == ')':
                res += sign * num; num = 0
                prev, psign = st.pop()
                res = prev + psign * res
        return res + sign * num
""",
        gen=lambda r: (
            [["0"], ["-5"], ["(7)"], ["- (3 + (4 + 5))"]]
            + [[_calc_expr(r, 3)] for _ in range(20)]
            + [[" + ".join(["(1-(2+3))"] * 20_000)]]
        ),
    ),
    Problem(
        slug="longest-valid-parentheses",
        title="Longest Valid Parentheses",
        difficulty="Hard",
        pattern="stack",
        topics=["String", "Stack", "Dynamic Programming"],
        companies=[G, M],
        statement="Given a string of `(` and `)`, return the length of the longest contiguous substring that is a valid (well-formed) parentheses string.",
        entry="longestValidParentheses",
        params=[("s", "str")],
        returns="int",
        examples=[{"args": ["(()"]}, {"args": [")()())"]}, {"args": [""]}],
        constraints=["0 ≤ len(s) ≤ 3 × 10⁴"],
        hints=[
            "Stack of indices, seeded with −1 as the base of the current valid run.",
            "On `)`: pop; if the stack is empty push i as the new base, otherwise the run length is i − stack[-1].",
        ],
        reference="""
class Solution:
    def longestValidParentheses(self, s):
        st = [-1]; best = 0
        for i, c in enumerate(s):
            if c == '(':
                st.append(i)
            else:
                st.pop()
                if not st: st.append(i)
                else: best = max(best, i - st[-1])
        return best
""",
        gen=lambda r: (
            [["()"], [")("], ["()(()"], ["(()())"]]
            + [[word(r, r.randint(0, 30), "()")] for _ in range(18)]
            + [[word(r, 30_000, "(()")]]
        ),
    ),
    # ---------------------------------------------------------------- binary search
    Problem(
        slug="binary-search",
        title="Binary Search",
        difficulty="Easy",
        pattern="binary-search",
        topics=["Array", "Binary Search"],
        companies=[G, M],
        statement="`nums` is sorted ascending with distinct values. Return the index of `target`, or `-1` if it's absent. You must run in O(log n).",
        entry="search",
        params=[("nums", "List[int]"), ("target", "int")],
        returns="int",
        examples=[{"args": [[-1, 0, 3, 5, 9, 12], 9]}, {"args": [[-1, 0, 3, 5, 9, 12], 2]}],
        constraints=["1 ≤ len(nums) ≤ 10⁴", "Values are distinct and sorted"],
        hints=["Keep [lo, hi]; compare nums[mid] with target and discard the half that can't contain it."],
        reference="""
class Solution:
    def search(self, nums, target):
        i = bisect_left(nums, target)
        return i if i < len(nums) and nums[i] == target else -1
""",
        gen=lambda r: [_sorted_target(r, r.randint(1, 30)) for _ in range(20)] + [_sorted_target(r, 10_000)],
    ),
    Problem(
        slug="search-insert-position",
        title="Search Insert Position",
        difficulty="Easy",
        pattern="binary-search",
        topics=["Array", "Binary Search"],
        companies=[G, M],
        statement="`nums` is sorted ascending with distinct values. Return the index of `target` if present, otherwise the index where it would be inserted to keep the order. O(log n).",
        entry="searchInsert",
        params=[("nums", "List[int]"), ("target", "int")],
        returns="int",
        examples=[{"args": [[1, 3, 5, 6], 5]}, {"args": [[1, 3, 5, 6], 2]}, {"args": [[1, 3, 5, 6], 7]}],
        constraints=["1 ≤ len(nums) ≤ 10⁴"],
        hints=["You want the first index whose value is ≥ target."],
        reference="""
class Solution:
    def searchInsert(self, nums, target):
        return bisect_left(nums, target)
""",
        gen=lambda r: [_sorted_target(r, r.randint(1, 30)) for _ in range(20)] + [_sorted_target(r, 10_000)],
    ),
    Problem(
        slug="sqrtx",
        title="Sqrt(x)",
        difficulty="Easy",
        pattern="binary-search",
        topics=["Math", "Binary Search"],
        companies=[M, G],
        statement="Return the square root of the non-negative integer `x`, rounded down. Don't use `**`, `math.sqrt` or `math.isqrt`.",
        entry="mySqrt",
        params=[("x", "int")],
        returns="int",
        examples=[{"args": [4]}, {"args": [8], "note": "√8 ≈ 2.83, rounded down to 2."}],
        constraints=["0 ≤ x ≤ 2³¹ − 1"],
        hints=["Binary search for the largest m with m * m ≤ x."],
        reference="""
class Solution:
    def mySqrt(self, x):
        return math.isqrt(x)
""",
        gen=lambda r: (
            [[x] for x in [0, 1, 2, 3, 2**31 - 1, 2147395599, 2147395600]]
            + [[r.randint(0, 2**31 - 1)] for _ in range(14)]
            + [[r.randint(0, 100) ** 2] for _ in range(4)]
        ),
    ),
    Problem(
        slug="search-a-2d-matrix",
        title="Search a 2D Matrix",
        difficulty="Medium",
        pattern="binary-search",
        topics=["Array", "Binary Search", "Matrix"],
        companies=[G, M],
        statement="Each row of `matrix` is sorted ascending, and each row's first value is greater than the previous row's last value. Return `True` if `target` is in the matrix, in O(log(m · n)).",
        entry="searchMatrix",
        params=[("matrix", "List[List[int]]"), ("target", "int")],
        returns="bool",
        examples=[
            {"args": [[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3]},
            {"args": [[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13]},
        ],
        constraints=["1 ≤ m, n ≤ 100"],
        hints=["It's one sorted array of m · n values. Index k maps to matrix[k // n][k % n]."],
        reference="""
class Solution:
    def searchMatrix(self, matrix, target):
        return any(target in row for row in matrix)
""",
        gen=lambda r: (
            [_flat_matrix(r, r.randint(1, 6), r.randint(1, 6)) for _ in range(20)] + [_flat_matrix(r, 100, 100)]
        ),
    ),
    Problem(
        slug="search-a-2d-matrix-ii",
        title="Search a 2D Matrix II",
        difficulty="Medium",
        pattern="binary-search",
        topics=["Array", "Binary Search", "Matrix", "Divide and Conquer"],
        companies=[G, M],
        statement="Every row of `matrix` is sorted ascending left to right, and every column is sorted ascending top to bottom. Return `True` if `target` is in the matrix.",
        entry="searchMatrix",
        params=[("matrix", "List[List[int]]"), ("target", "int")],
        returns="bool",
        examples=[
            {
                "args": [
                    [
                        [1, 4, 7, 11, 15],
                        [2, 5, 8, 12, 19],
                        [3, 6, 9, 16, 22],
                        [10, 13, 14, 17, 24],
                        [18, 21, 23, 26, 30],
                    ],
                    5,
                ]
            },
            {
                "args": [
                    [
                        [1, 4, 7, 11, 15],
                        [2, 5, 8, 12, 19],
                        [3, 6, 9, 16, 22],
                        [10, 13, 14, 17, 24],
                        [18, 21, 23, 26, 30],
                    ],
                    20,
                ]
            },
        ],
        constraints=["1 ≤ m, n ≤ 300"],
        hints=["Start at the top-right corner. Too big → move left; too small → move down. O(m + n)."],
        reference="""
class Solution:
    def searchMatrix(self, matrix, target):
        return any(target in row for row in matrix)
""",
        gen=lambda r: (
            [_young_matrix(r, r.randint(1, 6), r.randint(1, 6)) for _ in range(20)] + [_young_matrix(r, 300, 300)]
        ),
    ),
    Problem(
        slug="find-minimum-in-rotated-sorted-array",
        title="Find Minimum in Rotated Sorted Array",
        difficulty="Medium",
        pattern="binary-search",
        topics=["Array", "Binary Search"],
        companies=[G, M],
        statement="A sorted array of distinct integers was rotated between 1 and n times (`[0,1,2,4,5,6,7]` → `[4,5,6,7,0,1,2]`). Return its minimum in O(log n).",
        entry="findMin",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[3, 4, 5, 1, 2]]}, {"args": [[4, 5, 6, 7, 0, 1, 2]]}, {"args": [[11, 13, 15, 17]]}],
        constraints=["1 ≤ len(nums) ≤ 5000", "Values are distinct"],
        hints=[
            "Compare nums[mid] with nums[hi]: if it's bigger, the minimum is right of mid; otherwise it's at mid or left."
        ],
        reference="""
class Solution:
    def findMin(self, nums):
        return min(nums)
""",
        gen=lambda r: [[_rotated(r, r.randint(1, 30))] for _ in range(20)] + [[_rotated(r, 5000)]],
    ),
    Problem(
        slug="find-first-and-last-position-of-element-in-sorted-array",
        title="Find First and Last Position of Element in Sorted Array",
        difficulty="Medium",
        pattern="binary-search",
        topics=["Array", "Binary Search"],
        companies=[M, G],
        statement="`nums` is sorted in non-decreasing order. Return `[first, last]`, the first and last index of `target`, or `[-1, -1]` if it's absent. O(log n).",
        entry="searchRange",
        params=[("nums", "List[int]"), ("target", "int")],
        returns="List[int]",
        examples=[{"args": [[5, 7, 7, 8, 8, 10], 8]}, {"args": [[5, 7, 7, 8, 8, 10], 6]}, {"args": [[], 0]}],
        constraints=["0 ≤ len(nums) ≤ 10⁵"],
        hints=["Two binary searches: the first index ≥ target and the first index > target."],
        reference="""
class Solution:
    def searchRange(self, nums, target):
        l, r = bisect_left(nums, target), bisect_right(nums, target)
        return [l, r - 1] if l < r else [-1, -1]
""",
        gen=lambda r: (
            [[sorted(ints(r, r.randint(0, 25), 0, 8)), r.randint(-1, 9)] for _ in range(20)]
            + [[sorted(ints(r, 100_000, 0, 50)), 25], [[7] * 100_000, 7]]
        ),
    ),
    Problem(
        slug="capacity-to-ship-packages-within-d-days",
        title="Capacity To Ship Packages Within D Days",
        difficulty="Medium",
        pattern="binary-search",
        topics=["Array", "Binary Search"],
        companies=[G, M],
        statement="Packages with `weights` must ship in the given order. Each day you load packages onto the ship until the next one would exceed its capacity. Return the smallest capacity that ships everything within `days` days.",
        entry="shipWithinDays",
        params=[("weights", "List[int]"), ("days", "int")],
        returns="int",
        examples=[
            {"args": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5]},
            {"args": [[3, 2, 2, 4, 1, 4], 3]},
            {"args": [[1, 2, 3, 1, 1], 4]},
        ],
        constraints=["1 ≤ days ≤ len(weights) ≤ 5 × 10⁴", "1 ≤ weights[i] ≤ 500"],
        hints=["Binary search the capacity between max(weights) and sum(weights); check each one greedily in O(n)."],
        reference="""
class Solution:
    def shipWithinDays(self, weights, days):
        def need(cap):
            d, load = 1, 0
            for w in weights:
                if load + w > cap: d += 1; load = 0
                load += w
            return d
        lo, hi = max(weights), sum(weights)
        while lo < hi:
            mid = (lo + hi) // 2
            if need(mid) <= days: hi = mid
            else: lo = mid + 1
        return lo
""",
        gen=lambda r: (
            [(lambda w: [w, r.randint(1, len(w))])(ints(r, r.randint(1, 20), 1, 20)) for _ in range(18)]
            + [[ints(r, 50_000, 1, 500), 1000]]
        ),
    ),
    Problem(
        slug="find-k-closest-elements",
        title="Find K Closest Elements",
        difficulty="Medium",
        pattern="binary-search",
        topics=["Array", "Two Pointers", "Binary Search", "Sliding Window"],
        companies=[M, G],
        statement="Given sorted `arr`, return the `k` values closest to `x`, sorted ascending. `a` is closer than `b` when `|a − x| < |b − x|`, or when they're equally close and `a < b`.",
        entry="findClosestElements",
        params=[("arr", "List[int]"), ("k", "int"), ("x", "int")],
        returns="List[int]",
        examples=[{"args": [[1, 2, 3, 4, 5], 4, 3]}, {"args": [[1, 1, 2, 3, 4, 5], 4, -1]}],
        constraints=["1 ≤ k ≤ len(arr) ≤ 10⁴", "−10⁴ ≤ arr[i], x ≤ 10⁴"],
        hints=[
            "The answer is a contiguous window. Binary search its left edge `i` in [0, n − k]: compare x − arr[mid] with arr[mid + k] − x."
        ],
        reference="""
class Solution:
    def findClosestElements(self, arr, k, x):
        return sorted(sorted(arr, key=lambda a: (abs(a - x), a))[:k])
""",
        gen=lambda r: (
            [
                (lambda a: [a, r.randint(1, len(a)), r.randint(-25, 25)])(sorted(ints(r, r.randint(1, 20), -20, 20)))
                for _ in range(20)
            ]
            + [[sorted(ints(r, 10_000, -(10**4), 10**4)), 2000, 37]]
        ),
    ),
    Problem(
        slug="single-element-in-a-sorted-array",
        title="Single Element in a Sorted Array",
        difficulty="Medium",
        pattern="binary-search",
        topics=["Array", "Binary Search"],
        companies=[G, M],
        statement="In the sorted array `nums`, every value appears exactly twice except one, which appears once. Return it in O(log n) time and O(1) space.",
        entry="singleNonDuplicate",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[1, 1, 2, 3, 3, 4, 4, 8, 8]]}, {"args": [[3, 3, 7, 7, 10, 11, 11]]}],
        constraints=["1 ≤ len(nums) ≤ 10⁵"],
        hints=[
            "Before the single element, pairs start at even indices; after it, at odd indices.",
            "Binary search on even mid: if nums[mid] == nums[mid + 1], the single is to the right.",
        ],
        reference="""
class Solution:
    def singleNonDuplicate(self, nums):
        return reduce(operator.xor, nums)
""",
        gen=lambda r: [[_single_sorted(r, n)] for n in [0, 0, 1, 2] + [r.randint(0, 15) for _ in range(16)] + [49_999]],
    ),
    Problem(
        slug="kth-missing-positive-number",
        title="Kth Missing Positive Number",
        difficulty="Easy",
        pattern="binary-search",
        topics=["Array", "Binary Search"],
        companies=[M],
        statement="`arr` is sorted strictly increasing and contains positive integers. Return the `k`-th positive integer missing from it.\n\nCan you beat O(n)?",
        entry="findKthPositive",
        params=[("arr", "List[int]"), ("k", "int")],
        returns="int",
        examples=[
            {"args": [[2, 3, 4, 7, 11], 5], "note": "Missing: 1, 5, 6, 8, 9, … → 9."},
            {"args": [[1, 2, 3, 4], 2]},
        ],
        constraints=["1 ≤ len(arr) ≤ 1000", "1 ≤ arr[i], k ≤ 1000"],
        hints=[
            "arr[i] − (i + 1) is how many numbers are missing before index i. Binary search for where that reaches k."
        ],
        reference="""
class Solution:
    def findKthPositive(self, arr, k):
        s = set(arr); x = 0
        while k:
            x += 1
            if x not in s: k -= 1
        return x
""",
        gen=lambda r: (
            [[sorted(r.sample(range(1, 61), r.randint(1, 30))), r.randint(1, 40)] for _ in range(20)]
            + [[list(range(1, 1001)), 1000]]
        ),
    ),
    Problem(
        slug="split-array-largest-sum",
        title="Split Array Largest Sum",
        difficulty="Hard",
        pattern="binary-search",
        topics=["Array", "Binary Search", "Dynamic Programming", "Greedy"],
        companies=[G, M],
        statement="Split `nums` into `k` non-empty contiguous subarrays so that the largest subarray sum is as small as possible. Return that minimised largest sum.",
        entry="splitArray",
        params=[("nums", "List[int]"), ("k", "int")],
        returns="int",
        examples=[{"args": [[7, 2, 5, 10, 8], 2], "note": "[7,2,5] and [10,8] → 18."}, {"args": [[1, 2, 3, 4, 5], 2]}],
        constraints=["1 ≤ len(nums) ≤ 1000", "0 ≤ nums[i] ≤ 10⁶", "1 ≤ k ≤ min(50, len(nums))"],
        hints=[
            "If a cap S is achievable, any bigger cap is too. Binary search S and greedily count how many pieces it needs."
        ],
        reference="""
class Solution:
    def splitArray(self, nums, k):
        def pieces(cap):
            n, s = 1, 0
            for x in nums:
                if s + x > cap: n += 1; s = 0
                s += x
            return n
        lo, hi = max(nums), sum(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if pieces(mid) <= k: hi = mid
            else: lo = mid + 1
        return lo
""",
        gen=lambda r: (
            [(lambda a: [a, r.randint(1, min(50, len(a)))])(ints(r, r.randint(1, 12), 0, 20)) for _ in range(18)]
            + [[ints(r, 1000, 0, 10**6), 50], [[0] * 1000, 7]]
        ),
    ),
    # ---------------------------------------------------------------- intervals & greedy
    Problem(
        slug="meeting-rooms",
        title="Meeting Rooms",
        difficulty="Easy",
        pattern="intervals-greedy",
        topics=["Array", "Sorting", "Intervals"],
        companies=[G, M],
        statement="Given meeting times `intervals[i] = [start, end)`, return `True` if one person could attend all of them. A meeting may start exactly when another ends.",
        entry="canAttendMeetings",
        params=[("intervals", "List[List[int]]")],
        returns="bool",
        examples=[{"args": [[[0, 30], [5, 10], [15, 20]]]}, {"args": [[[7, 10], [2, 4]]]}],
        constraints=["0 ≤ len(intervals) ≤ 10⁴", "0 ≤ start < end ≤ 10⁶"],
        hints=["Sort by start; any meeting that starts before the previous one ends is a clash."],
        reference="""
class Solution:
    def canAttendMeetings(self, intervals):
        iv = sorted(intervals)
        return all(iv[i][0] >= iv[i - 1][1] for i in range(1, len(iv)))
""",
        gen=lambda r: (
            [[[]], [[[1, 5], [5, 10]]]]
            + [[_meetings(r, r.randint(1, 8), 40)] for _ in range(18)]
            + [[_meetings(r, 10_000, 10**6)]]
        ),
    ),
    Problem(
        slug="insert-interval",
        title="Insert Interval",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["Array", "Intervals"],
        companies=[G, M],
        statement="`intervals` is sorted by start and non-overlapping. Insert `newInterval`, merging wherever needed, and return the resulting sorted, non-overlapping list. Touching intervals (`[1,2]` and `[2,3]`) merge.",
        entry="insert",
        params=[("intervals", "List[List[int]]"), ("newInterval", "List[int]")],
        returns="List[List[int]]",
        examples=[
            {"args": [[[1, 3], [6, 9]], [2, 5]]},
            {"args": [[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]]},
        ],
        constraints=["0 ≤ len(intervals) ≤ 10⁴", "0 ≤ start ≤ end ≤ 10⁵"],
        hints=[
            "Three phases: copy intervals ending before the new one, merge everything that overlaps it, copy the rest."
        ],
        reference="""
class Solution:
    def insert(self, intervals, newInterval):
        out = []
        for s, e in sorted(intervals + [newInterval]):
            if out and s <= out[-1][1]: out[-1][1] = max(out[-1][1], e)
            else: out.append([s, e])
        return out
""",
        gen=lambda r: (
            [[[], [5, 7]], [[[1, 5]], [6, 8]], [[[1, 5]], [0, 0]], [[[1, 5]], [5, 7]]]
            + [[_disjoint(r, r.randint(0, 8), 50), sorted(ints(r, 2, 0, 55))] for _ in range(18)]
            + [[_disjoint(r, 10_000, 10**5), [40_000, 60_000]]]
        ),
    ),
    Problem(
        slug="non-overlapping-intervals",
        title="Non-overlapping Intervals",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["Array", "Greedy", "Sorting", "Intervals"],
        companies=[G, M],
        statement="Return the minimum number of intervals to remove so the rest don't overlap. Intervals that only touch (`[1,2]` and `[2,3]`) don't overlap.",
        entry="eraseOverlapIntervals",
        params=[("intervals", "List[List[int]]")],
        returns="int",
        examples=[
            {"args": [[[1, 2], [2, 3], [3, 4], [1, 3]]]},
            {"args": [[[1, 2], [1, 2], [1, 2]]]},
            {"args": [[[1, 2], [2, 3]]]},
        ],
        constraints=["1 ≤ len(intervals) ≤ 10⁵", "−5 × 10⁴ ≤ start < end ≤ 5 × 10⁴"],
        hints=[
            "Sort by end. Greedily keep each interval that starts at or after the last kept end — earliest end leaves the most room."
        ],
        reference="""
class Solution:
    def eraseOverlapIntervals(self, intervals):
        kept, end = 0, -inf
        for s, e in sorted(intervals, key=lambda x: x[1]):
            if s >= end: kept += 1; end = e
        return len(intervals) - kept
""",
        gen=lambda r: [[_meetings(r, r.randint(1, 10), 20)] for _ in range(18)] + [[_meetings(r, 100_000, 50_000)]],
    ),
    Problem(
        slug="minimum-number-of-arrows-to-burst-balloons",
        title="Minimum Number of Arrows to Burst Balloons",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["Array", "Greedy", "Sorting", "Intervals"],
        companies=[G, M],
        statement="Each balloon spans `[xstart, xend]` horizontally. A vertical arrow shot at `x` bursts every balloon with `xstart ≤ x ≤ xend`. Return the minimum number of arrows that bursts all balloons.",
        entry="findMinArrowShots",
        params=[("points", "List[List[int]]")],
        returns="int",
        examples=[
            {"args": [[[10, 16], [2, 8], [1, 6], [7, 12]]]},
            {"args": [[[1, 2], [3, 4], [5, 6], [7, 8]]]},
            {"args": [[[1, 2], [2, 3], [3, 4], [4, 5]]]},
        ],
        constraints=["1 ≤ len(points) ≤ 10⁵", "−2³¹ ≤ xstart ≤ xend ≤ 2³¹ − 1"],
        hints=[
            "Sort by end and shoot at the end of the first unburst balloon; skip every balloon that starts at or before that point."
        ],
        reference="""
class Solution:
    def findMinArrowShots(self, points):
        arrows, x = 0, -inf
        for s, e in sorted(points, key=lambda p: p[1]):
            if s > x: arrows += 1; x = e
        return arrows
""",
        gen=lambda r: (
            [[[[-(2**31), 2**31 - 1]]], [[[0, 0], [0, 0]]]]
            + [[[sorted(ints(r, 2, 0, 30)) for _ in range(r.randint(1, 10))]] for _ in range(18)]
            + [[[sorted(ints(r, 2, -(2**31), 2**31 - 1)) for _ in range(100_000)]]]
        ),
    ),
    Problem(
        slug="interval-list-intersections",
        title="Interval List Intersections",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["Array", "Two Pointers", "Intervals"],
        companies=[M, G],
        statement="Each list of closed intervals is sorted and pairwise disjoint. Return the intersection of the two lists, sorted. Intervals that touch at a point intersect in that point, e.g. `[3, 3]`.",
        entry="intervalIntersection",
        params=[("firstList", "List[List[int]]"), ("secondList", "List[List[int]]")],
        returns="List[List[int]]",
        examples=[
            {"args": [[[0, 2], [5, 10], [13, 23], [24, 25]], [[1, 5], [8, 12], [15, 24], [25, 26]]]},
            {"args": [[[1, 3], [5, 9]], []]},
        ],
        constraints=["0 ≤ len(firstList), len(secondList) ≤ 1000", "0 ≤ start ≤ end ≤ 10⁹"],
        hints=[
            "Two pointers. The overlap is [max(starts), min(ends)] when non-empty; advance whichever interval ends first."
        ],
        reference="""
class Solution:
    def intervalIntersection(self, A, B):
        i = j = 0; out = []
        while i < len(A) and j < len(B):
            lo, hi = max(A[i][0], B[j][0]), min(A[i][1], B[j][1])
            if lo <= hi: out.append([lo, hi])
            if A[i][1] < B[j][1]: i += 1
            else: j += 1
        return out
""",
        gen=lambda r: (
            [[_disjoint(r, r.randint(0, 6), 40, True), _disjoint(r, r.randint(0, 6), 40, True)] for _ in range(20)]
            + [[_disjoint(r, 1000, 10**9, True), _disjoint(r, 1000, 10**9, True)]]
        ),
    ),
    Problem(
        slug="gas-station",
        title="Gas Station",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["Array", "Greedy"],
        companies=[G, M],
        statement="Stations sit on a circular route. Station `i` gives `gas[i]` fuel, and driving from `i` to `i + 1` costs `cost[i]`. You start with an empty tank. Return the starting station from which you can drive around the circuit once clockwise, or `-1` if impossible. If a solution exists it is unique.",
        entry="canCompleteCircuit",
        params=[("gas", "List[int]"), ("cost", "List[int]")],
        returns="int",
        examples=[{"args": [[1, 2, 3, 4, 5], [3, 4, 5, 1, 2]]}, {"args": [[2, 3, 4], [3, 4, 3]]}],
        constraints=["1 ≤ n ≤ 10⁵", "0 ≤ gas[i], cost[i] ≤ 10⁴"],
        hints=[
            "If total gas < total cost, it's impossible. Otherwise a valid start exists.",
            "Whenever the running tank goes negative at i, no station up to i can be the start — restart from i + 1.",
        ],
        reference="""
class Solution:
    def canCompleteCircuit(self, gas, cost):
        if sum(gas) < sum(cost): return -1
        start = tank = 0
        for i in range(len(gas)):
            tank += gas[i] - cost[i]
            if tank < 0: start = i + 1; tank = 0
        return start
""",
        gen=lambda r: [_gas(r, r.randint(1, 12)) for _ in range(20)] + [_gas(r, 100_000)],
    ),
    Problem(
        slug="jump-game-ii",
        title="Jump Game II",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["Array", "Greedy", "Dynamic Programming"],
        companies=[G, M],
        statement="You start at index 0; `nums[i]` is the longest jump from index `i`. Return the minimum number of jumps to reach the last index. It's always reachable.",
        entry="jump",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[2, 3, 1, 1, 4]]}, {"args": [[2, 3, 0, 1, 4]]}],
        constraints=["1 ≤ len(nums) ≤ 10⁴", "0 ≤ nums[i] ≤ 1000", "The last index is reachable"],
        hints=[
            "BFS by levels without a queue: track the end of the current jump's reach and the furthest the next jump can go."
        ],
        reference="""
class Solution:
    def jump(self, nums):
        jumps = end = far = 0
        for i in range(len(nums) - 1):
            far = max(far, i + nums[i])
            if i == end: jumps += 1; end = far
        return jumps
""",
        gen=lambda r: (
            [[[0]], [[1, 1]]] + [[_reachable(r, r.randint(1, 30), 4)] for _ in range(18)] + [[_reachable(r, 10_000, 3)]]
        ),
    ),
    Problem(
        slug="hand-of-straights",
        title="Hand of Straights",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["Array", "Hash Table", "Greedy", "Sorting"],
        companies=[G],
        statement="Return `True` if the cards in `hand` can be split into groups of size `groupSize`, where each group is `groupSize` consecutive values.",
        entry="isNStraightHand",
        params=[("hand", "List[int]"), ("groupSize", "int")],
        returns="bool",
        examples=[{"args": [[1, 2, 3, 6, 2, 3, 4, 7, 8], 3]}, {"args": [[1, 2, 3, 4, 5], 4]}],
        constraints=["1 ≤ len(hand) ≤ 10⁴", "1 ≤ groupSize ≤ len(hand)"],
        hints=[
            "The smallest remaining card must start a group. Count with a Counter and consume groups from the smallest value up."
        ],
        reference="""
class Solution:
    def isNStraightHand(self, hand, groupSize):
        cnt = Counter(hand)
        for x in sorted(cnt):
            k = cnt[x]
            if k:
                for y in range(x, x + groupSize):
                    if cnt[y] < k: return False
                    cnt[y] -= k
        return True
""",
        gen=lambda r: [_straights(r, r.randint(1, 4), r.randint(1, 5)) for _ in range(20)] + [_straights(r, 50, 200)],
    ),
    Problem(
        slug="partition-labels",
        title="Partition Labels",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["String", "Hash Table", "Greedy", "Two Pointers"],
        companies=[M, G],
        statement="Split `s` into as many parts as possible so that each letter appears in at most one part. Return the sizes of the parts, in order.",
        entry="partitionLabels",
        params=[("s", "str")],
        returns="List[int]",
        examples=[{"args": ["ababcbacadefegdehijhklij"]}, {"args": ["eccbbbbdec"]}],
        constraints=["1 ≤ len(s) ≤ 500", "Lowercase English letters"],
        hints=[
            "Record each letter's last index. Extend the current part's end to the last index of every letter in it; cut when i reaches the end."
        ],
        reference="""
class Solution:
    def partitionLabels(self, s):
        last = {c: i for i, c in enumerate(s)}
        out = []; start = end = 0
        for i, c in enumerate(s):
            end = max(end, last[c])
            if i == end:
                out.append(end - start + 1); start = i + 1
        return out
""",
        gen=lambda r: (
            [["a"], ["abc"]]
            + [[word(r, r.randint(1, 30), "abcdefgh"[: r.randint(2, 8)])] for _ in range(18)]
            + [[word(r, 500, "abcdefghijklmnopqrstuvwxyz")]]
        ),
    ),
    Problem(
        slug="valid-parenthesis-string",
        title="Valid Parenthesis String",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["String", "Greedy", "Stack", "Dynamic Programming"],
        companies=[M, G],
        statement="`s` contains `(`, `)` and `*`. Each `*` can act as `(`, `)` or an empty string. Return `True` if some choice makes `s` a valid parentheses string.",
        entry="checkValidString",
        params=[("s", "str")],
        returns="bool",
        examples=[{"args": ["()"]}, {"args": ["(*)"]}, {"args": ["(*))"]}, {"args": ["(((*)"]}],
        constraints=["1 ≤ len(s) ≤ 100"],
        hints=[
            "Track the range [lo, hi] of possible open-bracket counts. `*` widens it both ways; clamp lo at 0; fail if hi < 0."
        ],
        reference="""
class Solution:
    def checkValidString(self, s):
        lo = hi = 0
        for c in s:
            lo += 1 if c == '(' else -1
            hi += 1 if c != ')' else -1
            if hi < 0: return False
            lo = max(lo, 0)
        return lo == 0
""",
        gen=lambda r: (
            [["*"], [")*"], ["*("], ["**))"]]
            + [[word(r, r.randint(1, 16), "()*")] for _ in range(18)]
            + [[word(r, 100, "(()**")]]
        ),
    ),
    Problem(
        slug="best-time-to-buy-and-sell-stock-ii",
        title="Best Time to Buy and Sell Stock II",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["Array", "Greedy", "Dynamic Programming"],
        companies=[G, M],
        statement="`prices[i]` is the stock price on day `i`. You can hold at most one share at a time but may buy and sell as many times as you like (even sell and buy on the same day). Return the maximum profit.",
        entry="maxProfit",
        params=[("prices", "List[int]")],
        returns="int",
        examples=[{"args": [[7, 1, 5, 3, 6, 4]]}, {"args": [[1, 2, 3, 4, 5]]}, {"args": [[7, 6, 4, 3, 1]]}],
        constraints=["1 ≤ len(prices) ≤ 3 × 10⁴", "0 ≤ prices[i] ≤ 10⁴"],
        hints=["Collect every upward step: sum of max(0, prices[i] − prices[i − 1])."],
        reference="""
class Solution:
    def maxProfit(self, prices):
        return sum(max(0, b - a) for a, b in pairwise(prices))
""",
        gen=lambda r: [[[1]]] + [[ints(r, r.randint(1, 30), 0, 20)] for _ in range(18)] + [[ints(r, 30_000, 0, 10**4)]],
    ),
    Problem(
        slug="candy",
        title="Candy",
        difficulty="Hard",
        pattern="intervals-greedy",
        topics=["Array", "Greedy"],
        companies=[G, M],
        statement="Children stand in a line with `ratings`. Give each child at least one candy, and any child with a higher rating than an adjacent child must get more candies than that neighbour. Return the minimum total number of candies.",
        entry="candy",
        params=[("ratings", "List[int]")],
        returns="int",
        examples=[
            {"args": [[1, 0, 2]]},
            {"args": [[1, 2, 2]], "note": "[1, 2, 1] — equal neighbours have no constraint."},
        ],
        constraints=["1 ≤ len(ratings) ≤ 2 × 10⁴", "0 ≤ ratings[i] ≤ 2 × 10⁴"],
        hints=[
            "Left-to-right pass handles left neighbours, right-to-left pass handles right ones; take the max of both at each child."
        ],
        reference="""
class Solution:
    def candy(self, ratings):
        n = len(ratings); c = [1] * n
        for i in range(1, n):
            if ratings[i] > ratings[i - 1]: c[i] = c[i - 1] + 1
        for i in range(n - 2, -1, -1):
            if ratings[i] > ratings[i + 1]: c[i] = max(c[i], c[i + 1] + 1)
        return sum(c)
""",
        gen=lambda r: (
            [[[5]], [[1, 3, 2, 2, 1]], [[1, 2, 87, 87, 87, 2, 1]]]
            + [[ints(r, r.randint(1, 20), 0, 6)] for _ in range(17)]
            + [[ints(r, 20_000, 0, 20_000)], [list(range(20_000, 0, -1))]]
        ),
    ),
]


# ---------------------------------------------------------------- private generator helpers
def _stack_ops(r: random.Random, cls: str, n: int, reads: list[str]) -> list[Any]:
    """push/read ops that never read from an empty stack or queue; only `pop` removes an element."""
    ops: list[str] = [cls]
    args: list[list[Any]] = [[]]
    size = 0
    for _ in range(n):
        op = "push" if size == 0 or r.random() < 0.45 else r.choice(reads)
        ops.append(op)
        if op != "push":
            args.append([])
            size -= op == "pop"
        elif cls == "MyQueue":
            args.append([r.randint(1, 9)])
            size += 1
        else:
            args.append([r.randint(-20, 20) if r.random() < 0.9 else r.randint(-(2**31), 2**31 - 1)])
            size += 1
    return [{"ops": ops, "args": args}]


def _rpn(r: random.Random, leaves: int) -> list[str]:
    def apply(op: str, a: int, b: int) -> int | None:
        match op:
            case "+":
                return a + b
            case "-":
                return a - b
            case "*":
                return a * b
            case _:
                return None if b == 0 else abs(a) // abs(b) * (1 if (a >= 0) == (b > 0) else -1)

    def build(k: int) -> tuple[list[str], int]:
        if k == 1:
            v = r.randint(-20, 20)
            return [str(v)], v
        left = r.randint(1, k - 1)
        a, va = build(left)
        b, vb = build(k - left)
        for op in r.sample("+-*/", 4):  # first op whose result stays a valid 32-bit integer
            res = apply(op, va, vb)
            if res is not None and abs(res) < 2**31:
                return [*a, *b, op], res
        raise AssertionError("+ or / always fits")

    return build(leaves)[0]


def _encoded(r: random.Random, depth: int) -> str:
    parts = []
    for _ in range(r.randint(1, 3)):
        if depth and r.random() < 0.5:
            parts.append(f"{r.randint(1, 4)}[{_encoded(r, depth - 1)}]")
        else:
            parts.append(word(r, r.randint(1, 3), "abcxyz"))
    return "".join(parts)


def _calc_expr(r: random.Random, depth: int) -> str:
    s = ""
    for i in range(r.randint(1, 4)):
        t = f"({_calc_expr(r, depth - 1)})" if depth and r.random() < 0.4 else str(r.randint(0, 200))
        s += t if i == 0 else r.choice([" + ", " - ", "+", "-"]) + t
    return "-" + s if r.random() < 0.2 else s


def _fleet(r: random.Random, n: int, target: int) -> list[Any]:
    return [target, r.sample(range(target), min(n, target)), ints(r, min(n, target), 1, 10)]


def _sorted_target(r: random.Random, n: int) -> list[Any]:
    nums = sorted(distinct(r, n, -(10**4), 10**4))
    return [nums, r.choice(nums) if r.random() < 0.6 else r.randint(-(10**4) - 1, 10**4 + 1)]


def _flat_matrix(r: random.Random, R: int, C: int) -> list[Any]:
    vals = sorted(distinct(r, R * C, -(10**4), 10**4))
    m = [vals[i * C : (i + 1) * C] for i in range(R)]
    return [m, r.choice(vals) if r.random() < 0.5 else r.randint(-(10**4), 10**4)]


def _young_matrix(r: random.Random, R: int, C: int) -> list[Any]:
    m = [[0] * C for _ in range(R)]
    for i in range(R):
        for j in range(C):
            m[i][j] = max(m[i - 1][j] if i else -50, m[i][j - 1] if j else -50) + r.randint(0, 3)
    flat = [x for row in m for x in row]
    return [m, r.choice(flat) if r.random() < 0.5 else r.randint(min(flat) - 2, max(flat) + 2)]


def _rotated(r: random.Random, n: int) -> list[int]:
    nums = sorted(distinct(r, n, -5000, 5000))
    k = r.randrange(n)
    return nums[k:] + nums[:k]


def _single_sorted(r: random.Random, pairs: int) -> list[int]:
    vals = sorted(distinct(r, pairs + 1, 0, 10**5))
    single = r.choice(vals)
    return sorted([v for v in vals for _ in range(1 if v == single else 2)])


def _meetings(r: random.Random, n: int, span: int) -> list[list[int]]:
    return [(lambda s: [s, s + r.randint(1, max(1, span // 4))])(r.randint(-span, span)) for _ in range(n)]


def _disjoint(r: random.Random, n: int, span: int, points: bool = False) -> list[list[int]]:
    """n sorted intervals in [0, span] that neither overlap nor touch; `points` also allows [x, x]."""
    pts = sorted(r.sample(range(span + 1), 2 * n))
    return [[a, a] if points and r.random() < 0.2 else [a, b] for a, b in zip(pts[::2], pts[1::2], strict=True)]


def _gas(r: random.Random, n: int) -> list[Any]:
    while True:
        gas = ints(r, n, 0, 10)
        cost = ints(r, n, 0, 10)
        if sum(gas) < sum(cost):
            return [gas, cost]
        prefix, p = [], 0
        for g, c in zip(gas, cost, strict=True):
            prefix.append(p)
            p += g - c
        if prefix.count(min(prefix)) == 1:  # the start is unique
            return [gas, cost]


def _reachable(r: random.Random, n: int, mx: int) -> list[int]:
    return [r.randint(1, mx) if i < n - 1 else r.randint(0, mx) for i in range(n)]


def _straights(r: random.Random, size: int, groups: int) -> list[Any]:
    hand: list[int] = []
    for _ in range(groups):
        s = r.randint(0, 20)
        hand += range(s, s + size)
    if r.random() < 0.4:
        hand[r.randrange(len(hand))] += r.choice([-1, 1])
    r.shuffle(hand)
    return [hand, size]
