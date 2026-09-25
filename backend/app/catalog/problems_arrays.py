import random
from typing import Any

from .base import Problem, distinct, ints, word

G, M = "google", "meta"

PROBLEMS = [
    Problem(
        slug="two-sum",
        title="Two Sum",
        difficulty="Easy",
        pattern="arrays-hashing",
        topics=["Array", "Hash Table"],
        companies=[G, M],
        statement="Given an array of integers `nums` and an integer `target`, return the indices of two numbers that add up to `target`.\n\nYou may not use the same element twice. Any valid pair of indices is accepted, in any order.",
        entry="twoSum",
        params=[("nums", "List[int]"), ("target", "int")],
        returns="List[int]",
        examples=[
            {"args": [[2, 7, 11, 15], 9], "note": "nums[0] + nums[1] = 9."},
            {"args": [[3, 2, 4], 6]},
            {"args": [[3, 3], 6]},
        ],
        constraints=["2 ≤ len(nums) ≤ 10⁴", "−10⁹ ≤ nums[i], target ≤ 10⁹", "At least one valid answer exists."],
        hints=[
            "Checking every pair is O(n²). How can you find a number's complement in O(1)?",
            "Store value → index in a dict as you scan; check for `target - x` before inserting `x`.",
        ],
        reference="""
class Solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, x in enumerate(nums):
            if target - x in seen:
                return [seen[target - x], i]
            seen[x] = i
""",
        gen=lambda r: (
            [[[0, 4, 3, 0], 0], [[-1, -2, -3, -4, -5], -8]]
            + [
                (lambda nums: [nums, nums[0] + nums[-1]] if r.random() < 0.3 else [nums, sum(r.sample(nums, 2))])(
                    distinct(r, n, -(10**6), 10**6)
                )
                for n in [r.randint(2, 50) for _ in range(20)] + [10_000]
            ]
        ),
        compare="two_sum",
    ),
    Problem(
        slug="group-anagrams",
        title="Group Anagrams",
        difficulty="Medium",
        pattern="arrays-hashing",
        topics=["Array", "Hash Table", "String", "Sorting"],
        companies=[M, G],
        statement="Given an array of strings `strs`, group the anagrams together. You can return the groups, and the words within each group, in any order.",
        entry="groupAnagrams",
        params=[("strs", "List[str]")],
        returns="List[List[str]]",
        examples=[{"args": [["eat", "tea", "tan", "ate", "nat", "bat"]]}, {"args": [[""]]}, {"args": [["a"]]}],
        constraints=["1 ≤ len(strs) ≤ 10⁴", "0 ≤ len(strs[i]) ≤ 100", "Lowercase English letters"],
        hints=[
            "Anagrams share the same letter counts. What key could represent that?",
            "Sorted letters or a 26-length count tuple both work as dict keys.",
        ],
        reference="""
class Solution:
    def groupAnagrams(self, strs):
        groups = defaultdict(list)
        for s in strs:
            groups[''.join(sorted(s))].append(s)
        return list(groups.values())
""",
        gen=lambda r: (
            [[["", ""]], [["ab", "ba", "abc", "cab", "x"]]]
            + [[[word(r, r.randint(0, 5), "abcd") for _ in range(r.randint(1, 40))]] for _ in range(18)]
            + [[[word(r, r.randint(1, 8), "abcdef") for _ in range(10_000)]]]
        ),
        compare="nested_sorted",
    ),
    Problem(
        slug="top-k-frequent-elements",
        title="Top K Frequent Elements",
        difficulty="Medium",
        pattern="heap",
        topics=["Array", "Hash Table", "Heap", "Bucket Sort"],
        companies=[M, G],
        statement="Given an integer array `nums` and an integer `k`, return the `k` most frequent elements, in any order. The answer is guaranteed to be unique.\n\nAim for better than O(n log n).",
        entry="topKFrequent",
        params=[("nums", "List[int]"), ("k", "int")],
        returns="List[int]",
        examples=[{"args": [[1, 1, 1, 2, 2, 3], 2]}, {"args": [[1], 1]}],
        constraints=["1 ≤ len(nums) ≤ 10⁵", "k is in range [1, number of unique elements]", "The answer is unique."],
        hints=["Count with a Counter first.", "A heap of size k gives O(n log k); bucketing by frequency gives O(n)."],
        reference="""
class Solution:
    def topKFrequent(self, nums, k):
        return [x for x, _ in Counter(nums).most_common(k)]
""",
        gen=lambda r: [_topk_case(r, r.randint(1, 15)) for _ in range(18)] + [_topk_case(r, 300)],
        compare="sorted",
    ),
    Problem(
        slug="product-of-array-except-self",
        title="Product of Array Except Self",
        difficulty="Medium",
        pattern="prefix-sum",
        topics=["Array", "Prefix Sum"],
        companies=[M, G],
        statement="Given an integer array `nums`, return an array `answer` where `answer[i]` equals the product of all elements except `nums[i]`.\n\nSolve it in O(n) time **without division**. Bonus: O(1) extra space besides the output.",
        entry="productExceptSelf",
        params=[("nums", "List[int]")],
        returns="List[int]",
        examples=[{"args": [[1, 2, 3, 4]]}, {"args": [[-1, 1, 0, -3, 3]]}],
        constraints=[
            "2 ≤ len(nums) ≤ 10⁵",
            "−30 ≤ nums[i] ≤ 30",
            "Every prefix/suffix product fits in a 32-bit integer.",
        ],
        hints=[
            "answer[i] = (product of everything left of i) × (product of everything right of i).",
            "Fill left products in one pass, multiply right products in a backwards pass.",
        ],
        reference="""
class Solution:
    def productExceptSelf(self, nums):
        n = len(nums); ans = [1] * n; p = 1
        for i in range(n):
            ans[i] = p; p *= nums[i]
        p = 1
        for i in range(n - 1, -1, -1):
            ans[i] *= p; p *= nums[i]
        return ans
""",
        gen=lambda r: (
            [[[0, 0]], [[2, 3]], [[0, 4, 0]], [[5, 0, 2]]]
            + [[ints(r, r.randint(2, 12), -3, 3)] for _ in range(18)]
            + [[[r.choice([1, -1]) for _ in range(50_000)]]]
        ),
    ),
    Problem(
        slug="longest-consecutive-sequence",
        title="Longest Consecutive Sequence",
        difficulty="Medium",
        pattern="arrays-hashing",
        topics=["Array", "Hash Table", "Union Find"],
        companies=[G, M],
        statement="Given an unsorted array of integers `nums`, return the length of the longest run of consecutive integers (e.g. 4, 5, 6, 7) whose values all appear in the array.\n\nYour algorithm should run in O(n).",
        entry="longestConsecutive",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[
            {"args": [[100, 4, 200, 1, 3, 2]], "note": "1, 2, 3, 4 has length 4."},
            {"args": [[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]]},
        ],
        constraints=["0 ≤ len(nums) ≤ 10⁵", "−10⁹ ≤ nums[i] ≤ 10⁹"],
        hints=[
            "Put everything in a set.",
            "Only start counting from x when x − 1 is not in the set: each run is walked once.",
        ],
        reference="""
class Solution:
    def longestConsecutive(self, nums):
        s = set(nums); best = 0
        for x in s:
            if x - 1 not in s:
                y = x
                while y + 1 in s:
                    y += 1
                best = max(best, y - x + 1)
        return best
""",
        gen=lambda r: (
            [[[]], [[5]], [[1, 2, 0, 1]], [[9, 1, -3, 2, 4, 8, 3, -1, -2, 0]]]
            + [[ints(r, r.randint(1, 60), -30, 30)] for _ in range(16)]
            + [[ints(r, 100_000, -(10**9), 10**9)], [list(range(50_000, 0, -1))]]
        ),
    ),
    Problem(
        slug="subarray-sum-equals-k",
        title="Subarray Sum Equals K",
        difficulty="Medium",
        pattern="prefix-sum",
        topics=["Array", "Hash Table", "Prefix Sum"],
        companies=[M, G],
        statement="Given an integer array `nums` and an integer `k`, return the number of contiguous, non-empty subarrays whose sum equals `k`.",
        entry="subarraySum",
        params=[("nums", "List[int]"), ("k", "int")],
        returns="int",
        examples=[{"args": [[1, 1, 1], 2]}, {"args": [[1, 2, 3], 3]}],
        constraints=["1 ≤ len(nums) ≤ 2 × 10⁴", "−1000 ≤ nums[i] ≤ 1000", "−10⁷ ≤ k ≤ 10⁷"],
        hints=[
            "Negative numbers break the sliding window idea.",
            "sum(i..j) = prefix[j] − prefix[i−1]. Count how many earlier prefixes equal prefix − k.",
        ],
        reference="""
class Solution:
    def subarraySum(self, nums, k):
        count = Counter({0: 1}); p = ans = 0
        for x in nums:
            p += x
            ans += count[p - k]
            count[p] += 1
        return ans
""",
        gen=lambda r: (
            [[[0, 0, 0], 0], [[-1, -1, 1], 0], [[1], 0]]
            + [[ints(r, r.randint(1, 60), -5, 5), r.randint(-6, 6)] for _ in range(18)]
            + [[ints(r, 20_000, -1000, 1000), r.randint(-100, 100)]]
        ),
    ),
    Problem(
        slug="valid-palindrome-ii",
        title="Valid Palindrome II",
        difficulty="Easy",
        pattern="two-pointers",
        topics=["String", "Two Pointers", "Greedy"],
        companies=[M],
        statement="Given a string `s`, return `True` if it can be a palindrome after deleting **at most one** character.",
        entry="validPalindrome",
        params=[("s", "str")],
        returns="bool",
        examples=[{"args": ["aba"]}, {"args": ["abca"], "note": "Delete 'c'."}, {"args": ["abc"]}],
        constraints=["1 ≤ len(s) ≤ 10⁵", "Lowercase English letters"],
        hints=[
            "Walk two pointers inward. At the first mismatch you have exactly two choices: skip the left char or skip the right one."
        ],
        reference="""
class Solution:
    def validPalindrome(self, s):
        def pal(i, j):
            while i < j:
                if s[i] != s[j]:
                    return False
                i += 1; j -= 1
            return True
        i, j = 0, len(s) - 1
        while i < j:
            if s[i] != s[j]:
                return pal(i + 1, j) or pal(i, j - 1)
            i += 1; j -= 1
        return True
""",
        gen=lambda r: (
            [["a"], ["ab"], ["deeee"], ["cbbcc"], ["ebcbbececabbacecbbcbe"]]
            + [[_pal_variant(r, r.randint(1, 30))] for _ in range(20)]
            + [[_pal_variant(r, 50_000)]]
        ),
    ),
    Problem(
        slug="3sum",
        title="3Sum",
        difficulty="Medium",
        pattern="two-pointers",
        topics=["Array", "Two Pointers", "Sorting"],
        companies=[M, G],
        statement="Given an integer array `nums`, return all **unique** triplets `[a, b, c]` of values from different indices such that `a + b + c == 0`.\n\nThe order of triplets and of values inside a triplet doesn't matter, but there must be no duplicate triplets.",
        entry="threeSum",
        params=[("nums", "List[int]")],
        returns="List[List[int]]",
        examples=[{"args": [[-1, 0, 1, 2, -1, -4]]}, {"args": [[0, 1, 1]]}, {"args": [[0, 0, 0]]}],
        constraints=["3 ≤ len(nums) ≤ 3000", "−10⁵ ≤ nums[i] ≤ 10⁵"],
        hints=[
            "Sort first. Fix the first number, then solve two-sum on the rest with two pointers.",
            "Skip equal neighbours to avoid duplicates.",
        ],
        reference="""
class Solution:
    def threeSum(self, nums):
        nums.sort(); res = []; n = len(nums)
        for i in range(n - 2):
            if i and nums[i] == nums[i - 1]:
                continue
            l, r = i + 1, n - 1
            while l < r:
                s = nums[i] + nums[l] + nums[r]
                if s < 0: l += 1
                elif s > 0: r -= 1
                else:
                    res.append([nums[i], nums[l], nums[r]])
                    while l < r and nums[l] == nums[l + 1]: l += 1
                    l += 1; r -= 1
        return res
""",
        gen=lambda r: (
            [[[0, 0, 0, 0]], [[-2, 0, 1, 1, 2]], [[1, 2, 3]]]
            + [[ints(r, r.randint(3, 40), -10, 10)] for _ in range(18)]
            + [[ints(r, 1200, -(10**5), 10**5)], [ints(r, 3000, -15, 15)]]
        ),
        compare="nested_sorted",
    ),
    Problem(
        slug="container-with-most-water",
        title="Container With Most Water",
        difficulty="Medium",
        pattern="two-pointers",
        topics=["Array", "Two Pointers", "Greedy"],
        companies=[G, M],
        statement="`height[i]` is the height of a vertical line at position `i`. Pick two lines that, together with the x-axis, form a container holding the most water. Return that maximum area.",
        entry="maxArea",
        params=[("height", "List[int]")],
        returns="int",
        examples=[
            {"args": [[1, 8, 6, 2, 5, 4, 8, 3, 7]], "note": "Lines at index 1 and 8: min(8, 7) × 7 = 49."},
            {"args": [[1, 1]]},
        ],
        constraints=["2 ≤ len(height) ≤ 10⁵", "0 ≤ height[i] ≤ 10⁴"],
        hints=["Start with the widest container. Moving the taller line inward can never help — why?"],
        reference="""
class Solution:
    def maxArea(self, h):
        l, r, best = 0, len(h) - 1, 0
        while l < r:
            best = max(best, min(h[l], h[r]) * (r - l))
            if h[l] < h[r]: l += 1
            else: r -= 1
        return best
""",
        gen=lambda r: (
            [[[4, 3, 2, 1, 4]], [[1, 2, 1]], [[0, 0]]]
            + [[ints(r, r.randint(2, 50), 0, 20)] for _ in range(18)]
            + [[ints(r, 100_000, 0, 10_000)]]
        ),
    ),
    Problem(
        slug="trapping-rain-water",
        title="Trapping Rain Water",
        difficulty="Hard",
        pattern="two-pointers",
        topics=["Array", "Two Pointers", "Monotonic Stack"],
        companies=[G, M],
        statement="`height` is an elevation map where every bar is 1 unit wide. Return how much rain water it can trap.",
        entry="trap",
        params=[("height", "List[int]")],
        returns="int",
        examples=[
            {"args": [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], "note": "6 units of water are trapped."},
            {"args": [[4, 2, 0, 3, 2, 5]]},
        ],
        constraints=["1 ≤ len(height) ≤ 2 × 10⁴", "0 ≤ height[i] ≤ 10⁵"],
        hints=[
            "Water above bar i = min(max to the left, max to the right) − height[i].",
            "Two pointers: always move the side with the smaller max — its water level is already decided.",
        ],
        reference="""
class Solution:
    def trap(self, h):
        l, r, lm, rm, w = 0, len(h) - 1, 0, 0, 0
        while l < r:
            if h[l] < h[r]:
                lm = max(lm, h[l]); w += lm - h[l]; l += 1
            else:
                rm = max(rm, h[r]); w += rm - h[r]; r -= 1
        return w
""",
        gen=lambda r: (
            [[[5]], [[2, 0, 2]], [[3, 0, 0, 2, 0, 4]], [[1, 2, 3, 4, 5]]]
            + [[ints(r, r.randint(1, 60), 0, 10)] for _ in range(18)]
            + [[ints(r, 20_000, 0, 100_000)]]
        ),
    ),
    Problem(
        slug="longest-substring-without-repeating-characters",
        title="Longest Substring Without Repeating Characters",
        difficulty="Medium",
        pattern="sliding-window",
        topics=["String", "Hash Table", "Sliding Window"],
        companies=[G, M],
        statement="Given a string `s`, return the length of the longest substring that contains no repeated characters.",
        entry="lengthOfLongestSubstring",
        params=[("s", "str")],
        returns="int",
        examples=[
            {"args": ["abcabcbb"], "note": '"abc"'},
            {"args": ["bbbbb"]},
            {"args": ["pwwkew"], "note": '"wke" — "pwke" is not contiguous.'},
        ],
        constraints=["0 ≤ len(s) ≤ 5 × 10⁴", "Letters, digits, symbols and spaces"],
        hints=["Keep a window with no repeats. When s[r] repeats, jump the left edge past its previous position."],
        reference="""
class Solution:
    def lengthOfLongestSubstring(self, s):
        last = {}; l = best = 0
        for r, c in enumerate(s):
            if c in last and last[c] >= l:
                l = last[c] + 1
            last[c] = r
            best = max(best, r - l + 1)
        return best
""",
        gen=lambda r: (
            [[""], [" "], ["au"], ["dvdf"], ["abba"], ["tmmzuxt"]]
            + [[word(r, r.randint(0, 80), "abcdefgh xyz0!"[: r.randint(2, 14)])] for _ in range(18)]
            + [[word(r, 50_000, "abcdefghijklmnopqrstuvwxyz")]]
        ),
    ),
    Problem(
        slug="minimum-window-substring",
        title="Minimum Window Substring",
        difficulty="Hard",
        pattern="sliding-window",
        topics=["String", "Hash Table", "Sliding Window"],
        companies=[M, G],
        statement='Given strings `s` and `t`, return the shortest substring of `s` containing every character of `t` (duplicates included). Return `""` if none exists.\n\nIf several shortest windows exist, any of them is accepted.',
        entry="minWindow",
        params=[("s", "str"), ("t", "str")],
        returns="str",
        examples=[{"args": ["ADOBECODEBANC", "ABC"], "note": '"BANC"'}, {"args": ["a", "a"]}, {"args": ["a", "aa"]}],
        constraints=["1 ≤ len(s), len(t) ≤ 10⁵", "Upper and lowercase English letters"],
        hints=[
            "Expand right until the window covers t, then shrink left while it still does.",
            "Track how many required characters are still missing so each check is O(1).",
        ],
        reference="""
class Solution:
    def minWindow(self, s, t):
        need = Counter(t); missing = len(t); l = 0; best = (inf, 0)
        for r, c in enumerate(s):
            if need[c] > 0: missing -= 1
            need[c] -= 1
            while missing == 0:
                if r - l + 1 < best[0]: best = (r - l + 1, l)
                need[s[l]] += 1
                if need[s[l]] > 0: missing += 1
                l += 1
        return "" if best[0] == inf else s[best[1]:best[1] + best[0]]
""",
        gen=lambda r: (
            [["ab", "b"], ["bba", "ab"], ["aa", "aa"], ["abc", "d"]]
            + [[word(r, r.randint(1, 60), a), word(r, r.randint(1, 5), a)] for a in ["ABCabc", "ABCDEFabcdef"] * 9]
            + [[word(r, 100_000, "ABCDEFGHIJ"), word(r, 40, "ABCDEFGHIJ")]]
        ),
        compare="min_window",
    ),
    Problem(
        slug="longest-repeating-character-replacement",
        title="Longest Repeating Character Replacement",
        difficulty="Medium",
        pattern="sliding-window",
        topics=["String", "Hash Table", "Sliding Window"],
        companies=[G],
        statement="You may change at most `k` characters of the uppercase string `s` to any other uppercase letter. Return the length of the longest substring of identical letters you can get.",
        entry="characterReplacement",
        params=[("s", "str"), ("k", "int")],
        returns="int",
        examples=[{"args": ["ABAB", 2]}, {"args": ["AABABBA", 1]}],
        constraints=["1 ≤ len(s) ≤ 10⁵", "0 ≤ k ≤ len(s)"],
        hints=["A window is fixable when (window length − count of its most common letter) ≤ k."],
        reference="""
class Solution:
    def characterReplacement(self, s, k):
        cnt = Counter(); l = top = best = 0
        for r, c in enumerate(s):
            cnt[c] += 1; top = max(top, cnt[c])
            while r - l + 1 - top > k:
                cnt[s[l]] -= 1; l += 1
            best = max(best, r - l + 1)
        return best
""",
        gen=lambda r: (
            [["A", 0], ["ABCDE", 1], ["AAAA", 2]]
            + [[word(r, n, "ABC"[: r.randint(1, 3)]), r.randint(0, n)] for n in [r.randint(1, 40) for _ in range(18)]]
            + [[word(r, 100_000, "ABCD"), 500]]
        ),
    ),
    Problem(
        slug="valid-parentheses",
        title="Valid Parentheses",
        difficulty="Easy",
        pattern="stack",
        topics=["String", "Stack"],
        companies=[G, M],
        statement="Given a string `s` of `()[]{}` characters, return `True` if every bracket is closed by the same type, in the correct order.",
        entry="isValid",
        params=[("s", "str")],
        returns="bool",
        examples=[{"args": ["()[]{}"]}, {"args": ["(]"]}, {"args": ["([)]"]}],
        constraints=["1 ≤ len(s) ≤ 10⁴"],
        hints=["The most recently opened bracket must close first — a stack."],
        reference="""
class Solution:
    def isValid(self, s):
        st = []; pairs = {')': '(', ']': '[', '}': '{'}
        for c in s:
            if c in pairs:
                if not st or st.pop() != pairs[c]: return False
            else:
                st.append(c)
        return not st
""",
        gen=lambda r: (
            [["("], [")"], ["(("], ["){"], ["{[]}"]]
            + [[_brackets(r, r.randint(1, 20), r.random() < 0.5)] for _ in range(20)]
            + [[_brackets(r, 5000, False)]]
        ),
    ),
    Problem(
        slug="minimum-remove-to-make-valid-parentheses",
        title="Minimum Remove to Make Valid Parentheses",
        difficulty="Medium",
        pattern="stack",
        topics=["String", "Stack"],
        companies=[M],
        statement="`s` contains lowercase letters and `(`, `)`. Remove the minimum number of parentheses so the result is valid, and return any such result.",
        entry="minRemoveToMakeValid",
        params=[("s", "str")],
        returns="str",
        examples=[{"args": ["lee(t(c)o)de)"]}, {"args": ["a)b(c)d"]}, {"args": ["))(("]}],
        constraints=["1 ≤ len(s) ≤ 10⁵"],
        hints=[
            "Scan left to right: a `)` with nothing open must go. Any `(` still open at the end must go too.",
            "Stack the indices of unmatched `(`.",
        ],
        reference="""
class Solution:
    def minRemoveToMakeValid(self, s):
        s = list(s); st = []
        for i, c in enumerate(s):
            if c == '(':
                st.append(i)
            elif c == ')':
                if st: st.pop()
                else: s[i] = ''
        for i in st: s[i] = ''
        return ''.join(s)
""",
        gen=lambda r: (
            [["("], ["a"], ["())()((("]]
            + [[word(r, r.randint(1, 40), "ab()()")] for _ in range(20)]
            + [[word(r, 100_000, "abc()")]]
        ),
        compare="min_remove_parens",
    ),
    Problem(
        slug="daily-temperatures",
        title="Daily Temperatures",
        difficulty="Medium",
        pattern="stack",
        topics=["Array", "Stack", "Monotonic Stack"],
        companies=[G, M],
        statement="Given daily `temperatures`, return `answer` where `answer[i]` is how many days you wait after day `i` for a warmer temperature, or `0` if it never comes.",
        entry="dailyTemperatures",
        params=[("temperatures", "List[int]")],
        returns="List[int]",
        examples=[{"args": [[73, 74, 75, 71, 69, 72, 76, 73]]}, {"args": [[30, 60, 90]]}],
        constraints=["1 ≤ len(temperatures) ≤ 10⁵", "30 ≤ temperatures[i] ≤ 100"],
        hints=["Keep a stack of days still waiting for a warmer day. Their temperatures are decreasing."],
        reference="""
class Solution:
    def dailyTemperatures(self, t):
        ans = [0] * len(t); st = []
        for i, x in enumerate(t):
            while st and t[st[-1]] < x:
                j = st.pop(); ans[j] = i - j
            st.append(i)
        return ans
""",
        gen=lambda r: (
            [[[50]], [[90, 80, 70]], [[70, 70, 71]]]
            + [[ints(r, r.randint(1, 50), 30, 100)] for _ in range(18)]
            + [[ints(r, 100_000, 30, 100)], [list(range(100, 30, -1)) * 1000]]
        ),
    ),
    Problem(
        slug="basic-calculator-ii",
        title="Basic Calculator II",
        difficulty="Medium",
        pattern="stack",
        topics=["Math", "String", "Stack"],
        companies=[M, G],
        statement="Evaluate the expression string `s`, which contains non-negative integers, `+ - * /` and spaces. Integer division truncates toward zero. Don't use `eval`.\n\nThe expression is always valid and all intermediate results fit in a 32-bit integer.",
        entry="calculate",
        params=[("s", "str")],
        returns="int",
        examples=[{"args": ["3+2*2"]}, {"args": [" 3/2 "]}, {"args": [" 3+5 / 2 "]}],
        constraints=["1 ≤ len(s) ≤ 3 × 10⁵", "No parentheses", "No division by zero"],
        hints=[
            "Handle * and / immediately against the previous term; defer + and − by pushing signed terms to a stack, then sum."
        ],
        reference="""
class Solution:
    def calculate(self, s):
        st = []; num = 0; op = '+'
        for i, c in enumerate(s + '+'):
            if c.isdigit():
                num = num * 10 + int(c)
            elif c in '+-*/':
                if op == '+': st.append(num)
                elif op == '-': st.append(-num)
                elif op == '*': st.append(st.pop() * num)
                else:
                    a = st.pop(); q = abs(a) // num
                    st.append(q if a >= 0 else -q)
                num = 0; op = c
        return sum(st)
""",
        gen=lambda r: (
            [["0"], ["42"], ["14-3/2"], ["1-1*5/2"], ["100 / 7 * 3 - 2"]]
            + [[_expr(r, r.randint(1, 8))] for _ in range(20)]
            + [[" + ".join(str(r.randint(0, 9)) for _ in range(20_000))]]
        ),
    ),
    Problem(
        slug="search-in-rotated-sorted-array",
        title="Search in Rotated Sorted Array",
        difficulty="Medium",
        pattern="binary-search",
        topics=["Array", "Binary Search"],
        companies=[M, G],
        statement="A sorted array of **distinct** integers was rotated at an unknown pivot (e.g. `[0,1,2,4,5,6,7]` → `[4,5,6,7,0,1,2]`). Return the index of `target`, or `-1` if absent.\n\nYou must run in O(log n).",
        entry="search",
        params=[("nums", "List[int]"), ("target", "int")],
        returns="int",
        examples=[{"args": [[4, 5, 6, 7, 0, 1, 2], 0]}, {"args": [[4, 5, 6, 7, 0, 1, 2], 3]}, {"args": [[1], 0]}],
        constraints=["1 ≤ len(nums) ≤ 5000", "Values are distinct"],
        hints=["At any mid, at least one half is sorted. Check whether target lies inside that sorted half."],
        reference="""
class Solution:
    def search(self, nums, target):
        try:
            return nums.index(target)
        except ValueError:
            return -1
""",
        gen=lambda r: [_rotated_case(r, r.randint(1, 40)) for _ in range(22)] + [_rotated_case(r, 5000)],
    ),
    Problem(
        slug="find-peak-element",
        title="Find Peak Element",
        difficulty="Medium",
        pattern="binary-search",
        topics=["Array", "Binary Search"],
        companies=[M, G],
        statement="A peak is an element strictly greater than its neighbours; `nums[-1]` and `nums[n]` count as −∞. Neighbouring values are never equal. Return the index of **any** peak in O(log n).",
        entry="findPeakElement",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[1, 2, 3, 1]]}, {"args": [[1, 2, 1, 3, 5, 6, 4]], "note": "1 or 5 are both accepted."}],
        constraints=["1 ≤ len(nums) ≤ 1000", "nums[i] ≠ nums[i + 1]"],
        hints=["If nums[mid] < nums[mid + 1], a peak must exist to the right. Why?"],
        reference="""
class Solution:
    def findPeakElement(self, nums):
        return max(range(len(nums)), key=lambda i: nums[i])
""",
        gen=lambda r: (
            [[[1]], [[1, 2]], [[2, 1]]]
            + [[_no_equal_neighbours(r, r.randint(1, 60))] for _ in range(18)]
            + [[_no_equal_neighbours(r, 1000)]]
        ),
        compare="peak",
    ),
    Problem(
        slug="koko-eating-bananas",
        title="Koko Eating Bananas",
        difficulty="Medium",
        pattern="binary-search",
        topics=["Array", "Binary Search"],
        companies=[G],
        statement="There are `piles` of bananas and `h` hours. Each hour Koko eats up to `k` bananas from one pile (if the pile has fewer, she finishes it and waits). Return the minimum integer `k` that lets her finish within `h` hours.",
        entry="minEatingSpeed",
        params=[("piles", "List[int]"), ("h", "int")],
        returns="int",
        examples=[{"args": [[3, 6, 7, 11], 8]}, {"args": [[30, 11, 23, 4, 20], 5]}, {"args": [[30, 11, 23, 4, 20], 6]}],
        constraints=["1 ≤ len(piles) ≤ 10⁴", "len(piles) ≤ h ≤ 10⁹", "1 ≤ piles[i] ≤ 10⁹"],
        hints=["If speed k works, every faster speed works too. Binary search on the answer."],
        reference="""
class Solution:
    def minEatingSpeed(self, piles, h):
        lo, hi = 1, max(piles)
        while lo < hi:
            k = (lo + hi) // 2
            if sum((p + k - 1) // k for p in piles) <= h: hi = k
            else: lo = k + 1
        return lo
""",
        gen=lambda r: (
            [[[1], 1], [[1000000000], 2], [[312884470], 968709470]]
            + [(lambda p: [p, r.randint(len(p), len(p) * 4)])(ints(r, r.randint(1, 20), 1, 100)) for _ in range(18)]
            + [[ints(r, 10_000, 1, 10**9), 10**6]]
        ),
    ),
    Problem(
        slug="median-of-two-sorted-arrays",
        title="Median of Two Sorted Arrays",
        difficulty="Hard",
        pattern="binary-search",
        topics=["Array", "Binary Search", "Divide and Conquer"],
        companies=[G],
        statement="Given two sorted arrays `nums1` and `nums2`, return the median of all their values combined.\n\nThe target complexity is O(log(m + n)). Answers within 10⁻⁵ are accepted.",
        entry="findMedianSortedArrays",
        params=[("nums1", "List[int]"), ("nums2", "List[int]")],
        returns="float",
        examples=[{"args": [[1, 3], [2]]}, {"args": [[1, 2], [3, 4]]}],
        constraints=["0 ≤ m, n ≤ 1000", "1 ≤ m + n"],
        hints=[
            "Binary search a split in the shorter array so the left halves together hold half the values and every left value ≤ every right value."
        ],
        reference="""
class Solution:
    def findMedianSortedArrays(self, a, b):
        m = sorted(a + b); n = len(m)
        return float(m[n // 2]) if n % 2 else (m[n // 2 - 1] + m[n // 2]) / 2
""",
        gen=lambda r: (
            [[[], [1]], [[2], []], [[0, 0], [0, 0]]]
            + [
                [sorted(ints(r, r.randint(0, 30), -100, 100)), sorted(ints(r, r.randint(1, 30), -100, 100))]
                for _ in range(18)
            ]
            + [[sorted(ints(r, 1000, -(10**6), 10**6)), sorted(ints(r, 999, -(10**6), 10**6))]]
        ),
        compare="float",
    ),
    Problem(
        slug="merge-intervals",
        title="Merge Intervals",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["Array", "Sorting", "Intervals"],
        companies=[G, M],
        statement="Given `intervals[i] = [start, end]`, merge all overlapping intervals and return the result. Touching intervals like `[1,4]` and `[4,5]` overlap. Any output order is accepted.",
        entry="merge",
        params=[("intervals", "List[List[int]]")],
        returns="List[List[int]]",
        examples=[{"args": [[[1, 3], [2, 6], [8, 10], [15, 18]]]}, {"args": [[[1, 4], [4, 5]]]}],
        constraints=["1 ≤ len(intervals) ≤ 10⁴", "0 ≤ start ≤ end ≤ 10⁴"],
        hints=["Sort by start; each interval either extends the last merged one or starts a new one."],
        reference="""
class Solution:
    def merge(self, intervals):
        out = []
        for s, e in sorted(intervals):
            if out and s <= out[-1][1]: out[-1][1] = max(out[-1][1], e)
            else: out.append([s, e])
        return out
""",
        gen=lambda r: (
            [[[[1, 4]]], [[[1, 4], [0, 4]]], [[[1, 4], [2, 3]]], [[[1, 4], [0, 0]]]]
            + [
                [[(lambda s: [s, s + r.randint(0, 20)])(r.randint(0, 100)) for _ in range(r.randint(1, 30))]]
                for _ in range(18)
            ]
            + [[[(lambda s: [s, s + r.randint(0, 5)])(r.randint(0, 10_000)) for _ in range(10_000)]]]
        ),
        compare="sorted",
    ),
    Problem(
        slug="meeting-rooms-ii",
        title="Meeting Rooms II",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["Array", "Sorting", "Heap", "Intervals"],
        companies=[G, M],
        statement="Given meeting time `intervals[i] = [start, end)`, return the minimum number of conference rooms required. A meeting ending at time t frees its room for one starting at t.",
        entry="minMeetingRooms",
        params=[("intervals", "List[List[int]]")],
        returns="int",
        examples=[{"args": [[[0, 30], [5, 10], [15, 20]]]}, {"args": [[[7, 10], [2, 4]]]}],
        constraints=["1 ≤ len(intervals) ≤ 10⁴", "0 ≤ start < end ≤ 10⁶"],
        hints=[
            "Sort by start; keep a min-heap of end times of rooms in use.",
            "Alternative: sweep sorted starts and sorted ends with two pointers.",
        ],
        reference="""
class Solution:
    def minMeetingRooms(self, intervals):
        ev = sorted([(s, 1) for s, _ in intervals] + [(e, -1) for _, e in intervals])
        cur = best = 0
        for _, d in ev:
            cur += d; best = max(best, cur)
        return best
""",
        gen=lambda r: (
            [[[[1, 5], [5, 10]]], [[[1, 2]]], [[[1, 10], [2, 3], [3, 4], [4, 5]]]]
            + [
                [[(lambda s: [s, s + r.randint(1, 20)])(r.randint(0, 60)) for _ in range(r.randint(1, 25))]]
                for _ in range(18)
            ]
            + [[[(lambda s: [s, s + r.randint(1, 1000)])(r.randint(0, 10**6)) for _ in range(10_000)]]]
        ),
    ),
    Problem(
        slug="jump-game",
        title="Jump Game",
        difficulty="Medium",
        pattern="intervals-greedy",
        topics=["Array", "Greedy", "Dynamic Programming"],
        companies=[G, M],
        statement="You start at index 0 of `nums`; `nums[i]` is your maximum jump length from index `i`. Return `True` if you can reach the last index.",
        entry="canJump",
        params=[("nums", "List[int]")],
        returns="bool",
        examples=[{"args": [[2, 3, 1, 1, 4]]}, {"args": [[3, 2, 1, 0, 4]]}],
        constraints=["1 ≤ len(nums) ≤ 10⁴", "0 ≤ nums[i] ≤ 10⁵"],
        hints=["Track the furthest index reachable so far. If you ever stand beyond it, you're stuck."],
        reference="""
class Solution:
    def canJump(self, nums):
        far = 0
        for i, x in enumerate(nums):
            if i > far: return False
            far = max(far, i + x)
        return True
""",
        gen=lambda r: (
            [[[0]], [[0, 1]], [[1, 0]], [[2, 0, 0]]]
            + [[ints(r, r.randint(1, 30), 0, 3)] for _ in range(18)]
            + [[[1] * 9999 + [0]], [ints(r, 10_000, 0, 2)]]
        ),
    ),
    Problem(
        slug="best-time-to-buy-and-sell-stock",
        title="Best Time to Buy and Sell Stock",
        difficulty="Easy",
        pattern="arrays-hashing",
        topics=["Array", "Greedy"],
        companies=[G, M],
        statement="`prices[i]` is a stock price on day `i`. Choose one day to buy and a later day to sell. Return the maximum profit, or `0` if no profit is possible.",
        entry="maxProfit",
        params=[("prices", "List[int]")],
        returns="int",
        examples=[{"args": [[7, 1, 5, 3, 6, 4]]}, {"args": [[7, 6, 4, 3, 1]]}],
        constraints=["1 ≤ len(prices) ≤ 10⁵", "0 ≤ prices[i] ≤ 10⁴"],
        hints=["For each day, the best sale is today's price minus the lowest price seen before it."],
        reference="""
class Solution:
    def maxProfit(self, prices):
        lo, best = inf, 0
        for p in prices:
            lo = min(lo, p); best = max(best, p - lo)
        return best
""",
        gen=lambda r: (
            [[[1]], [[2, 4, 1]], [[3, 3, 3]]]
            + [[ints(r, r.randint(1, 60), 0, 100)] for _ in range(18)]
            + [[ints(r, 100_000, 0, 10_000)]]
        ),
    ),
]


# ---------------------------------------------------------------- private generator helpers
def _topk_case(r: random.Random, m: int) -> list[Any]:
    vals = distinct(r, m, -1000, 1000)
    counts = list(range(1, m + 1))
    r.shuffle(counts)
    nums = [v for v, c in zip(vals, counts, strict=True) for _ in range(c)]
    r.shuffle(nums)
    return [nums, r.randint(1, m)]


def _pal_variant(r: random.Random, n: int) -> str:
    half = word(r, n // 2, "abc")
    s = list(half + (r.choice("abc") if n % 2 else "") + half[::-1])
    for _ in range(r.choice([0, 1, 1, 2])):
        s.insert(r.randint(0, len(s)), r.choice("abc"))
    return "".join(s) or "a"


def _brackets(r: random.Random, pairs: int, corrupt: bool) -> str:
    opens, closes = "([{", ")]}"
    st: list[int] = []
    s: list[str] = []
    left = pairs
    while left or st:
        if left and (not st or r.random() < 0.5):
            t = r.randrange(3)
            st.append(t)
            s.append(opens[t])
            left -= 1
        else:
            s.append(closes[st.pop()])
    if corrupt:
        i = r.randrange(len(s))
        if r.random() < 0.5:
            s.pop(i)
        else:
            s[i] = r.choice("()[]{}")
    return "".join(s) or "("


def _expr(r: random.Random, terms: int) -> str:
    parts = [str(r.randint(0, 100))]
    for _ in range(terms - 1):
        op = r.choice("+-*/")
        num = r.randint(1, 20) if op in "*/" else r.randint(0, 100)
        parts += [op, str(num)]
    return "".join(p + (" " * r.randint(0, 1)) for p in parts)


def _rotated_case(r: random.Random, n: int) -> list[Any]:
    nums = sorted(distinct(r, n, -10_000, 10_000))
    k = r.randrange(n)
    nums = nums[k:] + nums[:k]
    target = r.choice(nums) if r.random() < 0.6 else r.randint(-10_001, 10_001)
    return [nums, target]


def _no_equal_neighbours(r: random.Random, n: int) -> list[int]:
    out = [r.randint(-50, 50)]
    while len(out) < n:
        x = r.randint(-50, 50)
        if x != out[-1]:
            out.append(x)
    return out
