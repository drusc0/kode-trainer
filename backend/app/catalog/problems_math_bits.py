import random
from typing import Any

from .base import Problem, distinct, ints

G, M = "google", "meta"

PROBLEMS = [
    # ---------------------------------------------------------------- math & geometry
    Problem(
        slug="rotate-image",
        title="Rotate Image",
        difficulty="Medium",
        pattern="math-geometry",
        topics=["Array", "Math", "Matrix"],
        companies=[G, M],
        statement="Rotate the `n × n` matrix 90° clockwise **in place** (don't allocate another matrix) and return it.",
        entry="rotate",
        params=[("matrix", "List[List[int]]")],
        returns="List[List[int]]",
        examples=[
            {"args": [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]]},
            {"args": [[[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]]]},
        ],
        constraints=["1 ≤ n ≤ 20", "−1000 ≤ matrix[i][j] ≤ 1000"],
        hints=["Transpose (swap matrix[i][j] with matrix[j][i]), then reverse each row."],
        reference="""
class Solution:
    def rotate(self, matrix):
        matrix[:] = [list(row) for row in zip(*matrix[::-1])]
        return matrix
""",
        gen=lambda r: [(lambda n: [[ints(r, n, -1000, 1000) for _ in range(n)]])(n) for n in range(1, 21)],
    ),
    Problem(
        slug="spiral-matrix",
        title="Spiral Matrix",
        difficulty="Medium",
        pattern="math-geometry",
        topics=["Array", "Matrix", "Simulation"],
        companies=[G, M],
        statement="Return all elements of the `m × n` matrix in spiral order: along the top row left to right, down the right column, back along the bottom row, up the left column, then inward.",
        entry="spiralOrder",
        params=[("matrix", "List[List[int]]")],
        returns="List[int]",
        examples=[
            {"args": [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]]},
            {"args": [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]]},
        ],
        constraints=["1 ≤ m, n ≤ 10"],
        hints=[
            "Keep four boundaries (top, bottom, left, right) and shrink one after walking each side. Check they haven't crossed before the last two sides."
        ],
        reference="""
class Solution:
    def spiralOrder(self, matrix):
        out, m = [], [row[:] for row in matrix]
        while m:
            out += m.pop(0)
            m = [list(row) for row in zip(*m)][::-1]
        return out
""",
        gen=lambda r: [
            [[ints(r, c, -100, 100) for _ in range(rr)]]
            for rr, c in [(r.randint(1, 10), r.randint(1, 10)) for _ in range(20)]
        ],
    ),
    Problem(
        slug="set-matrix-zeroes",
        title="Set Matrix Zeroes",
        difficulty="Medium",
        pattern="math-geometry",
        topics=["Array", "Hash Table", "Matrix"],
        companies=[G, M],
        statement="If an element of the matrix is `0`, set its entire row and column to `0`. Do it in place and return the matrix.\n\nBonus: O(1) extra space.",
        entry="setZeroes",
        params=[("matrix", "List[List[int]]")],
        returns="List[List[int]]",
        examples=[
            {"args": [[[1, 1, 1], [1, 0, 1], [1, 1, 1]]]},
            {"args": [[[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]]},
        ],
        constraints=["1 ≤ m, n ≤ 200"],
        hints=[
            "Record which rows and columns contain a zero first, then clear them. For O(1) space, use the first row and column as the markers."
        ],
        reference="""
class Solution:
    def setZeroes(self, matrix):
        rows = {i for i, row in enumerate(matrix) for x in row if x == 0}
        cols = {j for row in matrix for j, x in enumerate(row) if x == 0}
        for i, row in enumerate(matrix):
            for j in range(len(row)):
                if i in rows or j in cols: row[j] = 0
        return matrix
""",
        gen=lambda r: (
            [
                [[[0 if r.random() < 0.1 else r.randint(-9, 9) for _ in range(c)] for _ in range(rr)]]
                for rr, c in [(r.randint(1, 8), r.randint(1, 8)) for _ in range(18)]
            ]
            + [[[[0 if r.random() < 0.001 else 1 for _ in range(200)] for _ in range(200)]]]
        ),
    ),
    Problem(
        slug="game-of-life",
        title="Game of Life",
        difficulty="Medium",
        pattern="math-geometry",
        topics=["Array", "Matrix", "Simulation"],
        companies=[G, M],
        statement="`board` holds live (`1`) and dead (`0`) cells. Compute the next generation, where each cell looks at its 8 neighbours:\n\n- A live cell with fewer than 2 or more than 3 live neighbours dies.\n- A live cell with 2 or 3 live neighbours lives.\n- A dead cell with exactly 3 live neighbours becomes live.\n\nAll cells update at the same time. Update `board` in place and return it.",
        entry="gameOfLife",
        params=[("board", "List[List[int]]")],
        returns="List[List[int]]",
        examples=[{"args": [[[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]]]}, {"args": [[[1, 1], [1, 0]]]}],
        constraints=["1 ≤ m, n ≤ 25"],
        hints=[
            "To update in place, encode transitions in extra bits (e.g. bit 1 = next state) and shift everything at the end."
        ],
        reference="""
class Solution:
    def gameOfLife(self, board):
        R, C = len(board), len(board[0])
        old = [row[:] for row in board]
        for i in range(R):
            for j in range(C):
                k = sum(old[x][y] for x in range(max(0, i - 1), min(R, i + 2)) for y in range(max(0, j - 1), min(C, j + 2))) - old[i][j]
                board[i][j] = int(k == 3 or (old[i][j] == 1 and k == 2))
        return board
""",
        gen=lambda r: [
            [[ints(r, c, 0, 1) for _ in range(rr)]]
            for rr, c in [(r.randint(1, 25), r.randint(1, 25)) for _ in range(20)]
        ],
    ),
    Problem(
        slug="pow-x-n",
        title="Pow(x, n)",
        difficulty="Medium",
        pattern="math-geometry",
        topics=["Math", "Recursion"],
        companies=[M, G],
        statement="Return `x` raised to the power `n`, without using `**` or `pow`. Answers within 10⁻⁵ are accepted.",
        entry="myPow",
        params=[("x", "float"), ("n", "int")],
        returns="float",
        examples=[{"args": [2.0, 10]}, {"args": [2.1, 3]}, {"args": [2.0, -2]}],
        constraints=["−100 < x < 100", "−2³¹ ≤ n ≤ 2³¹ − 1", "x ≠ 0 or n > 0", "−10⁴ ≤ xⁿ ≤ 10⁴"],
        hints=[
            "Fast exponentiation: x^n = (x²)^(n/2), times x when n is odd. O(log n) multiplications. Handle n < 0 with 1 / x^−n."
        ],
        reference="""
class Solution:
    def myPow(self, x, n):
        return x ** n
""",
        gen=lambda r: (
            [[1.0, -(2**31)], [1.0, 2**31 - 1], [-1.0, 2**31 - 1], [0.0, 5], [2.0, -(2**31)], [0.5, 13]]
            + [_pow_case(r) for _ in range(18)]
        ),
        compare="float",
    ),
    Problem(
        slug="multiply-strings",
        title="Multiply Strings",
        difficulty="Medium",
        pattern="math-geometry",
        topics=["Math", "String", "Simulation"],
        companies=[M, G],
        statement="`num1` and `num2` are non-negative integers written as strings. Return their product as a string, without converting the whole inputs to integers.",
        entry="multiply",
        params=[("num1", "str"), ("num2", "str")],
        returns="str",
        examples=[{"args": ["2", "3"]}, {"args": ["123", "456"]}],
        constraints=["1 ≤ len(num1), len(num2) ≤ 200", "No leading zeros except '0' itself"],
        hints=[
            "Digit i of num1 times digit j of num2 lands in position i + j (+1) of the result array. Add them all, then carry once."
        ],
        reference="""
class Solution:
    def multiply(self, num1, num2):
        return str(int(num1) * int(num2))
""",
        gen=lambda r: (
            [["0", "52"], ["9999", "0"], ["999", "999"]]
            + [[_num(r, r.randint(1, 12)), _num(r, r.randint(1, 12))] for _ in range(16)]
            + [[_num(r, 200), _num(r, 200)]]
        ),
    ),
    Problem(
        slug="happy-number",
        title="Happy Number",
        difficulty="Easy",
        pattern="math-geometry",
        topics=["Hash Table", "Math", "Two Pointers"],
        companies=[G, M],
        statement="Repeatedly replace `n` by the sum of the squares of its digits. `n` is happy if this process reaches 1; otherwise it loops forever in a cycle without 1. Return `True` if `n` is happy.",
        entry="isHappy",
        params=[("n", "int")],
        returns="bool",
        examples=[{"args": [19], "note": "1² + 9² = 82 → 68 → 100 → 1."}, {"args": [2]}],
        constraints=["1 ≤ n ≤ 2³¹ − 1"],
        hints=["Detect the cycle with a seen-set, or with fast/slow pointers as in a linked list."],
        reference="""
class Solution:
    def isHappy(self, n):
        seen = set()
        while n != 1 and n not in seen:
            seen.add(n); n = sum(int(d) ** 2 for d in str(n))
        return n == 1
""",
        gen=lambda r: (
            [[n] for n in [1, 7, 4, 2**31 - 1, 1111111]]
            + [[r.randint(1, 2**31 - 1)] for _ in range(10)]
            + [[r.randint(1, 1000)] for _ in range(10)]
        ),
    ),
    # ---------------------------------------------------------------- bit manipulation
    Problem(
        slug="single-number",
        title="Single Number",
        difficulty="Easy",
        pattern="bit-manipulation",
        topics=["Array", "Bit Manipulation"],
        companies=[G, M],
        statement="Every element of `nums` appears twice except one. Return that one, in O(n) time and O(1) extra space.",
        entry="singleNumber",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[2, 2, 1]]}, {"args": [[4, 1, 2, 1, 2]]}, {"args": [[1]]}],
        constraints=["1 ≤ len(nums) ≤ 3 × 10⁴", "−3 × 10⁴ ≤ nums[i] ≤ 3 × 10⁴"],
        hints=["x ^ x = 0 and x ^ 0 = x, and XOR is order-independent. XOR everything together."],
        reference="""
class Solution:
    def singleNumber(self, nums):
        return next(x for x, c in Counter(nums).items() if c == 1)
""",
        gen=lambda r: [_single(r, r.randint(0, 15)) for _ in range(20)] + [_single(r, 14_999)],
    ),
    Problem(
        slug="number-of-1-bits",
        title="Number of 1 Bits",
        difficulty="Easy",
        pattern="bit-manipulation",
        topics=["Divide and Conquer", "Bit Manipulation"],
        companies=[G, M],
        statement="Return the number of `1` bits in the binary form of the positive integer `n` (its Hamming weight).",
        entry="hammingWeight",
        params=[("n", "int")],
        returns="int",
        examples=[{"args": [11], "note": "1011 has three 1 bits."}, {"args": [128]}, {"args": [2147483645]}],
        constraints=["1 ≤ n ≤ 2³¹ − 1"],
        hints=["`n & (n − 1)` clears the lowest set bit. Count how many times you can do that before n is 0."],
        reference="""
class Solution:
    def hammingWeight(self, n):
        return bin(n).count('1')
""",
        gen=lambda r: [[1], [2**31 - 1], [2**30]] + [[r.randint(1, 2**31 - 1)] for _ in range(17)],
    ),
    Problem(
        slug="counting-bits",
        title="Counting Bits",
        difficulty="Easy",
        pattern="bit-manipulation",
        topics=["Dynamic Programming", "Bit Manipulation"],
        companies=[G, M],
        statement="Return an array `ans` of length `n + 1` where `ans[i]` is the number of `1` bits in `i`.\n\nCan you do it in O(n) without counting each number's bits from scratch?",
        entry="countBits",
        params=[("n", "int")],
        returns="List[int]",
        examples=[{"args": [2]}, {"args": [5]}],
        constraints=["0 ≤ n ≤ 10⁵"],
        hints=["ans[i] = ans[i >> 1] + (i & 1): i has the same bits as i // 2, plus its last bit."],
        reference="""
class Solution:
    def countBits(self, n):
        return [bin(i).count('1') for i in range(n + 1)]
""",
        gen=lambda r: [[0], [1], [100_000]] + [[r.randint(0, 200)] for _ in range(15)],
    ),
    Problem(
        slug="missing-number",
        title="Missing Number",
        difficulty="Easy",
        pattern="bit-manipulation",
        topics=["Array", "Hash Table", "Math", "Bit Manipulation"],
        companies=[G, M],
        statement="`nums` contains `n` distinct numbers from the range `[0, n]`. Return the one number in the range that is missing. Aim for O(n) time and O(1) extra space.",
        entry="missingNumber",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[3, 0, 1]]}, {"args": [[0, 1]]}, {"args": [[9, 6, 4, 2, 3, 5, 7, 0, 1]]}],
        constraints=["1 ≤ n ≤ 10⁴"],
        hints=[
            "XOR every index 0..n with every value; pairs cancel and the missing number is left. (Or: n(n + 1)/2 − sum.)"
        ],
        reference="""
class Solution:
    def missingNumber(self, nums):
        return len(nums) * (len(nums) + 1) // 2 - sum(nums)
""",
        gen=lambda r: [[[0]], [[1]]] + [_missing(r, r.randint(1, 30)) for _ in range(18)] + [_missing(r, 10_000)],
    ),
    Problem(
        slug="reverse-bits",
        title="Reverse Bits",
        difficulty="Easy",
        pattern="bit-manipulation",
        topics=["Divide and Conquer", "Bit Manipulation"],
        companies=[G, M],
        statement="Reverse the bits of the 32-bit unsigned integer `n` and return the result as an unsigned integer.\n\nFor example, `43261596` is `00000010100101000001111010011100`; reversed it's `00111001011110000010100101000000` = `964176192`.",
        entry="reverseBits",
        params=[("n", "int")],
        returns="int",
        examples=[{"args": [43261596]}, {"args": [4294967293]}],
        constraints=["0 ≤ n < 2³²"],
        hints=["32 times: shift the result left, add n's lowest bit, shift n right."],
        reference="""
class Solution:
    def reverseBits(self, n):
        return int(f'{n:032b}'[::-1], 2)
""",
        gen=lambda r: [[0], [1], [2**32 - 1], [2**31]] + [[r.randint(0, 2**32 - 1)] for _ in range(16)],
    ),
    Problem(
        slug="sum-of-two-integers",
        title="Sum of Two Integers",
        difficulty="Medium",
        pattern="bit-manipulation",
        topics=["Math", "Bit Manipulation"],
        companies=[G, M],
        statement="Return `a + b` without using the `+` or `-` operators.",
        entry="getSum",
        params=[("a", "int"), ("b", "int")],
        returns="int",
        examples=[{"args": [1, 2]}, {"args": [2, 3]}, {"args": [-12, -8]}],
        constraints=["−1000 ≤ a, b ≤ 1000"],
        hints=[
            "a ^ b adds without carries; (a & b) << 1 is the carries. Repeat until there are no carries.",
            "Python ints are unbounded, so mask to 32 bits (0xFFFFFFFF) while looping and convert back to a signed value at the end.",
        ],
        reference="""
class Solution:
    def getSum(self, a, b):
        return a + b
""",
        gen=lambda r: (
            [[0, 0], [-1, 1], [-1000, -1000], [1000, 1000], [-1, -1]]
            + [[r.randint(-1000, 1000), r.randint(-1000, 1000)] for _ in range(15)]
        ),
    ),
]


# ---------------------------------------------------------------- private generator helpers
def _pow_case(r: random.Random) -> list[Any]:
    while True:
        x = round(r.uniform(-3, 3), 2)
        n = r.randint(-30, 30)
        if x != 0 and abs(x) ** n <= 10**4:
            return [x, n]


def _num(r: random.Random, n: int) -> str:
    return str(r.randint(1, 9)) + "".join(str(r.randint(0, 9)) for _ in range(n - 1))


def _single(r: random.Random, pairs: int) -> list[Any]:
    vals = distinct(r, pairs + 1, -30_000, 30_000)
    nums = vals[1:] * 2 + vals[:1]
    r.shuffle(nums)
    return [nums]


def _missing(r: random.Random, n: int) -> list[Any]:
    nums = list(range(n + 1))
    nums.pop(r.randrange(n + 1))
    r.shuffle(nums)
    return [nums]
