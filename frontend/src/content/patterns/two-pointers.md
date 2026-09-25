## Recognise it

The input is **sorted** (or you can sort it), or you compare elements from both ends: palindromes, pair sums, container widths.

## Core idea

Two indices move monotonically, so together they make at most n steps. Each step discards candidates that can't beat the current best.

## Template

```python
def pair_with_sum(nums, target):   # nums sorted
    l, r = 0, len(nums) - 1
    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            return l, r
        if s < target:
            l += 1                 # need a bigger sum
        else:
            r -= 1                 # need a smaller sum
    return None
```

For k-sum, fix one element with a loop and run two pointers on the rest: 3Sum is O(n²).

## Complexity

O(n) per two-pointer pass, plus O(n log n) if you sort first.

## Pitfalls

- Skip duplicates after a match (`while l < r and nums[l] == nums[l + 1]`) to avoid repeated triplets.
- Argue why moving a pointer is safe. For Container With Most Water, moving the taller side can never increase the area.
- Valid Palindrome II: at the first mismatch, try both skips, but only once.
