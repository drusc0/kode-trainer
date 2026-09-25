## Recognise it

"Number of ways", "minimum / maximum cost", "is it possible", where the answer depends on answers to smaller versions of the same question.

## Four steps

1. **State:** what does `dp[i]` (or `dp[i][j]`) mean, in words?
2. **Transition:** how is it built from smaller states?
3. **Base cases.**
4. **Order:** fill states so dependencies are ready — or memoize top-down with `@cache`.

## Templates

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

## Common state shapes

| Shape | Examples |
|---|---|
| prefix `dp[i]` | Climbing Stairs, House Robber, Decode Ways, Word Break |
| amount `dp[x]` | Coin Change |
| two prefixes `dp[i][j]` | Edit Distance, LCS |
| interval `dp[l][r]` | Longest Palindromic Substring |
| LIS | O(n²) dp, or O(n log n) patience sorting with `bisect` |

## Pitfalls

- Say what the state means out loud before writing code. Most DP bugs are unclear states.
- Rolling arrays reduce space from O(n²) to O(n). Mention it after you have a working solution.
- Decode Ways: `"0"` can't stand alone, and `"06"` isn't a valid pair.
