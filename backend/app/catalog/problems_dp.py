import random
from typing import Any

from .base import Problem, distinct, ints, word

G, M = "google", "meta"

PROBLEMS = [
    Problem(
        slug="min-cost-climbing-stairs",
        title="Min Cost Climbing Stairs",
        difficulty="Easy",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming"],
        companies=[G, M],
        statement="`cost[i]` is the price of stepping on stair `i`. After paying, you can climb one or two stairs. You may start on stair 0 or stair 1. Return the minimum cost to reach the top, just past the last stair.",
        entry="minCostClimbingStairs",
        params=[("cost", "List[int]")],
        returns="int",
        examples=[{"args": [[10, 15, 20]]}, {"args": [[1, 100, 1, 1, 1, 100, 1, 1, 100, 1]]}],
        constraints=["2 ≤ len(cost) ≤ 1000", "0 ≤ cost[i] ≤ 999"],
        hints=[
            "best(i) = cost[i] + min(best(i − 1), best(i − 2)). The top is reached from either of the last two stairs."
        ],
        reference="""
class Solution:
    def minCostClimbingStairs(self, cost):
        a = b = 0
        for c in cost: a, b = b, c + min(a, b)
        return min(a, b)
""",
        gen=lambda r: [[ints(r, r.randint(2, 15), 0, 20)] for _ in range(18)] + [[ints(r, 1000, 0, 999)]],
    ),
    Problem(
        slug="house-robber-ii",
        title="House Robber II",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming"],
        companies=[G, M],
        statement="Houses are arranged in a **circle**, so the first and last are neighbours. `nums[i]` is the money in house `i`. You can't rob two adjacent houses. Return the most money you can rob.",
        entry="rob",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[2, 3, 2]]}, {"args": [[1, 2, 3, 1]]}, {"args": [[1, 2, 3]]}],
        constraints=["1 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 1000"],
        hints=[
            "You can't take both the first and the last house. Run House Robber on nums[1:] and on nums[:-1]; take the better."
        ],
        reference="""
class Solution:
    def rob(self, nums):
        def line(a):
            x = y = 0
            for v in a: x, y = y, max(y, x + v)
            return y
        return nums[0] if len(nums) == 1 else max(line(nums[1:]), line(nums[:-1]))
""",
        gen=lambda r: (
            [[[5]], [[1, 9]]] + [[ints(r, r.randint(1, 12), 0, 20)] for _ in range(18)] + [[ints(r, 100, 0, 1000)]]
        ),
    ),
    Problem(
        slug="maximum-subarray",
        title="Maximum Subarray",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Array", "Divide and Conquer", "Dynamic Programming"],
        companies=[G, M],
        statement="Return the largest sum of a non-empty contiguous subarray of `nums`.",
        entry="maxSubArray",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[
            {"args": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "note": "[4, -1, 2, 1] sums to 6."},
            {"args": [[1]]},
            {"args": [[5, 4, -1, 7, 8]]},
        ],
        constraints=["1 ≤ len(nums) ≤ 10⁵", "−10⁴ ≤ nums[i] ≤ 10⁴"],
        hints=[
            "Kadane: the best subarray ending here either extends the previous one or starts fresh — whichever is larger."
        ],
        reference="""
class Solution:
    def maxSubArray(self, nums):
        best = cur = nums[0]
        for x in nums[1:]:
            cur = max(x, cur + x); best = max(best, cur)
        return best
""",
        gen=lambda r: (
            [[[-3]], [[-2, -1]]]
            + [[ints(r, r.randint(1, 30), -10, 10)] for _ in range(18)]
            + [[ints(r, 100_000, -(10**4), 10**4)]]
        ),
    ),
    Problem(
        slug="maximum-product-subarray",
        title="Maximum Product Subarray",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming"],
        companies=[G, M],
        statement="Return the largest product of a non-empty contiguous subarray of `nums`. The answer fits in a 32-bit integer.",
        entry="maxProduct",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[2, 3, -2, 4]]}, {"args": [[-2, 0, -1]]}],
        constraints=["1 ≤ len(nums) ≤ 2 × 10⁴", "−10 ≤ nums[i] ≤ 10"],
        hints=[
            "A negative number swaps the biggest and smallest products. Track both the max and min product ending at each index."
        ],
        reference="""
class Solution:
    def maxProduct(self, nums):
        best = hi = lo = nums[0]
        for x in nums[1:]:
            hi, lo = max(x, hi * x, lo * x), min(x, hi * x, lo * x)
            best = max(best, hi)
        return best
""",
        gen=lambda r: (
            [[[-2]], [[0, 2]], [[-2, 3, -4]]]
            + [[ints(r, r.randint(1, 12), -5, 5)] for _ in range(17)]
            + [[_small_products(r, 20_000)]]
        ),
    ),
    Problem(
        slug="palindromic-substrings",
        title="Palindromic Substrings",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Two Pointers", "String", "Dynamic Programming"],
        companies=[M, G],
        statement="Return the number of palindromic substrings of `s`. Substrings at different positions count separately even if they're equal.",
        entry="countSubstrings",
        params=[("s", "str")],
        returns="int",
        examples=[{"args": ["abc"]}, {"args": ["aaa"], "note": "a, a, a, aa, aa, aaa."}],
        constraints=["1 ≤ len(s) ≤ 1000"],
        hints=[
            "Expand around each of the 2n − 1 centres (a letter or a gap between letters), counting as long as both ends match."
        ],
        reference="""
class Solution:
    def countSubstrings(self, s):
        n, total = len(s), 0
        for c in range(2 * n - 1):
            l, r = c // 2, (c + 1) // 2
            while l >= 0 and r < n and s[l] == s[r]:
                total += 1; l -= 1; r += 1
        return total
""",
        gen=lambda r: [[word(r, r.randint(1, 20), "ab")] for _ in range(18)] + [["a" * 1000], [word(r, 1000, "abc")]],
    ),
    Problem(
        slug="partition-equal-subset-sum",
        title="Partition Equal Subset Sum",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming"],
        companies=[G, M],
        statement="Return `True` if `nums` can be split into two subsets with equal sums.",
        entry="canPartition",
        params=[("nums", "List[int]")],
        returns="bool",
        examples=[{"args": [[1, 5, 11, 5]]}, {"args": [[1, 2, 3, 5]]}],
        constraints=["1 ≤ len(nums) ≤ 200", "1 ≤ nums[i] ≤ 100"],
        hints=[
            "It's subset sum to total / 2. Keep the set of reachable sums (or a boolean array), adding each number once."
        ],
        reference="""
class Solution:
    def canPartition(self, nums):
        total = sum(nums)
        if total % 2: return False
        reach = 1
        for x in nums: reach |= reach << x
        return bool(reach >> (total // 2) & 1)
""",
        gen=lambda r: (
            [[[1]], [[2, 2]], [[100, 100, 100, 100, 100, 100, 100, 100, 100, 99, 1]]]
            + [[ints(r, r.randint(1, 12), 1, 20)] for _ in range(17)]
            + [[ints(r, 200, 1, 100)], [[r.choice([3, 5]) for _ in range(199)] + [1]]]
        ),
    ),
    Problem(
        slug="unique-paths",
        title="Unique Paths",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Math", "Dynamic Programming", "Combinatorics"],
        companies=[G, M],
        statement="A robot starts at the top-left of an `m × n` grid and can only move right or down. Return the number of different paths to the bottom-right corner.",
        entry="uniquePaths",
        params=[("m", "int"), ("n", "int")],
        returns="int",
        examples=[{"args": [3, 7]}, {"args": [3, 2]}],
        constraints=["1 ≤ m, n ≤ 100", "The answer is at most 2 × 10⁹"],
        hints=["paths(i, j) = paths(i − 1, j) + paths(i, j − 1). One row of the table is enough."],
        reference="""
class Solution:
    def uniquePaths(self, m, n):
        return math.comb(m + n - 2, m - 1)
""",
        gen=lambda r: (
            [[1, 1], [1, 100], [100, 1], [17, 17]] + [[r.randint(1, 12), r.randint(1, 12)] for _ in range(16)]
        ),
    ),
    Problem(
        slug="longest-common-subsequence",
        title="Longest Common Subsequence",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["String", "Dynamic Programming"],
        companies=[G, M],
        statement="Return the length of the longest subsequence common to `text1` and `text2`, or `0` if there is none. A subsequence keeps the original order but may skip characters.",
        entry="longestCommonSubsequence",
        params=[("text1", "str"), ("text2", "str")],
        returns="int",
        examples=[{"args": ["abcde", "ace"]}, {"args": ["abc", "abc"]}, {"args": ["abc", "def"]}],
        constraints=["1 ≤ len(text1), len(text2) ≤ 1000"],
        hints=[
            "dp[i][j] for prefixes: if the last letters match, 1 + dp[i−1][j−1]; otherwise max(dp[i−1][j], dp[i][j−1])."
        ],
        reference="""
class Solution:
    def longestCommonSubsequence(self, a, b):
        prev = [0] * (len(b) + 1)
        for x in a:
            cur = [0]
            for j, y in enumerate(b):
                cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
            prev = cur
        return prev[-1]
""",
        gen=lambda r: (
            [[word(r, r.randint(1, 12), "abc"), word(r, r.randint(1, 12), "abc")] for _ in range(18)]
            + [[word(r, 1000, "abcd"), word(r, 1000, "abcd")]]
        ),
        time_limit_ms=4000,
    ),
    Problem(
        slug="best-time-to-buy-and-sell-stock-with-cooldown",
        title="Best Time to Buy and Sell Stock with Cooldown",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming"],
        companies=[G, M],
        statement="`prices[i]` is the price on day `i`. You may complete as many buy/sell transactions as you like, holding at most one share, but after selling you must wait one day (cooldown) before buying again. Return the maximum profit.",
        entry="maxProfit",
        params=[("prices", "List[int]")],
        returns="int",
        examples=[{"args": [[1, 2, 3, 0, 2]], "note": "buy, sell, cooldown, buy, sell → 3."}, {"args": [[1]]}],
        constraints=["1 ≤ len(prices) ≤ 5000", "0 ≤ prices[i] ≤ 1000"],
        hints=[
            "Three states per day: holding, just sold (cooling down), and resting without a share. Write each one's transition from yesterday."
        ],
        reference="""
class Solution:
    def maxProfit(self, prices):
        hold, sold, rest = -inf, 0, 0
        for p in prices:
            hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
        return max(sold, rest)
""",
        gen=lambda r: [[ints(r, r.randint(1, 12), 0, 10)] for _ in range(18)] + [[ints(r, 5000, 0, 1000)]],
    ),
    Problem(
        slug="coin-change-ii",
        title="Coin Change II",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming"],
        companies=[G, M],
        statement="Return the number of combinations of `coins` (unlimited supply of each, distinct denominations) that make up `amount`. Order doesn't matter: 1+2 and 2+1 are the same combination.",
        entry="change",
        params=[("amount", "int"), ("coins", "List[int]")],
        returns="int",
        examples=[{"args": [5, [1, 2, 5]]}, {"args": [3, [2]]}, {"args": [10, [10]]}],
        constraints=["0 ≤ amount ≤ 5000", "1 ≤ len(coins) ≤ 300", "The answer fits in a signed 32-bit integer"],
        hints=[
            "Loop over coins in the outer loop and amounts in the inner loop, so each combination is counted in one order only."
        ],
        reference="""
class Solution:
    def change(self, amount, coins):
        ways = [1] + [0] * amount
        for c in coins:
            for a in range(c, amount + 1): ways[a] += ways[a - c]
        return ways[amount]
""",
        gen=lambda r: (
            [[0, [7]]]
            + [[r.randint(0, 30), distinct(r, r.randint(1, 5), 1, 12)] for _ in range(18)]
            + [[5000, [11, 24, 37, 50, 73, 99, 128, 250, 500]]]
        ),
    ),
    Problem(
        slug="target-sum",
        title="Target Sum",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming", "Backtracking"],
        companies=[G, M],
        statement="Put `+` or `-` in front of every number in `nums` and add them up. Return how many sign assignments give `target`.",
        entry="findTargetSumWays",
        params=[("nums", "List[int]"), ("target", "int")],
        returns="int",
        examples=[{"args": [[1, 1, 1, 1, 1], 3]}, {"args": [[1], 1]}],
        constraints=["1 ≤ len(nums) ≤ 20", "0 ≤ nums[i] ≤ 1000", "−1000 ≤ target ≤ 1000"],
        hints=["Keep a Counter of reachable sums after each number: each sum s branches to s + x and s − x."],
        reference="""
class Solution:
    def findTargetSumWays(self, nums, target):
        ways = Counter({0: 1})
        for x in nums:
            nxt = Counter()
            for s, c in ways.items(): nxt[s + x] += c; nxt[s - x] += c
            ways = nxt
        return ways[target]
""",
        gen=lambda r: (
            [[[0, 0, 1], 1]]
            + [[ints(r, r.randint(1, 12), 0, 5), r.randint(-6, 6)] for _ in range(18)]
            + [[ints(r, 20, 0, 1000), 0], [[1] * 20, 0]]
        ),
    ),
    Problem(
        slug="interleaving-string",
        title="Interleaving String",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["String", "Dynamic Programming"],
        companies=[G, M],
        statement="Return `True` if `s3` can be formed by interleaving `s1` and `s2`: splitting both into pieces and merging the pieces while keeping each string's own order.",
        entry="isInterleave",
        params=[("s1", "str"), ("s2", "str"), ("s3", "str")],
        returns="bool",
        examples=[
            {"args": ["aabcc", "dbbca", "aadbbcbcac"]},
            {"args": ["aabcc", "dbbca", "aadbbbaccc"]},
            {"args": ["", "", ""]},
        ],
        constraints=["0 ≤ len(s1), len(s2) ≤ 100", "0 ≤ len(s3) ≤ 200"],
        hints=[
            "dp[i][j]: can s1[:i] and s2[:j] form s3[:i + j]? Each cell looks at the cell above (took from s1) and to the left (took from s2)."
        ],
        reference="""
class Solution:
    def isInterleave(self, s1, s2, s3):
        if len(s1) + len(s2) != len(s3): return False
        dp = [True] + [False] * len(s2)
        for j in range(1, len(s2) + 1): dp[j] = dp[j - 1] and s2[j - 1] == s3[j - 1]
        for i in range(1, len(s1) + 1):
            dp[0] = dp[0] and s1[i - 1] == s3[i - 1]
            for j in range(1, len(s2) + 1):
                dp[j] = (dp[j] and s1[i - 1] == s3[i + j - 1]) or (dp[j - 1] and s2[j - 1] == s3[i + j - 1])
        return dp[-1]
""",
        gen=lambda r: (
            [_interleave(r, r.randint(0, 8), r.randint(0, 8)) for _ in range(20)] + [_interleave(r, 100, 100)]
        ),
    ),
    Problem(
        slug="maximal-square",
        title="Maximal Square",
        difficulty="Medium",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming", "Matrix"],
        companies=[G, M],
        statement='`matrix` is filled with `"0"` and `"1"`. Return the area of the largest square containing only `"1"`s.',
        entry="maximalSquare",
        params=[("matrix", "List[List[str]]")],
        returns="int",
        examples=[
            {
                "args": [
                    [
                        ["1", "0", "1", "0", "0"],
                        ["1", "0", "1", "1", "1"],
                        ["1", "1", "1", "1", "1"],
                        ["1", "0", "0", "1", "0"],
                    ]
                ]
            },
            {"args": [[["0", "1"], ["1", "0"]]]},
            {"args": [[["0"]]]},
        ],
        constraints=["1 ≤ rows, cols ≤ 300"],
        hints=[
            "side(i, j) = 1 + min(up, left, up-left) when the cell is '1'. The answer is the largest side, squared."
        ],
        reference="""
class Solution:
    def maximalSquare(self, matrix):
        C = len(matrix[0]); prev = [0] * (C + 1); best = 0
        for row in matrix:
            cur = [0] * (C + 1)
            for j in range(C):
                if row[j] == '1':
                    cur[j + 1] = 1 + min(prev[j], prev[j + 1], cur[j]); best = max(best, cur[j + 1])
            prev = cur
        return best * best
""",
        gen=lambda r: (
            [
                [[["1" if r.random() < 0.7 else "0" for _ in range(c)] for _ in range(rr)]]
                for rr, c in [(r.randint(1, 8), r.randint(1, 8)) for _ in range(18)]
            ]
            + [[[["1" if r.random() < 0.9 else "0" for _ in range(300)] for _ in range(300)]]]
        ),
    ),
    Problem(
        slug="longest-increasing-path-in-a-matrix",
        title="Longest Increasing Path in a Matrix",
        difficulty="Hard",
        pattern="dynamic-programming",
        topics=["Array", "DFS", "Topological Sort", "Memoization", "Matrix"],
        companies=[G, M],
        statement="Return the length of the longest strictly increasing path in `matrix`, moving up, down, left or right (no diagonals, no wrapping).",
        entry="longestIncreasingPath",
        params=[("matrix", "List[List[int]]")],
        returns="int",
        examples=[
            {"args": [[[9, 9, 4], [6, 6, 8], [2, 1, 1]]], "note": "1 → 2 → 6 → 9."},
            {"args": [[[3, 4, 5], [3, 2, 6], [2, 2, 1]]]},
        ],
        constraints=["1 ≤ rows, cols ≤ 200"],
        hints=[
            "Memoised DFS: the longest path starting at a cell is 1 + the best over its larger neighbours. Increasing paths can't cycle, so memoisation is safe."
        ],
        reference="""
class Solution:
    def longestIncreasingPath(self, m):
        R, C = len(m), len(m[0]); best = {}
        for v, i, j in sorted(((m[i][j], i, j) for i in range(R) for j in range(C)), reverse=True):
            best[(i, j)] = 1 + max([best[(x, y)] for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))
                                    if 0 <= x < R and 0 <= y < C and m[x][y] > v], default=0)
        return max(best.values())
""",
        gen=lambda r: (
            [
                [[ints(r, c, 0, 9) for _ in range(rr)]]
                for rr, c in [(r.randint(1, 7), r.randint(1, 7)) for _ in range(18)]
            ]
            + [
                [[ints(r, 200, 0, 10**6) for _ in range(200)]],
                [[list(range(i * 60, i * 60 + 60))[:: 1 if i % 2 == 0 else -1] for i in range(60)]],
            ]
        ),
    ),
    Problem(
        slug="distinct-subsequences",
        title="Distinct Subsequences",
        difficulty="Hard",
        pattern="dynamic-programming",
        topics=["String", "Dynamic Programming"],
        companies=[G, M],
        statement="Return the number of distinct ways to pick a subsequence of `s` that equals `t` (choices of different positions count separately). The answer fits in a 32-bit integer.",
        entry="numDistinct",
        params=[("s", "str"), ("t", "str")],
        returns="int",
        examples=[{"args": ["rabbbit", "rabbit"]}, {"args": ["babgbag", "bag"]}],
        constraints=["1 ≤ len(s), len(t) ≤ 1000"],
        hints=[
            "dp[j] = ways to form t[:j] from the processed part of s. For each letter of s, update j from right to left: dp[j] += dp[j − 1] when s[i] == t[j − 1]."
        ],
        reference="""
class Solution:
    def numDistinct(self, s, t):
        dp = [1] + [0] * len(t)
        for c in s:
            for j in range(len(t), 0, -1):
                if t[j - 1] == c: dp[j] += dp[j - 1]
        return dp[-1]
""",
        gen=lambda r: (
            [[word(r, r.randint(1, 14), "ab"), word(r, r.randint(1, 4), "ab")] for _ in range(18)]
            + [
                [word(r, 1000, "abcdefghij"), word(r, 4, "abcdefghij")],
                [word(r, 1000, "abcdefghijklmnopqrstuvwxyz"), word(r, 1000, "abcdefghijklmnopqrstuvwxyz")],
            ]
        ),
    ),
    Problem(
        slug="burst-balloons",
        title="Burst Balloons",
        difficulty="Hard",
        pattern="dynamic-programming",
        topics=["Array", "Dynamic Programming"],
        companies=[G, M],
        statement="Bursting balloon `i` earns `nums[left] * nums[i] * nums[right]`, where `left` and `right` are its current neighbours (a missing neighbour counts as 1). After bursting, its neighbours become adjacent. Return the most coins you can collect by bursting all balloons.",
        entry="maxCoins",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[3, 1, 5, 8]], "note": "3·1·5 + 3·5·8 + 1·3·8 + 1·8·1 = 167."}, {"args": [[1, 5]]}],
        constraints=["1 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 100"],
        hints=[
            "Think about the **last** balloon k burst inside an open interval (l, r): its neighbours then are exactly l and r.",
            "dp[l][r] = max over k of dp[l][k] + dp[k][r] + v[l]·v[k]·v[r], with 1s padded at both ends.",
        ],
        reference="""
class Solution:
    def maxCoins(self, nums):
        v = [1] + nums + [1]; n = len(v)
        dp = [[0] * n for _ in range(n)]
        for gap in range(2, n):
            for l in range(n - gap):
                r = l + gap; vl, vr = v[l], v[r]; row = dp[l]
                row[r] = max(row[k] + dp[k][r] + vl * v[k] * vr for k in range(l + 1, r))
        return dp[0][n - 1]
""",
        gen=lambda r: (
            [[[0]], [[7]]] + [[ints(r, r.randint(1, 8), 0, 10)] for _ in range(18)] + [[ints(r, 100, 0, 100)]]
        ),
    ),
    Problem(
        slug="regular-expression-matching",
        title="Regular Expression Matching",
        difficulty="Hard",
        pattern="dynamic-programming",
        topics=["String", "Dynamic Programming", "Recursion"],
        companies=[G, M],
        statement="Implement regular expression matching where `.` matches any single character and `*` matches zero or more of the element right before it. The pattern must match the **whole** string `s`.\n\nEvery `*` has a valid preceding character.",
        entry="isMatch",
        params=[("s", "str"), ("p", "str")],
        returns="bool",
        examples=[{"args": ["aa", "a"]}, {"args": ["aa", "a*"]}, {"args": ["ab", ".*"]}, {"args": ["aab", "c*a*b"]}],
        constraints=[
            "1 ≤ len(s) ≤ 20",
            "1 ≤ len(p) ≤ 20",
            "s has lowercase letters; p has lowercase letters, '.' and '*'",
        ],
        hints=[
            "match(i, j) for suffixes s[i:], p[j:]. If p[j + 1] is '*', either skip `x*` (j + 2) or, when s[i] matches x, consume one character (i + 1, same j).",
            "Memoise on (i, j).",
        ],
        reference="""
class Solution:
    def isMatch(self, s, p):
        @cache
        def m(i, j):
            if j == len(p): return i == len(s)
            first = i < len(s) and p[j] in (s[i], '.')
            if j + 1 < len(p) and p[j + 1] == '*':
                return m(i, j + 2) or (first and m(i + 1, j))
            return first and m(i + 1, j + 1)
        return m(0, 0)
""",
        gen=lambda r: (
            [["a", ".*..a*"], ["aaa", "ab*a*c*a"], ["mississippi", "mis*is*p*."]]
            + [[word(r, r.randint(1, 10), "ab"), _regex(r, r.randint(1, 8))] for _ in range(20)]
            + [["a" * 20, "a*" * 9 + "b"]]
        ),
    ),
]


# ---------------------------------------------------------------- private generator helpers
def _small_products(r: random.Random, n: int) -> list[int]:
    nums = [r.choice([1, -1, 1, -1, 0]) for _ in range(n)]
    for i in r.sample(range(n), 25):  # few ±2s keep every product within 32 bits
        nums[i] = r.choice([2, -2])
    return nums


def _interleave(r: random.Random, a: int, b: int) -> list[Any]:
    s1, s2 = word(r, a, "ab"), word(r, b, "ab")
    i = j = 0
    out = []
    while i < a or j < b:
        if j == b or (i < a and r.random() < 0.5):
            out.append(s1[i])
            i += 1
        else:
            out.append(s2[j])
            j += 1
    s3 = "".join(out)
    if s3 and r.random() < 0.4:
        k = r.randrange(len(s3))
        s3 = s3[:k] + ("a" if s3[k] == "b" else "b") + s3[k + 1 :]
    return [s1, s2, s3]


def _regex(r: random.Random, n: int) -> str:
    return "".join(r.choice("ab.") + ("*" if r.random() < 0.4 else "") for _ in range(n))[:20]
