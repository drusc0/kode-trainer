## The idea in plain words

Backtracking is **exploring a maze with a ball of string**. At each fork you pick a path and unroll string as you go. When you hit a dead end (or find an exit and write it down), you **wind the string back** to the last fork and try the next path.

In code, it's three moves repeated over and over: **choose → explore → un-choose**. The "un-choose" step is the winding back. Skipping it is the most common bug.

## You'll know it's this pattern when…

- The question says "return **all** …": subsets, permutations, combinations, paths, board placements.
- The input is small (n ≤ ~20), a hint that exponential time is expected.
- You search for a word or path in a grid.

## Picture it

Subsets of `[1, 2, 3]`: at each number, decide whether to take it or skip it.

```text
                        []
              take 1 /      \ skip 1
                [1]            []
             /      \        /     \
         [1,2]      [1]    [2]      []
         /   \     /   \   /  \    /  \
    [1,2,3] [1,2] [1,3] [1] [2,3] [2] [3] []
```

The 8 leaves are the 8 subsets. Each step down is "choose", and each step back up is "un-choose".

## Walk through an example

Permutations of `[1, 2, 3]`, starting with `path = []`:

1. Choose 1 → `[1]`. Choose 2 → `[1, 2]`. Choose 3 → `[1, 2, 3]`, which is complete, so record a **copy**.
2. Un-choose 3 → `[1, 2]`. Nothing else is unused, so un-choose 2 → `[1]`.
3. Choose 3 → `[1, 3]`. Choose 2 → `[1, 3, 2]` and record it.
4. Keep winding back and trying the next option until every branch is explored: 6 permutations.

## The code

```python
def backtrack(path, choices):
    if is_complete(path):
        results.append(path[:])        # copy! path keeps changing
        return
    for c in choices:
        if not valid(c, path):
            continue                   # prune: don't walk down a dead branch
        path.append(c)                 # choose
        backtrack(path, next_choices(c))
        path.pop()                     # un-choose
```

### The three classics

| Problem | Recursion shape |
|---|---|
| Subsets | at each index: include or skip |
| Permutations | at each position: any unused element |
| Combination Sum | loop from `start` so combinations stay non-decreasing (no duplicates); reuse is allowed, so recurse with `i`, not `i + 1` |

### Grid search (Word Search)

Mark the cell (for example `board[i][j] = "#"`) before recursing and restore it afterwards, which is the un-choose step. Return as soon as any branch succeeds.

## How fast is it?

As big as the output: O(2ⁿ · n) for subsets and O(n! · n) for permutations. Pruning dead branches early is what makes it practical.

## Common mistakes

- Appending `path` itself instead of a copy: every stored result ends up as the same (empty) list.
- Forgetting to un-choose (pop or restore the cell).
- Sort the candidates first so you can `break` once a candidate is bigger than the remaining target.
