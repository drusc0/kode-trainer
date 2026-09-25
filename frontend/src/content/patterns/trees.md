## Recognise it

`TreeNode` inputs. Ask yourself: does each node need information **from its children** (DFS, post-order) or **per level** (BFS)?

## DFS: return information upward

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

## BFS: level by level

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

## BST validation

Pass a `(low, high)` range down, or check that an in-order traversal is strictly increasing. Comparing only a node's direct children is the classic bug.

## Lowest common ancestor

Return the node if it's `p` or `q`. If both subtrees return something, the current node is the answer; otherwise pass up whichever side is non-empty.

## Complexity

O(n) time. O(h) space for DFS, O(width) for BFS.
