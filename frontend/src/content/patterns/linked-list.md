## Recognise it

`ListNode` inputs: reversing, merging, finding the middle or k-th node from the end, detecting cycles.

## Core ideas

- A **dummy head** removes special cases for the first node.
- **Fast/slow pointers** find the middle, detect cycles, and find the k-th node from the end.
- **In-place reversal** needs three pointers: `prev`, `cur`, `next`.

## Templates

```python
def reverse(head):
    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev, head = head, nxt
    return prev

def merge_two(a, b):
    dummy = tail = ListNode()
    while a and b:
        if a.val <= b.val: tail.next, a = a, a.next
        else:              tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next

def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow
```

## Complexity

O(n) time and O(1) extra space for most list manipulation.

## Pitfalls

- Save `next` before you overwrite a pointer.
- Merge k lists with a heap of `(val, list_index, node)`. The index breaks ties, because nodes can't be compared.
- Recursive reversal uses O(n) stack. Mention it for long lists.
