## The idea in plain words

Dynamic programming means **"don't solve the same small problem twice; write the answer down."**

Climbing stairs: you can take 1 or 2 steps at a time. How many ways are there to reach step 10? Your **last move** was either from step 9 or from step 8, so:

`ways(10) = ways(9) + ways(8)`

The big answer is built from smaller answers. Plain recursion would recompute `ways(5)` dozens of times; DP computes it once and stores it in a table, like filling in a **spreadsheet** where each cell is calculated from cells you've already filled.

## You'll know it's this pattern when…

- The question asks for the **number of ways**, the **minimum / maximum cost**, or **whether it's possible**.
- You make a **choice at each step** (take or skip, which coin, which edit).
- A brute-force recursion tree would hit the same sub-question many times.

## Picture it

Climbing stairs: each cell is the sum of the two before it.

```text
step:   0   1   2   3   4   5
ways:   1   1   2   3   5   8
                ↑
          ways[2] = ways[1] + ways[0]
```

House robber with `[2, 7, 9, 3, 1]`. For each house: rob it (best from two houses back + this one) or skip it (best so far):

```text
house:    2    7    9     3     1
best:     2    7   11    11    12
               ↑    ↑
       max(2, 7)   max(7, 2 + 9)
```

## Walk through an example

Every DP problem follows four steps. Here they are for Coin Change, `coins = [1, 2, 5]`, `amount = 11`:

1. **State:** `dp[x]` = the fewest coins that make amount `x`.
2. **Transition:** the last coin was some `c`, so `dp[x] = 1 + min(dp[x - c])` over all coins.
3. **Base case:** `dp[0] = 0` (zero coins make zero).
4. **Order:** fill `x = 1, 2, …, 11` so the smaller amounts are ready first.

```text
x:    0  1  2  3  4  5  6  7  8  9  10  11
dp:   0  1  1  2  2  1  2  2  3  3   2   3     → 11 = 5 + 5 + 1
```

## The code

```python
# 1-D: House Robber — best[i] = max(skip i, take i)
a = b = 0
for x in nums:
    a, b = b, max(b, a + x)

# Unbounded knapsack: Coin Change
dp = [0] + [inf] * amount
for x in range(1, amount + 1):
    for c in coins:
        if c <= x:
            dp[x] = min(dp[x], dp[x - c] + 1)

# 2-D on two strings: Edit Distance
# dp[i][j] = cost to turn a[:i] into b[:j]
# same char   -> dp[i-1][j-1]
# otherwise   -> 1 + min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1])
```

Prefer to think top-down? Write the plain recursion and add `@cache` above it. That's DP too (memoization).

### Common state shapes

| Shape | Examples |
|---|---|
| prefix `dp[i]` | Climbing Stairs, House Robber, Decode Ways, Word Break |
| amount `dp[x]` | Coin Change |
| two prefixes `dp[i][j]` | Edit Distance, LCS |
| interval `dp[l][r]` | Longest Palindromic Substring |
| LIS | O(n²) dp, or O(n log n) patience sorting with `bisect` |

## How fast is it?

(number of states) × (work per state). Coin Change is `amount × len(coins)`, and Edit Distance is `len(a) × len(b)`.

## Common mistakes

- Say what the state means **in words** before writing code. Most DP bugs come from a fuzzy state.
- Off-by-one in base cases: what's the answer for 0, or for an empty string?
- Rolling arrays reduce space from O(n²) to O(n). Mention it after you have a working solution.
- Decode Ways: `"0"` can't stand alone, and `"06"` isn't a valid pair.
