## The idea in plain words

Picture a bookshelf sorted from thinnest to thickest book. You want two books whose widths add up to exactly 10 cm. Put your **left hand on the thinnest** and your **right hand on the thickest**.

- Too wide together? The thickest book is the problem, so move your right hand one book left.
- Too narrow? Move your left hand one book right.

Each move rules out a book for good, so your hands meet after at most n moves. That's the whole trick: **two indices that only ever move inward (or forward)**, each step throwing away options that can't work.

## You'll know it's this pattern when…

- The input is **sorted**, or sorting it doesn't break the question.
- You compare things **from both ends**: palindromes, pair sums, the widest container.
- You need to rearrange an array **in place** (move zeros, remove duplicates).

## Picture it

Find a pair summing to 9 in the sorted array `[1, 3, 4, 6, 8]`:

```text
 [1, 3, 4, 6, 8]
  L           R     1 + 8 = 9  ✓  done

Target 10 instead:
 [1, 3, 4, 6, 8]
  L           R     1 + 8 = 9   too small → move L right
     L        R     3 + 8 = 11  too big   → move R left
     L     R        3 + 6 = 9   too small → move L right
        L  R        4 + 6 = 10  ✓
```

## Walk through an example

Valid palindrome: is `"racecar"` the same forwards and backwards?

1. `L` at index 0 (`r`), `R` at index 6 (`r`). They match, so step both inward.
2. `a` and `a` match. Step inward.
3. `c` and `c` match. Step inward.
4. `L == R` (the middle `e`), so stop. Every pair matched, so it's a palindrome.

## The code

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

For 3Sum, fix one number with an outer loop and run two pointers on the rest of the array, which is O(n²) overall.

## How fast is it?

O(n) per pass, because the two pointers make at most n moves between them. Add O(n log n) if you have to sort first. O(1) extra space.

## Common mistakes

- Skip duplicates after a match (`while l < r and nums[l] == nums[l + 1]`), or 3Sum returns the same triplet twice.
- Be able to say **why** a move is safe. In Container With Most Water, moving the taller wall can never give more water, because the shorter wall still limits the height.
- Valid Palindrome II: at the first mismatch, try skipping the left character and the right character, but only once.
