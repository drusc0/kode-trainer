import random
from typing import Any

from .base import Problem, course_case, ints, word

G, M = "google", "meta"
INF = 2147483647
_SUDOKU_PUZZLES = [
    "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79",
    "..9748...7.........2.1.9.....7...24..64.1.59..98...3.....8.3.2.........6...2759..",
    "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..",
]

PROBLEMS = [
    # ---------------------------------------------------------------- graphs
    Problem(
        slug="flood-fill",
        title="Flood Fill",
        difficulty="Easy",
        pattern="graphs",
        topics=["Array", "DFS", "BFS", "Matrix"],
        companies=[G, M],
        statement="Starting from pixel `(sr, sc)` of `image`, recolour it and every pixel connected to it (up, down, left, right) that has the same original colour as the start, to `color`. Return the image.",
        entry="floodFill",
        params=[("image", "List[List[int]]"), ("sr", "int"), ("sc", "int"), ("color", "int")],
        returns="List[List[int]]",
        examples=[{"args": [[[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2]}, {"args": [[[0, 0, 0], [0, 0, 0]], 0, 0, 0]}],
        constraints=["1 ≤ rows, cols ≤ 50", "0 ≤ image[i][j], color < 2¹⁶"],
        hints=[
            "DFS or BFS from the start. If the new colour equals the old one, return immediately — otherwise you loop forever."
        ],
        reference="""
class Solution:
    def floodFill(self, image, sr, sc, color):
        old = image[sr][sc]
        if old == color: return image
        st = [(sr, sc)]
        while st:
            i, j = st.pop()
            if 0 <= i < len(image) and 0 <= j < len(image[0]) and image[i][j] == old:
                image[i][j] = color
                st += [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
        return image
""",
        gen=lambda r: [_flood(r, r.randint(1, 8), r.randint(1, 8)) for _ in range(18)] + [_flood(r, 50, 50)],
    ),
    Problem(
        slug="max-area-of-island",
        title="Max Area of Island",
        difficulty="Medium",
        pattern="graphs",
        topics=["Array", "DFS", "BFS", "Union Find", "Matrix"],
        companies=[G, M],
        statement="`grid` is a map of `1` (land) and `0` (water). An island is a group of land cells connected up, down, left or right. Return the area of the largest island, or `0` if there is none.",
        entry="maxAreaOfIsland",
        params=[("grid", "List[List[int]]")],
        returns="int",
        examples=[
            {"args": [[[0, 0, 1, 0, 0], [1, 1, 1, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 1]]]},
            {"args": [[[0, 0, 0, 0]]]},
        ],
        constraints=["1 ≤ rows, cols ≤ 50"],
        hints=["Like Number of Islands, but count cells as you flood each island."],
        reference="""
class Solution:
    def maxAreaOfIsland(self, grid):
        R, C = len(grid), len(grid[0]); seen = set(); best = 0
        for i in range(R):
            for j in range(C):
                if grid[i][j] and (i, j) not in seen:
                    seen.add((i, j)); st = [(i, j)]; area = 0
                    while st:
                        a, b = st.pop(); area += 1
                        for x, y in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                            if 0 <= x < R and 0 <= y < C and grid[x][y] and (x, y) not in seen:
                                seen.add((x, y)); st.append((x, y))
                    best = max(best, area)
        return best
""",
        gen=lambda r: (
            [[_bits(r, r.randint(1, 8), r.randint(1, 8), r.uniform(0.2, 0.7))] for _ in range(18)]
            + [[_bits(r, 50, 50, 0.55)], [[[1] * 50 for _ in range(50)]]]
        ),
    ),
    Problem(
        slug="pacific-atlantic-water-flow",
        title="Pacific Atlantic Water Flow",
        difficulty="Medium",
        pattern="graphs",
        topics=["Array", "DFS", "BFS", "Matrix"],
        companies=[G, M],
        statement="`heights` is an island map. The Pacific touches the top and left edges; the Atlantic touches the bottom and right edges. Rain flows from a cell to a neighbour (up/down/left/right) whose height is less than or equal, and from edge cells into the adjacent ocean.\n\nReturn every `[r, c]` from which water can reach **both** oceans, in any order.",
        entry="pacificAtlantic",
        params=[("heights", "List[List[int]]")],
        returns="List[List[int]]",
        examples=[
            {"args": [[[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]]},
            {"args": [[[1]]]},
        ],
        constraints=["1 ≤ rows, cols ≤ 200", "0 ≤ heights[r][c] ≤ 10⁵"],
        hints=[
            "Search backwards from each ocean: walk uphill (to neighbours ≥ current) from its edge cells. Answer = cells reached by both searches."
        ],
        reference="""
class Solution:
    def pacificAtlantic(self, h):
        R, C = len(h), len(h[0])
        def reach(starts):
            seen = set(starts); st = list(starts)
            while st:
                i, j = st.pop()
                for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                    if 0 <= x < R and 0 <= y < C and (x, y) not in seen and h[x][y] >= h[i][j]:
                        seen.add((x, y)); st.append((x, y))
            return seen
        pac = reach([(0, j) for j in range(C)] + [(i, 0) for i in range(R)])
        atl = reach([(R - 1, j) for j in range(C)] + [(i, C - 1) for i in range(R)])
        return [list(p) for p in pac & atl]
""",
        gen=lambda r: (
            [
                [[ints(r, c, 0, 4) for _ in range(rr)]]
                for rr, c in [(r.randint(1, 8), r.randint(1, 8)) for _ in range(18)]
            ]
            + [[[ints(r, 200, 0, 10) for _ in range(200)]]]
        ),
        compare="sorted",
    ),
    Problem(
        slug="surrounded-regions",
        title="Surrounded Regions",
        difficulty="Medium",
        pattern="graphs",
        topics=["Array", "DFS", "BFS", "Union Find", "Matrix"],
        companies=[G, M],
        statement='`board` contains `"X"` and `"O"`. Capture every region of `"O"` cells (connected up/down/left/right) that does not touch the border, by flipping it to `"X"`. Modify `board` in place and return it.',
        entry="solve",
        params=[("board", "List[List[str]]")],
        returns="List[List[str]]",
        examples=[
            {"args": [[["X", "X", "X", "X"], ["X", "O", "O", "X"], ["X", "X", "O", "X"], ["X", "O", "X", "X"]]]},
            {"args": [[["X"]]]},
        ],
        constraints=["1 ≤ rows, cols ≤ 200"],
        hints=["Flip the logic: mark every O reachable from a border O as safe. Then flip all unmarked O's."],
        reference="""
class Solution:
    def solve(self, board):
        R, C = len(board), len(board[0])
        st = [(i, j) for i in range(R) for j in range(C) if (i in (0, R - 1) or j in (0, C - 1)) and board[i][j] == 'O']
        safe = set(st)
        while st:
            i, j = st.pop()
            for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= x < R and 0 <= y < C and board[x][y] == 'O' and (x, y) not in safe:
                    safe.add((x, y)); st.append((x, y))
        for i in range(R):
            for j in range(C):
                if board[i][j] == 'O' and (i, j) not in safe: board[i][j] = 'X'
        return board
""",
        gen=lambda r: [[_xo(r, r.randint(1, 8), r.randint(1, 8))] for _ in range(18)] + [[_xo(r, 200, 200)]],
    ),
    Problem(
        slug="walls-and-gates",
        title="Walls and Gates",
        difficulty="Medium",
        pattern="graphs",
        topics=["Array", "BFS", "Matrix"],
        companies=[M, G],
        statement="`rooms` holds `-1` (wall), `0` (gate) or `2147483647` (empty room). Fill each empty room with the number of steps (up/down/left/right) to its nearest gate; leave it as `2147483647` if no gate is reachable. Modify `rooms` in place and return it.",
        entry="wallsAndGates",
        params=[("rooms", "List[List[int]]")],
        returns="List[List[int]]",
        examples=[
            {"args": [[[INF, -1, 0, INF], [INF, INF, INF, -1], [INF, -1, INF, -1], [0, -1, INF, INF]]]},
            {"args": [[[-1]]]},
        ],
        constraints=["1 ≤ rows, cols ≤ 250"],
        hints=["Multi-source BFS: put every gate in the queue at distance 0, then expand once."],
        reference="""
class Solution:
    def wallsAndGates(self, rooms):
        R, C = len(rooms), len(rooms[0])
        q = deque((i, j) for i in range(R) for j in range(C) if rooms[i][j] == 0)
        while q:
            i, j = q.popleft()
            for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= x < R and 0 <= y < C and rooms[x][y] == 2147483647:
                    rooms[x][y] = rooms[i][j] + 1; q.append((x, y))
        return rooms
""",
        gen=lambda r: [[_rooms(r, r.randint(1, 8), r.randint(1, 8))] for _ in range(18)] + [[_rooms(r, 250, 250)]],
    ),
    Problem(
        slug="course-schedule-ii",
        title="Course Schedule II",
        difficulty="Medium",
        pattern="graphs",
        topics=["Graph", "Topological Sort", "BFS", "DFS"],
        companies=[G, M],
        statement="There are `numCourses` courses labelled `0` to `numCourses − 1`. `prerequisites[i] = [a, b]` means you must take `b` before `a`. Return an order in which you can take all courses, or `[]` if that's impossible. Any valid order is accepted.",
        entry="findOrder",
        params=[("numCourses", "int"), ("prerequisites", "List[List[int]]")],
        returns="List[int]",
        examples=[{"args": [2, [[1, 0]]]}, {"args": [4, [[1, 0], [2, 0], [3, 1], [3, 2]]]}, {"args": [1, []]}],
        constraints=["1 ≤ numCourses ≤ 2000", "0 ≤ len(prerequisites) ≤ 5000", "All pairs are distinct"],
        hints=[
            "Kahn's algorithm: repeatedly take a course with no remaining prerequisites. If some course is never taken, there's a cycle."
        ],
        reference="""
class Solution:
    def findOrder(self, numCourses, prerequisites):
        indeg = [0] * numCourses; adj = defaultdict(list)
        for a, b in prerequisites:
            adj[b].append(a); indeg[a] += 1
        q = deque(i for i in range(numCourses) if indeg[i] == 0); order = []
        while q:
            c = q.popleft(); order.append(c)
            for d in adj[c]:
                indeg[d] -= 1
                if indeg[d] == 0: q.append(d)
        return order if len(order) == numCourses else []
""",
        gen=lambda r: (
            [[3, []], [2, [[0, 1], [1, 0]]]]
            + [course_case(r, r.randint(2, 15), r.random() < 0.4) for _ in range(18)]
            + [course_case(r, 2000, False), course_case(r, 2000, True)]
        ),
        compare="topo_order",
    ),
    Problem(
        slug="number-of-connected-components-in-an-undirected-graph",
        title="Number of Connected Components in an Undirected Graph",
        difficulty="Medium",
        pattern="graphs",
        topics=["Graph", "Union Find", "DFS", "BFS"],
        companies=[G, M],
        statement="A graph has `n` nodes labelled `0` to `n − 1` and undirected `edges`. Return the number of connected components.",
        entry="countComponents",
        params=[("n", "int"), ("edges", "List[List[int]]")],
        returns="int",
        examples=[{"args": [5, [[0, 1], [1, 2], [3, 4]]]}, {"args": [5, [[0, 1], [1, 2], [2, 3], [3, 4]]]}],
        constraints=["1 ≤ n ≤ 2000", "0 ≤ len(edges) ≤ 5000", "No repeated edges or self-loops"],
        hints=["Union-find: start with n components and subtract one for every edge that joins two different sets."],
        reference="""
class Solution:
    def countComponents(self, n, edges):
        p = list(range(n))
        def find(x):
            while p[x] != x: p[x] = p[p[x]]; x = p[x]
            return x
        comps = n
        for a, b in edges:
            ra, rb = find(a), find(b)
            if ra != rb: p[ra] = rb; comps -= 1
        return comps
""",
        gen=lambda r: (
            [[1, []]]
            + [(lambda n: [n, _edges(r, n, r.randint(0, n + 2))])(r.randint(2, 12)) for _ in range(19)]
            + [[2000, _edges(r, 2000, 1900)]]
        ),
    ),
    Problem(
        slug="graph-valid-tree",
        title="Graph Valid Tree",
        difficulty="Medium",
        pattern="graphs",
        topics=["Graph", "Union Find", "DFS", "BFS"],
        companies=[G, M],
        statement="Given `n` nodes labelled `0` to `n − 1` and undirected `edges`, return `True` if the edges form a valid tree: connected with no cycles.",
        entry="validTree",
        params=[("n", "int"), ("edges", "List[List[int]]")],
        returns="bool",
        examples=[
            {"args": [5, [[0, 1], [0, 2], [0, 3], [1, 4]]]},
            {"args": [5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]]},
        ],
        constraints=["1 ≤ n ≤ 2000", "0 ≤ len(edges) ≤ 5000", "No repeated edges or self-loops"],
        hints=[
            "A tree has exactly n − 1 edges. With that many edges, it's a tree iff it's connected (or iff no edge closes a cycle)."
        ],
        reference="""
class Solution:
    def validTree(self, n, edges):
        if len(edges) != n - 1: return False
        p = list(range(n))
        def find(x):
            while p[x] != x: p[x] = p[p[x]]; x = p[x]
            return x
        for a, b in edges:
            ra, rb = find(a), find(b)
            if ra == rb: return False
            p[ra] = rb
        return True
""",
        gen=lambda r: (
            [[1, []], [2, []]] + [_maybe_tree(r, r.randint(2, 12)) for _ in range(18)] + [_maybe_tree(r, 2000)]
        ),
    ),
    Problem(
        slug="redundant-connection",
        title="Redundant Connection",
        difficulty="Medium",
        pattern="graphs",
        topics=["Graph", "Union Find", "DFS", "BFS"],
        companies=[G, M],
        statement="A tree with `n` nodes labelled `1` to `n` had one extra edge added. `edges` lists all `n` edges. Return an edge that can be removed so the rest is a tree; if several work, return the one that appears **last** in `edges`.",
        entry="findRedundantConnection",
        params=[("edges", "List[List[int]]")],
        returns="List[int]",
        examples=[{"args": [[[1, 2], [1, 3], [2, 3]]]}, {"args": [[[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]]}],
        constraints=["3 ≤ n ≤ 1000", "No repeated edges"],
        hints=[
            "Union-find over the edges in order: the first edge whose endpoints are already connected closes the cycle — and it's the last cycle edge in the input."
        ],
        reference="""
class Solution:
    def findRedundantConnection(self, edges):
        p = list(range(len(edges) + 1))
        def find(x):
            while p[x] != x: p[x] = p[p[x]]; x = p[x]
            return x
        for a, b in edges:
            ra, rb = find(a), find(b)
            if ra == rb: return [a, b]
            p[ra] = rb
""",
        gen=lambda r: [[_redundant(r, r.randint(3, 12))] for _ in range(20)] + [[_redundant(r, 1000)]],
    ),
    Problem(
        slug="number-of-provinces",
        title="Number of Provinces",
        difficulty="Medium",
        pattern="graphs",
        topics=["Graph", "Union Find", "DFS", "BFS"],
        companies=[G, M],
        statement="`isConnected[i][j] = 1` when cities `i` and `j` are directly connected. A province is a group of cities connected directly or indirectly. Return the number of provinces.",
        entry="findCircleNum",
        params=[("isConnected", "List[List[int]]")],
        returns="int",
        examples=[{"args": [[[1, 1, 0], [1, 1, 0], [0, 0, 1]]]}, {"args": [[[1, 0, 0], [0, 1, 0], [0, 0, 1]]]}],
        constraints=["1 ≤ n ≤ 200", "isConnected is symmetric with 1s on the diagonal"],
        hints=["Count how many times you have to start a new DFS from an unvisited city."],
        reference="""
class Solution:
    def findCircleNum(self, m):
        n = len(m); seen = set(); count = 0
        for s in range(n):
            if s in seen: continue
            count += 1; seen.add(s); st = [s]
            while st:
                i = st.pop()
                for j in range(n):
                    if m[i][j] and j not in seen: seen.add(j); st.append(j)
        return count
""",
        gen=lambda r: (
            [[_adj_matrix(r, r.randint(1, 10), r.uniform(0, 0.3))] for _ in range(18)] + [[_adj_matrix(r, 200, 0.004)]]
        ),
    ),
    Problem(
        slug="is-graph-bipartite",
        title="Is Graph Bipartite?",
        difficulty="Medium",
        pattern="graphs",
        topics=["Graph", "DFS", "BFS", "Union Find"],
        companies=[M, G],
        statement="`graph[u]` lists the neighbours of node `u` in an undirected graph (no self-loops or parallel edges; it may be disconnected). Return `True` if the nodes can be split into two sets so every edge goes between the sets.",
        entry="isBipartite",
        params=[("graph", "List[List[int]]")],
        returns="bool",
        examples=[{"args": [[[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]]}, {"args": [[[1, 3], [0, 2], [1, 3], [0, 2]]]}],
        constraints=["1 ≤ n ≤ 100"],
        hints=[
            "2-colour each component with BFS: neighbours get the opposite colour. A neighbour with the same colour means no."
        ],
        reference="""
class Solution:
    def isBipartite(self, graph):
        color = {}
        for s in range(len(graph)):
            if s in color: continue
            color[s] = 0; q = deque([s])
            while q:
                u = q.popleft()
                for v in graph[u]:
                    if v not in color: color[v] = 1 - color[u]; q.append(v)
                    elif color[v] == color[u]: return False
        return True
""",
        gen=lambda r: (
            [[[[]]]] + [[_maybe_bipartite(r, r.randint(2, 10))] for _ in range(19)] + [[_maybe_bipartite(r, 100)]]
        ),
    ),
    Problem(
        slug="01-matrix",
        title="01 Matrix",
        difficulty="Medium",
        pattern="graphs",
        topics=["Array", "BFS", "Dynamic Programming", "Matrix"],
        companies=[G, M],
        statement="For every cell of the binary matrix `mat`, return the distance (number of up/down/left/right steps) to the nearest `0`. There is at least one `0`.",
        entry="updateMatrix",
        params=[("mat", "List[List[int]]")],
        returns="List[List[int]]",
        examples=[{"args": [[[0, 0, 0], [0, 1, 0], [0, 0, 0]]]}, {"args": [[[0, 0, 0], [0, 1, 0], [1, 1, 1]]]}],
        constraints=["1 ≤ rows · cols ≤ 10⁴"],
        hints=["Multi-source BFS from every 0 at once. (Or two DP passes: top-left then bottom-right.)"],
        reference="""
class Solution:
    def updateMatrix(self, mat):
        R, C = len(mat), len(mat[0])
        dist = [[-1] * C for _ in range(R)]
        q = deque()
        for i in range(R):
            for j in range(C):
                if mat[i][j] == 0: dist[i][j] = 0; q.append((i, j))
        while q:
            i, j = q.popleft()
            for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= x < R and 0 <= y < C and dist[x][y] < 0:
                    dist[x][y] = dist[i][j] + 1; q.append((x, y))
        return dist
""",
        gen=lambda r: (
            [[_with_zero(r, r.randint(1, 8), r.randint(1, 8))] for _ in range(18)] + [[_with_zero(r, 100, 100)]]
        ),
    ),
    Problem(
        slug="shortest-path-in-binary-matrix",
        title="Shortest Path in Binary Matrix",
        difficulty="Medium",
        pattern="graphs",
        topics=["Array", "BFS", "Matrix"],
        companies=[M, G],
        statement="In an `n × n` binary grid, find the shortest clear path from the top-left to the bottom-right cell. A clear path visits only `0` cells and moves in any of the **8** directions. Return the number of cells on the path, or `-1` if there is none.",
        entry="shortestPathBinaryMatrix",
        params=[("grid", "List[List[int]]")],
        returns="int",
        examples=[
            {"args": [[[0, 1], [1, 0]]]},
            {"args": [[[0, 0, 0], [1, 1, 0], [1, 1, 0]]]},
            {"args": [[[1, 0, 0], [1, 1, 0], [1, 1, 0]]]},
        ],
        constraints=["1 ≤ n ≤ 100"],
        hints=["Plain BFS with 8 neighbours. Check the start and end cells are 0 first."],
        reference="""
class Solution:
    def shortestPathBinaryMatrix(self, grid):
        n = len(grid)
        if grid[0][0] or grid[-1][-1]: return -1
        dist = {(0, 0): 1}; q = deque([(0, 0)])
        while q:
            i, j = q.popleft()
            if (i, j) == (n - 1, n - 1): return dist[(i, j)]
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    x, y = i + dx, j + dy
                    if 0 <= x < n and 0 <= y < n and not grid[x][y] and (x, y) not in dist:
                        dist[(x, y)] = dist[(i, j)] + 1; q.append((x, y))
        return -1
""",
        gen=lambda r: (
            [[[[0]]], [[[1]]]]
            + [(lambda n: [_bits(r, n, n, r.uniform(0.1, 0.4))])(r.randint(2, 8)) for _ in range(18)]
            + [[_bits(r, 100, 100, 0.3)]]
        ),
    ),
    Problem(
        slug="open-the-lock",
        title="Open the Lock",
        difficulty="Medium",
        pattern="graphs",
        topics=["Array", "Hash Table", "String", "BFS"],
        companies=[G, M],
        statement='A lock has four wheels, each showing a digit 0–9 that wraps around (9 → 0 and 0 → 9). One move turns one wheel by one slot. The lock starts at `"0000"`. If it ever shows a code in `deadends`, it jams.\n\nReturn the minimum number of moves to reach `target`, or `-1` if it\'s impossible.',
        entry="openLock",
        params=[("deadends", "List[str]"), ("target", "str")],
        returns="int",
        examples=[
            {"args": [["0201", "0101", "0102", "1212", "2002"], "0202"]},
            {"args": [["8888"], "0009"]},
            {"args": [["0000"], "8888"]},
        ],
        constraints=["1 ≤ len(deadends) ≤ 500", "target is not in deadends"],
        hints=["BFS over the 10⁴ codes; each code has 8 neighbours. Treat deadends as already visited."],
        reference="""
class Solution:
    def openLock(self, deadends, target):
        dead = set(deadends)
        if '0000' in dead: return -1
        dist = {'0000': 0}; q = deque(['0000'])
        while q:
            s = q.popleft()
            if s == target: return dist[s]
            for i in range(4):
                for d in (1, 9):
                    t = s[:i] + str((int(s[i]) + d) % 10) + s[i + 1:]
                    if t not in dist and t not in dead:
                        dist[t] = dist[s] + 1; q.append(t)
        return -1
""",
        gen=lambda r: (
            [_lock(r, r.randint(1, 40)) for _ in range(16)]
            + [[["0001", "0010", "0100", "1000", "0009", "0090", "0900", "9000"], "1111"], _lock(r, 500)]
        ),
    ),
    Problem(
        slug="network-delay-time",
        title="Network Delay Time",
        difficulty="Medium",
        pattern="graphs",
        topics=["Graph", "Heap", "Shortest Path", "Dijkstra"],
        companies=[G, M],
        statement="A network has `n` nodes labelled `1` to `n`. `times[i] = [u, v, w]` is a directed edge: a signal takes `w` time to go from `u` to `v`. A signal is sent from node `k`. Return how long until every node has received it, or `-1` if some node never does.",
        entry="networkDelayTime",
        params=[("times", "List[List[int]]"), ("n", "int"), ("k", "int")],
        returns="int",
        examples=[
            {"args": [[[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2]},
            {"args": [[[1, 2, 1]], 2, 1]},
            {"args": [[[1, 2, 1]], 2, 2]},
        ],
        constraints=["1 ≤ k ≤ n ≤ 100", "0 ≤ w ≤ 100", "All (u, v) pairs are distinct"],
        hints=["Dijkstra from k with a min-heap. The answer is the largest shortest distance."],
        reference="""
class Solution:
    def networkDelayTime(self, times, n, k):
        adj = defaultdict(list)
        for u, v, w in times: adj[u].append((v, w))
        dist = {}; h = [(0, k)]
        while h:
            d, u = heappop(h)
            if u in dist: continue
            dist[u] = d
            for v, w in adj[u]:
                if v not in dist: heappush(h, (d + w, v))
        return max(dist.values()) if len(dist) == n else -1
""",
        gen=lambda r: [_weighted(r, r.randint(1, 8), 0, 10) for _ in range(18)] + [_weighted(r, 100, 0, 100)],
    ),
    Problem(
        slug="cheapest-flights-within-k-stops",
        title="Cheapest Flights Within K Stops",
        difficulty="Medium",
        pattern="graphs",
        topics=["Graph", "Dynamic Programming", "BFS", "Shortest Path"],
        companies=[G, M],
        statement="There are `n` cities and directed `flights[i] = [from, to, price]`. Return the cheapest price from `src` to `dst` using at most `k` stops (so at most `k + 1` flights), or `-1` if there is no such route.",
        entry="findCheapestPrice",
        params=[("n", "int"), ("flights", "List[List[int]]"), ("src", "int"), ("dst", "int"), ("k", "int")],
        returns="int",
        examples=[
            {
                "args": [4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1],
                "note": "0 → 1 → 3 costs 700; 0 → 1 → 2 → 3 is cheaper but needs 2 stops.",
            },
            {"args": [3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1]},
            {"args": [3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0]},
        ],
        constraints=["1 ≤ n ≤ 100", "1 ≤ price ≤ 10⁴", "0 ≤ k < n", "src ≠ dst", "No duplicate flights or self-loops"],
        hints=[
            "Bellman-Ford limited to k + 1 rounds. Relax from a copy of last round's prices so one round adds at most one flight."
        ],
        reference="""
class Solution:
    def findCheapestPrice(self, n, flights, src, dst, k):
        cost = [inf] * n; cost[src] = 0
        for _ in range(k + 1):
            nxt = cost[:]
            for u, v, p in flights:
                if cost[u] + p < nxt[v]: nxt[v] = cost[u] + p
            cost = nxt
        return -1 if cost[dst] == inf else cost[dst]
""",
        gen=lambda r: [_flights(r, r.randint(2, 8)) for _ in range(18)] + [_flights(r, 100)],
    ),
    Problem(
        slug="min-cost-to-connect-all-points",
        title="Min Cost to Connect All Points",
        difficulty="Medium",
        pattern="graphs",
        topics=["Array", "Graph", "Union Find", "Minimum Spanning Tree"],
        companies=[G, M],
        statement="Connecting points `[xi, yi]` and `[xj, yj]` costs their Manhattan distance `|xi − xj| + |yi − yj|`. Return the minimum total cost to connect all `points` so there is exactly one path between any two.",
        entry="minCostConnectPoints",
        params=[("points", "List[List[int]]")],
        returns="int",
        examples=[{"args": [[[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]]}, {"args": [[[3, 12], [-2, 5], [-4, 1]]]}],
        constraints=["1 ≤ len(points) ≤ 1000", "−10⁶ ≤ xi, yi ≤ 10⁶", "Points are distinct"],
        hints=[
            "It's a minimum spanning tree on a complete graph. Prim's in O(n²) with an array of best distances beats sorting n² edges."
        ],
        reference="""
class Solution:
    def minCostConnectPoints(self, points):
        n = len(points); best = [inf] * n; best[0] = 0; used = [False] * n; total = 0
        for _ in range(n):
            u = min((i for i in range(n) if not used[i]), key=best.__getitem__)
            used[u] = True; total += best[u]; ux, uy = points[u]
            for v in range(n):
                if not used[v]:
                    d = abs(ux - points[v][0]) + abs(uy - points[v][1])
                    if d < best[v]: best[v] = d
        return total
""",
        gen=lambda r: [[_points(r, r.randint(1, 10), 20)] for _ in range(18)] + [[_points(r, 1000, 10**6)]],
    ),
    Problem(
        slug="path-with-minimum-effort",
        title="Path With Minimum Effort",
        difficulty="Medium",
        pattern="graphs",
        topics=["Array", "Binary Search", "Heap", "Matrix", "Dijkstra"],
        companies=[G, M],
        statement="Walk from the top-left to the bottom-right cell of `heights`, moving up/down/left/right. A route's effort is the largest absolute height difference between two consecutive cells on it. Return the minimum effort.",
        entry="minimumEffortPath",
        params=[("heights", "List[List[int]]")],
        returns="int",
        examples=[{"args": [[[1, 2, 2], [3, 8, 2], [5, 3, 5]]]}, {"args": [[[1, 2, 3], [3, 8, 4], [5, 3, 5]]]}],
        constraints=["1 ≤ rows, cols ≤ 100", "1 ≤ heights[i][j] ≤ 10⁶"],
        hints=[
            "Dijkstra where a path's cost is its max step instead of its sum. (Or binary search the effort and BFS.)"
        ],
        reference="""
class Solution:
    def minimumEffortPath(self, h):
        R, C = len(h), len(h[0]); best = {(0, 0): 0}; pq = [(0, 0, 0)]
        while pq:
            e, i, j = heappop(pq)
            if (i, j) == (R - 1, C - 1): return e
            if e > best[(i, j)]: continue
            for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= x < R and 0 <= y < C:
                    ne = max(e, abs(h[x][y] - h[i][j]))
                    if ne < best.get((x, y), inf): best[(x, y)] = ne; heappush(pq, (ne, x, y))
""",
        gen=lambda r: (
            [
                [[ints(r, c, 1, 10) for _ in range(rr)]]
                for rr, c in [(r.randint(1, 7), r.randint(1, 7)) for _ in range(18)]
            ]
            + [[[ints(r, 100, 1, 10**6) for _ in range(100)]]]
        ),
    ),
    Problem(
        slug="swim-in-rising-water",
        title="Swim in Rising Water",
        difficulty="Hard",
        pattern="graphs",
        topics=["Array", "Binary Search", "Heap", "Union Find", "Matrix"],
        companies=[G, M],
        statement="`grid` is `n × n` and holds each value `0` to `n² − 1` once, the elevation of each cell. At time `t` the water level is `t`, and you can swim between adjacent cells (up/down/left/right) when both elevations are ≤ `t`. Swimming takes no time.\n\nReturn the least time at which you can get from the top-left to the bottom-right.",
        entry="swimInWater",
        params=[("grid", "List[List[int]]")],
        returns="int",
        examples=[
            {"args": [[[0, 2], [1, 3]]]},
            {
                "args": [
                    [[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]]
                ]
            },
        ],
        constraints=["1 ≤ n ≤ 50"],
        hints=["Dijkstra minimising the maximum elevation on the path. Always expand the lowest reachable cell."],
        reference="""
class Solution:
    def swimInWater(self, grid):
        n = len(grid); seen = {(0, 0)}; pq = [(grid[0][0], 0, 0)]; t = 0
        while pq:
            e, i, j = heappop(pq); t = max(t, e)
            if (i, j) == (n - 1, n - 1): return t
            for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= x < n and 0 <= y < n and (x, y) not in seen:
                    seen.add((x, y)); heappush(pq, (grid[x][y], x, y))
""",
        gen=lambda r: [[[[0]]]] + [[_perm_grid(r, r.randint(2, 7))] for _ in range(18)] + [[_perm_grid(r, 50)]],
    ),
    Problem(
        slug="accounts-merge",
        title="Accounts Merge",
        difficulty="Medium",
        pattern="graphs",
        topics=["Array", "Hash Table", "String", "Union Find", "DFS"],
        companies=[M, G],
        statement="Each account is `[name, email1, email2, …]`. Two accounts belong to the same person if they share any email (a person's accounts all have the same name, but different people can share a name).\n\nMerge the accounts. Return each person as `[name, emails…]` with the emails **sorted**. The people can be in any order.",
        entry="accountsMerge",
        params=[("accounts", "List[List[str]]")],
        returns="List[List[str]]",
        examples=[
            {
                "args": [
                    [
                        ["John", "johnsmith@mail.com", "john_newyork@mail.com"],
                        ["John", "johnsmith@mail.com", "john00@mail.com"],
                        ["Mary", "mary@mail.com"],
                        ["John", "johnnybravo@mail.com"],
                    ]
                ]
            }
        ],
        constraints=["1 ≤ len(accounts) ≤ 1000", "2 ≤ len(accounts[i]) ≤ 10"],
        hints=[
            "Union-find over emails: union every email in an account with the account's first email. Then group emails by root."
        ],
        reference="""
class Solution:
    def accountsMerge(self, accounts):
        p = {}; owner = {}
        def find(x):
            while p[x] != x: p[x] = p[p[x]]; x = p[x]
            return x
        for acc in accounts:
            for e in acc[1:]:
                p.setdefault(e, e); owner[e] = acc[0]
                p[find(e)] = find(acc[1])
        groups = defaultdict(list)
        for e in p: groups[find(e)].append(e)
        return [[owner[root]] + sorted(es) for root, es in groups.items()]
""",
        gen=lambda r: [[_accounts(r, r.randint(1, 6))] for _ in range(18)] + [[_accounts(r, 300)]],
        compare="sorted",
    ),
    Problem(
        slug="reconstruct-itinerary",
        title="Reconstruct Itinerary",
        difficulty="Hard",
        pattern="graphs",
        topics=["Graph", "DFS", "Eulerian Circuit"],
        companies=[G, M],
        statement='`tickets[i] = [from, to]` are one-way flights. Every itinerary starts at `"JFK"` and must use every ticket exactly once. Among all valid itineraries, return the lexicographically smallest one (compare the lists of airport codes). At least one valid itinerary exists.',
        entry="findItinerary",
        params=[("tickets", "List[List[str]]")],
        returns="List[str]",
        examples=[
            {"args": [[["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]]},
            {
                "args": [[["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]],
                "note": "JFK → SFO → … is valid too, but larger.",
            },
        ],
        constraints=["1 ≤ len(tickets) ≤ 300", "Airports are 3 uppercase letters"],
        hints=[
            "It's an Eulerian path. Hierholzer's algorithm: DFS taking the smallest destination first, and add an airport to the route only once it has no tickets left. Reverse at the end.",
        ],
        reference="""
class Solution:
    def findItinerary(self, tickets):
        adj = defaultdict(list)
        for a, b in sorted(tickets, reverse=True): adj[a].append(b)
        route, st = [], ['JFK']
        while st:
            while adj[st[-1]]: st.append(adj[st[-1]].pop())
            route.append(st.pop())
        return route[::-1]
""",
        gen=lambda r: (
            [[_itinerary(r, r.randint(1, 8), r.randint(2, 4))] for _ in range(18)] + [[_itinerary(r, 300, 12)]]
        ),
    ),
    Problem(
        slug="making-a-large-island",
        title="Making A Large Island",
        difficulty="Hard",
        pattern="graphs",
        topics=["Array", "DFS", "BFS", "Union Find", "Matrix"],
        companies=[M, G],
        statement="`grid` is `n × n` with `1` for land and `0` for water. You may change **at most one** `0` to `1`. Return the size of the largest island (4-directionally connected land) you can get.",
        entry="largestIsland",
        params=[("grid", "List[List[int]]")],
        returns="int",
        examples=[{"args": [[[1, 0], [0, 1]]]}, {"args": [[[1, 1], [1, 0]]]}, {"args": [[[1, 1], [1, 1]]]}],
        constraints=["1 ≤ n ≤ 500"],
        hints=[
            "Label every island with an id and record its size.",
            "For each 0, add 1 plus the sizes of the distinct island ids around it. Remember the all-land case.",
        ],
        reference="""
class Solution:
    def largestIsland(self, grid):
        n = len(grid); label = [[0] * n for _ in range(n)]; size = {}; nid = 0
        for i in range(n):
            for j in range(n):
                if grid[i][j] and not label[i][j]:
                    nid += 1; label[i][j] = nid; st = [(i, j)]; c = 0
                    while st:
                        a, b = st.pop(); c += 1
                        for x, y in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                            if 0 <= x < n and 0 <= y < n and grid[x][y] and not label[x][y]:
                                label[x][y] = nid; st.append((x, y))
                    size[nid] = c
        best = max(size.values(), default=0)
        for i in range(n):
            for j in range(n):
                if not grid[i][j]:
                    ids = {label[x][y] for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)) if 0 <= x < n and 0 <= y < n}
                    best = max(best, 1 + sum(size.get(k, 0) for k in ids))
        return best
""",
        gen=lambda r: (
            [[[[0]]], [[[1]]]]
            + [(lambda n: [_bits(r, n, n, r.uniform(0.3, 0.7))])(r.randint(2, 7)) for _ in range(18)]
            + [[_bits(r, 500, 500, 0.5)]]
        ),
    ),
    # ---------------------------------------------------------------- backtracking
    Problem(
        slug="subsets-ii",
        title="Subsets II",
        difficulty="Medium",
        pattern="backtracking",
        topics=["Array", "Backtracking", "Bit Manipulation"],
        companies=[G, M],
        statement="`nums` may contain duplicates. Return all possible subsets without duplicate subsets, in any order.",
        entry="subsetsWithDup",
        params=[("nums", "List[int]")],
        returns="List[List[int]]",
        examples=[{"args": [[1, 2, 2]]}, {"args": [[0]]}],
        constraints=["1 ≤ len(nums) ≤ 10", "−10 ≤ nums[i] ≤ 10"],
        hints=[
            "Sort first. At each recursion depth, skip a value equal to the previous one you already tried at that depth."
        ],
        reference="""
class Solution:
    def subsetsWithDup(self, nums):
        return [list(c) for c in {tuple(sorted(c)) for k in range(len(nums) + 1) for c in combinations(nums, k)}]
""",
        gen=lambda r: [[ints(r, r.randint(1, 10), -3, 3)] for _ in range(18)] + [[[5] * 10]],
        compare="nested_sorted",
    ),
    Problem(
        slug="combination-sum-ii",
        title="Combination Sum II",
        difficulty="Medium",
        pattern="backtracking",
        topics=["Array", "Backtracking"],
        companies=[G, M],
        statement="Return every unique combination of `candidates` that sums to `target`. Each candidate can be used once (but `candidates` may contain duplicates), and the result must not contain duplicate combinations. Any order is accepted.",
        entry="combinationSum2",
        params=[("candidates", "List[int]"), ("target", "int")],
        returns="List[List[int]]",
        examples=[{"args": [[10, 1, 2, 7, 6, 1, 5], 8]}, {"args": [[2, 5, 2, 1, 2], 5]}],
        constraints=["1 ≤ len(candidates) ≤ 100", "1 ≤ candidates[i] ≤ 50", "1 ≤ target ≤ 30"],
        hints=[
            "Sort, then backtrack from index i; skip a candidate equal to its predecessor at the same depth, and stop once the sum passes target."
        ],
        reference="""
class Solution:
    def combinationSum2(self, candidates, target):
        c = sorted(candidates); out = []
        def go(i, left, path):
            if left == 0: out.append(path[:]); return
            for j in range(i, len(c)):
                if c[j] > left: break
                if j > i and c[j] == c[j - 1]: continue
                path.append(c[j]); go(j + 1, left - c[j], path); path.pop()
        go(0, target, [])
        return out
""",
        gen=lambda r: (
            [[ints(r, r.randint(1, 15), 1, 10), r.randint(1, 30)] for _ in range(18)]
            + [[ints(r, 100, 1, 50), 30], [[1] * 100, 30]]
        ),
        compare="nested_sorted",
    ),
    Problem(
        slug="permutations-ii",
        title="Permutations II",
        difficulty="Medium",
        pattern="backtracking",
        topics=["Array", "Backtracking"],
        companies=[G, M],
        statement="`nums` may contain duplicates. Return all **unique** permutations, in any order.",
        entry="permuteUnique",
        params=[("nums", "List[int]")],
        returns="List[List[int]]",
        examples=[{"args": [[1, 1, 2]]}, {"args": [[1, 2, 3]]}],
        constraints=["1 ≤ len(nums) ≤ 8", "−10 ≤ nums[i] ≤ 10"],
        hints=[
            "Backtrack over a Counter of remaining values instead of positions — each distinct value is tried once per slot."
        ],
        reference="""
class Solution:
    def permuteUnique(self, nums):
        return [list(p) for p in set(permutations(nums))]
""",
        gen=lambda r: [[ints(r, r.randint(1, 7), -2, 2)] for _ in range(18)] + [[[1, 1, 2, 2, 3, 3, 4, 4]]],
        compare="sorted",
    ),
    Problem(
        slug="letter-combinations-of-a-phone-number",
        title="Letter Combinations of a Phone Number",
        difficulty="Medium",
        pattern="backtracking",
        topics=["Hash Table", "String", "Backtracking"],
        companies=[G, M],
        statement="Each digit 2–9 maps to letters as on a phone keypad (`2 → abc`, `3 → def`, `4 → ghi`, `5 → jkl`, `6 → mno`, `7 → pqrs`, `8 → tuv`, `9 → wxyz`). Return every letter combination the string `digits` could represent, in any order. For an empty string, return `[]`.",
        entry="letterCombinations",
        params=[("digits", "str")],
        returns="List[str]",
        examples=[{"args": ["23"]}, {"args": [""]}, {"args": ["2"]}],
        constraints=["0 ≤ len(digits) ≤ 4", "digits[i] in '2'–'9'"],
        hints=["Backtrack one digit at a time, appending each of its letters."],
        reference="""
class Solution:
    def letterCombinations(self, digits):
        if not digits: return []
        pad = {'2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl', '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'}
        return [''.join(p) for p in product(*(pad[d] for d in digits))]
""",
        gen=lambda r: [[word(r, r.randint(1, 4), "23456789")] for _ in range(16)] + [["7979"]],
        compare="sorted",
    ),
    Problem(
        slug="generate-parentheses",
        title="Generate Parentheses",
        difficulty="Medium",
        pattern="backtracking",
        topics=["String", "Backtracking", "Dynamic Programming"],
        companies=[G, M],
        statement="Return every well-formed string of `n` pairs of parentheses, in any order.",
        entry="generateParenthesis",
        params=[("n", "int")],
        returns="List[str]",
        examples=[{"args": [3]}, {"args": [1]}],
        constraints=["1 ≤ n ≤ 8"],
        hints=[
            "Build left to right: add `(` while you have some left; add `)` only while it doesn't exceed the opens so far."
        ],
        reference="""
class Solution:
    def generateParenthesis(self, n):
        out = []
        def go(s, o, c):
            if len(s) == 2 * n: out.append(s); return
            if o < n: go(s + '(', o + 1, c)
            if c < o: go(s + ')', o, c + 1)
        go('', 0, 0)
        return out
""",
        gen=lambda r: [[n] for n in range(2, 9)],
        compare="sorted",
    ),
    Problem(
        slug="combinations",
        title="Combinations",
        difficulty="Medium",
        pattern="backtracking",
        topics=["Backtracking"],
        companies=[G, M],
        statement="Return all combinations of `k` numbers chosen from `1` to `n`, in any order.",
        entry="combine",
        params=[("n", "int"), ("k", "int")],
        returns="List[List[int]]",
        examples=[{"args": [4, 2]}, {"args": [1, 1]}],
        constraints=["1 ≤ k ≤ n ≤ 20"],
        hints=["Backtrack choosing the next number greater than the last; prune when not enough numbers remain."],
        reference="""
class Solution:
    def combine(self, n, k):
        return [list(c) for c in combinations(range(1, n + 1), k)]
""",
        gen=lambda r: (
            [(lambda n: [n, r.randint(1, n)])(r.randint(1, 9)) for _ in range(14)] + [[20, 3], [20, 1], [15, 7]]
        ),
        compare="nested_sorted",
    ),
    Problem(
        slug="palindrome-partitioning",
        title="Palindrome Partitioning",
        difficulty="Medium",
        pattern="backtracking",
        topics=["String", "Backtracking", "Dynamic Programming"],
        companies=[G, M],
        statement="Split `s` into pieces that are all palindromes. Return every possible split (each as a list of pieces in order), in any order.",
        entry="partition",
        params=[("s", "str")],
        returns="List[List[str]]",
        examples=[{"args": ["aab"]}, {"args": ["a"]}],
        constraints=["1 ≤ len(s) ≤ 16", "Lowercase English letters"],
        hints=["Backtrack over the end of the first piece; recurse on the rest only when the piece is a palindrome."],
        reference="""
class Solution:
    def partition(self, s):
        out = []
        def go(i, path):
            if i == len(s): out.append(path[:]); return
            for j in range(i + 1, len(s) + 1):
                if s[i:j] == s[i:j][::-1]:
                    path.append(s[i:j]); go(j, path); path.pop()
        go(0, [])
        return out
""",
        gen=lambda r: (
            [[word(r, r.randint(1, 10), "ab")] for _ in range(16)] + [["aaaaaaaaaaaaaaa"], ["abacabadabacaba"]]
        ),
        compare="sorted",
    ),
    Problem(
        slug="restore-ip-addresses",
        title="Restore IP Addresses",
        difficulty="Medium",
        pattern="backtracking",
        topics=["String", "Backtracking"],
        companies=[M, G],
        statement='Insert three dots into the digit string `s` to make a valid IPv4 address: four parts, each between 0 and 255, with no leading zeros (`"0"` is fine, `"01"` is not). Return every valid address, in any order.',
        entry="restoreIpAddresses",
        params=[("s", "str")],
        returns="List[str]",
        examples=[{"args": ["25525511135"]}, {"args": ["0000"]}, {"args": ["101023"]}],
        constraints=["1 ≤ len(s) ≤ 20", "Digits only"],
        hints=["Backtrack over 1–3 digit parts. Prune when the remaining length can't fill the remaining parts."],
        reference="""
class Solution:
    def restoreIpAddresses(self, s):
        def ok(p): return p == '0' or (p[0] != '0' and int(p) <= 255)
        out = []
        for a in range(1, 4):
            for b in range(a + 1, a + 4):
                for c in range(b + 1, b + 4):
                    parts = [s[:a], s[a:b], s[b:c], s[c:]]
                    if c < len(s) and all(p and len(p) <= 3 and ok(p) for p in parts):
                        out.append('.'.join(parts))
        return out
""",
        gen=lambda r: (
            [[word(r, r.randint(1, 13), "0125")] for _ in range(16)]
            + [["1111"], ["255255255255"], ["010010"], ["99999999999999999999"]]
        ),
        compare="sorted",
    ),
    Problem(
        slug="n-queens",
        title="N-Queens",
        difficulty="Hard",
        pattern="backtracking",
        topics=["Array", "Backtracking"],
        companies=[G, M],
        statement='Place `n` queens on an `n × n` chessboard so no two attack each other (same row, column or diagonal). Return every distinct solution, in any order. A solution is a list of rows like `".Q.."`.',
        entry="solveNQueens",
        params=[("n", "int")],
        returns="List[List[str]]",
        examples=[{"args": [4]}, {"args": [1]}],
        constraints=["1 ≤ n ≤ 9"],
        hints=["One queen per row. Track used columns and both diagonals (r − c and r + c) in sets."],
        reference="""
class Solution:
    def solveNQueens(self, n):
        out = []
        def go(r, cols, d1, d2, placed):
            if r == n:
                out.append(['.' * c + 'Q' + '.' * (n - c - 1) for c in placed]); return
            for c in range(n):
                if c not in cols and r - c not in d1 and r + c not in d2:
                    go(r + 1, cols | {c}, d1 | {r - c}, d2 | {r + c}, placed + [c])
        go(0, set(), set(), set(), [])
        return out
""",
        gen=lambda r: [[n] for n in range(2, 10)],
        compare="sorted",
    ),
    Problem(
        slug="sudoku-solver",
        title="Sudoku Solver",
        difficulty="Hard",
        pattern="backtracking",
        topics=["Array", "Hash Table", "Backtracking", "Matrix"],
        companies=[G, M],
        statement='Fill the empty cells (`"."`) of the 9×9 `board` so every row, every column and every 3×3 box contains the digits 1–9 exactly once. The puzzle has exactly one solution. Modify `board` in place and return it.',
        entry="solveSudoku",
        params=[("board", "List[List[str]]")],
        returns="List[List[str]]",
        examples=[
            {
                "args": [
                    [
                        ["5", "3", ".", ".", "7", ".", ".", ".", "."],
                        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
                        [".", "9", "8", ".", ".", ".", ".", "6", "."],
                        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
                        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
                        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
                        [".", "6", ".", ".", ".", ".", "2", "8", "."],
                        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
                        [".", ".", ".", ".", "8", ".", ".", "7", "9"],
                    ]
                ]
            }
        ],
        constraints=["board is 9×9", "Exactly one solution"],
        hints=[
            "Backtrack over empty cells, trying digits not already in that row, column or box (keep three lists of sets).",
            "Filling the cell with the fewest options first makes it much faster.",
        ],
        reference="""
class Solution:
    def solveSudoku(self, board):
        rows = [set() for _ in range(9)]; cols = [set() for _ in range(9)]; boxes = [set() for _ in range(9)]; empty = []
        for i in range(9):
            for j in range(9):
                d = board[i][j]
                if d == '.': empty.append((i, j))
                else: rows[i].add(d); cols[j].add(d); boxes[i // 3 * 3 + j // 3].add(d)
        def go():
            if not empty: return True
            k = max(range(len(empty)), key=lambda k: len(rows[empty[k][0]] | cols[empty[k][1]] | boxes[empty[k][0] // 3 * 3 + empty[k][1] // 3]))
            empty[k], empty[-1] = empty[-1], empty[k]
            i, j = empty.pop(); b = i // 3 * 3 + j // 3
            for d in '123456789':
                if d not in rows[i] and d not in cols[j] and d not in boxes[b]:
                    board[i][j] = d; rows[i].add(d); cols[j].add(d); boxes[b].add(d)
                    if go(): return True
                    rows[i].remove(d); cols[j].remove(d); boxes[b].remove(d)
            board[i][j] = '.'; empty.append((i, j))
            return False
        go()
        return board
""",
        gen=lambda r: [[_sudoku_variant(r, p)] for p in _SUDOKU_PUZZLES for _ in range(4)],
    ),
    Problem(
        slug="expression-add-operators",
        title="Expression Add Operators",
        difficulty="Hard",
        pattern="backtracking",
        topics=["Math", "String", "Backtracking"],
        companies=[M, G],
        statement='Insert `+`, `-` or `*` between the digits of `num` (or nothing, to join digits into a longer number) so the expression evaluates to `target`. Operands can\'t have leading zeros (`"05"` is not allowed, `"0"` is). Return every such expression, in any order.',
        entry="addOperators",
        params=[("num", "str"), ("target", "int")],
        returns="List[str]",
        examples=[{"args": ["123", 6]}, {"args": ["232", 8]}, {"args": ["3456237490", 9191]}],
        constraints=["1 ≤ len(num) ≤ 10", "−2³¹ ≤ target ≤ 2³¹ − 1"],
        hints=[
            "Backtrack over the next operand. Track the running value and the last term so `*` can undo it: value − last + last × operand.",
        ],
        reference="""
class Solution:
    def addOperators(self, num, target):
        out = []
        def go(i, expr, val, last):
            if i == len(num):
                if val == target: out.append(expr)
                return
            for j in range(i + 1, len(num) + 1):
                s = num[i:j]
                if len(s) > 1 and s[0] == '0': break
                x = int(s)
                if i == 0: go(j, s, x, x)
                else:
                    go(j, expr + '+' + s, val + x, x)
                    go(j, expr + '-' + s, val - x, -x)
                    go(j, expr + '*' + s, val - last + last * x, last * x)
        go(0, '', 0, 0)
        return out
""",
        gen=lambda r: (
            [["00", 0], ["105", 5], ["2147483648", -2147483648]]
            + [[word(r, r.randint(1, 7), "0123456789"), r.randint(-20, 60)] for _ in range(16)]
            + [["1234567890", 45], ["9999999999", 0]]
        ),
        compare="sorted",
        time_limit_ms=4000,
    ),
]


# ---------------------------------------------------------------- private generator helpers
def _flood(r: random.Random, R: int, C: int) -> list[Any]:
    return [[ints(r, C, 0, 2) for _ in range(R)], r.randrange(R), r.randrange(C), r.randint(0, 3)]


def _bits(r: random.Random, R: int, C: int, p: float) -> list[list[int]]:
    return [[int(r.random() < p) for _ in range(C)] for _ in range(R)]


def _xo(r: random.Random, R: int, C: int) -> list[list[str]]:
    return [["O" if r.random() < 0.45 else "X" for _ in range(C)] for _ in range(R)]


def _rooms(r: random.Random, R: int, C: int) -> list[list[int]]:
    return [[r.choices([-1, 0, INF], [3, 1, 12])[0] for _ in range(C)] for _ in range(R)]


def _edges(r: random.Random, n: int, m: int) -> list[list[int]]:
    pairs = {tuple(sorted(r.sample(range(n), 2))) for _ in range(m)}
    return [list(p) for p in pairs]


def _maybe_tree(r: random.Random, n: int) -> list[Any]:
    edges = [[r.randrange(i), i] for i in range(1, n)]
    match r.randrange(3):
        case 0:
            pass
        case 1 if len(edges) > 1:
            edges.pop(r.randrange(len(edges)))
            a, b = r.sample(range(n), 2)
            if [a, b] not in edges and [b, a] not in edges:
                edges.append([a, b])
        case _:
            edges.pop(r.randrange(len(edges)))
    r.shuffle(edges)
    return [n, edges]


def _redundant(r: random.Random, n: int) -> list[list[int]]:
    edges = [[r.randint(1, i), i + 1] for i in range(1, n)]
    while True:
        a, b = sorted(r.sample(range(1, n + 1), 2))
        if [a, b] not in edges and [b, a] not in edges:
            break
    edges.append([a, b])
    r.shuffle(edges)
    return edges


def _adj_matrix(r: random.Random, n: int, p: float) -> list[list[int]]:
    m = [[int(i == j) for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if r.random() < p:
                m[i][j] = m[j][i] = 1
    return m


def _maybe_bipartite(r: random.Random, n: int) -> list[list[int]]:
    side = [r.randrange(2) for _ in range(n)]
    adj: list[set[int]] = [set() for _ in range(n)]
    for _ in range(n * 2):
        a, b = r.sample(range(n), 2)
        if side[a] != side[b] or r.random() < 0.03:
            adj[a].add(b)
            adj[b].add(a)
    return [sorted(s) for s in adj]


def _with_zero(r: random.Random, R: int, C: int) -> list[list[int]]:
    m = _bits(r, R, C, r.uniform(0.5, 0.95))
    m[r.randrange(R)][r.randrange(C)] = 0
    return m


def _lock(r: random.Random, n: int) -> list[Any]:
    dead = list({word(r, 4, "0123456789") for _ in range(n)})
    if r.random() < 0.9 and "0000" in dead:
        dead.remove("0000")
    while (target := word(r, 4, "0123456789")) in dead:
        pass
    return [dead, target]


def _weighted(r: random.Random, n: int, lo: int, hi: int) -> list[Any]:
    pairs = {(a, b) for _ in range(n * 3) for a, b in [r.sample(range(1, n + 1), 2)]} if n > 1 else set()
    return [[[a, b, r.randint(lo, hi)] for a, b in sorted(pairs)], n, r.randint(1, n)]


def _flights(r: random.Random, n: int) -> list[Any]:
    pairs = {(a, b) for _ in range(n * 3) for a, b in [r.sample(range(n), 2)]}
    src, dst = r.sample(range(n), 2)
    return [n, [[a, b, r.randint(1, 100)] for a, b in sorted(pairs)], src, dst, r.randint(0, n - 1)]


def _points(r: random.Random, n: int, span: int) -> list[list[int]]:
    pts = {(r.randint(-span, span), r.randint(-span, span)) for _ in range(n)}
    return [list(p) for p in pts]


def _perm_grid(r: random.Random, n: int) -> list[list[int]]:
    vals = r.sample(range(n * n), n * n)
    return [vals[i * n : (i + 1) * n] for i in range(n)]


def _accounts(r: random.Random, people: int) -> list[list[str]]:
    out = []
    for p in range(people):
        name = r.choice(["Ann", "Bob", "Cy"])
        emails = [f"{name.lower()}{p}_{k}@mail.com" for k in range(r.randint(1, 6))]
        for _ in range(r.randint(1, 3)):  # each account is a subset sharing at least one email with the next
            out.append([name, *r.sample(emails, r.randint(1, min(4, len(emails))))])
        if len(emails) > 1:
            out.append([name, *emails[:2]])
    r.shuffle(out)
    return out


def _itinerary(r: random.Random, n: int, airports: int) -> list[list[str]]:
    codes = [
        "JFK",
        *r.sample(
            ["ATL", "SFO", "LAX", "MUC", "LHR", "CDG", "NRT", "SYD", "DXB", "AMS", "MAD", "YYZ", "GRU"], airports - 1
        ),
    ]
    cur, tickets = "JFK", []
    for _ in range(n):
        nxt = r.choice([c for c in codes if c != cur])
        tickets.append([cur, nxt])
        cur = nxt
    r.shuffle(tickets)
    return tickets


def _sudoku_variant(r: random.Random, puzzle: str) -> list[list[str]]:
    """Relabel digits and shuffle rows/columns within bands: every variant keeps a unique solution."""
    digits = list("123456789")
    r.shuffle(digits)
    relabel = dict(zip("123456789", digits, strict=True)) | {".": "."}
    grid = [[relabel[puzzle[i * 9 + j]] for j in range(9)] for i in range(9)]
    rows = [b * 3 + i for b in r.sample(range(3), 3) for i in r.sample(range(3), 3)]
    cols = [b * 3 + i for b in r.sample(range(3), 3) for i in r.sample(range(3), 3)]
    grid = [[grid[i][j] for j in cols] for i in rows]
    return [list(row) for row in zip(*grid, strict=True)] if r.random() < 0.5 else grid
