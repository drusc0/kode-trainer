## The idea in plain words

A graph is a **map of places (nodes) and roads (edges)**. A grid is a graph too: each cell is a place and you can walk to its four neighbours.

- **BFS** is like a **ripple in a pond**: drop a stone and the wave reaches everything 1 step away, then 2 steps, then 3. The first time the ripple touches your target, you've found the **fewest steps**.
- **DFS / flood fill** is like **spilling paint**: it spreads into everything connected. Count how many times you have to start a new spill and you've counted the islands.
- **Topological sort** is **getting dressed**: socks before shoes, shirt before jacket. Start with whatever has no prerequisites left, then unlock what depended on it.

## You'll know it's this pattern when…

- There's a **grid** or explicit connections between things.
- The question asks for the **minimum number of steps / moves / transformations** (BFS).
- You count **connected groups**: islands, provinces (DFS).
- Tasks have **prerequisites**, or you must detect a dependency cycle (topological sort).

## Picture it

BFS ripple from S on a grid (`#` is a wall). Numbers are the step at which each cell is reached:

```text
S 1 2 #        S = start
1 # 3 4        the ripple grows one ring per step
2 # 4 T        T is reached at step 5
3 4 5 #
```

## Walk through an example

Course schedule: 3 courses, prerequisites `[[1, 0], [2, 1]]` (take 0 before 1, and 1 before 2).

```text
in-degree (prerequisites still missing):  0:0  1:1  2:1
queue starts with the courses that need nothing: [0]
take 0 → course 1 now needs nothing → queue [1]
take 1 → course 2 now needs nothing → queue [2]
take 2
order = [0, 1, 2]; all 3 taken → no cycle
```

If a cycle existed (1 needs 2 and 2 needs 1), neither would reach 0 prerequisites, and `order` would come out shorter than n.

## The code

### BFS: fewest steps in an unweighted graph

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

**Multi-source BFS** (Rotting Oranges) puts every source in the queue at distance 0, so all the ripples start at once.

### DFS / flood fill: components

```python
for i in range(R):
    for j in range(C):
        if grid[i][j] == "1" and (i, j) not in seen:
            islands += 1
            fill(i, j)                 # iterative stack avoids recursion limits
```

### Topological sort (Kahn): dependencies

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

## How fast is it?

O(V + E): every node and every edge is handled once. A grid has V = rows × cols and E ≈ 4V.

## Common mistakes

- Mark cells visited when you **enqueue** them, not when you pop them, or the same cell gets queued many times.
- Word Ladder: generate neighbours by changing each letter (26 × word length per word) instead of comparing every pair of words.
- DFS can't give the shortest path in general. Use BFS for "fewest steps".
