## Recognise it

Grids, "minimum number of steps", word transformations, dependencies between tasks, connected components.

## BFS: fewest steps in an unweighted graph

```python
def bfs(start, target, neighbours):
    q, seen = deque([(start, 0)]), {start}
    while q:
        node, dist = q.popleft()
        if node == target:
            return dist
        for nxt in neighbours(node):
            if nxt not in seen:
                seen.add(nxt)          # mark when ENQUEUED, not when popped
                q.append((nxt, dist + 1))
    return -1
```

**Multi-source BFS** (Rotting Oranges) starts with every source in the queue at distance 0.

## DFS / flood fill: components

```python
for i in range(R):
    for j in range(C):
        if grid[i][j] == "1" and (i, j) not in seen:
            islands += 1
            fill(i, j)                 # iterative stack avoids recursion limits
```

## Topological sort (Kahn): dependencies

```python
indeg = [0] * n; g = defaultdict(list)
for a, b in prereqs:                   # b before a
    g[b].append(a); indeg[a] += 1
q = deque(i for i in range(n) if indeg[i] == 0)
order = []
while q:
    x = q.popleft(); order.append(x)
    for y in g[x]:
        indeg[y] -= 1
        if indeg[y] == 0: q.append(y)
has_cycle = len(order) < n
```

## Complexity

O(V + E). A grid has V = R·C and E ≈ 4V.

## Pitfalls

- Mark cells visited when you enqueue them, or you'll enqueue duplicates.
- Word Ladder: generate neighbours by changing each letter (26·L per word) instead of comparing all pairs of words.
