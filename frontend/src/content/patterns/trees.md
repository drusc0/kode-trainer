## The idea in plain words

A binary tree is a **family tree**: each person has at most two children. There are two ways to explore it:

- **DFS (depth-first)** is like asking a question that each person answers by first asking their children. "How tall is your family below you?" Each node asks its two kids, takes the bigger answer and adds 1. Information flows **up** from the leaves. Recursion does this naturally.
- **BFS (breadth-first)** is like taking a **family photo one generation at a time**: grandparents, then parents, then kids. A queue holds the people waiting for their turn.

The key question for every tree problem is: **what does each node need from its children?**

## You'll know it's this pattern when…

- The input is a `TreeNode`.
- You're asked about depth, height, diameter, paths or balance (DFS).
- You're asked about levels, a "right side view" or zigzag order (BFS).
- It's a binary search tree: left < node < right.

## Picture it

```text
          1             DFS height (answers flow up):
        /   \             4 → 1, 5 → 1, 3 → 1
       2     3            2 → 1 + max(1, 1) = 2
      / \                 1 → 1 + max(2, 1) = 3
     4   5
                        BFS levels (queue, one row at a time):
                          [1]  →  [2, 3]  →  [4, 5]
```

## Walk through an example

The diameter (the longest path between any two nodes) of the tree above:

1. At each node, the longest path **through it** is `left height + right height`.
2. Node 2: left height 1 (node 4) + right height 1 (node 5) = 2 edges.
3. Node 1: left height 2 + right height 1 = 3 edges (4 → 2 → 1 → 3).
4. Keep the best seen: 3. Each node still **returns its height** to its parent, because that's what the parent needs.

## The code

### DFS: return information upward

```python
def diameter(root):
    best = 0
    def height(node):
        nonlocal best
        if not node:
            return 0
        l, r = height(node.left), height(node.right)
        best = max(best, l + r)      # longest path through this node
        return 1 + max(l, r)         # what the parent needs
    height(root)
    return best
```

### BFS: level by level

```python
def levels(root):
    out, q = [], deque([root] if root else [])
    while q:
        level = []
        for _ in range(len(q)):      # exactly one level
            node = q.popleft()
            level.append(node.val)
            if node.left: q.append(node.left)
            if node.right: q.append(node.right)
        out.append(level)
    return out
```

### BST validation

Pass a `(low, high)` range down as you go, or check that an in-order traversal is strictly increasing. Comparing a node only with its direct children is the classic bug: a grandchild can still break the rule.

### Lowest common ancestor

Return the node if it's `p` or `q`. If both subtrees return something, the current node is the answer; otherwise pass up whichever side found something.

## How fast is it?

O(n) time, because every node is visited once. Space is O(h) for DFS (h is the height, from the recursion) or O(width) for BFS (from the queue).

## Common mistakes

- Forgetting the `None` base case: every recursive function starts with "if not node".
- Mixing up "what I return to my parent" with "the answer I'm tracking" (like height versus diameter above).
- Very deep, skewed trees can hit Python's recursion limit. Mention an iterative version.
