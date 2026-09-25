## Recognise it

"k largest / smallest / closest / most frequent", merging k sorted sources, or repeatedly taking the cheapest next item.

## Core idea

`heapq` keeps the minimum at `heap[0]`. To keep the **k largest**, hold a min-heap of size k and pop whenever it grows past k. The root is then the k-th largest.

## Templates

```python
def kth_largest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)
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

## Complexity

O(n log k) for top-k, O(N log k) for merging k lists. `heapify` is O(n).

## Alternatives worth mentioning

- **Quickselect**: O(n) average for the k-th element.
- **Bucket sort** by frequency: O(n) for top-k frequent.
- `heapq.nlargest(k, xs, key=…)` is fine in an interview if you can explain the cost.
