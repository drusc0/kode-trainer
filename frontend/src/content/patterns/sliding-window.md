## Recognise it

"Longest / shortest **contiguous** substring or subarray such that…" where the condition can be updated incrementally as elements enter and leave.

## Core idea

Grow `right` one step at a time. While the window breaks the rule, shrink `left`. Each index enters and leaves once, so the whole scan is O(n).

## Template

```python
def longest_valid(s):
    count = Counter()
    left = best = 0
    for right, ch in enumerate(s):
        count[ch] += 1                     # add s[right]
        while window_invalid(count):       # e.g. a repeat, or too many replacements
            count[s[left]] -= 1            # remove s[left]
            left += 1
        best = max(best, right - left + 1)
    return best
```

For **minimum** windows (Minimum Window Substring), shrink while the window is still *valid*, and record the best inside the while-loop.

## Complexity

O(n) time. O(alphabet) space for the counts.

## Pitfalls

- Keep a single "missing" counter instead of comparing whole count maps each step.
- Negative numbers break "shrink when sum is too big" — use prefix sums instead.
- Character Replacement: validity is `window_len - max_count <= k`. The max count never needs to decrease for the answer to stay correct.
