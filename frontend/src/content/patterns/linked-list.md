## The idea in plain words

A linked list is a **treasure hunt**: each clue (node) holds a value and tells you where the next clue is. You can't jump to clue 5 directly; you follow the chain. Every trick here is about rewiring the "next clue" arrows without losing your place.

Three tools solve most problems:

- **Dummy head**: a fake first node, so the real first node is never a special case.
- **Fast and slow runners**: two walkers, one twice as fast. When the fast one reaches the end, the slow one is in the middle. If there's a loop, the fast one laps the slow one and they meet.
- **Reversal**: walk the list and turn each arrow around, holding on to the next node first.

## You'll know it's this pattern when…

- The input is a `ListNode`.
- You reverse, merge, reorder or remove nodes.
- You need the middle, the k-th node from the end, or to detect a cycle.

## Picture it

Reversing `1 → 2 → 3`:

```text
start:   None    1 → 2 → 3 → None
         prev   cur

step 1:  None ← 1    2 → 3 → None      (saved nxt = 2 before flipping)
                prev cur
step 2:  None ← 1 ← 2    3 → None
                    prev cur
step 3:  None ← 1 ← 2 ← 3    None
                        prev cur      → return prev (3)
```

## Walk through an example

Find the middle of `1 → 2 → 3 → 4 → 5`:

```text
slow: 1   fast: 1
slow: 2   fast: 3
slow: 3   fast: 5      fast.next is None → stop, the middle is 3
```

Fast moves twice as far, so when it has covered the whole list, slow has covered half.

## The code

```python
def reverse(head):
    prev = None
    while head:
        nxt = head.next              # save the next clue before rewiring
        head.next = prev             # flip the arrow
        prev, head = head, nxt
    return prev

def merge_two(a, b):
    dummy = tail = ListNode()        # fake head: no special case for the first node
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

## How fast is it?

O(n) time and O(1) extra space for most list problems: you walk the chain once and only keep a few pointers.

## Common mistakes

- Save `next` before you overwrite a pointer, or the rest of the list is lost.
- Merge k lists with a heap of `(val, list_index, node)`. The index breaks ties, because nodes can't be compared.
- Recursive reversal uses O(n) call-stack space. Mention it for long lists.
