## The idea in plain words

The **guess-the-number game**: "I'm thinking of a number from 1 to 100." You guess 50 and hear "higher", so 1–50 are gone in one go. Guess 75 and hear "lower". Every guess **cuts the possibilities in half**, so even a million options take only about 20 guesses.

Binary search works whenever you can look at the middle and know **which half to throw away**. That works on a sorted array, and it also works on the *answer itself*: if a speed of 5 is fast enough, every speed above 5 is too, so you can binary search for the smallest speed that works.

## You'll know it's this pattern when…

- The input is **sorted**, or sorted and then rotated.
- The problem demands O(log n).
- The question is "**minimum k such that** …" or "maximum k such that …", and once k works, every bigger (or smaller) k works too.

## Picture it

Think of the possibilities as a row of answers to "does this work?". It's a run of ✗ followed by a run of ✓, and you want the first ✓:

```text
k:     1  2  3  4  5  6  7  8
ok?    ✗  ✗  ✗  ✗  ✓  ✓  ✓  ✓
       lo          mid       hi     mid=4 ✗ → lo = 5
                   lo mid    hi     mid=6 ✓ → hi = 6
                   lo hi            mid=5 ✓ → hi = 5
                   ↑ lo == hi → answer 5
```

## Walk through an example

Koko eats bananas: `piles = [3, 6, 7, 11]` and she has `h = 8` hours. What's the slowest speed that still finishes?

1. Speeds range from 1 to 11 (the biggest pile).
2. Try mid = 6. Hours needed are 1 + 1 + 2 + 2 = 6, which is ≤ 8, so 6 works. Look lower: `hi = 6`.
3. Try mid = 3. Hours needed are 1 + 2 + 3 + 4 = 10 > 8, so 3 is too slow: `lo = 4`.
4. Try mid = 5. That's 1 + 2 + 2 + 3 = 8 hours, which works: `hi = 5`.
5. Try mid = 4. That's 1 + 2 + 2 + 3 = 8 hours, which works: `hi = 4`. Now `lo == hi == 4`, so the answer is 4.

## The code: first index where `ok(x)` is true

```python
def first_true(lo, hi, ok):          # answer in [lo, hi]; ok is False...False True...True
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid                 # mid might be the answer
        else:
            lo = mid + 1
    return lo

# Koko: minimum speed that finishes in h hours
speed = first_true(1, max(piles), lambda k: sum((p + k - 1) // k for p in piles) <= h)
```

### Rotated arrays

`[4, 5, 6, 7, 0, 1, 2]`: at any `mid`, **one half is still sorted**. Check whether the target sits inside that sorted half's range. If it does, search there; otherwise search the other half.

## How fast is it?

O(log n) steps × the cost of one `ok` check. Halving 1,000,000 takes about 20 steps.

## Common mistakes

- Infinite loops: with `hi = mid`, `mid` must round down; with `lo = mid`, round up. Pick one convention and stick to it.
- Peak finding works on unsorted data: if `nums[mid] < nums[mid + 1]`, there must be a peak to the right.
- Median of two sorted arrays: binary search where to split the **shorter** array.
