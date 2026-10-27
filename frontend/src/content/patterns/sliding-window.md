## The idea in plain words

Think of a **caterpillar crawling along a string**. Its head (`right`) moves forward one letter at a time and swallows it. If the caterpillar now breaks a rule (say, "no repeated letters"), its tail (`left`) moves forward until the rule holds again. At every moment, the caterpillar's body is a valid stretch, and you remember the longest one you've seen.

Head and tail only move forward, so each letter enters once and leaves once. That's why the scan is O(n) and not O(n²).

## You'll know it's this pattern when…

- The question asks for the **longest or shortest contiguous** substring or subarray that satisfies some rule.
- The rule can be kept up to date cheaply as one item enters and one leaves (a count, a sum, a set).
- You see "at most k" or "at least k", and the numbers are non-negative.

## Picture it

Longest substring without repeating characters in `"abcabcbb"`:

```text
 a b c a b c b b
[a]                   len 1
[a b]                 len 2
[a b c]               len 3   ← best so far
  [b c a]             'a' repeated → tail moves past the first 'a'
    [c a b]           'b' repeated → tail moves
      [a b c]
          [c b]       'b' repeated → tail jumps past it
              [b]     ...
best = 3 ("abc")
```

## Walk through an example

`"pwwkew"`, same question:

1. Head eats `p`, then `w`. Window `pw`, length 2.
2. Head eats a second `w`. Rule broken, so the tail moves until there's only one `w`: window `w`.
3. Head eats `k`, then `e`. Window `wke`, length 3, the new best.
4. Head eats another `w`. The tail moves past the old `w`: window `kew`, still length 3.
5. Answer: 3.

## The code

```python
def longest_valid(s):
    count = Counter()
    left = best = 0
    for right, ch in enumerate(s):
        count[ch] += 1                     # head eats s[right]
        while window_invalid(count):       # e.g. a repeat, or too many replacements
            count[s[left]] -= 1            # tail lets go of s[left]
            left += 1
        best = max(best, right - left + 1)
    return best
```

For **shortest** windows (Minimum Window Substring), flip it: shrink while the window is still *valid*, and record the best inside the `while` loop.

## How fast is it?

O(n) time, because each index enters and leaves the window once. O(alphabet) space for the counts.

## Common mistakes

- Keep a single "how many are still missing" counter instead of comparing whole count maps at every step.
- Negative numbers break "shrink when the sum is too big", because shrinking might make the sum bigger. Use prefix sums instead.
- Character Replacement: the window is valid when `window_len - max_count <= k`. `max_count` never has to go down for the answer to stay correct.
