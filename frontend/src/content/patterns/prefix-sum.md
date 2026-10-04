## The idea in plain words

Think of a car's **odometer**. To find how far you drove between Tuesday and Friday, you don't add up each day's trips. You take Friday's reading minus Tuesday's.

A prefix sum is that odometer for an array: `prefix[i]` is the total of everything up to index `i`. Then the sum of any range is **one subtraction**.

## You'll know it's this pattern when…

- You're asked for many **range sums**.
- You count subarrays whose sum equals `k`, and the numbers can be **negative** (so a sliding window doesn't work).
- You see "product of everything **except** index i".

## Picture it

```text
index:     0   1   2   3   4
nums:      3   1   4   1   5
prefix: 0  3   4   8   9  14      ← a leading 0 is the "empty" prefix

sum of nums[1..3] = prefix after 3 − prefix before 1
                  =       9       −       3          = 6   (1 + 4 + 1 ✓)
```

## Walk through an example

Count subarrays summing to `k = 2` in `[1, 1, 1]`.

The trick: a subarray ending here sums to `k` when **some earlier prefix equals `current − k`**. So keep a count of the prefixes you've seen so far.

```text
x   prefix   need (prefix − 2)   seen before            add
-   0        –                   {0:1}                  –
1   1        −1                  {0:1}                  0
1   2         0                  {0:1, 1:1}             1   (subarray [1,1])
1   3         1                  {0:1, 1:1, 2:1}        1   (the other [1,1])
                                                 total = 2
```

## The code

```python
def subarray_sum(nums, k):
    seen = Counter({0: 1})     # the empty prefix
    prefix = count = 0
    for x in nums:
        prefix += x
        count += seen[prefix - k]
        seen[prefix] += 1
    return count
```

"Product except self" uses the same idea: one pass stores the product of everything to the **left**, and a second pass backwards multiplies in everything to the **right**.

## How fast is it?

O(n) time and O(n) space. The two-pass product trick needs only O(1) extra space.

## Common mistakes

- Seed the map with `{0: 1}`, or you miss subarrays that start at index 0.
- Update the map *after* counting, or you count a zero-length subarray.
- 2-D prefix sums: `P[i][j] = grid[i][j] + P[i-1][j] + P[i][j-1] - P[i-1][j-1]`. The last term removes the corner you added twice.
