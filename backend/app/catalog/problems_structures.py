import random
from collections.abc import Callable
from typing import Any

from .base import Problem, distinct, ints, random_bst, random_tree, word

G, M = "google", "meta"

PROBLEMS = [
    # ---------------------------------------------------------------- linked lists
    Problem(
        slug="reverse-linked-list",
        title="Reverse Linked List",
        difficulty="Easy",
        pattern="linked-list",
        topics=["Linked List", "Recursion"],
        companies=[M, G],
        statement="Given the `head` of a singly linked list, reverse it and return the new head. Lists are shown as arrays, e.g. `[1,2,3]`.\n\nCan you do it both iteratively and recursively?",
        entry="reverseList",
        params=[("head", "Optional[ListNode]")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 2, 3, 4, 5]]}, {"args": [[1, 2]]}, {"args": [[]]}],
        constraints=["0 ≤ number of nodes ≤ 5000"],
        hints=["Walk the list keeping `prev`; point each node's `next` at `prev` before moving on."],
        reference="""
class Solution:
    def reverseList(self, head):
        prev = None
        while head:
            head.next, prev, head = prev, head, head.next
        return prev
""",
        gen=lambda r: [[[7]]] + [[ints(r, r.randint(0, 30), -100, 100)] for _ in range(15)] + [[list(range(5000))]],
    ),
    Problem(
        slug="merge-k-sorted-lists",
        title="Merge k Sorted Lists",
        difficulty="Hard",
        pattern="heap",
        topics=["Linked List", "Heap", "Divide and Conquer"],
        companies=[M, G],
        statement="You're given an array of `k` sorted linked lists. Merge them into one sorted linked list and return it.",
        entry="mergeKLists",
        params=[("lists", "List[Optional[ListNode]]")],
        returns="Optional[ListNode]",
        examples=[{"args": [[[1, 4, 5], [1, 3, 4], [2, 6]]]}, {"args": [[]]}, {"args": [[[]]]}],
        constraints=["0 ≤ k ≤ 10⁴", "Total nodes ≤ 10⁴"],
        hints=[
            "A min-heap of the current head of each list gives O(N log k).",
            "Tie-break heap entries by list index — ListNode isn't comparable.",
        ],
        reference="""
class Solution:
    def mergeKLists(self, lists):
        vals = []
        node_lists = lists
        for n in node_lists:
            while n:
                vals.append(n.val); n = n.next
        dummy = cur = ListNode()
        for v in sorted(vals):
            cur.next = ListNode(v); cur = cur.next
        return dummy.next
""",
        gen=lambda r: (
            [[[[], [1]]], [[[2], [], [1]]]]
            + [[[sorted(ints(r, r.randint(0, 8), -50, 50)) for _ in range(r.randint(0, 8))]] for _ in range(18)]
            + [[[sorted(ints(r, 10, -(10**4), 10**4)) for _ in range(1000)]]]
        ),
    ),
    Problem(
        slug="lru-cache",
        title="LRU Cache",
        difficulty="Medium",
        pattern="design",
        kind="design",
        topics=["Design", "Hash Table", "Linked List"],
        companies=[M, G],
        statement="Design a Least Recently Used cache.\n\n- `LRUCache(capacity)` creates the cache.\n- `get(key)` returns the value, or `-1` if the key is absent.\n- `put(key, value)` inserts or updates the key. If this pushes the size over `capacity`, evict the least recently used key.\n\nBoth `get` and `put` must run in O(1) on average.\n\nTests are a list of operations and their arguments; the output lists each call's return value (`None` for the constructor and `put`).",
        entry="LRUCache",
        params=[("operations", "List[str]"), ("arguments", "List[List[int]]")],
        returns="List",
        starter="""
class LRUCache:

    def __init__(self, capacity: int):
        

    def get(self, key: int) -> int:
        

    def put(self, key: int, value: int) -> None:
        
""",
        examples=[
            {
                "args": [
                    {
                        "ops": ["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"],
                        "args": [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]],
                    }
                ]
            }
        ],
        constraints=["1 ≤ capacity ≤ 3000", "At most 2 × 10⁵ calls"],
        hints=[
            "A dict gives O(1) lookup; a doubly linked list gives O(1) move-to-front and evict-from-back.",
            "In Python, `OrderedDict.move_to_end` and `popitem(last=False)` do the same job — but know how to build it yourself.",
        ],
        reference="""
class LRUCache:
    def __init__(self, capacity):
        self.c = capacity; self.d = OrderedDict()
    def get(self, key):
        if key not in self.d: return -1
        self.d.move_to_end(key); return self.d[key]
    def put(self, key, value):
        self.d[key] = value; self.d.move_to_end(key)
        if len(self.d) > self.c: self.d.popitem(last=False)
""",
        gen=lambda r: (
            [
                _ops_case(
                    r,
                    "LRUCache",
                    [r.randint(1, 4)],
                    r.randint(1, 30),
                    lambda: r.choice([("get", [r.randint(1, 6)]), ("put", [r.randint(1, 6), r.randint(0, 100)])]),
                )
                for _ in range(15)
            ]
            + [
                _ops_case(
                    r,
                    "LRUCache",
                    [1000],
                    50_000,
                    lambda: r.choice(
                        [("get", [r.randint(1, 3000)]), ("put", [r.randint(1, 3000), r.randint(0, 10**5)])]
                    ),
                )
            ]
        ),
    ),
    # ---------------------------------------------------------------- trees
    Problem(
        slug="binary-tree-level-order-traversal",
        title="Binary Tree Level Order Traversal",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "BFS"],
        companies=[M, G],
        statement="Return the node values of a binary tree level by level, left to right. Trees are shown in level order with `None` for missing children, e.g. `[3,9,20,None,None,15,7]`.",
        entry="levelOrder",
        params=[("root", "Optional[TreeNode]")],
        returns="List[List[int]]",
        examples=[{"args": [[3, 9, 20, None, None, 15, 7]]}, {"args": [[1]]}, {"args": [[]]}],
        constraints=["0 ≤ number of nodes ≤ 2000"],
        hints=["BFS with a queue; process exactly `len(queue)` nodes per level."],
        reference="""
class Solution:
    def levelOrder(self, root):
        res, q = [], deque([root] if root else [])
        while q:
            res.append([])
            for _ in range(len(q)):
                n = q.popleft(); res[-1].append(n.val)
                if n.left: q.append(n.left)
                if n.right: q.append(n.right)
        return res
""",
        gen=lambda r: (
            [[random_tree(r, ints(r, r.randint(0, 25), -100, 100))] for _ in range(18)]
            + [[random_tree(r, ints(r, 2000, -1000, 1000))]]
        ),
    ),
    Problem(
        slug="binary-tree-right-side-view",
        title="Binary Tree Right Side View",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "BFS", "DFS"],
        companies=[M],
        statement="Imagine standing to the right of a binary tree. Return the values you can see, from top to bottom.",
        entry="rightSideView",
        params=[("root", "Optional[TreeNode]")],
        returns="List[int]",
        examples=[
            {"args": [[1, 2, 3, None, 5, None, 4]]},
            {"args": [[1, 2, 3, 4, None, None, None, 5]]},
            {"args": [[]]},
        ],
        constraints=["0 ≤ number of nodes ≤ 100"],
        hints=[
            "It's the last node of each BFS level. Or DFS right-first, recording the first node seen at each depth."
        ],
        reference="""
class Solution:
    def rightSideView(self, root):
        res, q = [], deque([root] if root else [])
        while q:
            res.append(q[-1].val)
            for _ in range(len(q)):
                n = q.popleft()
                if n.left: q.append(n.left)
                if n.right: q.append(n.right)
        return res
""",
        gen=lambda r: [[random_tree(r, ints(r, r.randint(0, 40), 0, 100))] for _ in range(20)],
    ),
    Problem(
        slug="diameter-of-binary-tree",
        title="Diameter of Binary Tree",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "DFS"],
        companies=[M, G],
        statement="Return the length (number of edges) of the longest path between any two nodes of a binary tree. The path doesn't have to pass through the root.",
        entry="diameterOfBinaryTree",
        params=[("root", "Optional[TreeNode]")],
        returns="int",
        examples=[{"args": [[1, 2, 3, 4, 5]], "note": "Path 4 → 2 → 1 → 3 has 3 edges."}, {"args": [[1, 2]]}],
        constraints=["1 ≤ number of nodes ≤ 10⁴"],
        hints=[
            "At each node, the longest path through it = left height + right height. Return height upward, update a global best."
        ],
        reference="""
class Solution:
    def diameterOfBinaryTree(self, root):
        best = 0
        # iterative post-order to avoid recursion depth in the reference
        heights = {None: 0}; st = [(root, False)]
        while st:
            n, done = st.pop()
            if n is None: continue
            if done:
                l, r = heights[n.left], heights[n.right]
                best = max(best, l + r); heights[n] = 1 + max(l, r)
            else:
                st += [(n, True), (n.left, False), (n.right, False)]
        return best
""",
        gen=lambda r: (
            [[random_tree(r, ints(r, r.randint(1, 40), 0, 100))] for _ in range(18)]
            + [[random_tree(r, ints(r, 10_000, 0, 100))]]
        ),
    ),
    Problem(
        slug="validate-binary-search-tree",
        title="Validate Binary Search Tree",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "DFS", "Binary Search Tree"],
        companies=[M, G],
        statement="Return `True` if the binary tree is a valid BST: every node's left subtree holds only smaller values, its right subtree only larger values, and both subtrees are BSTs.",
        entry="isValidBST",
        params=[("root", "Optional[TreeNode]")],
        returns="bool",
        examples=[
            {"args": [[2, 1, 3]]},
            {"args": [[5, 1, 4, None, None, 3, 6]], "note": "4 is in the right subtree of 5 but is smaller."},
            {"args": [[5, 4, 6, None, None, 3, 7]]},
        ],
        constraints=["1 ≤ number of nodes ≤ 10⁴", "−2³¹ ≤ Node.val ≤ 2³¹ − 1"],
        hints=[
            "Checking only direct children isn't enough — pass down a (low, high) range.",
            "Or: an in-order traversal of a BST is strictly increasing.",
        ],
        reference="""
class Solution:
    def isValidBST(self, root):
        st, prev, n = [], None, root
        while st or n:
            while n:
                st.append(n); n = n.left
            n = st.pop()
            if prev is not None and n.val <= prev: return False
            prev = n.val; n = n.right
        return True
""",
        gen=lambda r: (
            [[[1, 1]], [[2147483647]], [[3, 1, 5, 0, 2, 4, 6, None, None, None, 3]]]
            + [[_maybe_break_bst(r, random_bst(r, r.randint(1, 30), -100, 100))] for _ in range(20)]
            + [[random_bst(r, 5000, -(10**6), 10**6)]]
        ),
    ),
    Problem(
        slug="lowest-common-ancestor-of-a-binary-tree",
        title="Lowest Common Ancestor of a Binary Tree",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "DFS"],
        companies=[M, G],
        statement="Given a binary tree with unique values and two nodes `p` and `q` in it, return their lowest common ancestor: the deepest node that has both as descendants (a node counts as a descendant of itself).\n\nIn tests, `p` and `q` are given by value and the output shows the subtree rooted at the node you return.",
        entry="lowestCommonAncestor",
        params=[("root", "TreeNode"), ("p", "TreeNode@0"), ("q", "TreeNode@0")],
        returns="TreeNode",
        examples=[
            {"args": [[3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 1]},
            {"args": [[3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 4]},
        ],
        constraints=["2 ≤ number of nodes ≤ 10⁵", "All values are unique", "p ≠ q, both exist in the tree"],
        hints=[
            "Recurse: if a subtree contains p or q, return what you found. The first node where both sides report a find is the answer."
        ],
        reference="""
class Solution:
    def lowestCommonAncestor(self, root, p, q):
        parent = {root: None}; st = [root]
        while st:
            n = st.pop()
            for c in (n.left, n.right):
                if c: parent[c] = n; st.append(c)
        anc = set()
        while p: anc.add(p); p = parent[p]
        while q not in anc: q = parent[q]
        return q
""",
        gen=lambda r: [
            (lambda vals: [random_tree(r, vals), *r.sample(vals, 2)])(distinct(r, r.randint(2, 40), 0, 500))
            for _ in range(20)
        ],
    ),
    # ---------------------------------------------------------------- heaps
    Problem(
        slug="kth-largest-element-in-an-array",
        title="Kth Largest Element in an Array",
        difficulty="Medium",
        pattern="heap",
        topics=["Array", "Heap", "Quickselect"],
        companies=[M, G],
        statement="Return the `k`-th largest element of `nums` (in sorted order, not the k-th distinct). Try to beat O(n log n).",
        entry="findKthLargest",
        params=[("nums", "List[int]"), ("k", "int")],
        returns="int",
        examples=[{"args": [[3, 2, 1, 5, 6, 4], 2]}, {"args": [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4]}],
        constraints=["1 ≤ k ≤ len(nums) ≤ 10⁵"],
        hints=[
            "A min-heap of size k keeps the k largest seen so far — its top is the answer.",
            "Quickselect gives O(n) on average.",
        ],
        reference="""
class Solution:
    def findKthLargest(self, nums, k):
        return sorted(nums)[-k]
""",
        gen=lambda r: (
            [(lambda a: [a, r.randint(1, len(a))])(ints(r, r.randint(1, 50), -20, 20)) for _ in range(20)]
            + [[ints(r, 100_000, -(10**4), 10**4), 50_000]]
        ),
    ),
    Problem(
        slug="k-closest-points-to-origin",
        title="K Closest Points to Origin",
        difficulty="Medium",
        pattern="heap",
        topics=["Array", "Heap", "Geometry"],
        companies=[M],
        statement="Given `points[i] = [x, y]` and an integer `k`, return the `k` points closest to the origin by Euclidean distance, in any order. In the tests the answer is unique.",
        entry="kClosest",
        params=[("points", "List[List[int]]"), ("k", "int")],
        returns="List[List[int]]",
        examples=[{"args": [[[1, 3], [-2, 2]], 1]}, {"args": [[[3, 3], [5, -1], [-2, 4]], 2]}],
        constraints=["1 ≤ k ≤ len(points) ≤ 10⁴", "−10⁴ ≤ x, y ≤ 10⁴"],
        hints=["Compare squared distances — no square roots needed.", "Max-heap of size k, or heapq.nsmallest."],
        reference="""
class Solution:
    def kClosest(self, points, k):
        return sorted(points, key=lambda p: p[0] * p[0] + p[1] * p[1])[:k]
""",
        gen=lambda r: [_closest_case(r, r.randint(1, 30), 50) for _ in range(20)] + [_closest_case(r, 10_000, 10_000)],
        compare="sorted",
    ),
    # ---------------------------------------------------------------- graphs
    Problem(
        slug="number-of-islands",
        title="Number of Islands",
        difficulty="Medium",
        pattern="graphs",
        topics=["Matrix", "BFS", "DFS", "Union Find"],
        companies=[G, M],
        statement='Given a grid of `"1"` (land) and `"0"` (water), return the number of islands. Islands connect horizontally and vertically, and everything outside the grid is water.',
        entry="numIslands",
        params=[("grid", "List[List[str]]")],
        returns="int",
        examples=[
            {
                "args": [
                    [
                        ["1", "1", "1", "1", "0"],
                        ["1", "1", "0", "1", "0"],
                        ["1", "1", "0", "0", "0"],
                        ["0", "0", "0", "0", "0"],
                    ]
                ]
            },
            {
                "args": [
                    [
                        ["1", "1", "0", "0", "0"],
                        ["1", "1", "0", "0", "0"],
                        ["0", "0", "1", "0", "0"],
                        ["0", "0", "0", "1", "1"],
                    ]
                ]
            },
        ],
        constraints=["1 ≤ rows, cols ≤ 300"],
        hints=["Each unvisited land cell starts a new island; flood-fill it (BFS or DFS) so you never count it again."],
        reference="""
class Solution:
    def numIslands(self, grid):
        R, C = len(grid), len(grid[0]); seen = set(); n = 0
        for i in range(R):
            for j in range(C):
                if grid[i][j] == '1' and (i, j) not in seen:
                    n += 1; st = [(i, j)]; seen.add((i, j))
                    while st:
                        a, b = st.pop()
                        for x, y in ((a+1, b), (a-1, b), (a, b+1), (a, b-1)):
                            if 0 <= x < R and 0 <= y < C and grid[x][y] == '1' and (x, y) not in seen:
                                seen.add((x, y)); st.append((x, y))
        return n
""",
        gen=lambda r: (
            [[[["0"]]], [[["1"]]]]
            + [[_grid(r, r.randint(1, 15), r.randint(1, 15), "10", 0.45)] for _ in range(18)]
            + [[_grid(r, 300, 300, "10", 0.55)]]
        ),
    ),
    Problem(
        slug="rotting-oranges",
        title="Rotting Oranges",
        difficulty="Medium",
        pattern="graphs",
        topics=["Matrix", "BFS"],
        companies=[G, M],
        statement="In the grid, `0` is empty, `1` a fresh orange and `2` a rotten one. Each minute, fresh oranges next to a rotten one (4 directions) rot. Return the minutes until no fresh orange remains, or `-1` if that never happens.",
        entry="orangesRotting",
        params=[("grid", "List[List[int]]")],
        returns="int",
        examples=[
            {"args": [[[2, 1, 1], [1, 1, 0], [0, 1, 1]]]},
            {"args": [[[2, 1, 1], [0, 1, 1], [1, 0, 1]]]},
            {"args": [[[0, 2]]]},
        ],
        constraints=["1 ≤ rows, cols ≤ 10"],
        hints=["Multi-source BFS: start the queue with every rotten orange at once, one level per minute."],
        reference="""
class Solution:
    def orangesRotting(self, grid):
        g = [row[:] for row in grid]; R, C = len(g), len(g[0])
        q = deque((i, j) for i in range(R) for j in range(C) if g[i][j] == 2)
        fresh = sum(row.count(1) for row in g); t = 0
        while q and fresh:
            t += 1
            for _ in range(len(q)):
                a, b = q.popleft()
                for x, y in ((a+1, b), (a-1, b), (a, b+1), (a, b-1)):
                    if 0 <= x < R and 0 <= y < C and g[x][y] == 1:
                        g[x][y] = 2; fresh -= 1; q.append((x, y))
        return -1 if fresh else t
""",
        gen=lambda r: (
            [[[[0]]], [[[1]]], [[[2]]]] + [[_int_grid(r, r.randint(1, 10), r.randint(1, 10))] for _ in range(22)]
        ),
    ),
    Problem(
        slug="course-schedule",
        title="Course Schedule",
        difficulty="Medium",
        pattern="graphs",
        topics=["Graph", "Topological Sort", "DFS", "BFS"],
        companies=[G, M],
        statement="There are `numCourses` courses labelled `0` to `numCourses − 1`. `prerequisites[i] = [a, b]` means you must take `b` before `a`. Return `True` if you can finish every course.",
        entry="canFinish",
        params=[("numCourses", "int"), ("prerequisites", "List[List[int]]")],
        returns="bool",
        examples=[{"args": [2, [[1, 0]]]}, {"args": [2, [[1, 0], [0, 1]]]}],
        constraints=["1 ≤ numCourses ≤ 2000", "0 ≤ len(prerequisites) ≤ 5000", "All pairs are distinct"],
        hints=[
            "It's possible exactly when the directed graph has no cycle.",
            "Kahn's algorithm: repeatedly take courses with in-degree 0 and count them.",
        ],
        reference="""
class Solution:
    def canFinish(self, n, pre):
        g = defaultdict(list); indeg = [0] * n
        for a, b in pre:
            g[b].append(a); indeg[a] += 1
        q = deque(i for i in range(n) if indeg[i] == 0); done = 0
        while q:
            x = q.popleft(); done += 1
            for y in g[x]:
                indeg[y] -= 1
                if indeg[y] == 0: q.append(y)
        return done == n
""",
        gen=lambda r: (
            [[1, []], [3, [[1, 0], [2, 1], [0, 2]]], [3, [[0, 0]]]]
            + [_course_case(r, r.randint(2, 20), r.random() < 0.5) for _ in range(20)]
            + [_course_case(r, 2000, False), _course_case(r, 2000, True)]
        ),
    ),
    Problem(
        slug="word-ladder",
        title="Word Ladder",
        difficulty="Hard",
        pattern="graphs",
        topics=["BFS", "Hash Table", "String"],
        companies=[G, M],
        statement="Transform `beginWord` into `endWord` by changing one letter at a time; every intermediate word must be in `wordList` (`beginWord` itself need not be). Return the number of words in the shortest sequence, including both ends, or `0` if impossible.",
        entry="ladderLength",
        params=[("beginWord", "str"), ("endWord", "str"), ("wordList", "List[str]")],
        returns="int",
        examples=[
            {"args": ["hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]], "note": "hit → hot → dot → dog → cog"},
            {"args": ["hit", "cog", ["hot", "dot", "dog", "lot", "log"]]},
        ],
        constraints=["1 ≤ len(beginWord) ≤ 10", "1 ≤ len(wordList) ≤ 5000", "All words have the same length"],
        hints=[
            "BFS over words. Generating neighbours by trying all 26 letters per position beats comparing every pair.",
            "Bucketing by wildcard patterns like `h*t` is another fast option.",
        ],
        reference="""
class Solution:
    def ladderLength(self, begin, end, words):
        ws = set(words)
        if end not in ws: return 0
        q = deque([(begin, 1)]); seen = {begin}
        while q:
            w, d = q.popleft()
            if w == end: return d
            for i in range(len(w)):
                for c in 'abcdefghijklmnopqrstuvwxyz':
                    nw = w[:i] + c + w[i+1:]
                    if nw in ws and nw not in seen:
                        seen.add(nw); q.append((nw, d + 1))
        return 0
""",
        gen=lambda r: (
            [_ladder_case(r, 3, "abcd", r.randint(5, 40)) for _ in range(18)] + [_ladder_case(r, 5, "abcdef", 5000)]
        ),
    ),
    # ---------------------------------------------------------------- backtracking
    Problem(
        slug="subsets",
        title="Subsets",
        difficulty="Medium",
        pattern="backtracking",
        topics=["Array", "Backtracking", "Bit Manipulation"],
        companies=[M, G],
        statement="Given an array of **distinct** integers, return all possible subsets (the power set), in any order, without duplicates.",
        entry="subsets",
        params=[("nums", "List[int]")],
        returns="List[List[int]]",
        examples=[{"args": [[1, 2, 3]]}, {"args": [[0]]}],
        constraints=["1 ≤ len(nums) ≤ 10"],
        hints=["For each element, branch on include vs. exclude."],
        reference="""
class Solution:
    def subsets(self, nums):
        res = [[]]
        for x in nums:
            res += [s + [x] for s in res]
        return res
""",
        gen=lambda r: [[distinct(r, r.randint(1, 10), -10, 10)] for _ in range(12)],
        compare="nested_sorted",
    ),
    Problem(
        slug="permutations",
        title="Permutations",
        difficulty="Medium",
        pattern="backtracking",
        topics=["Array", "Backtracking"],
        companies=[M, G],
        statement="Given an array of **distinct** integers, return all its permutations, in any order.",
        entry="permute",
        params=[("nums", "List[int]")],
        returns="List[List[int]]",
        examples=[{"args": [[1, 2, 3]]}, {"args": [[0, 1]]}],
        constraints=["1 ≤ len(nums) ≤ 7"],
        hints=[
            "Build the permutation position by position, choosing from unused numbers, and undo the choice when you return."
        ],
        reference="""
class Solution:
    def permute(self, nums):
        return [list(p) for p in permutations(nums)]
""",
        gen=lambda r: [[distinct(r, r.randint(1, 7), -10, 10)] for _ in range(10)],
        compare="sorted",
    ),
    Problem(
        slug="combination-sum",
        title="Combination Sum",
        difficulty="Medium",
        pattern="backtracking",
        topics=["Array", "Backtracking"],
        companies=[G, M],
        statement="Given distinct positive `candidates` and a `target`, return every unique combination of candidates that sums to `target`. A number may be used any number of times. Combinations may be returned in any order.",
        entry="combinationSum",
        params=[("candidates", "List[int]"), ("target", "int")],
        returns="List[List[int]]",
        examples=[{"args": [[2, 3, 6, 7], 7]}, {"args": [[2, 3, 5], 8]}, {"args": [[2], 1]}],
        constraints=["1 ≤ len(candidates) ≤ 30", "2 ≤ candidates[i] ≤ 40", "1 ≤ target ≤ 40"],
        hints=[
            "Recurse with a start index so each combination is built in non-decreasing order — that removes duplicates.",
            "Stop a branch as soon as the remaining target goes negative.",
        ],
        reference="""
class Solution:
    def combinationSum(self, cands, target):
        cands = sorted(cands); res = []
        def go(start, rem, path):
            if rem == 0: res.append(path[:]); return
            for i in range(start, len(cands)):
                if cands[i] > rem: break
                path.append(cands[i]); go(i, rem - cands[i], path); path.pop()
        go(0, target, [])
        return res
""",
        gen=lambda r: [[distinct(r, r.randint(1, 6), 2, 20), r.randint(1, 30)] for _ in range(18)],
        compare="nested_sorted",
    ),
    Problem(
        slug="word-search",
        title="Word Search",
        difficulty="Medium",
        pattern="backtracking",
        topics=["Matrix", "Backtracking", "DFS"],
        companies=[M, G],
        statement="Given a grid of letters `board` and a string `word`, return `True` if `word` can be spelled by moving between horizontally or vertically adjacent cells, using each cell at most once.",
        entry="exist",
        params=[("board", "List[List[str]]"), ("word", "str")],
        returns="bool",
        examples=[
            {"args": [[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED"]},
            {"args": [[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCB"]},
        ],
        constraints=["1 ≤ rows, cols ≤ 6", "1 ≤ len(word) ≤ 15"],
        hints=["DFS from every cell; mark the cell as used while exploring and unmark it when backtracking."],
        reference="""
class Solution:
    def exist(self, board, word):
        R, C = len(board), len(board[0])
        def dfs(i, j, k):
            if k == len(word): return True
            if not (0 <= i < R and 0 <= j < C) or board[i][j] != word[k]: return False
            ch = board[i][j]; board[i][j] = '#'
            ok = dfs(i+1, j, k+1) or dfs(i-1, j, k+1) or dfs(i, j+1, k+1) or dfs(i, j-1, k+1)
            board[i][j] = ch
            return ok
        return any(dfs(i, j, 0) for i in range(R) for j in range(C))
""",
        gen=lambda r: [_word_search_case(r) for _ in range(20)] + [[[["A"] * 6 for _ in range(6)], "A" * 11 + "B"]],
    ),
    # ---------------------------------------------------------------- dynamic programming
    Problem(
        slug="climbing-stairs",
        title="Climbing Stairs",
        difficulty="Easy",
        pattern="dynamic-programming",
        topics=["Math", "Dynamic Programming", "Memoization"],
        companies=[G],
        statement="A staircase has `n` steps and you climb 1 or 2 steps at a time. How many distinct ways can you reach the top?",
        entry="climbStairs",
        params=[("n", "int")],
        returns="int",
        examples=[{"args": [2]}, {"args": [3]}],
        constraints=["1 ≤ n ≤ 45"],
        hints=["ways(n) = ways(n − 1) + ways(n − 2). You only need the last two values."],
        reference="""
class Solution:
    def climbStairs(self, n):
        a = b = 1
        for _ in range(n - 1): a, b = b, a + b
        return b
""",
        gen=lambda r: [[1], [4], [10], [30], [44], [45]] + [[r.randint(1, 45)] for _ in range(6)],
    ),
    Problem(
        slug="house-robber",
        title="House Robber",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming"],
        companies=[G],
        statement="`nums[i]` is the money in house `i` along a street. You can't rob two adjacent houses. Return the maximum amount you can rob.",
        entry="rob",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[1, 2, 3, 1]]}, {"args": [[2, 7, 9, 3, 1]]}],
        constraints=["1 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 400"],
        hints=["best(i) = max(best(i − 1), best(i − 2) + nums[i])."],
        reference="""
class Solution:
    def rob(self, nums):
        a = b = 0
        for x in nums: a, b = b, max(b, a + x)
        return b
""",
        gen=lambda r: [[[5]], [[2, 1]], [[2, 1, 1, 2]]] + [[ints(r, r.randint(1, 100), 0, 400)] for _ in range(15)],
    ),
    Problem(
        slug="coin-change",
        title="Coin Change",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming", "BFS"],
        companies=[G, M],
        statement="Given coin denominations `coins` (unlimited supply) and an `amount`, return the fewest coins that make up exactly `amount`, or `-1` if it can't be done.",
        entry="coinChange",
        params=[("coins", "List[int]"), ("amount", "int")],
        returns="int",
        examples=[{"args": [[1, 2, 5], 11]}, {"args": [[2], 3]}, {"args": [[1], 0]}],
        constraints=["1 ≤ len(coins) ≤ 12", "0 ≤ amount ≤ 10⁴"],
        hints=["Greedy fails for coins [1, 3, 4] and amount 6.", "dp[x] = 1 + min(dp[x − c]) over coins c."],
        reference="""
class Solution:
    def coinChange(self, coins, amount):
        dp = [0] + [inf] * amount
        for x in range(1, amount + 1):
            for c in coins:
                if c <= x and dp[x - c] + 1 < dp[x]: dp[x] = dp[x - c] + 1
        return -1 if dp[amount] == inf else dp[amount]
""",
        gen=lambda r: (
            [[[1, 3, 4], 6], [[186, 419, 83, 408], 6249], [[3, 7], 1], [[5], 0]]
            + [[distinct(r, r.randint(1, 5), 1, 50), r.randint(0, 800)] for _ in range(16)]
            + [[[7, 13, 29, 101], 10_000]]
        ),
    ),
    Problem(
        slug="longest-increasing-subsequence",
        title="Longest Increasing Subsequence",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming", "Binary Search"],
        companies=[G, M],
        statement="Return the length of the longest strictly increasing subsequence of `nums`.\n\nO(n²) DP is the classic answer; O(n log n) is the follow-up.",
        entry="lengthOfLIS",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[
            {"args": [[10, 9, 2, 5, 3, 7, 101, 18]], "note": "[2, 3, 7, 101]"},
            {"args": [[0, 1, 0, 3, 2, 3]]},
            {"args": [[7, 7, 7, 7]]},
        ],
        constraints=["1 ≤ len(nums) ≤ 2500", "−10⁴ ≤ nums[i] ≤ 10⁴"],
        hints=[
            "dp[i] = longest increasing subsequence ending at i.",
            "Patience sorting: keep `tails[k]` = smallest tail of an increasing subsequence of length k + 1, and binary search it.",
        ],
        reference="""
class Solution:
    def lengthOfLIS(self, nums):
        tails = []
        for x in nums:
            i = bisect_left(tails, x)
            if i == len(tails): tails.append(x)
            else: tails[i] = x
        return len(tails)
""",
        gen=lambda r: (
            [[[1]], [[3, 2, 1]]]
            + [[ints(r, r.randint(1, 60), -20, 20)] for _ in range(16)]
            + [[ints(r, 2500, -(10**4), 10**4)]]
        ),
    ),
    Problem(
        slug="word-break",
        title="Word Break",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["String", "Dynamic Programming", "Trie"],
        companies=[M, G],
        statement="Return `True` if string `s` can be split into a sequence of one or more words from `wordDict`. Words can be reused.",
        entry="wordBreak",
        params=[("s", "str"), ("wordDict", "List[str]")],
        returns="bool",
        examples=[
            {"args": ["leetcode", ["leet", "code"]]},
            {"args": ["applepenapple", ["apple", "pen"]]},
            {"args": ["catsandog", ["cats", "dog", "sand", "and", "cat"]]},
        ],
        constraints=["1 ≤ len(s) ≤ 300", "1 ≤ len(wordDict) ≤ 1000", "Words are unique"],
        hints=[
            "ok[i] = True if s[:i] can be segmented. ok[i] is True if some word ends at i and ok[i − len(word)] is True."
        ],
        reference="""
class Solution:
    def wordBreak(self, s, words):
        ws = set(words); lens = {len(w) for w in ws}
        ok = [True] + [False] * len(s)
        for i in range(1, len(s) + 1):
            ok[i] = any(L <= i and ok[i - L] and s[i - L:i] in ws for L in lens)
        return ok[-1]
""",
        gen=lambda r: (
            [_word_break_case(r) for _ in range(20)]
            + [["a" * 299 + "b", ["a", "aa", "aaa", "aaaa", "aaaaa", "aaaaaa"]]]
        ),
    ),
    Problem(
        slug="decode-ways",
        title="Decode Ways",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["String", "Dynamic Programming"],
        companies=[M, G],
        statement='Letters are encoded as numbers: `A → "1"`, …, `Z → "26"`. Given a digit string `s`, return how many ways it can be decoded. Codes with leading zeros like `"06"` are invalid.',
        entry="numDecodings",
        params=[("s", "str")],
        returns="int",
        examples=[{"args": ["12"], "note": '"AB" or "L".'}, {"args": ["226"]}, {"args": ["06"]}],
        constraints=["1 ≤ len(s) ≤ 100"],
        hints=["ways(i) = ways(i − 1) if s[i − 1] ≠ '0', plus ways(i − 2) if s[i−2:i] is between 10 and 26."],
        reference="""
class Solution:
    def numDecodings(self, s):
        a, b = 1, (1 if s[0] != '0' else 0)
        for i in range(2, len(s) + 1):
            c = (b if s[i-1] != '0' else 0) + (a if 10 <= int(s[i-2:i]) <= 26 else 0)
            a, b = b, c
        return b
""",
        gen=lambda r: (
            [["0"], ["10"], ["100"], ["2101"], ["27"], ["1111111111"]]
            + [[word(r, r.randint(1, 100), "0112223456")] for _ in range(18)]
            + [["1" * 100]]
        ),
    ),
    Problem(
        slug="edit-distance",
        title="Edit Distance",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["String", "Dynamic Programming"],
        companies=[G],
        statement="Return the minimum number of single-character inserts, deletes or replacements needed to turn `word1` into `word2`.",
        entry="minDistance",
        params=[("word1", "str"), ("word2", "str")],
        returns="int",
        examples=[{"args": ["horse", "ros"]}, {"args": ["intention", "execution"]}],
        constraints=["0 ≤ len(word1), len(word2) ≤ 500"],
        hints=[
            "dp[i][j] = cost for prefixes word1[:i], word2[:j]. If the last chars match, it's dp[i−1][j−1]; otherwise 1 + min of the three neighbours."
        ],
        reference="""
class Solution:
    def minDistance(self, a, b):
        prev = list(range(len(b) + 1))
        for i in range(1, len(a) + 1):
            cur = [i] + [0] * len(b)
            for j in range(1, len(b) + 1):
                cur[j] = prev[j-1] if a[i-1] == b[j-1] else 1 + min(prev[j-1], prev[j], cur[j-1])
            prev = cur
        return prev[-1]
""",
        gen=lambda r: (
            [["", ""], ["", "abc"], ["abc", ""], ["same", "same"]]
            + [[word(r, r.randint(0, 30), "abcd"), word(r, r.randint(0, 30), "abcd")] for _ in range(16)]
            + [[word(r, 500, "abcde"), word(r, 500, "abcde")]]
        ),
    ),
    Problem(
        slug="longest-palindromic-substring",
        title="Longest Palindromic Substring",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["String", "Dynamic Programming", "Two Pointers"],
        companies=[M, G],
        statement="Return the longest palindromic substring of `s`. If several have the maximum length, any of them is accepted.",
        entry="longestPalindrome",
        params=[("s", "str")],
        returns="str",
        examples=[{"args": ["babad"], "note": '"aba" is also accepted.'}, {"args": ["cbbd"]}],
        constraints=["1 ≤ len(s) ≤ 1000"],
        hints=[
            "Every palindrome has a centre: a character or a gap between two characters. Expand outward from each of the 2n − 1 centres."
        ],
        reference="""
class Solution:
    def longestPalindrome(self, s):
        best = s[0]
        for c in range(2 * len(s) - 1):
            l, r = c // 2, (c + 1) // 2
            while l >= 0 and r < len(s) and s[l] == s[r]: l -= 1; r += 1
            if r - l - 1 > len(best): best = s[l+1:r]
        return best
""",
        gen=lambda r: (
            [["a"], ["ac"], ["aaaa"], ["abacdfgdcaba"]]
            + [[word(r, r.randint(1, 60), "ab"[: r.randint(1, 2)] + "c" * r.randint(0, 1))] for _ in range(16)]
            + [[word(r, 1000, "ab")]]
        ),
        compare="palindrome",
    ),
    # ---------------------------------------------------------------- design + trie
    Problem(
        slug="time-based-key-value-store",
        title="Time Based Key-Value Store",
        difficulty="Medium",
        pattern="design",
        kind="design",
        topics=["Design", "Hash Table", "Binary Search"],
        companies=[G],
        statement='Design `TimeMap`:\n\n- `set(key, value, timestamp)` stores the value at that time.\n- `get(key, timestamp)` returns the value set for `key` at the largest timestamp ≤ `timestamp`, or `""` if there is none.\n\nTimestamps passed to `set` are strictly increasing.',
        entry="TimeMap",
        params=[("operations", "List[str]"), ("arguments", "List[list]")],
        returns="List",
        starter="""
class TimeMap:

    def __init__(self):
        

    def set(self, key: str, value: str, timestamp: int) -> None:
        

    def get(self, key: str, timestamp: int) -> str:
        
""",
        examples=[
            {
                "args": [
                    {
                        "ops": ["TimeMap", "set", "get", "get", "set", "get", "get"],
                        "args": [
                            [],
                            ["foo", "bar", 1],
                            ["foo", 1],
                            ["foo", 3],
                            ["foo", "bar2", 4],
                            ["foo", 4],
                            ["foo", 5],
                        ],
                    }
                ]
            }
        ],
        constraints=["At most 2 × 10⁵ calls", "1 ≤ timestamp ≤ 10⁷"],
        hints=[
            "Per key, keep (timestamp, value) pairs — already sorted because timestamps increase. Binary search on get."
        ],
        reference="""
class TimeMap:
    def __init__(self):
        self.d = defaultdict(list)
    def set(self, key, value, timestamp):
        self.d[key].append((timestamp, value))
    def get(self, key, timestamp):
        arr = self.d.get(key, [])
        i = bisect_right(arr, (timestamp, chr(0x10FFFF)))
        return arr[i - 1][1] if i else ""
""",
        gen=lambda r: [_timemap_case(r, r.randint(2, 30), 3) for _ in range(14)] + [_timemap_case(r, 50_000, 50)],
    ),
    Problem(
        slug="implement-trie-prefix-tree",
        title="Implement Trie (Prefix Tree)",
        difficulty="Medium",
        pattern="trie",
        kind="design",
        topics=["Design", "Trie", "String"],
        companies=[G, M],
        statement="Implement a `Trie`:\n\n- `insert(word)` adds a word.\n- `search(word)` returns `True` if the exact word was inserted.\n- `startsWith(prefix)` returns `True` if any inserted word starts with `prefix`.",
        entry="Trie",
        params=[("operations", "List[str]"), ("arguments", "List[List[str]]")],
        returns="List",
        starter="""
class Trie:

    def __init__(self):
        

    def insert(self, word: str) -> None:
        

    def search(self, word: str) -> bool:
        

    def startsWith(self, prefix: str) -> bool:
        
""",
        examples=[
            {
                "args": [
                    {
                        "ops": ["Trie", "insert", "search", "search", "startsWith", "insert", "search"],
                        "args": [[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]],
                    }
                ]
            }
        ],
        constraints=["1 ≤ len(word), len(prefix) ≤ 2000", "At most 3 × 10⁴ calls"],
        hints=["Each node holds a dict of children and an end-of-word flag."],
        reference="""
class Trie:
    def __init__(self):
        self.words = set(); self.prefixes = set()
    def insert(self, word):
        self.words.add(word)
        for i in range(1, len(word) + 1): self.prefixes.add(word[:i])
    def search(self, word):
        return word in self.words
    def startsWith(self, prefix):
        return prefix in self.prefixes
""",
        gen=lambda r: (
            [
                _ops_case(
                    r,
                    "Trie",
                    [],
                    r.randint(3, 40),
                    lambda: (r.choice(["insert", "insert", "search", "startsWith"]), [word(r, r.randint(1, 4), "abc")]),
                )
                for _ in range(14)
            ]
            + [
                _ops_case(
                    r,
                    "Trie",
                    [],
                    30_000,
                    lambda: (r.choice(["insert", "search", "startsWith"]), [word(r, r.randint(1, 12), "abcde")]),
                )
            ]
        ),
    ),
]


# ---------------------------------------------------------------- private generator helpers
def _ops_case(
    r: random.Random, cls: str, ctor_args: list[Any], n: int, make: Callable[[], tuple[str, list[Any]]]
) -> list[Any]:
    ops, args = [cls], [ctor_args]
    for _ in range(n):
        op, a = make()
        ops.append(op)
        args.append(a)
    return [{"ops": ops, "args": args}]


def _timemap_case(r: random.Random, n: int, nkeys: int) -> list[Any]:
    keys = [word(r, 3, "abc") for _ in range(nkeys)]
    ops = ["TimeMap"]
    args: list[list[Any]] = [[]]
    t = 0
    for _ in range(n):
        if r.random() < 0.5:
            t += r.randint(1, 5)
            ops.append("set")
            args.append([r.choice(keys), word(r, 4, "xyz"), t])
        else:
            ops.append("get")
            args.append([r.choice(keys), r.randint(1, t + 5)])
    return [{"ops": ops, "args": args}]


def _maybe_break_bst(r: random.Random, tree: list[int | None]) -> list[int | None]:
    if len(tree) > 1 and r.random() < 0.5:
        idx = [i for i, v in enumerate(tree) if v is not None]
        i = r.choice(idx)
        tree = tree[:]
        value = tree[i]
        assert value is not None
        tree[i] = value + r.choice([-3, -1, 1, 3])
    return tree


def _closest_case(r: random.Random, n: int, span: int) -> list[Any]:
    seen: set[int] = set()
    pts: list[list[int]] = []
    while len(pts) < n:
        p = [r.randint(-span, span), r.randint(-span, span)]
        d = p[0] ** 2 + p[1] ** 2
        if d not in seen:
            seen.add(d)
            pts.append(p)
    return [pts, r.randint(1, n)]


def _grid(r: random.Random, R: int, C: int, alphabet: str, density: float) -> list[list[str]]:
    return [[alphabet[0] if r.random() < density else alphabet[1] for _ in range(C)] for _ in range(R)]


def _int_grid(r: random.Random, R: int, C: int) -> list[list[int]]:
    return [[r.choice([0, 1, 1, 1, 2]) for _ in range(C)] for _ in range(R)]


def _course_case(r: random.Random, n: int, cyclic: bool) -> list[Any]:
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


def _ladder_case(r: random.Random, L: int, alpha: str, n: int) -> list[Any]:
    words = list({word(r, L, alpha) for _ in range(n)})
    begin = word(r, L, alpha)
    end = r.choice(words) if r.random() < 0.8 else word(r, L, alpha)
    return [begin, end, words]


def _word_search_case(r: random.Random) -> list[Any]:
    R, C = r.randint(1, 5), r.randint(1, 5)
    board = [[r.choice("ABCE") for _ in range(C)] for _ in range(R)]
    if r.random() < 0.6:  # walk a random path so the word exists
        i, j = r.randrange(R), r.randrange(C)
        used = {(i, j)}
        w = board[i][j]
        for _ in range(r.randint(0, 8)):
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
        return [board, w]
    return [board, word(r, r.randint(1, 8), "ABCE")]


def _word_break_case(r: random.Random) -> list[Any]:
    words = list({word(r, r.randint(1, 4), "abc") for _ in range(r.randint(1, 8))})
    s = "".join(r.choice(words) for _ in range(r.randint(1, 12)))
    if r.random() < 0.4:
        i = r.randrange(len(s) + 1)
        s = s[:i] + r.choice("abcd") + s[i:]
    return [s[:300], words]
