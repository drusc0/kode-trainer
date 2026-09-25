## Recognise it

"Return **all** subsets / permutations / combinations / paths", with small inputs (n ≤ ~20).

## Core idea

Make a choice, recurse, **undo the choice**. Prune branches that can't lead to an answer.

## Template

```python
def backtrack(path, choices):
    if is_complete(path):
        results.append(path[:])        # copy! path keeps changing
        return
    for c in choices:
        if not valid(c, path):
            continue
        path.append(c)                 # choose
        backtrack(path, next_choices(c))
        path.pop()                     # un-choose
```

## The three classics

| Problem | Recursion shape |
|---|---|
| Subsets | at each index: include or skip |
| Permutations | at each position: any unused element |
| Combination Sum | loop from `start` so combinations stay non-decreasing (no duplicates); reuse allowed, so recurse with `i`, not `i + 1` |

## Grid search (Word Search)

Mark the cell (for example `board[i][j] = "#"`) before recursing and restore it afterwards. Return as soon as any branch succeeds.

## Complexity

Output-sized: O(2ⁿ · n) for subsets, O(n! · n) for permutations.

## Pitfalls

- Append a copy of `path`, not the list itself.
- Sort the candidates first so you can `break` once a candidate exceeds the remaining target.
