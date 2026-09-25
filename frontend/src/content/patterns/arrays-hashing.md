## Recognise it

You need to know quickly whether you've **seen something before**: a complement, a duplicate, a count, or a group key. The brute force re-scans the array for every element.

## Core idea

Replace the inner loop with an O(1) lookup in a `dict` or `set`. You spend O(n) memory to save a factor of n in time.

## Template

```python
def two_sum(nums, target):
    seen = {}                      # value -> index
    for i, x in enumerate(nums):
        if target - x in seen:     # complement already seen?
            return [seen[target - x], i]
        seen[x] = i                # insert AFTER checking, so x doesn't pair with itself

def group(words):
    groups = defaultdict(list)
    for w in words:
        groups[key(w)].append(w)   # choose a canonical key, e.g. ''.join(sorted(w))
    return list(groups.values())
```

## Complexity

O(n) time and O(n) space. Sorting-based keys add O(k log k) per item.

## Pitfalls

- Check before you insert, or an element pairs with itself.
- Lists aren't hashable. Convert keys to a `tuple` or a string.
- "Longest consecutive" style problems: only start counting from a run's first element (`x - 1 not in s`) to stay O(n).
