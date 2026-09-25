## Recognise it

Sorted or rotated input, a stated O(log n) requirement, or an optimisation question where **feasibility is monotonic**: if speed `k` works, every larger `k` works too.

## Core idea

Keep an interval that always contains the answer and halve it each step. Pick one convention and use it everywhere.

## Template: first index where `ok(x)` is true

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

## Rotated arrays

At any `mid`, one half is sorted. Check whether the target lies inside that sorted half's range, then discard the other half.

## Complexity

O(log n) iterations × the cost of `ok`.

## Pitfalls

- Infinite loops: with `hi = mid`, `mid` must round down; with `lo = mid`, round up.
- Peak finding works on unsorted data: if `nums[mid] < nums[mid + 1]`, a peak exists to the right.
- Median of two sorted arrays: binary search the partition of the shorter array.
