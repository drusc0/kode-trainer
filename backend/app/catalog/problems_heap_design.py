import random
from typing import Any

from .base import Problem, ints, ops_case, word

G, M = "google", "meta"

PROBLEMS = [
    # ---------------------------------------------------------------- heaps
    Problem(
        slug="last-stone-weight",
        title="Last Stone Weight",
        difficulty="Easy",
        pattern="heap",
        topics=["Array", "Heap"],
        companies=[G, M],
        statement="Each turn, smash the two heaviest stones `x ≤ y` together: if `x == y` both are destroyed, otherwise the result is one stone of weight `y − x`. Return the weight of the last stone, or `0` if none are left.",
        entry="lastStoneWeight",
        params=[("stones", "List[int]")],
        returns="int",
        examples=[{"args": [[2, 7, 4, 1, 8, 1]]}, {"args": [[1]]}],
        constraints=["1 ≤ len(stones) ≤ 30", "1 ≤ stones[i] ≤ 1000"],
        hints=["A max-heap gives the two heaviest in O(log n). Python's heapq is a min-heap, so push negated weights."],
        reference="""
class Solution:
    def lastStoneWeight(self, stones):
        s = sorted(stones)
        while len(s) > 1:
            y, x = s.pop(), s.pop()
            if y != x: insort(s, y - x)
        return s[0] if s else 0
""",
        gen=lambda r: (
            [[[2, 2]], [[3, 7, 2]]] + [[ints(r, r.randint(1, 30), 1, r.choice([5, 1000]))] for _ in range(18)]
        ),
    ),
    Problem(
        slug="kth-largest-element-in-a-stream",
        title="Kth Largest Element in a Stream",
        difficulty="Easy",
        pattern="heap",
        kind="design",
        topics=["Tree", "Design", "Heap", "Data Stream"],
        companies=[G, M],
        statement="Design `KthLargest`:\n\n- `KthLargest(k, nums)` starts with the scores `nums`.\n- `add(val)` adds a score and returns the `k`-th largest score so far.\n\nThere are always at least `k` scores when `add` returns.",
        entry="KthLargest",
        params=[("operations", "List[str]"), ("arguments", "List[list]")],
        returns="List",
        starter="""
class KthLargest:

    def __init__(self, k: int, nums: List[int]):


    def add(self, val: int) -> int:

""",
        examples=[
            {
                "args": [
                    {
                        "ops": ["KthLargest", "add", "add", "add", "add", "add"],
                        "args": [[3, [4, 5, 8, 2]], [3], [5], [10], [9], [4]],
                    }
                ]
            }
        ],
        constraints=["1 ≤ k ≤ 10⁴", "At most 10⁴ calls to add"],
        hints=["Keep a min-heap of the k largest scores; its top is the answer. Pop whenever it grows past k."],
        reference="""
class KthLargest:
    def __init__(self, k, nums):
        self.k = k; self.h = sorted(nums)
    def add(self, val):
        insort(self.h, val)
        return self.h[-self.k]
""",
        gen=lambda r: (
            [_kth_stream(r, r.randint(1, 5), r.randint(0, 4), r.randint(1, 20)) for _ in range(14)]
            + [_kth_stream(r, 500, 500, 10_000)]
        ),
    ),
    Problem(
        slug="find-median-from-data-stream",
        title="Find Median from Data Stream",
        difficulty="Hard",
        pattern="heap",
        kind="design",
        topics=["Two Pointers", "Design", "Sorting", "Heap", "Data Stream"],
        companies=[G, M],
        statement="Design `MedianFinder`:\n\n- `addNum(num)` adds an integer.\n- `findMedian()` returns the median of everything added so far: the middle value, or the mean of the two middle values when the count is even.\n\n`findMedian` is only called after at least one `addNum`.",
        entry="MedianFinder",
        params=[("operations", "List[str]"), ("arguments", "List[List[int]]")],
        returns="List",
        starter="""
class MedianFinder:

    def __init__(self):


    def addNum(self, num: int) -> None:


    def findMedian(self) -> float:

""",
        examples=[
            {
                "args": [
                    {
                        "ops": ["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"],
                        "args": [[], [1], [2], [], [3], []],
                    }
                ]
            }
        ],
        constraints=["−10⁵ ≤ num ≤ 10⁵", "At most 5 × 10⁴ calls"],
        hints=[
            "Two heaps: a max-heap for the smaller half and a min-heap for the larger half, kept within one element in size.",
            "The median is the top of the bigger heap, or the mean of both tops.",
        ],
        reference="""
class MedianFinder:
    def __init__(self):
        self.a = []
    def addNum(self, num):
        insort(self.a, num)
    def findMedian(self):
        a = self.a; n = len(a)
        return float(a[n // 2]) if n % 2 else (a[n // 2 - 1] + a[n // 2]) / 2
""",
        gen=lambda r: [_median_ops(r, r.randint(1, 30), 10) for _ in range(14)] + [_median_ops(r, 50_000, 10**5)],
    ),
    Problem(
        slug="task-scheduler",
        title="Task Scheduler",
        difficulty="Medium",
        pattern="heap",
        topics=["Array", "Hash Table", "Greedy", "Heap", "Counting"],
        companies=[M, G],
        statement="A CPU runs `tasks` (uppercase letters), one per time unit, in any order, or stays idle. Two runs of the same task must be at least `n` units apart. Return the minimum number of time units needed to run all tasks.",
        entry="leastInterval",
        params=[("tasks", "List[str]"), ("n", "int")],
        returns="int",
        examples=[
            {"args": [["A", "A", "A", "B", "B", "B"], 2], "note": "A B idle A B idle A B → 8."},
            {"args": [["A", "C", "A", "B", "D", "B"], 1]},
            {"args": [["A", "A", "A", "B", "B", "B"], 3]},
        ],
        constraints=["1 ≤ len(tasks) ≤ 10⁴", "0 ≤ n ≤ 100"],
        hints=[
            "Simulate with a max-heap of remaining counts and a cooldown queue, or…",
            "Count the most frequent task (f) and how many tasks share that count (m): answer = max(len(tasks), (f − 1)(n + 1) + m).",
        ],
        reference="""
class Solution:
    def leastInterval(self, tasks, n):
        c = Counter(tasks).values(); f = max(c)
        return max(len(tasks), (f - 1) * (n + 1) + sum(1 for x in c if x == f))
""",
        gen=lambda r: (
            [[list(word(r, r.randint(1, 20), "ABCDE"[: r.randint(1, 5)])), r.randint(0, 5)] for _ in range(18)]
            + [[list(word(r, 10_000, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")), 100], [["A"] * 10_000, 100]]
        ),
    ),
    Problem(
        slug="top-k-frequent-words",
        title="Top K Frequent Words",
        difficulty="Medium",
        pattern="heap",
        topics=["Hash Table", "String", "Trie", "Sorting", "Heap", "Counting"],
        companies=[G, M],
        statement="Return the `k` most frequent strings in `words`, sorted by frequency from highest to lowest. Words with the same frequency are sorted alphabetically.",
        entry="topKFrequent",
        params=[("words", "List[str]"), ("k", "int")],
        returns="List[str]",
        examples=[
            {"args": [["i", "love", "leetcode", "i", "love", "coding"], 2]},
            {"args": [["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4]},
        ],
        constraints=["1 ≤ len(words) ≤ 500", "k is in range [1, number of unique words]"],
        hints=["Count, then sort (or heap) by the key (−count, word)."],
        reference="""
class Solution:
    def topKFrequent(self, words, k):
        c = Counter(words)
        return sorted(c, key=lambda w: (-c[w], w))[:k]
""",
        gen=lambda r: (
            [
                (lambda w: [w, r.randint(1, len(set(w)))])(
                    [word(r, r.randint(1, 3), "abc") for _ in range(r.randint(1, 30))]
                )
                for _ in range(18)
            ]
            + [(lambda w: [w, 20])([word(r, r.randint(1, 4), "abcd") for _ in range(500)])]
        ),
    ),
    # ---------------------------------------------------------------- tries
    Problem(
        slug="design-add-and-search-words-data-structure",
        title="Design Add and Search Words Data Structure",
        difficulty="Medium",
        pattern="trie",
        kind="design",
        topics=["String", "DFS", "Design", "Trie"],
        companies=[M, G],
        statement="Design `WordDictionary`:\n\n- `addWord(word)` stores a word.\n- `search(word)` returns `True` if any stored word matches `word`, where `.` matches any single letter.",
        entry="WordDictionary",
        params=[("operations", "List[str]"), ("arguments", "List[List[str]]")],
        returns="List",
        starter="""
class WordDictionary:

    def __init__(self):


    def addWord(self, word: str) -> None:


    def search(self, word: str) -> bool:

""",
        examples=[
            {
                "args": [
                    {
                        "ops": [
                            "WordDictionary",
                            "addWord",
                            "addWord",
                            "addWord",
                            "search",
                            "search",
                            "search",
                            "search",
                        ],
                        "args": [[], ["bad"], ["dad"], ["mad"], ["pad"], ["bad"], [".ad"], ["b.."]],
                    }
                ]
            }
        ],
        constraints=["1 ≤ len(word) ≤ 25", "At most 2 dots per search", "At most 10⁴ calls"],
        hints=["A trie, with DFS at `.` over every child of the current node."],
        reference="""
class WordDictionary:
    def __init__(self):
        self.by_len = defaultdict(set)
    def addWord(self, word):
        self.by_len[len(word)].add(word)
    def search(self, word):
        if '.' not in word: return word in self.by_len[len(word)]
        return any(all(p in ('.', c) for p, c in zip(word, w)) for w in self.by_len[len(word)])
""",
        gen=lambda r: (
            [ops_case(r, "WordDictionary", [], r.randint(2, 30), lambda: _wd_op(r, "abc", 4)) for _ in range(14)]
            + [ops_case(r, "WordDictionary", [], 3000, lambda: _wd_op(r, "abcdefgh", 8))]
        ),
    ),
    Problem(
        slug="word-search-ii",
        title="Word Search II",
        difficulty="Hard",
        pattern="trie",
        topics=["Array", "String", "Backtracking", "Trie", "Matrix"],
        companies=[G, M],
        statement="Return every word from `words` that can be traced on `board` through horizontally or vertically adjacent cells, using each cell at most once per word. Any order is accepted.",
        entry="findWords",
        params=[("board", "List[List[str]]"), ("words", "List[str]")],
        returns="List[str]",
        examples=[
            {
                "args": [
                    [["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]],
                    ["oath", "pea", "eat", "rain"],
                ]
            },
            {"args": [[["a", "b"], ["c", "d"]], ["abcb"]]},
        ],
        constraints=["1 ≤ rows, cols ≤ 12", "1 ≤ len(words) ≤ 3 × 10⁴", "1 ≤ len(words[i]) ≤ 10", "words are unique"],
        hints=[
            "Running Word Search once per word repeats work. Put all words in a trie and DFS the board once, following trie edges.",
            "Remove a word from the trie once found, and prune empty branches, to stay fast.",
        ],
        reference="""
class Solution:
    def findWords(self, board, words):
        trie = {}
        for w in words:
            node = trie
            for c in w: node = node.setdefault(c, {})
            node['$'] = w
        R, C = len(board), len(board[0]); found = []
        def dfs(i, j, parent):
            c = board[i][j]; node = parent[c]
            if '$' in node: found.append(node.pop('$'))
            board[i][j] = '#'
            for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= x < R and 0 <= y < C and board[x][y] in node: dfs(x, y, node)
            board[i][j] = c
            if not node: parent.pop(c)
        for i in range(R):
            for j in range(C):
                if board[i][j] in trie: dfs(i, j, trie)
        return found
""",
        gen=lambda r: (
            [_word_board(r, r.randint(1, 4), r.randint(1, 4), r.randint(1, 15), "abc") for _ in range(18)]
            + [_word_board(r, 12, 12, 30_000, "abcdefghij")]
        ),
        compare="sorted",
    ),
    # ---------------------------------------------------------------- design
    Problem(
        slug="design-hit-counter",
        title="Design Hit Counter",
        difficulty="Medium",
        pattern="design",
        kind="design",
        topics=["Array", "Binary Search", "Design", "Queue"],
        companies=[G, M],
        statement="Design `HitCounter`, which counts hits in the past 5 minutes:\n\n- `hit(timestamp)` records a hit at `timestamp` seconds.\n- `getHits(timestamp)` returns the number of hits in the window `(timestamp − 300, timestamp]`.\n\nTimestamps are non-decreasing across calls, and several hits can share a timestamp.",
        entry="HitCounter",
        params=[("operations", "List[str]"), ("arguments", "List[List[int]]")],
        returns="List",
        starter="""
class HitCounter:

    def __init__(self):


    def hit(self, timestamp: int) -> None:


    def getHits(self, timestamp: int) -> int:

""",
        examples=[
            {
                "args": [
                    {
                        "ops": ["HitCounter", "hit", "hit", "hit", "getHits", "hit", "getHits", "getHits"],
                        "args": [[], [1], [2], [3], [4], [300], [300], [301]],
                    }
                ]
            }
        ],
        constraints=["1 ≤ timestamp ≤ 2 × 10⁹", "At most 300 calls"],
        hints=["Keep hit timestamps in a deque and pop from the front everything ≤ timestamp − 300."],
        reference="""
class HitCounter:
    def __init__(self):
        self.t = []
    def hit(self, timestamp):
        self.t.append(timestamp)
    def getHits(self, timestamp):
        return sum(1 for x in self.t if timestamp - 300 < x <= timestamp)
""",
        gen=lambda r: [_hits(r, r.randint(1, 40)) for _ in range(14)] + [_hits(r, 300)],
    ),
    Problem(
        slug="design-browser-history",
        title="Design Browser History",
        difficulty="Medium",
        pattern="design",
        kind="design",
        topics=["Array", "Linked List", "Stack", "Design"],
        companies=[G, M],
        statement="Design `BrowserHistory` for a single tab:\n\n- `BrowserHistory(homepage)` starts on `homepage`.\n- `visit(url)` goes to `url` and clears all forward history.\n- `back(steps)` moves back up to `steps` pages and returns the current url.\n- `forward(steps)` moves forward up to `steps` pages and returns the current url.",
        entry="BrowserHistory",
        params=[("operations", "List[str]"), ("arguments", "List[list]")],
        returns="List",
        starter="""
class BrowserHistory:

    def __init__(self, homepage: str):


    def visit(self, url: str) -> None:


    def back(self, steps: int) -> str:


    def forward(self, steps: int) -> str:

""",
        examples=[
            {
                "args": [
                    {
                        "ops": [
                            "BrowserHistory",
                            "visit",
                            "visit",
                            "visit",
                            "back",
                            "back",
                            "forward",
                            "visit",
                            "forward",
                            "back",
                            "back",
                        ],
                        "args": [
                            ["leetcode.com"],
                            ["google.com"],
                            ["facebook.com"],
                            ["youtube.com"],
                            [1],
                            [1],
                            [1],
                            ["linkedin.com"],
                            [2],
                            [2],
                            [7],
                        ],
                    }
                ]
            }
        ],
        constraints=["1 ≤ steps ≤ 100", "At most 5000 calls"],
        hints=[
            "A list of pages plus a current index and an end index: `visit` writes at index + 1 and moves the end there."
        ],
        reference="""
class BrowserHistory:
    def __init__(self, homepage):
        self.pages = [homepage]; self.i = 0
    def visit(self, url):
        del self.pages[self.i + 1:]; self.pages.append(url); self.i += 1
    def back(self, steps):
        self.i = max(0, self.i - steps); return self.pages[self.i]
    def forward(self, steps):
        self.i = min(len(self.pages) - 1, self.i + steps); return self.pages[self.i]
""",
        gen=lambda r: (
            [
                ops_case(r, "BrowserHistory", [word(r, 3, "xyz") + ".com"], r.randint(1, 30), lambda: _browser_op(r, 4))
                for _ in range(14)
            ]
            + [ops_case(r, "BrowserHistory", ["home.com"], 5000, lambda: _browser_op(r, 100))]
        ),
    ),
    Problem(
        slug="snapshot-array",
        title="Snapshot Array",
        difficulty="Medium",
        pattern="design",
        kind="design",
        topics=["Array", "Hash Table", "Binary Search", "Design"],
        companies=[G],
        statement="Design `SnapshotArray`:\n\n- `SnapshotArray(length)` creates an array of `length` zeros.\n- `set(index, val)` sets an element.\n- `snap()` takes a snapshot and returns its id: the number of times `snap` was called before, starting at 0.\n- `get(index, snap_id)` returns the element's value at the time of snapshot `snap_id`.\n\nCopying the whole array on every snap is too slow and too big.",
        entry="SnapshotArray",
        params=[("operations", "List[str]"), ("arguments", "List[List[int]]")],
        returns="List",
        starter="""
class SnapshotArray:

    def __init__(self, length: int):


    def set(self, index: int, val: int) -> None:


    def snap(self) -> int:


    def get(self, index: int, snap_id: int) -> int:

""",
        examples=[
            {
                "args": [
                    {"ops": ["SnapshotArray", "set", "snap", "set", "get"], "args": [[3], [0, 5], [], [0, 6], [0, 0]]}
                ]
            }
        ],
        constraints=["1 ≤ length ≤ 5 × 10⁴", "0 ≤ snap_id < number of snaps so far", "At most 5 × 10⁴ calls"],
        hints=[
            "Per index, keep a list of (snap_id, value) changes. `get` binary searches for the last change at or before snap_id."
        ],
        reference="""
class SnapshotArray:
    def __init__(self, length):
        self.cur = {}; self.snaps = []
    def set(self, index, val):
        self.cur[index] = val
    def snap(self):
        self.snaps.append(dict(self.cur)); return len(self.snaps) - 1
    def get(self, index, snap_id):
        return self.snaps[snap_id].get(index, 0)
""",
        gen=lambda r: [_snapshot(r, r.randint(1, 5), r.randint(1, 30)) for _ in range(14)] + [_snapshot(r, 50, 3000)],
    ),
    Problem(
        slug="lfu-cache",
        title="LFU Cache",
        difficulty="Hard",
        pattern="design",
        kind="design",
        topics=["Hash Table", "Linked List", "Design", "Doubly-Linked List"],
        companies=[G, M],
        statement="Design a Least Frequently Used cache:\n\n- `LFUCache(capacity)` creates it.\n- `get(key)` returns the value, or `-1` if absent.\n- `put(key, value)` inserts or updates the key. When the cache is full, first evict the key used the fewest times; among ties, evict the least recently used.\n\nEvery `get` or `put` on a key counts as a use. Both operations should be O(1) on average.",
        entry="LFUCache",
        params=[("operations", "List[str]"), ("arguments", "List[List[int]]")],
        returns="List",
        starter="""
class LFUCache:

    def __init__(self, capacity: int):


    def get(self, key: int) -> int:


    def put(self, key: int, value: int) -> None:

""",
        examples=[
            {
                "args": [
                    {
                        "ops": ["LFUCache", "put", "put", "get", "put", "get", "get", "put", "get", "get", "get"],
                        "args": [[2], [1, 1], [2, 2], [1], [3, 3], [2], [3], [4, 4], [1], [3], [4]],
                    }
                ]
            }
        ],
        constraints=["1 ≤ capacity ≤ 10⁴", "At most 2 × 10⁵ calls"],
        hints=[
            "Map key → (value, freq), and freq → OrderedDict of keys in recency order. Track the minimum frequency.",
            "A new key always has frequency 1, so it resets the minimum to 1.",
        ],
        reference="""
class LFUCache:
    def __init__(self, capacity):
        self.cap = capacity; self.val = {}; self.freq = {}; self.last = {}; self.t = 0
    def _use(self, key):
        self.t += 1; self.freq[key] = self.freq.get(key, 0) + 1; self.last[key] = self.t
    def get(self, key):
        if key not in self.val: return -1
        self._use(key); return self.val[key]
    def put(self, key, value):
        if key not in self.val and len(self.val) == self.cap:
            victim = min(self.val, key=lambda k: (self.freq[k], self.last[k]))
            del self.val[victim], self.freq[victim], self.last[victim]
        self.val[key] = value; self._use(key)
""",
        gen=lambda r: (
            [
                ops_case(
                    r,
                    "LFUCache",
                    [r.randint(1, 3)],
                    r.randint(1, 30),
                    lambda: r.choice([("get", [r.randint(1, 5)]), ("put", [r.randint(1, 5), r.randint(0, 9)])]),
                )
                for _ in range(14)
            ]
            + [
                ops_case(
                    r,
                    "LFUCache",
                    [50],
                    5000,
                    lambda: r.choice([("get", [r.randint(1, 120)]), ("put", [r.randint(1, 120), r.randint(0, 99)])]),
                )
            ]
        ),
    ),
]


# ---------------------------------------------------------------- private generator helpers
def _kth_stream(r: random.Random, k: int, extra: int, adds: int) -> list[Any]:
    nums = ints(r, k - 1 + extra, -50, 50)  # at least k - 1, so every add sees k scores
    return ops_case(r, "KthLargest", [k, nums], adds, lambda: ("add", [r.randint(-50, 50)]))


def _median_ops(r: random.Random, n: int, span: int) -> list[Any]:
    ops: list[str] = ["MedianFinder"]
    args: list[list[int]] = [[]]
    added = 0
    for _ in range(n):
        if added and r.random() < 0.4:
            ops.append("findMedian")
            args.append([])
        else:
            ops.append("addNum")
            args.append([r.randint(-span, span)])
            added += 1
    return [{"ops": ops, "args": args}]


def _wd_op(r: random.Random, alpha: str, maxlen: int) -> tuple[str, list[str]]:
    w = word(r, r.randint(1, maxlen), alpha)
    if r.random() < 0.5:
        return "addWord", [w]
    chars = list(w)
    for _ in range(r.randint(0, min(2, len(chars)))):
        chars[r.randrange(len(chars))] = "."
    return "search", ["".join(chars)]


def _word_board(r: random.Random, R: int, C: int, nwords: int, alpha: str) -> list[Any]:
    board = [[r.choice(alpha) for _ in range(C)] for _ in range(R)]
    words = set()
    for _ in range(nwords):
        if r.random() < 0.5:  # trace a random path so the word exists
            i, j = r.randrange(R), r.randrange(C)
            used = {(i, j)}
            w = board[i][j]
            for _ in range(r.randint(0, 9)):
                nxt = [
                    (x, y)
                    for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))
                    if 0 <= x < R and 0 <= y < C and (x, y) not in used
                ]
                if not nxt:
                    break
                i, j = r.choice(nxt)
                used.add((i, j))
                w += board[i][j]
            words.add(w)
        else:
            words.add(word(r, r.randint(1, 10), alpha))
    return [board, sorted(words)]


def _hits(r: random.Random, n: int) -> list[Any]:
    ops: list[str] = ["HitCounter"]
    args: list[list[int]] = [[]]
    t = r.randint(1, 10)
    for _ in range(n):
        t += r.choice([0, 0, 1, 5, 50, 150, 299, 300, 301])
        ops.append(r.choice(["hit", "hit", "getHits"]))
        args.append([t])
    return [{"ops": ops, "args": args}]


def _browser_op(r: random.Random, maxsteps: int) -> tuple[str, list[Any]]:
    op = r.choice(["visit", "back", "forward"])
    return op, [word(r, 3, "abc") + ".com"] if op == "visit" else [r.randint(1, maxsteps)]


def _snapshot(r: random.Random, length: int, n: int) -> list[Any]:
    ops: list[str] = ["SnapshotArray"]
    args: list[list[int]] = [[length]]
    snaps = 0
    for _ in range(n):
        op = r.choice(["set", "set", "snap", "get"] if snaps else ["set", "snap"])
        ops.append(op)
        if op == "set":
            args.append([r.randrange(length), r.randint(0, 100)])
        elif op == "snap":
            args.append([])
            snaps += 1
        else:
            args.append([r.randrange(length), r.randrange(snaps)])
    return [{"ops": ops, "args": args}]
