## Recognise it

Range sums, or counting subarrays with a given sum — especially when values can be **negative**, so a sliding window won't work.

## Core idea

`sum(i..j) = prefix[j] - prefix[i-1]`. To count subarrays summing to `k`, count how many earlier prefixes equal `prefix - k`.

## Template

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

The "product except self" variant uses the same idea: one pass stores left products, a second backward pass multiplies in right products.

## Complexity

O(n) time and O(n) space. The two-pass product trick needs O(1) extra space.

## Pitfalls

- Seed the map with `{0: 1}`, or you'll miss subarrays that start at index 0.
- Update the map *after* counting, or a zero-length subarray gets counted.
- 2-D prefix sums: `P[i][j] = grid + P[i-1][j] + P[i][j-1] - P[i-1][j-1]`.
