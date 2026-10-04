## The idea in plain words

Design problems ask you to build a small class where **every method has a speed limit**, for example "`get` and `put` must both be O(1)". Usually no single data structure can do it all, so you **combine two**, like a librarian who keeps both an **index card catalogue** (find any book instantly) and a **"recently returned" cart** (know what's oldest).

The skill is matching each requirement to a tool, then keeping the tools in sync inside every method.

## You'll know it's this pattern when…

- You're asked to implement a class with several methods.
- Each method has a complexity target (O(1) `get`/`put`, O(log n) lookups).
- The data is time-versioned, cached or ordered by recency.

## Picture it

An LRU cache is a hash map **plus** a doubly linked list ordered from most to least recently used:

```text
map:  { A → ●, B → ●, C → ● }       ← O(1) jump to any node
              │       │       │
list: HEAD ⇄ [A] ⇄ [B] ⇄ [C] ⇄ TAIL
       most recent ──────► least recent (evicted first)

get(C): unlink C, move it to the front →  HEAD ⇄ C ⇄ A ⇄ B ⇄ TAIL
put(D) when full: evict TAIL.prev (B), add D at the front
```

## Walk through an example

The approach, in three steps:

1. **List every operation and its target.** LRU: `get` O(1) and `put` O(1), and evict the least recently used item when full.
2. **Pick a structure per requirement.** O(1) lookup by key → hash map. O(1) "move to front" and "remove oldest" → doubly linked list. "Latest value at or before time t" → sorted list + binary search.
3. **Combine them and keep them in sync.** Every method that touches the list also updates the map, and vice versa.

## The code: LRU cache from scratch

```python
class Node:
    def __init__(self, k=0, v=0):
        self.k, self.v, self.prev, self.next = k, v, None, None

class LRUCache:
    def __init__(self, capacity):
        self.cap, self.map = capacity, {}
        self.head, self.tail = Node(), Node()        # sentinels: no empty-list special cases
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

### Time-based key-value store

Keep `key -> [(timestamp, value), ...]`. The list is already sorted because timestamps only increase, so `get` is a `bisect_right`.

## How fast is it?

Whatever each operation's target is. Say it out loud for every method, and make sure no hidden O(n) step (like `list.remove`) sneaks in.

## Common mistakes

- Updating the map but forgetting the list, or the other way round.
- Storing the key inside the node is required: when you evict a node, you need its key to delete it from the map.
