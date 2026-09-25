## Recognise it

Intervals, meetings or ranges, or a sequence of decisions where a **locally best choice is provably safe**.

## Core idea

Sort first (usually by start, sometimes by end), then sweep once with a small amount of state.

## Templates

```python
def merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)   # overlap: extend
        else:
            out.append([s, e])
    return out

def min_rooms(intervals):                     # sweep line
    events = sorted([(s, 1) for s, _ in intervals] + [(e, -1) for _, e in intervals])
    cur = best = 0
    for _, delta in events:                   # ends (-1) sort before starts at equal times
        cur += delta
        best = max(best, cur)
    return best

def can_jump(nums):                           # greedy reach
    far = 0
    for i, x in enumerate(nums):
        if i > far:
            return False
        far = max(far, i + x)
    return True
```

## Complexity

O(n log n) for the sort, then O(n).

## Pitfalls

- Decide whether touching intervals overlap. `[1,4]` and `[4,5]` merge; a meeting ending at 10 frees its room for one starting at 10.
- With a greedy approach, be ready to explain why it's correct (an exchange argument), not just that it works on examples.
