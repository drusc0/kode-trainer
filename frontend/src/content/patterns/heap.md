## The idea in plain words

A heap is a **hospital waiting room with triage**: whoever is most urgent is always seen next, regardless of arrival order. Adding a patient or calling the next one is fast (O(log n)), and you can always peek at who's next for free.

Python's `heapq` is a **min-heap**: the smallest item is at `heap[0]`.

The clever part for "top k" questions: to keep the **k largest**, use a min-heap of size k as a **VIP list with a bouncer**. The bouncer stands at the door (`heap[0]`, the smallest VIP). A newcomer bigger than the bouncer gets in, and the bouncer is kicked out. Once everyone has been seen, the bouncer is exactly the k-th largest.

## You'll know it's this pattern when…

- The question says "k largest / smallest / closest / most frequent".
- You **merge k sorted** lists or streams.
- You keep taking the **cheapest / earliest / best next** item (scheduling, Dijkstra).

## Picture it

The 2nd largest in `[3, 2, 1, 5, 6, 4]` uses a min-heap of size 2:

```text
push 3   heap [3]
push 2   heap [2, 3]
push 1   heap [1, 2, 3] → too big, pop 1 → [2, 3]
push 5   [2, 3, 5]      → pop 2         → [3, 5]
push 6   [3, 5, 6]      → pop 3         → [5, 6]
push 4   [4, 5, 6]      → pop 4         → [5, 6]
answer = heap[0] = 5
```

## Walk through an example

Merge `[1 → 4]`, `[1 → 3]`, `[2 → 6]`:

1. Put each list's head in the heap: `(1, list 0)`, `(1, list 1)`, `(2, list 2)`.
2. Pop the smallest (1 from list 0), add it to the output, and push its next node (4).
3. Pop 1 (list 1) and push 3. Pop 2 and push 6. Pop 3, pop 4, pop 6.
4. Output: `1 → 1 → 2 → 3 → 4 → 6`. The heap only ever holds k items, one per list.

## The code

```python
def kth_largest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)      # kick out the bouncer
    return heap[0]

def merge_k(lists):
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    heapq.heapify(heap)
    dummy = tail = ListNode()
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```

## How fast is it?

O(n log k) for top-k, because the heap never grows past k. O(N log k) to merge k lists with N nodes in total. `heapify` on a list is O(n).

## Alternatives worth mentioning

- **Quickselect**: O(n) on average for the k-th element.
- **Bucket sort** by frequency: O(n) for the top-k most frequent.
- `heapq.nlargest(k, xs, key=…)` is fine in an interview if you can explain what it costs.

## Common mistakes

- `heapq` is a **min**-heap. For a max-heap, push negated values.
- Tuples compare item by item, so add a tie-breaker index when the payload (like a `ListNode`) can't be compared.
