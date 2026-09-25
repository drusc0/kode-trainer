Interviewers at Google and Meta grade more than a working solution. They score **communication, problem solving, coding and verification**. Run the same loop on every practice problem so it's automatic on the day.

## 1. Clarify (2–3 min)

Restate the problem in your own words, then pin down the inputs.

- **Sizes:** how large can `n` get? This decides which complexity is acceptable (table below).
- **Values:** negatives? duplicates? empty input? already sorted?
- **Output:** any order? indices or values? what if there's no answer?

## 2. Examples (2 min)

Work one normal example by hand, then list the edge cases you'll test later: empty, one element, all equal, already sorted, maximum size.

## 3. Brute force, out loud (1–2 min)

State the obvious solution and its complexity before optimising. It shows you understand the problem and gives you a fallback.

## 4. Optimise (5–10 min)

Ask which work the brute force repeats, then match the problem's signals to a pattern:

| If you see… | Reach for… |
|---|---|
| pair, complement, seen-before | hash map |
| sorted input, pairs, palindromes | two pointers |
| longest/shortest contiguous run | sliding window |
| subarray sums with negatives | prefix sums + hash map |
| next greater, matching brackets | (monotonic) stack |
| sorted, or "minimum k such that…" | binary search (on the answer) |
| k largest, k-way merge | heap |
| grid, steps, dependencies | BFS / DFS / topological sort |
| "all combinations / permutations" | backtracking |
| count ways or min cost with choices | dynamic programming |

Agree on the approach and its complexity with the interviewer before writing code.

## 5. Code (15–20 min)

Clean code, clear names, helper functions instead of deep nesting. Narrate the non-obvious parts.

## 6. Verify (5 min)

Dry-run your example line by line, then walk the edge cases from step 2. Fix bugs calmly and say what you're fixing.

## 7. Analyse

State the final time and space complexity, and what you'd change under different constraints (streaming input, limited memory, huge `n`).

## Which complexity fits the input size

| n up to | Aim for |
|---|---|
| 10–12 | O(n!) — permutations |
| 20–25 | O(2ⁿ) — subsets, backtracking |
| 500 | O(n³) |
| 5,000 | O(n²) |
| 10⁵–10⁶ | O(n log n) or O(n) |
| 10⁹ and up | O(log n) or O(1) |

## Python tips for interviews

- `Counter`, `defaultdict`, `deque`, `heapq` and `bisect` are all fair game. Say what they cost when you use them.
- `heapq` is a min-heap. Push negated values for a max-heap, and add a tie-breaker when items aren't comparable: `(priority, index, item)`.
- Recursion depth is limited (about 1000 by default). For deep trees or long lists, mention an iterative version.
- Sort with key tuples for tie-breaks: `sorted(xs, key=lambda x: (x[0], -x[1]))`.
