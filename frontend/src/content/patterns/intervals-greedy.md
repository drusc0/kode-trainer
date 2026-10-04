## The idea in plain words

**Intervals:** picture meetings on a calendar. Almost every interval problem becomes easy once you **sort the meetings by start time** and walk through them left to right, like reading the calendar from morning to evening. You only need to remember a little, such as "when does the current block end?".

**Greedy** means making the choice that looks best **right now** and never going back on it. It's like always grabbing the meeting that ends earliest so your afternoon stays free. It only works when you can argue that the local choice is never a mistake, so be ready to explain why.

## You'll know it's this pattern when…

- The input is intervals, meetings, ranges or start/end times.
- You're asked for the minimum rooms, arrows or removals, or to merge overlapping ranges.
- A decision at each step can be made locally (how far can I reach? which one ends first?).

## Picture it

Merge overlapping intervals `[[1,3], [2,6], [8,10], [15,18]]`, already sorted by start:

```text
time:   1  2  3  4  5  6  7  8  9  10 ... 15 16 17 18
        [-----]                                   [1,3]
           [-----------]                          [2,6]  overlaps → [1,6]
                          [-------]               [8,10] gap → new block
                                       [--------] [15,18]
result: [1,6] [8,10] [15,18]
```

## Walk through an example

Meeting rooms: `[[0,30], [5,10], [15,20]]`. How many rooms do you need?

Turn each meeting into two events, `+1` at the start and `−1` at the end, then sweep through time:

```text
time  event    rooms in use
0     +1       1
5     +1       2   ← peak
10    −1       1
15    +1       2   ← peak
20    −1       1
30    −1       0
answer = 2
```

## The code

```python
def merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)   # overlap: extend the current block
        else:
            out.append([s, e])                # gap: start a new block
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
            return False                      # can't even get here
        far = max(far, i + x)
    return True
```

## How fast is it?

O(n log n) for the sort, then one O(n) sweep.

## Common mistakes

- Decide whether touching intervals overlap. `[1,4]` and `[4,5]` usually merge, but a meeting ending at 10 frees its room for one starting at 10.
- Sorting by the wrong end: "fewest removals / most non-overlapping" sorts by **end** time.
- With a greedy approach, be ready to explain why it's correct (an exchange argument: "swapping in my choice never makes things worse"), not just that it works on examples.
