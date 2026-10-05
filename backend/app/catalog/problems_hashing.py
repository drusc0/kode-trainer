import random
from typing import Any

from .base import Problem, distinct, ints, word

G, M = "google", "meta"

PROBLEMS = [
    # ---------------------------------------------------------------- arrays & hashing
    Problem(
        slug="contains-duplicate",
        title="Contains Duplicate",
        difficulty="Easy",
        pattern="arrays-hashing",
        topics=["Array", "Hash Table"],
        companies=[G, M],
        statement="Given an integer array `nums`, return `True` if any value appears at least twice, and `False` if every element is distinct.",
        entry="containsDuplicate",
        params=[("nums", "List[int]")],
        returns="bool",
        examples=[{"args": [[1, 2, 3, 1]]}, {"args": [[1, 2, 3, 4]]}, {"args": [[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]]}],
        constraints=["1 ≤ len(nums) ≤ 10⁵", "−10⁹ ≤ nums[i] ≤ 10⁹"],
        hints=["A set remembers what you've already seen in O(1) per lookup."],
        reference="""
class Solution:
    def containsDuplicate(self, nums):
        return len(set(nums)) < len(nums)
""",
        gen=lambda r: (
            [[[5]], [[-1, -1]]]
            + [[ints(r, r.randint(1, 30), -20, 20)] for _ in range(10)]
            + [[distinct(r, r.randint(1, 30), -1000, 1000)] for _ in range(6)]
            + [[distinct(r, 100_000, -(10**9), 10**9)], [[*list(range(99999)), 42]]]
        ),
    ),
    Problem(
        slug="valid-anagram",
        title="Valid Anagram",
        difficulty="Easy",
        pattern="arrays-hashing",
        topics=["String", "Hash Table", "Sorting"],
        companies=[G, M],
        statement="Given two strings `s` and `t`, return `True` if `t` is an anagram of `s`: the same letters, each used the same number of times, in any order.",
        entry="isAnagram",
        params=[("s", "str"), ("t", "str")],
        returns="bool",
        examples=[{"args": ["anagram", "nagaram"]}, {"args": ["rat", "car"]}],
        constraints=["1 ≤ len(s), len(t) ≤ 5 × 10⁴", "Lowercase English letters"],
        hints=["Count the letters of each string and compare the counts."],
        reference="""
class Solution:
    def isAnagram(self, s, t):
        return Counter(s) == Counter(t)
""",
        gen=lambda r: (
            [["a", "ab"], ["ab", "a"], ["aacc", "ccac"]]
            + [_anagram_pair(r, r.randint(1, 20), r.random() < 0.5) for _ in range(16)]
            + [_anagram_pair(r, 50_000, False), _anagram_pair(r, 50_000, True)]
        ),
    ),
    Problem(
        slug="majority-element",
        title="Majority Element",
        difficulty="Easy",
        pattern="arrays-hashing",
        topics=["Array", "Hash Table", "Counting"],
        companies=[G, M],
        statement="Given an array `nums` of size `n`, return the element that appears more than `⌊n / 2⌋` times. It always exists.\n\nBonus: O(n) time and O(1) extra space.",
        entry="majorityElement",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[3, 2, 3]]}, {"args": [[2, 2, 1, 1, 1, 2, 2]]}],
        constraints=["1 ≤ len(nums) ≤ 5 × 10⁴", "The majority element always exists."],
        hints=[
            "A Counter works in O(n) space.",
            "Boyer–Moore voting: keep a candidate and a count; matching values vote +1, others −1, and a count of 0 picks a new candidate.",
        ],
        reference="""
class Solution:
    def majorityElement(self, nums):
        return Counter(nums).most_common(1)[0][0]
""",
        gen=lambda r: (
            [[[7]], [[1, 2, 2]]] + [_majority(r, r.randint(1, 40)) for _ in range(16)] + [_majority(r, 50_000)]
        ),
    ),
    Problem(
        slug="roman-to-integer",
        title="Roman to Integer",
        difficulty="Easy",
        pattern="arrays-hashing",
        topics=["Math", "String", "Hash Table"],
        companies=[G, M],
        statement="Convert a Roman numeral to an integer. Symbols are `I=1, V=5, X=10, L=50, C=100, D=500, M=1000`.\n\nA smaller symbol written before a larger one is subtracted: `IV = 4`, `IX = 9`, `XL = 40`, `XC = 90`, `CD = 400`, `CM = 900`.",
        entry="romanToInt",
        params=[("s", "str")],
        returns="int",
        examples=[{"args": ["III"]}, {"args": ["LVIII"]}, {"args": ["MCMXCIV"], "note": "M + CM + XC + IV = 1994."}],
        constraints=["1 ≤ len(s) ≤ 15", "s is a valid numeral in [1, 3999]"],
        hints=["Scan left to right: subtract a symbol's value when the next symbol is larger, otherwise add it."],
        reference="""
class Solution:
    def romanToInt(self, s):
        v = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        total = 0
        for i, c in enumerate(s):
            if i + 1 < len(s) and v[c] < v[s[i + 1]]: total -= v[c]
            else: total += v[c]
        return total
""",
        gen=lambda r: (
            [[_roman(n)] for n in [1, 4, 9, 40, 3999, 3888]] + [[_roman(r.randint(1, 3999))] for _ in range(20)]
        ),
    ),
    Problem(
        slug="integer-to-roman",
        title="Integer to Roman",
        difficulty="Medium",
        pattern="arrays-hashing",
        topics=["Math", "String", "Hash Table"],
        companies=[G, M],
        statement="Convert an integer to a Roman numeral. Symbols are `I=1, V=5, X=10, L=50, C=100, D=500, M=1000`, and the six subtractive forms `IV, IX, XL, XC, CD, CM` are used instead of four repeated symbols (write `4` as `IV`, never `IIII`).",
        entry="intToRoman",
        params=[("num", "int")],
        returns="str",
        examples=[{"args": [3749]}, {"args": [58]}, {"args": [1994]}],
        constraints=["1 ≤ num ≤ 3999"],
        hints=[
            "List the 13 values from largest to smallest, including the subtractive pairs (1000, 900, 500, 400, …, 4, 1). Greedily take the largest that fits."
        ],
        reference="""
class Solution:
    def intToRoman(self, num):
        table = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'),
                 (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
        out = []
        for v, sym in table:
            k, num = divmod(num, v)
            out.append(sym * k)
        return ''.join(out)
""",
        gen=lambda r: (
            [[n] for n in [1, 4, 9, 14, 40, 90, 400, 900, 3999, 2024]] + [[r.randint(1, 3999)] for _ in range(14)]
        ),
    ),
    Problem(
        slug="longest-common-prefix",
        title="Longest Common Prefix",
        difficulty="Easy",
        pattern="arrays-hashing",
        topics=["String", "Trie"],
        companies=[G, M],
        statement='Return the longest string that is a prefix of every string in `strs`, or `""` if there is none.',
        entry="longestCommonPrefix",
        params=[("strs", "List[str]")],
        returns="str",
        examples=[{"args": [["flower", "flow", "flight"]]}, {"args": [["dog", "racecar", "car"]]}],
        constraints=["1 ≤ len(strs) ≤ 200", "0 ≤ len(strs[i]) ≤ 200", "Lowercase English letters"],
        hints=["Compare column by column: stop at the first index where some string ends or differs."],
        reference="""
class Solution:
    def longestCommonPrefix(self, strs):
        out = []
        for chars in zip(*strs):
            if len(set(chars)) > 1: break
            out.append(chars[0])
        return ''.join(out)
""",
        gen=lambda r: (
            [[[""]], [["a"]], [["ab", "a"]], [["", "b"]]]
            + [
                (lambda pre: [[pre + word(r, r.randint(0, 4), "ab") for _ in range(r.randint(1, 8))]])(
                    word(r, r.randint(0, 5), "abc")
                )
                for _ in range(16)
            ]
            + [[["x" * 199 + c for c in "abcdefghij" * 20]]]
        ),
    ),
    Problem(
        slug="ransom-note",
        title="Ransom Note",
        difficulty="Easy",
        pattern="arrays-hashing",
        topics=["String", "Hash Table", "Counting"],
        companies=[G, M],
        statement="Return `True` if `ransomNote` can be built from the letters of `magazine`, using each magazine letter at most once.",
        entry="canConstruct",
        params=[("ransomNote", "str"), ("magazine", "str")],
        returns="bool",
        examples=[{"args": ["a", "b"]}, {"args": ["aa", "ab"]}, {"args": ["aa", "aab"]}],
        constraints=["1 ≤ len(ransomNote), len(magazine) ≤ 10⁵", "Lowercase English letters"],
        hints=["Count the magazine letters, then spend them on the note."],
        reference="""
class Solution:
    def canConstruct(self, ransomNote, magazine):
        return not (Counter(ransomNote) - Counter(magazine))
""",
        gen=lambda r: (
            [[word(r, r.randint(1, 10), "abc"), word(r, r.randint(1, 20), "abc")] for _ in range(18)]
            + [[word(r, 50_000, "abcde"), word(r, 100_000, "abcde")]]
        ),
    ),
    Problem(
        slug="isomorphic-strings",
        title="Isomorphic Strings",
        difficulty="Easy",
        pattern="arrays-hashing",
        topics=["String", "Hash Table"],
        companies=[G],
        statement="Two strings are isomorphic if the characters of `s` can be replaced to get `t`: every occurrence of a character maps to the same character, and no two different characters map to the same one. Return `True` if `s` and `t` are isomorphic.",
        entry="isIsomorphic",
        params=[("s", "str"), ("t", "str")],
        returns="bool",
        examples=[
            {"args": ["egg", "add"]},
            {"args": ["foo", "bar"]},
            {"args": ["paper", "title"]},
            {"args": ["badc", "baba"]},
        ],
        constraints=["1 ≤ len(s) ≤ 5 × 10⁴", "len(t) == len(s)"],
        hints=["Keep two maps, s→t and t→s. A conflict in either direction means False."],
        reference="""
class Solution:
    def isIsomorphic(self, s, t):
        return len(set(s)) == len(set(t)) == len(set(zip(s, t)))
""",
        gen=lambda r: [_iso_pair(r, r.randint(1, 15)) for _ in range(20)] + [_iso_pair(r, 50_000)],
    ),
    Problem(
        slug="valid-sudoku",
        title="Valid Sudoku",
        difficulty="Medium",
        pattern="arrays-hashing",
        topics=["Array", "Hash Table", "Matrix"],
        companies=[G, M],
        statement='Decide whether a partially filled 9×9 Sudoku `board` is valid. Only the filled cells need to follow the rules:\n\n- each row contains the digits 1–9 at most once,\n- each column contains them at most once,\n- each of the nine 3×3 boxes contains them at most once.\n\nEmpty cells are `"."`. A valid board doesn\'t have to be solvable.',
        entry="isValidSudoku",
        params=[("board", "List[List[str]]")],
        returns="bool",
        examples=[
            {
                "args": [
                    [
                        ["5", "3", ".", ".", "7", ".", ".", ".", "."],
                        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
                        [".", "9", "8", ".", ".", ".", ".", "6", "."],
                        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
                        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
                        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
                        [".", "6", ".", ".", ".", ".", "2", "8", "."],
                        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
                        [".", ".", ".", ".", "8", ".", ".", "7", "9"],
                    ]
                ]
            },
            {
                "args": [
                    [
                        ["8", "3", ".", ".", "7", ".", ".", ".", "."],
                        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
                        [".", "9", "8", ".", ".", ".", ".", "6", "."],
                        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
                        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
                        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
                        [".", "6", ".", ".", ".", ".", "2", "8", "."],
                        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
                        [".", ".", ".", ".", "8", ".", ".", "7", "9"],
                    ]
                ],
                "note": "Two 8s in the first column (and in the top-left box).",
            },
        ],
        constraints=["board is 9×9", 'Each cell is "1"–"9" or "."'],
        hints=[
            "One pass: remember (row, digit), (col, digit) and (box, digit) in sets. Box index is (r // 3, c // 3)."
        ],
        reference="""
class Solution:
    def isValidSudoku(self, board):
        seen = set()
        for i in range(9):
            for j in range(9):
                d = board[i][j]
                if d == '.': continue
                keys = [('r', i, d), ('c', j, d), ('b', i // 3, j // 3, d)]
                if any(k in seen for k in keys): return False
                seen.update(keys)
        return True
""",
        gen=lambda r: [[_sudoku(r)] for _ in range(24)],
    ),
    Problem(
        slug="string-to-integer-atoi",
        title="String to Integer (atoi)",
        difficulty="Medium",
        pattern="arrays-hashing",
        topics=["String"],
        companies=[M, G],
        statement="Implement `myAtoi(s)`, which converts a string to a 32-bit signed integer:\n\n1. Skip leading spaces (`' '` only).\n2. Read an optional `+` or `-` sign.\n3. Read digits until a non-digit or the end. Leading zeros are fine. If no digits were read, the result is `0`.\n4. Clamp the result to `[−2³¹, 2³¹ − 1]`.\n\nEverything after the digits is ignored.",
        entry="myAtoi",
        params=[("s", "str")],
        returns="int",
        examples=[
            {"args": ["42"]},
            {"args": [" -042"]},
            {"args": ["1337c0d3"]},
            {"args": ["0-1"]},
            {"args": ["words and 987"]},
        ],
        constraints=["0 ≤ len(s) ≤ 200", "Letters, digits, spaces, '+', '-' and '.'"],
        hints=["Walk an index through the four steps in order. Clamp at the end (Python ints don't overflow)."],
        reference="""
class Solution:
    def myAtoi(self, s):
        i, n = 0, len(s)
        while i < n and s[i] == ' ': i += 1
        sign = 1
        if i < n and s[i] in '+-':
            sign = -1 if s[i] == '-' else 1
            i += 1
        num = 0
        while i < n and s[i].isdigit():
            num = num * 10 + int(s[i]); i += 1
        return max(-2**31, min(2**31 - 1, sign * num))
""",
        gen=lambda r: (
            [
                [""],
                [" "],
                ["+"],
                ["-"],
                ["+-12"],
                ["  +0 123"],
                ["2147483648"],
                ["-91283472332"],
                [".1"],
                ["00000-42a1234"],
            ]
            + [
                [
                    " " * r.randint(0, 3)
                    + r.choice(["", "+", "-", "+-"])
                    + word(r, r.randint(0, 14), "0123456789" * 3 + "a. -")
                ]
                for _ in range(20)
            ]
        ),
    ),
    Problem(
        slug="rotate-array",
        title="Rotate Array",
        difficulty="Medium",
        pattern="arrays-hashing",
        topics=["Array", "Math", "Two Pointers"],
        companies=[G, M],
        statement="Rotate `nums` to the right by `k` steps, in place, and return `nums`.\n\nBonus: O(1) extra space.",
        entry="rotate",
        params=[("nums", "List[int]"), ("k", "int")],
        returns="List[int]",
        examples=[{"args": [[1, 2, 3, 4, 5, 6, 7], 3]}, {"args": [[-1, -100, 3, 99], 2]}],
        constraints=["1 ≤ len(nums) ≤ 10⁵", "0 ≤ k ≤ 10⁵"],
        hints=["k can exceed n — use k % n.", "Reverse the whole array, then reverse the first k and the last n − k."],
        reference="""
class Solution:
    def rotate(self, nums, k):
        k %= len(nums)
        nums[:] = nums[-k:] + nums[:-k] if k else nums
        return nums
""",
        gen=lambda r: (
            [[[1], 0], [[1, 2], 3], [[1, 2, 3], 3]]
            + [[ints(r, n, -100, 100), r.randint(0, 2 * n)] for n in [r.randint(1, 20) for _ in range(16)]]
            + [[ints(r, 100_000, -1000, 1000), 99_999]]
        ),
    ),
    Problem(
        slug="next-permutation",
        title="Next Permutation",
        difficulty="Medium",
        pattern="arrays-hashing",
        topics=["Array", "Two Pointers"],
        companies=[M, G],
        statement="Rearrange `nums` into the next lexicographically greater permutation, in place, and return `nums`. If it's already the largest permutation, rearrange it into the smallest (sorted ascending).\n\nUse O(1) extra memory.",
        entry="nextPermutation",
        params=[("nums", "List[int]")],
        returns="List[int]",
        examples=[{"args": [[1, 2, 3]]}, {"args": [[3, 2, 1]]}, {"args": [[1, 1, 5]]}],
        constraints=["1 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 100"],
        hints=[
            "From the right, find the first i with nums[i] < nums[i + 1]. Everything after i is non-increasing.",
            "Swap nums[i] with the rightmost element bigger than it, then reverse the suffix after i.",
        ],
        reference="""
class Solution:
    def nextPermutation(self, nums):
        i = len(nums) - 2
        while i >= 0 and nums[i] >= nums[i + 1]: i -= 1
        if i >= 0:
            j = len(nums) - 1
            while nums[j] <= nums[i]: j -= 1
            nums[i], nums[j] = nums[j], nums[i]
        nums[i + 1:] = reversed(nums[i + 1:])
        return nums
""",
        gen=lambda r: (
            [[[1]], [[1, 3, 2]], [[2, 3, 1]], [[5, 4, 7, 5, 3, 2]], [[1, 5, 1]]]
            + [[ints(r, r.randint(1, 8), 0, 4)] for _ in range(16)]
            + [[sorted(ints(r, 100, 0, 100), reverse=True)], [ints(r, 100, 0, 100)]]
        ),
    ),
    Problem(
        slug="buildings-with-an-ocean-view",
        title="Buildings With an Ocean View",
        difficulty="Medium",
        pattern="arrays-hashing",
        topics=["Array", "Monotonic Stack"],
        companies=[M],
        statement="`heights[i]` is the height of building `i` in a row; the ocean is to the right of the last building. A building has an ocean view if every building to its right is strictly shorter. Return the indices of those buildings in increasing order.",
        entry="findBuildings",
        params=[("heights", "List[int]")],
        returns="List[int]",
        examples=[{"args": [[4, 2, 3, 1]]}, {"args": [[4, 3, 2, 1]]}, {"args": [[1, 3, 2, 4]]}],
        constraints=["1 ≤ len(heights) ≤ 10⁵", "1 ≤ heights[i] ≤ 10⁹"],
        hints=["Scan from the right, tracking the tallest building seen so far."],
        reference="""
class Solution:
    def findBuildings(self, heights):
        out, tallest = [], 0
        for i in range(len(heights) - 1, -1, -1):
            if heights[i] > tallest:
                out.append(i); tallest = heights[i]
        return out[::-1]
""",
        gen=lambda r: (
            [[[1]], [[2, 2, 2]], [[1, 2, 3]]]
            + [[ints(r, r.randint(1, 30), 1, 10)] for _ in range(16)]
            + [[ints(r, 100_000, 1, 10**9)]]
        ),
    ),
    Problem(
        slug="first-missing-positive",
        title="First Missing Positive",
        difficulty="Hard",
        pattern="arrays-hashing",
        topics=["Array", "Hash Table"],
        companies=[G, M],
        statement="Given an unsorted integer array `nums`, return the smallest positive integer that does not appear in it.\n\nThe target is O(n) time and O(1) extra space.",
        entry="firstMissingPositive",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[1, 2, 0]]}, {"args": [[3, 4, -1, 1]]}, {"args": [[7, 8, 9, 11, 12]]}],
        constraints=["1 ≤ len(nums) ≤ 10⁵", "−2³¹ ≤ nums[i] ≤ 2³¹ − 1"],
        hints=[
            "The answer is in [1, n + 1].",
            "Use the array itself as the hash set: swap each value v in [1, n] into slot v − 1, then find the first slot i with nums[i] ≠ i + 1.",
        ],
        reference="""
class Solution:
    def firstMissingPositive(self, nums):
        s = set(nums); k = 1
        while k in s: k += 1
        return k
""",
        gen=lambda r: (
            [[[1]], [[2]], [[1, 1]], [[-5]], [[2, 1]]]
            + [[ints(r, r.randint(1, 20), -3, 12)] for _ in range(16)]
            + [[r.sample(range(1, 100_001), 100_000)], [ints(r, 100_000, -(2**31), 2**31 - 1)]]
        ),
    ),
    # ---------------------------------------------------------------- two pointers
    Problem(
        slug="valid-palindrome",
        title="Valid Palindrome",
        difficulty="Easy",
        pattern="two-pointers",
        topics=["String", "Two Pointers"],
        companies=[M, G],
        statement="A phrase is a palindrome if, after lowercasing it and removing every non-alphanumeric character, it reads the same forwards and backwards. Return `True` if `s` is a palindrome.",
        entry="isPalindrome",
        params=[("s", "str")],
        returns="bool",
        examples=[{"args": ["A man, a plan, a canal: Panama"]}, {"args": ["race a car"]}, {"args": [" "]}],
        constraints=["1 ≤ len(s) ≤ 2 × 10⁵", "Printable ASCII"],
        hints=["Two pointers from both ends; skip non-alphanumeric characters and compare lowercase."],
        reference="""
class Solution:
    def isPalindrome(self, s):
        t = [c.lower() for c in s if c.isalnum()]
        return t == t[::-1]
""",
        gen=lambda r: (
            [["0P"], ["a."], [".,"], ["Aa"]]
            + [
                [(lambda h: h + r.choice(["", "x", "!"]) + h[::-1])(word(r, r.randint(0, 10), "aAb1 ,."))]
                for _ in range(10)
            ]
            + [[word(r, r.randint(1, 20), "aAbB1 ,:")] for _ in range(8)]
            + [[(lambda h: h + h[::-1].upper())(word(r, 100_000, "abc ,."))]]
        ),
    ),
    Problem(
        slug="two-sum-ii-input-array-is-sorted",
        title="Two Sum II - Input Array Is Sorted",
        difficulty="Medium",
        pattern="two-pointers",
        topics=["Array", "Two Pointers", "Binary Search"],
        companies=[G, M],
        statement="`numbers` is sorted in non-decreasing order. Return the **1-indexed** positions `[i, j]` (`i < j`) of the two numbers that add up to `target`. Exactly one solution exists.\n\nUse only O(1) extra space.",
        entry="twoSum",
        params=[("numbers", "List[int]"), ("target", "int")],
        returns="List[int]",
        examples=[{"args": [[2, 7, 11, 15], 9]}, {"args": [[2, 3, 4], 6]}, {"args": [[-1, 0], -1]}],
        constraints=["2 ≤ len(numbers) ≤ 3 × 10⁴", "−1000 ≤ numbers[i] ≤ 1000", "Exactly one solution"],
        hints=["Start at both ends. Sum too small → move left up; too big → move right down."],
        reference="""
class Solution:
    def twoSum(self, numbers, target):
        l, r = 0, len(numbers) - 1
        while True:
            s = numbers[l] + numbers[r]
            if s == target: return [l + 1, r + 1]
            if s < target: l += 1
            else: r -= 1
""",
        gen=lambda r: [_sorted_two_sum(r, r.randint(2, 30)) for _ in range(20)] + [_sorted_two_sum(r, 30_000)],
    ),
    Problem(
        slug="move-zeroes",
        title="Move Zeroes",
        difficulty="Easy",
        pattern="two-pointers",
        topics=["Array", "Two Pointers"],
        companies=[M, G],
        statement="Move every `0` in `nums` to the end while keeping the relative order of the non-zero elements. Do it in place and return `nums`.",
        entry="moveZeroes",
        params=[("nums", "List[int]")],
        returns="List[int]",
        examples=[{"args": [[0, 1, 0, 3, 12]]}, {"args": [[0]]}],
        constraints=["1 ≤ len(nums) ≤ 10⁴"],
        hints=["Keep a write pointer for the next non-zero slot; swap each non-zero into it."],
        reference="""
class Solution:
    def moveZeroes(self, nums):
        nz = [x for x in nums if x != 0]
        nums[:] = nz + [0] * (len(nums) - len(nz))
        return nums
""",
        gen=lambda r: (
            [[[1]], [[0, 0, 1]], [[1, 0]]]
            + [[[r.choice([0, 0, r.randint(-9, 9)]) for _ in range(r.randint(1, 25))]] for _ in range(16)]
            + [[[r.choice([0, r.randint(-9, 9)]) for _ in range(10_000)]]]
        ),
    ),
    Problem(
        slug="merge-sorted-array",
        title="Merge Sorted Array",
        difficulty="Easy",
        pattern="two-pointers",
        topics=["Array", "Two Pointers", "Sorting"],
        companies=[M, G],
        statement="`nums1` has length `m + n`: its first `m` values are sorted and the last `n` are `0` placeholders. `nums2` holds `n` sorted values. Merge `nums2` into `nums1` in place so `nums1` is sorted, and return `nums1`.\n\nTry O(m + n) time.",
        entry="merge",
        params=[("nums1", "List[int]"), ("m", "int"), ("nums2", "List[int]"), ("n", "int")],
        returns="List[int]",
        examples=[
            {"args": [[1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3]},
            {"args": [[1], 1, [], 0]},
            {"args": [[0], 0, [1], 1]},
        ],
        constraints=["0 ≤ m, n ≤ 200", "1 ≤ m + n"],
        hints=["Fill nums1 from the back: compare the largest remaining values of each array."],
        reference="""
class Solution:
    def merge(self, nums1, m, nums2, n):
        nums1[:] = sorted(nums1[:m] + nums2)
        return nums1
""",
        gen=lambda r: (
            [_merge_case(r, r.randint(0, 12), r.randint(0, 12)) for _ in range(18)] + [_merge_case(r, 200, 200)]
        ),
    ),
    Problem(
        slug="squares-of-a-sorted-array",
        title="Squares of a Sorted Array",
        difficulty="Easy",
        pattern="two-pointers",
        topics=["Array", "Two Pointers", "Sorting"],
        companies=[G, M],
        statement="Given `nums` sorted in non-decreasing order, return the squares of each number, also sorted.\n\nCan you do it in O(n) without sorting?",
        entry="sortedSquares",
        params=[("nums", "List[int]")],
        returns="List[int]",
        examples=[{"args": [[-4, -1, 0, 3, 10]]}, {"args": [[-7, -3, 2, 3, 11]]}],
        constraints=["1 ≤ len(nums) ≤ 10⁴", "−10⁴ ≤ nums[i] ≤ 10⁴"],
        hints=["The largest square is at one of the two ends. Fill the answer from the back."],
        reference="""
class Solution:
    def sortedSquares(self, nums):
        return sorted(x * x for x in nums)
""",
        gen=lambda r: (
            [[[0]], [[-1]], [[-3, -2, -1]]]
            + [[sorted(ints(r, r.randint(1, 30), -20, 20))] for _ in range(16)]
            + [[sorted(ints(r, 10_000, -(10**4), 10**4))]]
        ),
    ),
    Problem(
        slug="sort-colors",
        title="Sort Colors",
        difficulty="Medium",
        pattern="two-pointers",
        topics=["Array", "Two Pointers", "Sorting"],
        companies=[M, G],
        statement="`nums` contains only `0` (red), `1` (white) and `2` (blue). Sort it in place so equal colours are adjacent in the order red, white, blue, and return `nums`.\n\nDon't use a library sort. Bonus: a single pass with O(1) extra space.",
        entry="sortColors",
        params=[("nums", "List[int]")],
        returns="List[int]",
        examples=[{"args": [[2, 0, 2, 1, 1, 0]]}, {"args": [[2, 0, 1]]}],
        constraints=["1 ≤ len(nums) ≤ 300", "nums[i] ∈ {0, 1, 2}"],
        hints=[
            "Dutch national flag: keep `low`, `mid`, `high`. A 0 swaps to low, a 2 swaps to high (don't advance mid), a 1 just advances mid."
        ],
        reference="""
class Solution:
    def sortColors(self, nums):
        c = Counter(nums)
        nums[:] = [0] * c[0] + [1] * c[1] + [2] * c[2]
        return nums
""",
        gen=lambda r: [[[0]], [[2, 2]], [[1, 0]]] + [[ints(r, r.randint(1, 300), 0, 2)] for _ in range(18)],
    ),
    Problem(
        slug="3sum-closest",
        title="3Sum Closest",
        difficulty="Medium",
        pattern="two-pointers",
        topics=["Array", "Two Pointers", "Sorting"],
        companies=[M, G],
        statement="Find three numbers at different indices of `nums` whose sum is closest to `target`, and return that sum. Exactly one closest sum exists.",
        entry="threeSumClosest",
        params=[("nums", "List[int]"), ("target", "int")],
        returns="int",
        examples=[{"args": [[-1, 2, 1, -4], 1], "note": "-1 + 2 + 1 = 2."}, {"args": [[0, 0, 0], 1]}],
        constraints=["3 ≤ len(nums) ≤ 500", "−1000 ≤ nums[i] ≤ 1000", "−10⁴ ≤ target ≤ 10⁴"],
        hints=["Sort, fix the first number, then move two pointers toward the target, remembering the best sum."],
        reference="""
class Solution:
    def threeSumClosest(self, nums, target):
        nums.sort(); best = nums[0] + nums[1] + nums[2]
        for i in range(len(nums) - 2):
            l, r = i + 1, len(nums) - 1
            while l < r:
                s = nums[i] + nums[l] + nums[r]
                if abs(s - target) < abs(best - target): best = s
                if s < target: l += 1
                elif s > target: r -= 1
                else: return s
        return best
""",
        # all values are multiples of 3 and target ≡ 1 (mod 3), so no two sums are equally close
        gen=lambda r: (
            [
                [[3 * x for x in ints(r, n, -100, 100)], 3 * r.randint(-200, 200) + 1]
                for n in [r.randint(3, 25) for _ in range(20)]
            ]
            + [[[3 * x for x in ints(r, 500, -333, 333)], 3 * r.randint(-3000, 3000) + 1]]
        ),
    ),
    Problem(
        slug="is-subsequence",
        title="Is Subsequence",
        difficulty="Easy",
        pattern="two-pointers",
        topics=["String", "Two Pointers"],
        companies=[G, M],
        statement='Return `True` if `s` is a subsequence of `t`: `s` can be formed by deleting some (or no) characters of `t` without reordering the rest. For example, `"ace"` is a subsequence of `"abcde"`.',
        entry="isSubsequence",
        params=[("s", "str"), ("t", "str")],
        returns="bool",
        examples=[{"args": ["abc", "ahbgdc"]}, {"args": ["axc", "ahbgdc"]}],
        constraints=["0 ≤ len(s) ≤ 100", "0 ≤ len(t) ≤ 10⁴"],
        hints=["Walk through t once, advancing a pointer in s whenever the characters match."],
        reference="""
class Solution:
    def isSubsequence(self, s, t):
        it = iter(t)
        return all(c in it for c in s)
""",
        gen=lambda r: (
            [["", ""], ["", "a"], ["a", ""], ["aa", "a"]]
            + [[word(r, r.randint(0, 5), "abc"), word(r, r.randint(0, 15), "abc")] for _ in range(18)]
            + [[word(r, 100, "ab"), word(r, 10_000, "abc")]]
        ),
    ),
    Problem(
        slug="4sum",
        title="4Sum",
        difficulty="Medium",
        pattern="two-pointers",
        topics=["Array", "Two Pointers", "Sorting"],
        companies=[G, M],
        statement="Return all **unique** quadruplets `[a, b, c, d]` of values from four different indices of `nums` with `a + b + c + d == target`. Any order is accepted, but there must be no duplicate quadruplets.",
        entry="fourSum",
        params=[("nums", "List[int]"), ("target", "int")],
        returns="List[List[int]]",
        examples=[{"args": [[1, 0, -1, 0, -2, 2], 0]}, {"args": [[2, 2, 2, 2, 2], 8]}],
        constraints=["1 ≤ len(nums) ≤ 200", "−10⁹ ≤ nums[i], target ≤ 10⁹"],
        hints=[
            "Sort, fix two numbers with nested loops, then two-pointer the rest. Skip equal neighbours at every level."
        ],
        reference="""
class Solution:
    def fourSum(self, nums, target):
        nums.sort(); n = len(nums); res = []
        for i in range(n):
            if i and nums[i] == nums[i - 1]: continue
            for j in range(i + 1, n):
                if j > i + 1 and nums[j] == nums[j - 1]: continue
                l, r = j + 1, n - 1
                while l < r:
                    s = nums[i] + nums[j] + nums[l] + nums[r]
                    if s < target: l += 1
                    elif s > target: r -= 1
                    else:
                        res.append([nums[i], nums[j], nums[l], nums[r]])
                        while l < r and nums[l] == nums[l + 1]: l += 1
                        l += 1; r -= 1
        return res
""",
        gen=lambda r: (
            [[[0], 0], [[1, 1, 1], 3], [[10**9] * 4, -294967296]]
            + [[ints(r, r.randint(1, 30), -10, 10), r.randint(-10, 10)] for _ in range(16)]
            + [[ints(r, 200, -50, 50), r.randint(-20, 20)]]
        ),
        compare="nested_sorted",
    ),
    # ---------------------------------------------------------------- sliding window
    Problem(
        slug="contains-duplicate-ii",
        title="Contains Duplicate II",
        difficulty="Easy",
        pattern="sliding-window",
        topics=["Array", "Hash Table", "Sliding Window"],
        companies=[G, M],
        statement="Return `True` if there are two different indices `i` and `j` with `nums[i] == nums[j]` and `|i − j| ≤ k`.",
        entry="containsNearbyDuplicate",
        params=[("nums", "List[int]"), ("k", "int")],
        returns="bool",
        examples=[{"args": [[1, 2, 3, 1], 3]}, {"args": [[1, 0, 1, 1], 1]}, {"args": [[1, 2, 3, 1, 2, 3], 2]}],
        constraints=["1 ≤ len(nums) ≤ 10⁵", "0 ≤ k ≤ 10⁵"],
        hints=["Remember the last index of each value; or keep a set of the last k values."],
        reference="""
class Solution:
    def containsNearbyDuplicate(self, nums, k):
        last = {}
        for i, x in enumerate(nums):
            if x in last and i - last[x] <= k: return True
            last[x] = i
        return False
""",
        gen=lambda r: (
            [[[1], 0], [[1, 1], 0], [[1, 1], 1]]
            + [[ints(r, r.randint(1, 30), 0, 15), r.randint(0, 6)] for _ in range(16)]
            + [[list(range(50_000)) * 2, 49_999], [list(range(50_000)) * 2, 50_000]]
        ),
    ),
    Problem(
        slug="maximum-average-subarray-i",
        title="Maximum Average Subarray I",
        difficulty="Easy",
        pattern="sliding-window",
        topics=["Array", "Sliding Window"],
        companies=[G, M],
        statement="Find the contiguous subarray of length exactly `k` with the largest average, and return that average. Answers within 10⁻⁵ are accepted.",
        entry="findMaxAverage",
        params=[("nums", "List[int]"), ("k", "int")],
        returns="float",
        examples=[{"args": [[1, 12, -5, -6, 50, 3], 4], "note": "(12 − 5 − 6 + 50) / 4 = 12.75."}, {"args": [[5], 1]}],
        constraints=["1 ≤ k ≤ len(nums) ≤ 10⁵", "−10⁴ ≤ nums[i] ≤ 10⁴"],
        hints=["Slide a window of size k: add the entering value, subtract the leaving one. Divide once at the end."],
        reference="""
class Solution:
    def findMaxAverage(self, nums, k):
        s = best = sum(nums[:k])
        for i in range(k, len(nums)):
            s += nums[i] - nums[i - k]
            best = max(best, s)
        return best / k
""",
        gen=lambda r: (
            [[ints(r, n, -100, 100), r.randint(1, n)] for n in [r.randint(1, 30) for _ in range(18)]]
            + [[ints(r, 100_000, -(10**4), 10**4), 777]]
        ),
        compare="float",
    ),
    Problem(
        slug="permutation-in-string",
        title="Permutation in String",
        difficulty="Medium",
        pattern="sliding-window",
        topics=["String", "Hash Table", "Sliding Window"],
        companies=[M, G],
        statement="Return `True` if `s2` contains a permutation of `s1` as a contiguous substring.",
        entry="checkInclusion",
        params=[("s1", "str"), ("s2", "str")],
        returns="bool",
        examples=[{"args": ["ab", "eidbaooo"], "note": '"ba" is in s2.'}, {"args": ["ab", "eidboaoo"]}],
        constraints=["1 ≤ len(s1), len(s2) ≤ 10⁴", "Lowercase English letters"],
        hints=["Slide a window of length len(s1) over s2 and compare letter counts."],
        reference="""
class Solution:
    def checkInclusion(self, s1, s2):
        k = len(s1); need = Counter(s1); win = Counter(s2[:k])
        if win == need: return True
        for i in range(k, len(s2)):
            win[s2[i]] += 1; win[s2[i - k]] -= 1
            if win == need: return True
        return False
""",
        gen=lambda r: (
            [["a", "a"], ["abc", "ab"], ["adc", "dcda"]]
            + [[word(r, r.randint(1, 4), "abc"), word(r, r.randint(1, 20), "abc")] for _ in range(18)]
            + [[word(r, 26, "abcdefghijklmnopqrstuvwxyz"), word(r, 10_000, "abcdefghijklmnopqrstuvwxyz")]]
        ),
    ),
    Problem(
        slug="find-all-anagrams-in-a-string",
        title="Find All Anagrams in a String",
        difficulty="Medium",
        pattern="sliding-window",
        topics=["String", "Hash Table", "Sliding Window"],
        companies=[M, G],
        statement="Return the start indices of every substring of `s` that is an anagram of `p`, in any order.",
        entry="findAnagrams",
        params=[("s", "str"), ("p", "str")],
        returns="List[int]",
        examples=[{"args": ["cbaebabacd", "abc"]}, {"args": ["abab", "ab"]}],
        constraints=["1 ≤ len(s), len(p) ≤ 3 × 10⁴", "Lowercase English letters"],
        hints=["Fixed-size window of len(p); keep counts in sync as it slides and record each match."],
        reference="""
class Solution:
    def findAnagrams(self, s, p):
        k = len(p); need = Counter(p); win = Counter(s[:k]); out = []
        if len(s) >= k and win == need: out.append(0)
        for i in range(k, len(s)):
            win[s[i]] += 1; win[s[i - k]] -= 1
            if win == need: out.append(i - k + 1)
        return out
""",
        gen=lambda r: (
            [["a", "ab"], ["aaaa", "a"]]
            + [[word(r, r.randint(1, 25), "ab"), word(r, r.randint(1, 3), "ab")] for _ in range(18)]
            + [[word(r, 30_000, "abc"), word(r, 5, "abc")]]
        ),
        compare="sorted",
    ),
    Problem(
        slug="minimum-size-subarray-sum",
        title="Minimum Size Subarray Sum",
        difficulty="Medium",
        pattern="sliding-window",
        topics=["Array", "Sliding Window", "Prefix Sum"],
        companies=[G, M],
        statement="Given positive integers `nums` and a positive `target`, return the length of the shortest contiguous subarray whose sum is at least `target`, or `0` if none exists.",
        entry="minSubArrayLen",
        params=[("target", "int"), ("nums", "List[int]")],
        returns="int",
        examples=[
            {"args": [7, [2, 3, 1, 2, 4, 3]], "note": "[4, 3]"},
            {"args": [4, [1, 4, 4]]},
            {"args": [11, [1, 1, 1, 1, 1, 1, 1, 1]]},
        ],
        constraints=["1 ≤ target ≤ 10⁹", "1 ≤ len(nums) ≤ 10⁵", "1 ≤ nums[i] ≤ 10⁴"],
        hints=[
            "All values are positive, so grow the right edge, then shrink the left while the sum still reaches target."
        ],
        reference="""
class Solution:
    def minSubArrayLen(self, target, nums):
        l = s = 0; best = inf
        for r, x in enumerate(nums):
            s += x
            while s >= target:
                best = min(best, r - l + 1); s -= nums[l]; l += 1
        return 0 if best == inf else best
""",
        gen=lambda r: (
            [[r.randint(1, 60), ints(r, r.randint(1, 25), 1, 10)] for _ in range(18)]
            + [[10**8, ints(r, 100_000, 1, 10**4)], [10**9, [1] * 100_000]]
        ),
    ),
    Problem(
        slug="max-consecutive-ones-iii",
        title="Max Consecutive Ones III",
        difficulty="Medium",
        pattern="sliding-window",
        topics=["Array", "Sliding Window"],
        companies=[M, G],
        statement="Given a binary array `nums` and an integer `k`, return the length of the longest run of `1`s you can get by flipping at most `k` zeros.",
        entry="longestOnes",
        params=[("nums", "List[int]"), ("k", "int")],
        returns="int",
        examples=[
            {"args": [[1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2]},
            {"args": [[0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3]},
        ],
        constraints=["1 ≤ len(nums) ≤ 10⁵", "0 ≤ k ≤ len(nums)"],
        hints=["Longest window containing at most k zeros."],
        reference="""
class Solution:
    def longestOnes(self, nums, k):
        l = zeros = best = 0
        for r, x in enumerate(nums):
            zeros += x == 0
            while zeros > k:
                zeros -= nums[l] == 0; l += 1
            best = max(best, r - l + 1)
        return best
""",
        gen=lambda r: (
            [[[0], 0], [[0], 1], [[1, 1], 0]]
            + [[ints(r, n, 0, 1), r.randint(0, n)] for n in [r.randint(1, 30) for _ in range(16)]]
            + [[ints(r, 100_000, 0, 1), 1000]]
        ),
    ),
    Problem(
        slug="fruit-into-baskets",
        title="Fruit Into Baskets",
        difficulty="Medium",
        pattern="sliding-window",
        topics=["Array", "Hash Table", "Sliding Window"],
        companies=[G],
        statement="`fruits[i]` is the type of fruit on tree `i` in a row. You have two baskets, each holding one type (any amount). Start at any tree and pick one fruit from every tree moving right, stopping when a fruit fits neither basket. Return the most fruit you can pick.\n\nIn other words: the longest subarray with at most two distinct values.",
        entry="totalFruit",
        params=[("fruits", "List[int]")],
        returns="int",
        examples=[{"args": [[1, 2, 1]]}, {"args": [[0, 1, 2, 2]]}, {"args": [[1, 2, 3, 2, 2]]}],
        constraints=["1 ≤ len(fruits) ≤ 10⁵", "0 ≤ fruits[i] < len(fruits)"],
        hints=["Window with a Counter; shrink from the left while it holds more than two types."],
        reference="""
class Solution:
    def totalFruit(self, fruits):
        cnt = Counter(); l = best = 0
        for r, f in enumerate(fruits):
            cnt[f] += 1
            while len(cnt) > 2:
                cnt[fruits[l]] -= 1
                if cnt[fruits[l]] == 0: del cnt[fruits[l]]
                l += 1
            best = max(best, r - l + 1)
        return best
""",
        gen=lambda r: (
            [[[0]], [[3, 3, 3, 1, 2, 1, 1, 2, 3, 3, 4]]]
            + [[ints(r, n, 0, min(n - 1, 3))] for n in [r.randint(1, 30) for _ in range(18)]]
            + [[ints(r, 100_000, 0, 3)]]
        ),
    ),
    Problem(
        slug="longest-substring-with-at-most-k-distinct-characters",
        title="Longest Substring with At Most K Distinct Characters",
        difficulty="Medium",
        pattern="sliding-window",
        topics=["String", "Hash Table", "Sliding Window"],
        companies=[M, G],
        statement="Return the length of the longest substring of `s` that contains at most `k` distinct characters.",
        entry="lengthOfLongestSubstringKDistinct",
        params=[("s", "str"), ("k", "int")],
        returns="int",
        examples=[{"args": ["eceba", 2], "note": '"ece"'}, {"args": ["aa", 1]}],
        constraints=["1 ≤ len(s) ≤ 5 × 10⁴", "0 ≤ k ≤ 50"],
        hints=["Same as Fruit Into Baskets with k instead of 2."],
        reference="""
class Solution:
    def lengthOfLongestSubstringKDistinct(self, s, k):
        cnt = Counter(); l = best = 0
        for r, c in enumerate(s):
            cnt[c] += 1
            while len(cnt) > k:
                cnt[s[l]] -= 1
                if cnt[s[l]] == 0: del cnt[s[l]]
                l += 1
            best = max(best, r - l + 1)
        return best
""",
        gen=lambda r: (
            [["a", 0], ["abc", 5]]
            + [[word(r, r.randint(1, 30), "abcde"), r.randint(0, 5)] for _ in range(18)]
            + [[word(r, 50_000, "abcdefghij"), 4]]
        ),
    ),
    Problem(
        slug="sliding-window-maximum",
        title="Sliding Window Maximum",
        difficulty="Hard",
        pattern="sliding-window",
        topics=["Array", "Queue", "Sliding Window", "Monotonic Queue"],
        companies=[G, M],
        statement="A window of size `k` slides over `nums` from left to right, one position at a time. Return the maximum of each window.",
        entry="maxSlidingWindow",
        params=[("nums", "List[int]"), ("k", "int")],
        returns="List[int]",
        examples=[{"args": [[1, 3, -1, -3, 5, 3, 6, 7], 3]}, {"args": [[1], 1]}],
        constraints=["1 ≤ len(nums) ≤ 10⁵", "1 ≤ k ≤ len(nums)"],
        hints=[
            "Keep a deque of indices whose values are decreasing. The front is the current max.",
            "Pop smaller values from the back before pushing; pop the front when it leaves the window.",
        ],
        reference="""
class Solution:
    def maxSlidingWindow(self, nums, k):
        q = deque(); out = []
        for i, x in enumerate(nums):
            while q and nums[q[-1]] <= x: q.pop()
            q.append(i)
            if q[0] <= i - k: q.popleft()
            if i >= k - 1: out.append(nums[q[0]])
        return out
""",
        gen=lambda r: (
            [[ints(r, n, -10, 10), r.randint(1, n)] for n in [r.randint(1, 30) for _ in range(18)]]
            + [[ints(r, 100_000, -(10**4), 10**4), 1000], [list(range(100_000, 0, -1)), 50_000]]
        ),
    ),
    # ---------------------------------------------------------------- prefix sums
    Problem(
        slug="find-pivot-index",
        title="Find Pivot Index",
        difficulty="Easy",
        pattern="prefix-sum",
        topics=["Array", "Prefix Sum"],
        companies=[G, M],
        statement="The pivot index is where the sum of everything strictly to its left equals the sum of everything strictly to its right (an empty side sums to 0). Return the leftmost pivot index, or `-1` if there is none.",
        entry="pivotIndex",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[1, 7, 3, 6, 5, 6]]}, {"args": [[1, 2, 3]]}, {"args": [[2, 1, -1]]}],
        constraints=["1 ≤ len(nums) ≤ 10⁴", "−1000 ≤ nums[i] ≤ 1000"],
        hints=["right sum = total − left sum − nums[i]."],
        reference="""
class Solution:
    def pivotIndex(self, nums):
        total, left = sum(nums), 0
        for i, x in enumerate(nums):
            if left == total - left - x: return i
            left += x
        return -1
""",
        gen=lambda r: (
            [[[0]], [[0, 0]], [[-1, -1, -1, 0, 1, 1]]]
            + [[ints(r, r.randint(1, 15), -3, 3)] for _ in range(18)]
            + [[ints(r, 10_000, -1000, 1000)], [[0] * 10_000]]
        ),
    ),
    Problem(
        slug="range-sum-query-immutable",
        title="Range Sum Query - Immutable",
        difficulty="Easy",
        pattern="prefix-sum",
        kind="design",
        topics=["Array", "Design", "Prefix Sum"],
        companies=[M, G],
        statement="Design `NumArray`:\n\n- `NumArray(nums)` stores the array.\n- `sumRange(left, right)` returns `nums[left] + … + nums[right]` (inclusive).\n\nThere can be many queries, so each one should be O(1).",
        entry="NumArray",
        params=[("operations", "List[str]"), ("arguments", "List[list]")],
        returns="List",
        starter="""
class NumArray:

    def __init__(self, nums: List[int]):


    def sumRange(self, left: int, right: int) -> int:

""",
        examples=[
            {
                "args": [
                    {
                        "ops": ["NumArray", "sumRange", "sumRange", "sumRange"],
                        "args": [[[-2, 0, 3, -5, 2, -1]], [0, 2], [2, 5], [0, 5]],
                    }
                ]
            }
        ],
        constraints=["1 ≤ len(nums) ≤ 10⁴", "0 ≤ left ≤ right < len(nums)", "At most 10⁴ calls to sumRange"],
        hints=["Precompute prefix[i] = sum of the first i values; then sumRange = prefix[right + 1] − prefix[left]."],
        reference="""
class NumArray:
    def __init__(self, nums):
        self.p = [0, *accumulate(nums)]
    def sumRange(self, left, right):
        return self.p[right + 1] - self.p[left]
""",
        gen=lambda r: (
            [_range_sum_case(r, r.randint(1, 15), r.randint(1, 15)) for _ in range(14)]
            + [_range_sum_case(r, 10_000, 10_000)]
        ),
    ),
    Problem(
        slug="contiguous-array",
        title="Contiguous Array",
        difficulty="Medium",
        pattern="prefix-sum",
        topics=["Array", "Hash Table", "Prefix Sum"],
        companies=[M, G],
        statement="Given a binary array `nums`, return the length of the longest contiguous subarray with an equal number of `0`s and `1`s.",
        entry="findMaxLength",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[0, 1]]}, {"args": [[0, 1, 0]]}, {"args": [[0, 1, 1, 1, 1, 1, 0, 0, 0]]}],
        constraints=["1 ≤ len(nums) ≤ 10⁵"],
        hints=[
            "Treat 0 as −1. A balanced subarray has sum 0.",
            "Remember the first index where each running sum appears; equal sums at i and j mean (i, j] is balanced.",
        ],
        reference="""
class Solution:
    def findMaxLength(self, nums):
        first = {0: -1}; s = best = 0
        for i, x in enumerate(nums):
            s += 1 if x else -1
            if s in first: best = max(best, i - first[s])
            else: first[s] = i
        return best
""",
        gen=lambda r: (
            [[[0]], [[1, 1]]] + [[ints(r, r.randint(1, 30), 0, 1)] for _ in range(18)] + [[ints(r, 100_000, 0, 1)]]
        ),
    ),
    Problem(
        slug="continuous-subarray-sum",
        title="Continuous Subarray Sum",
        difficulty="Medium",
        pattern="prefix-sum",
        topics=["Array", "Hash Table", "Prefix Sum", "Math"],
        companies=[M, G],
        statement="Return `True` if `nums` has a contiguous subarray of **length at least 2** whose sum is a multiple of `k` (0 counts as a multiple).",
        entry="checkSubarraySum",
        params=[("nums", "List[int]"), ("k", "int")],
        returns="bool",
        examples=[
            {"args": [[23, 2, 4, 6, 7], 6], "note": "[2, 4] sums to 6."},
            {"args": [[23, 2, 6, 4, 7], 6]},
            {"args": [[23, 2, 6, 4, 7], 13]},
        ],
        constraints=["1 ≤ len(nums) ≤ 10⁵", "0 ≤ nums[i] ≤ 10⁹", "1 ≤ k ≤ 2³¹ − 1"],
        hints=[
            "Two prefix sums with the same remainder mod k bound a subarray whose sum is a multiple of k.",
            "Store the first index of each remainder (seed {0: −1}) and check the gap is ≥ 2.",
        ],
        reference="""
class Solution:
    def checkSubarraySum(self, nums, k):
        first = {0: -1}; s = 0
        for i, x in enumerate(nums):
            s = (s + x) % k
            if s in first:
                if i - first[s] >= 2: return True
            else:
                first[s] = i
        return False
""",
        gen=lambda r: (
            [[[0], 1], [[0, 0], 1], [[5, 0, 0, 0], 3], [[1, 0], 2], [[2, 4, 3], 6]]
            + [[ints(r, r.randint(1, 12), 0, 20), r.randint(1, 30)] for _ in range(16)]
            + [[ints(r, 100_000, 0, 10**9), 2**31 - 1], [[1] * 100_000, 200_000]]
        ),
    ),
    Problem(
        slug="subarray-sums-divisible-by-k",
        title="Subarray Sums Divisible by K",
        difficulty="Medium",
        pattern="prefix-sum",
        topics=["Array", "Hash Table", "Prefix Sum"],
        companies=[M, G],
        statement="Return the number of non-empty contiguous subarrays of `nums` whose sum is divisible by `k`.",
        entry="subarraysDivByK",
        params=[("nums", "List[int]"), ("k", "int")],
        returns="int",
        examples=[{"args": [[4, 5, 0, -2, -3, 1], 5]}, {"args": [[5], 9]}],
        constraints=["1 ≤ len(nums) ≤ 3 × 10⁴", "−10⁴ ≤ nums[i] ≤ 10⁴", "2 ≤ k ≤ 10⁴"],
        hints=["Count prefix sums by remainder mod k. Each earlier prefix with the same remainder makes one subarray."],
        reference="""
class Solution:
    def subarraysDivByK(self, nums, k):
        cnt = Counter({0: 1}); s = ans = 0
        for x in nums:
            s = (s + x) % k
            ans += cnt[s]; cnt[s] += 1
        return ans
""",
        gen=lambda r: (
            [[ints(r, r.randint(1, 30), -10, 10), r.randint(2, 7)] for _ in range(18)]
            + [[ints(r, 30_000, -(10**4), 10**4), r.randint(2, 50)]]
        ),
    ),
    Problem(
        slug="range-sum-query-2d-immutable",
        title="Range Sum Query 2D - Immutable",
        difficulty="Medium",
        pattern="prefix-sum",
        kind="design",
        topics=["Array", "Design", "Matrix", "Prefix Sum"],
        companies=[M, G],
        statement="Design `NumMatrix`:\n\n- `NumMatrix(matrix)` stores a 2-D matrix.\n- `sumRegion(row1, col1, row2, col2)` returns the sum of the rectangle with top-left `(row1, col1)` and bottom-right `(row2, col2)`, inclusive.\n\n`sumRegion` should run in O(1).",
        entry="NumMatrix",
        params=[("operations", "List[str]"), ("arguments", "List[list]")],
        returns="List",
        starter="""
class NumMatrix:

    def __init__(self, matrix: List[List[int]]):


    def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:

""",
        examples=[
            {
                "args": [
                    {
                        "ops": ["NumMatrix", "sumRegion", "sumRegion", "sumRegion"],
                        "args": [
                            [[[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]]],
                            [2, 1, 4, 3],
                            [1, 1, 2, 2],
                            [1, 2, 2, 4],
                        ],
                    }
                ]
            }
        ],
        constraints=["1 ≤ rows, cols ≤ 200", "At most 10⁴ calls to sumRegion"],
        hints=[
            "P[i][j] = sum of the rectangle above-left of (i, j). Build it with P[i][j] = v + P[i−1][j] + P[i][j−1] − P[i−1][j−1].",
            "A region is P[r2+1][c2+1] − P[r1][c2+1] − P[r2+1][c1] + P[r1][c1].",
        ],
        reference="""
class NumMatrix:
    def __init__(self, matrix):
        R, C = len(matrix), len(matrix[0])
        self.p = [[0] * (C + 1) for _ in range(R + 1)]
        for i in range(R):
            for j in range(C):
                self.p[i + 1][j + 1] = matrix[i][j] + self.p[i][j + 1] + self.p[i + 1][j] - self.p[i][j]
    def sumRegion(self, row1, col1, row2, col2):
        p = self.p
        return p[row2 + 1][col2 + 1] - p[row1][col2 + 1] - p[row2 + 1][col1] + p[row1][col1]
""",
        gen=lambda r: (
            [_region_case(r, r.randint(1, 6), r.randint(1, 6), r.randint(1, 12)) for _ in range(14)]
            + [_region_case(r, 200, 200, 10_000)]
        ),
    ),
]


# ---------------------------------------------------------------- private generator helpers
def _anagram_pair(r: random.Random, n: int, same: bool) -> list[Any]:
    s = word(r, n, "abcde")
    t = list(s)
    r.shuffle(t)
    if not same:
        t[r.randrange(n)] = r.choice("abcdef")
    return [s, "".join(t)]


def _majority(r: random.Random, n: int) -> list[Any]:
    m = r.randint(-1000, 1000)
    k = r.randint(n // 2 + 1, n)
    nums = [m] * k + ints(r, n - k, -1000, 1000)
    r.shuffle(nums)
    return [nums]


def _roman(n: int) -> str:
    out = ""
    for v, sym in zip(
        [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1],
        ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"],
        strict=True,
    ):
        k, n = divmod(n, v)
        out += sym * k
    return out


def _iso_pair(r: random.Random, n: int) -> list[Any]:
    s = word(r, n, "abcdef")
    letters = list("abcdefghij")
    r.shuffle(letters)
    t = [letters["abcdef".index(c)] for c in s]
    if r.random() < 0.5:
        t[r.randrange(n)] = r.choice("abcdefghij")
    return [s, "".join(t)]


def _sudoku(r: random.Random) -> list[list[str]]:
    digits = list("123456789")
    r.shuffle(digits)
    board = [[digits[(i * 3 + i // 3 + j) % 9] for j in range(9)] for i in range(9)]
    keep = r.uniform(0.2, 0.6)
    board = [[c if r.random() < keep else "." for c in row] for row in board]
    for _ in range(r.choice([0, 0, 1, 2])):
        board[r.randrange(9)][r.randrange(9)] = r.choice(digits)
    return board


def _sorted_two_sum(r: random.Random, n: int) -> list[Any]:
    # a even + b odd = odd target; every filler is even and lies below a or above b, so no other pair hits it
    a = 2 * r.randint(-300, 100)
    b = 2 * r.randint(a // 2, 300) + 1
    fill = [
        2 * r.randint(-500, (a - 2) // 2) if r.random() < 0.5 else 2 * r.randint((b + 1) // 2, 500)
        for _ in range(n - 2)
    ]
    return [sorted([a, b, *fill]), a + b]


def _merge_case(r: random.Random, m: int, n: int) -> list[Any]:
    a = sorted(ints(r, m, -50, 50))
    b = sorted(ints(r, n, -50, 50))
    if m + n == 0:
        a = [1]
        m = 1
    return [a + [0] * n, m, b, n]


def _range_sum_case(r: random.Random, n: int, q: int) -> list[Any]:
    ops: list[str] = ["NumArray"]
    args: list[list[Any]] = [[ints(r, n, -(10**5), 10**5)]]
    for _ in range(q):
        i, j = sorted([r.randrange(n), r.randrange(n)])
        ops.append("sumRange")
        args.append([i, j])
    return [{"ops": ops, "args": args}]


def _region_case(r: random.Random, R: int, C: int, q: int) -> list[Any]:
    ops: list[str] = ["NumMatrix"]
    args: list[list[Any]] = [[[ints(r, C, -(10**4), 10**4) for _ in range(R)]]]
    for _ in range(q):
        r1, r2 = sorted([r.randrange(R), r.randrange(R)])
        c1, c2 = sorted([r.randrange(C), r.randrange(C)])
        ops.append("sumRegion")
        args.append([r1, c1, r2, c2])
    return [{"ops": ops, "args": args}]
