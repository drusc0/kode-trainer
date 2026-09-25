## Recognise it

A class with several methods and complexity targets, such as "`get` and `put` in O(1)".

## Approach

1. List every operation and its target complexity.
2. Pick a structure per requirement: O(1) lookup → hash map; order or recency → linked list or deque; "latest value ≤ t" → sorted list + binary search.
3. Combine them and keep them in sync inside every method.

## LRU cache from scratch

```python
class Node:
    def __init__(self, k=0, v=0):
        self.k, self.v, self.prev, self.next = k, v, None, None

class LRUCache:
    def __init__(self, capacity):
        self.cap, self.map = capacity, {}
        self.head, self.tail = Node(), Node()        # sentinels
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, n):
        n.prev.next, n.next.prev = n.next, n.prev

    def _add_front(self, n):
        n.prev, n.next = self.head, self.head.next
        self.head.next.prev = n
        self.head.next = n

    def get(self, key):
        if key not in self.map:
            return -1
        n = self.map[key]
        self._remove(n); self._add_front(n)
        return n.v

    def put(self, key, value):
        if key in self.map:
            self._remove(self.map[key])
        n = self.map[key] = Node(key, value)
        self._add_front(n)
        if len(self.map) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.k]
```

`OrderedDict` with `move_to_end` and `popitem(last=False)` does the same in a few lines. Know both, and ask which one the interviewer wants.

## Time-based key-value store

Keep `key -> [(timestamp, value), ...]`. The list is already sorted because timestamps increase, so `get` is a `bisect_right`.
