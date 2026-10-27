import random
from collections import deque
from typing import Any

from .base import Problem, distinct, ints, level_order, random_bst, random_tree

G, M = "google", "meta"

LIST_NOTE = "Lists are shown as arrays, e.g. `[1,2,3]`."
TREE_NOTE = "Trees are shown in level order with `None` for missing children, e.g. `[3,9,20,None,None,15,7]`."

PROBLEMS = [
    # ---------------------------------------------------------------- linked lists
    Problem(
        slug="merge-two-sorted-lists",
        title="Merge Two Sorted Lists",
        difficulty="Easy",
        pattern="linked-list",
        topics=["Linked List", "Recursion"],
        companies=[G, M],
        statement=f"Merge two sorted linked lists into one sorted list by splicing their nodes together, and return its head. {LIST_NOTE}",
        entry="mergeTwoLists",
        params=[("list1", "Optional[ListNode]"), ("list2", "Optional[ListNode]")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 2, 4], [1, 3, 4]]}, {"args": [[], []]}, {"args": [[], [0]]}],
        constraints=["0 ≤ nodes in each list ≤ 50", "Both lists are sorted ascending"],
        hints=["A dummy head node avoids special-casing the first node. Attach the smaller head each step."],
        reference="""
class Solution:
    def mergeTwoLists(self, list1, list2):
        dummy = cur = ListNode()
        while list1 and list2:
            if list1.val <= list2.val: cur.next, list1 = list1, list1.next
            else: cur.next, list2 = list2, list2.next
            cur = cur.next
        cur.next = list1 or list2
        return dummy.next
""",
        gen=lambda r: [
            [sorted(ints(r, r.randint(0, 50), -100, 100)), sorted(ints(r, r.randint(0, 50), -100, 100))]
            for _ in range(20)
        ],
    ),
    Problem(
        slug="middle-of-the-linked-list",
        title="Middle of the Linked List",
        difficulty="Easy",
        pattern="linked-list",
        topics=["Linked List", "Two Pointers"],
        companies=[G, M],
        statement=f"Return the middle node of a non-empty linked list. With two middle nodes, return the second one. {LIST_NOTE} The output shows the list starting at the node you return.",
        entry="middleNode",
        params=[("head", "Optional[ListNode]")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 2, 3, 4, 5]]}, {"args": [[1, 2, 3, 4, 5, 6]]}],
        constraints=["1 ≤ nodes ≤ 100"],
        hints=["Slow pointer moves one step, fast moves two. When fast runs off the end, slow is in the middle."],
        reference="""
class Solution:
    def middleNode(self, head):
        slow = fast = head
        while fast and fast.next:
            slow, fast = slow.next, fast.next.next
        return slow
""",
        gen=lambda r: [[[1]], [[1, 2]]] + [[ints(r, r.randint(1, 100), 1, 100)] for _ in range(18)],
    ),
    Problem(
        slug="palindrome-linked-list",
        title="Palindrome Linked List",
        difficulty="Easy",
        pattern="linked-list",
        topics=["Linked List", "Two Pointers", "Stack"],
        companies=[M, G],
        statement=f"Return `True` if the linked list reads the same forwards and backwards. {LIST_NOTE}\n\nBonus: O(n) time and O(1) space.",
        entry="isPalindrome",
        params=[("head", "Optional[ListNode]")],
        returns="bool",
        examples=[{"args": [[1, 2, 2, 1]]}, {"args": [[1, 2]]}],
        constraints=["1 ≤ nodes ≤ 10⁵", "0 ≤ Node.val ≤ 9"],
        hints=["Find the middle with fast/slow pointers, reverse the second half, then compare the halves."],
        reference="""
class Solution:
    def isPalindrome(self, head):
        vals = []
        while head: vals.append(head.val); head = head.next
        return vals == vals[::-1]
""",
        gen=lambda r: (
            [[[1]]] + [[_maybe_palindrome(r, r.randint(1, 20))] for _ in range(18)] + [[_maybe_palindrome(r, 100_000)]]
        ),
    ),
    Problem(
        slug="remove-duplicates-from-sorted-list",
        title="Remove Duplicates from Sorted List",
        difficulty="Easy",
        pattern="linked-list",
        topics=["Linked List"],
        companies=[G, M],
        statement=f"The linked list is sorted. Delete duplicates so each value appears once, and return the head. {LIST_NOTE}",
        entry="deleteDuplicates",
        params=[("head", "Optional[ListNode]")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 1, 2]]}, {"args": [[1, 1, 2, 3, 3]]}],
        constraints=["0 ≤ nodes ≤ 300"],
        hints=["While the next node has the same value, skip it: `cur.next = cur.next.next`."],
        reference="""
class Solution:
    def deleteDuplicates(self, head):
        cur = head
        while cur and cur.next:
            if cur.next.val == cur.val: cur.next = cur.next.next
            else: cur = cur.next
        return head
""",
        gen=lambda r: (
            [[[]], [[1, 1, 1]]]
            + [[sorted(ints(r, r.randint(0, 30), 0, 10))] for _ in range(18)]
            + [[sorted(ints(r, 300, -100, 100))]]
        ),
    ),
    Problem(
        slug="remove-linked-list-elements",
        title="Remove Linked List Elements",
        difficulty="Easy",
        pattern="linked-list",
        topics=["Linked List", "Recursion"],
        companies=[G, M],
        statement=f"Remove every node whose value equals `val`, and return the new head. {LIST_NOTE}",
        entry="removeElements",
        params=[("head", "Optional[ListNode]"), ("val", "int")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 2, 6, 3, 4, 5, 6], 6]}, {"args": [[], 1]}, {"args": [[7, 7, 7, 7], 7]}],
        constraints=["0 ≤ nodes ≤ 10⁴", "1 ≤ Node.val, val ≤ 50"],
        hints=["A dummy node before the head makes removing the head the same as removing any other node."],
        reference="""
class Solution:
    def removeElements(self, head, val):
        dummy = cur = ListNode(0, head)
        while cur.next:
            if cur.next.val == val: cur.next = cur.next.next
            else: cur = cur.next
        return dummy.next
""",
        gen=lambda r: (
            [[ints(r, r.randint(0, 20), 1, 4), r.randint(1, 4)] for _ in range(20)] + [[ints(r, 10_000, 1, 3), 2]]
        ),
    ),
    Problem(
        slug="reorder-list",
        title="Reorder List",
        difficulty="Medium",
        pattern="linked-list",
        topics=["Linked List", "Two Pointers", "Stack"],
        companies=[M, G],
        statement=f"Reorder the list `L0 → L1 → … → Ln` into `L0 → Ln → L1 → Ln−1 → L2 → …` by relinking nodes (not changing values). Do it in place and return `head`. {LIST_NOTE}",
        entry="reorderList",
        params=[("head", "Optional[ListNode]")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 2, 3, 4]]}, {"args": [[1, 2, 3, 4, 5]]}],
        constraints=["1 ≤ nodes ≤ 5 × 10⁴"],
        hints=[
            "Three steps you already know: find the middle, reverse the second half, merge the two halves alternately."
        ],
        reference="""
class Solution:
    def reorderList(self, head):
        nodes = []
        cur = head
        while cur: nodes.append(cur); cur = cur.next
        i, j = 0, len(nodes) - 1
        while i < j:
            nodes[i].next = nodes[j]; i += 1
            if i == j: break
            nodes[j].next = nodes[i]; j -= 1
        nodes[i].next = None
        return head
""",
        gen=lambda r: (
            [[[1]], [[1, 2]]] + [[ints(r, r.randint(1, 20), 1, 100)] for _ in range(18)] + [[list(range(50_000))]]
        ),
    ),
    Problem(
        slug="remove-nth-node-from-end-of-list",
        title="Remove Nth Node From End of List",
        difficulty="Medium",
        pattern="linked-list",
        topics=["Linked List", "Two Pointers"],
        companies=[M, G],
        statement=f"Remove the `n`-th node from the end of the list and return its head. {LIST_NOTE}\n\nCan you do it in one pass?",
        entry="removeNthFromEnd",
        params=[("head", "Optional[ListNode]"), ("n", "int")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 2, 3, 4, 5], 2]}, {"args": [[1], 1]}, {"args": [[1, 2], 1]}],
        constraints=["1 ≤ nodes ≤ 30", "1 ≤ n ≤ nodes"],
        hints=["Move a fast pointer n steps ahead (from a dummy node), then move both until fast reaches the end."],
        reference="""
class Solution:
    def removeNthFromEnd(self, head, n):
        dummy = ListNode(0, head); fast = slow = dummy
        for _ in range(n): fast = fast.next
        while fast.next: fast, slow = fast.next, slow.next
        slow.next = slow.next.next
        return dummy.next
""",
        gen=lambda r: [(lambda a: [a, r.randint(1, len(a))])(ints(r, r.randint(1, 30), 0, 100)) for _ in range(20)],
    ),
    Problem(
        slug="add-two-numbers",
        title="Add Two Numbers",
        difficulty="Medium",
        pattern="linked-list",
        topics=["Linked List", "Math", "Recursion"],
        companies=[G, M],
        statement=f"Two non-negative integers are stored as linked lists of digits in **reverse** order (`[2,4,3]` is 342). Return their sum as a list in the same format. {LIST_NOTE}",
        entry="addTwoNumbers",
        params=[("l1", "Optional[ListNode]"), ("l2", "Optional[ListNode]")],
        returns="Optional[ListNode]",
        examples=[
            {"args": [[2, 4, 3], [5, 6, 4]], "note": "342 + 465 = 807."},
            {"args": [[0], [0]]},
            {"args": [[9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9]]},
        ],
        constraints=["1 ≤ nodes ≤ 100", "No leading zeros except the number 0 itself"],
        hints=["Add digit by digit with a carry, like on paper. Don't forget a final carry."],
        reference="""
class Solution:
    def addTwoNumbers(self, l1, l2):
        dummy = cur = ListNode(); carry = 0
        while l1 or l2 or carry:
            s = carry + (l1.val if l1 else 0) + (l2.val if l2 else 0)
            carry, d = divmod(s, 10)
            cur.next = ListNode(d); cur = cur.next
            l1 = l1.next if l1 else None; l2 = l2.next if l2 else None
        return dummy.next
""",
        gen=lambda r: (
            [[_digits(r, r.randint(1, 15)), _digits(r, r.randint(1, 15))] for _ in range(18)]
            + [[_digits(r, 100), _digits(r, 100)]]
        ),
    ),
    Problem(
        slug="reverse-linked-list-ii",
        title="Reverse Linked List II",
        difficulty="Medium",
        pattern="linked-list",
        topics=["Linked List"],
        companies=[M, G],
        statement=f"Reverse the nodes from position `left` to position `right` (1-indexed, inclusive) and return the head. {LIST_NOTE}\n\nCan you do it in one pass?",
        entry="reverseBetween",
        params=[("head", "Optional[ListNode]"), ("left", "int"), ("right", "int")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 2, 3, 4, 5], 2, 4]}, {"args": [[5], 1, 1]}],
        constraints=["1 ≤ nodes ≤ 500", "1 ≤ left ≤ right ≤ nodes"],
        hints=[
            "Walk to the node before `left`. Then repeatedly move the node after the sublist's tail to the front of the sublist."
        ],
        reference="""
class Solution:
    def reverseBetween(self, head, left, right):
        vals = []
        cur = head
        while cur: vals.append(cur.val); cur = cur.next
        vals[left - 1:right] = vals[left - 1:right][::-1]
        cur = head
        for v in vals: cur.val = v; cur = cur.next
        return head
""",
        gen=lambda r: (
            [
                (lambda a: [a, *sorted([r.randint(1, len(a)), r.randint(1, len(a))])])(ints(r, r.randint(1, 20), 0, 50))
                for _ in range(20)
            ]
            + [[list(range(500)), 1, 500]]
        ),
    ),
    Problem(
        slug="swap-nodes-in-pairs",
        title="Swap Nodes in Pairs",
        difficulty="Medium",
        pattern="linked-list",
        topics=["Linked List", "Recursion"],
        companies=[G, M],
        statement=f"Swap every two adjacent nodes and return the head. Swap the nodes themselves, not their values. {LIST_NOTE}",
        entry="swapPairs",
        params=[("head", "Optional[ListNode]")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 2, 3, 4]]}, {"args": [[]]}, {"args": [[1, 2, 3]]}],
        constraints=["0 ≤ nodes ≤ 100"],
        hints=["With a dummy `prev`: a = prev.next, b = a.next; relink prev → b → a → (rest), then prev = a."],
        reference="""
class Solution:
    def swapPairs(self, head):
        dummy = prev = ListNode(0, head)
        while prev.next and prev.next.next:
            a, b = prev.next, prev.next.next
            prev.next, b.next, a.next = b, a, b.next
            prev = a
        return dummy.next
""",
        gen=lambda r: [[[1]]] + [[ints(r, r.randint(0, 100), 0, 100)] for _ in range(19)],
    ),
    Problem(
        slug="rotate-list",
        title="Rotate List",
        difficulty="Medium",
        pattern="linked-list",
        topics=["Linked List", "Two Pointers"],
        companies=[G, M],
        statement=f"Rotate the list to the right by `k` places and return the new head. {LIST_NOTE}",
        entry="rotateRight",
        params=[("head", "Optional[ListNode]"), ("k", "int")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 2, 3, 4, 5], 2]}, {"args": [[0, 1, 2], 4]}],
        constraints=["0 ≤ nodes ≤ 500", "0 ≤ k ≤ 2 × 10⁹"],
        hints=["k can be huge — reduce it mod the length. Make the list a ring, then cut it at the right place."],
        reference="""
class Solution:
    def rotateRight(self, head, k):
        vals = []
        cur = head
        while cur: vals.append(cur.val); cur = cur.next
        if not vals: return None
        k %= len(vals)
        vals = vals[-k:] + vals[:-k] if k else vals
        dummy = cur = ListNode()
        for v in vals: cur.next = ListNode(v); cur = cur.next
        return dummy.next
""",
        gen=lambda r: (
            [[[], 3], [[1], 2 * 10**9]]
            + [[ints(r, r.randint(1, 12), 0, 9), r.randint(0, 30)] for _ in range(18)]
            + [[list(range(500)), 2 * 10**9]]
        ),
    ),
    Problem(
        slug="odd-even-linked-list",
        title="Odd Even Linked List",
        difficulty="Medium",
        pattern="linked-list",
        topics=["Linked List"],
        companies=[G, M],
        statement=f"Group all nodes at odd positions (1st, 3rd, …) first, followed by the nodes at even positions, keeping the relative order inside each group. Return the head. {LIST_NOTE}\n\nUse O(1) extra space.",
        entry="oddEvenList",
        params=[("head", "Optional[ListNode]")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 2, 3, 4, 5]]}, {"args": [[2, 1, 3, 5, 6, 4, 7]]}],
        constraints=["0 ≤ nodes ≤ 10⁴"],
        hints=["Keep two chains, odd and even, and append nodes to them alternately. Join odd's tail to even's head."],
        reference="""
class Solution:
    def oddEvenList(self, head):
        vals = []
        while head: vals.append(head.val); head = head.next
        vals = vals[::2] + vals[1::2]
        dummy = cur = ListNode()
        for v in vals: cur.next = ListNode(v); cur = cur.next
        return dummy.next
""",
        gen=lambda r: [[[]], [[1]]] + [[ints(r, r.randint(1, 20), 0, 50)] for _ in range(18)] + [[list(range(10_000))]],
    ),
    Problem(
        slug="sort-list",
        title="Sort List",
        difficulty="Medium",
        pattern="linked-list",
        topics=["Linked List", "Sorting", "Divide and Conquer", "Merge Sort"],
        companies=[M, G],
        statement=f"Sort the linked list in ascending order and return its head. {LIST_NOTE}\n\nAim for O(n log n) time.",
        entry="sortList",
        params=[("head", "Optional[ListNode]")],
        returns="Optional[ListNode]",
        examples=[{"args": [[4, 2, 1, 3]]}, {"args": [[-1, 5, 3, 4, 0]]}, {"args": [[]]}],
        constraints=["0 ≤ nodes ≤ 5 × 10⁴"],
        hints=["Merge sort fits lists well: split at the middle with fast/slow pointers, sort each half, merge."],
        reference="""
class Solution:
    def sortList(self, head):
        vals = []
        while head: vals.append(head.val); head = head.next
        dummy = cur = ListNode()
        for v in sorted(vals): cur.next = ListNode(v); cur = cur.next
        return dummy.next
""",
        gen=lambda r: (
            [[ints(r, r.randint(0, 30), -50, 50)] for _ in range(18)]
            + [[ints(r, 50_000, -(10**5), 10**5)], [list(range(50_000, 0, -1))]]
        ),
    ),
    Problem(
        slug="partition-list",
        title="Partition List",
        difficulty="Medium",
        pattern="linked-list",
        topics=["Linked List", "Two Pointers"],
        companies=[G, M],
        statement=f"Rearrange the list so every node with value less than `x` comes before every node with value ≥ `x`, keeping the original relative order inside both groups. Return the head. {LIST_NOTE}",
        entry="partition",
        params=[("head", "Optional[ListNode]"), ("x", "int")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 4, 3, 2, 5, 2], 3]}, {"args": [[2, 1], 2]}],
        constraints=["0 ≤ nodes ≤ 200", "−100 ≤ Node.val, x ≤ 100"],
        hints=[
            "Build two lists with dummy heads (less, rest) as you walk; join them at the end and terminate the second."
        ],
        reference="""
class Solution:
    def partition(self, head, x):
        vals = []
        while head: vals.append(head.val); head = head.next
        vals = [v for v in vals if v < x] + [v for v in vals if v >= x]
        dummy = cur = ListNode()
        for v in vals: cur.next = ListNode(v); cur = cur.next
        return dummy.next
""",
        gen=lambda r: (
            [[[], 0]]
            + [[ints(r, r.randint(1, 20), -5, 5), r.randint(-6, 6)] for _ in range(19)]
            + [[ints(r, 200, -100, 100), 0]]
        ),
    ),
    Problem(
        slug="find-the-duplicate-number",
        title="Find the Duplicate Number",
        difficulty="Medium",
        pattern="linked-list",
        topics=["Array", "Two Pointers", "Binary Search", "Bit Manipulation"],
        companies=[G, M],
        statement="`nums` has `n + 1` integers, each in `[1, n]`. Exactly one value is repeated (possibly several times). Return it **without modifying** `nums` and using O(1) extra space.",
        entry="findDuplicate",
        params=[("nums", "List[int]")],
        returns="int",
        examples=[{"args": [[1, 3, 4, 2, 2]]}, {"args": [[3, 1, 3, 4, 2]]}, {"args": [[3, 3, 3, 3, 3]]}],
        constraints=["1 ≤ n ≤ 10⁵", "len(nums) == n + 1", "1 ≤ nums[i] ≤ n"],
        hints=[
            "Treat i → nums[i] as a linked list. The duplicate value is where two arrows point into the same node: the start of a cycle.",
            "Floyd's tortoise and hare finds the cycle entrance in O(1) space.",
        ],
        reference="""
class Solution:
    def findDuplicate(self, nums):
        return Counter(nums).most_common(1)[0][0]
""",
        gen=lambda r: [[[1, 1]]] + [_dup_case(r, r.randint(1, 20)) for _ in range(19)] + [_dup_case(r, 100_000)],
    ),
    Problem(
        slug="reverse-nodes-in-k-group",
        title="Reverse Nodes in k-Group",
        difficulty="Hard",
        pattern="linked-list",
        topics=["Linked List", "Recursion"],
        companies=[M, G],
        statement=f"Reverse the nodes of the list `k` at a time and return the head. If the number of nodes left at the end is less than `k`, leave them as they are. Change links, not values. {LIST_NOTE}\n\nUse O(1) extra space.",
        entry="reverseKGroup",
        params=[("head", "Optional[ListNode]"), ("k", "int")],
        returns="Optional[ListNode]",
        examples=[{"args": [[1, 2, 3, 4, 5], 2]}, {"args": [[1, 2, 3, 4, 5], 3]}],
        constraints=["1 ≤ k ≤ nodes ≤ 5000"],
        hints=[
            "First check that k nodes remain. Reverse exactly those k, then reconnect: the group's old head becomes its tail and links to the next group.",
        ],
        reference="""
class Solution:
    def reverseKGroup(self, head, k):
        vals = []
        while head: vals.append(head.val); head = head.next
        full = len(vals) - len(vals) % k
        vals = [v for i in range(0, full, k) for v in vals[i:i + k][::-1]] + vals[full:]
        dummy = cur = ListNode()
        for v in vals: cur.next = ListNode(v); cur = cur.next
        return dummy.next
""",
        gen=lambda r: (
            [(lambda a: [a, r.randint(1, len(a))])(ints(r, r.randint(1, 20), 0, 50)) for _ in range(20)]
            + [[list(range(5000)), 7]]
        ),
    ),
    # ---------------------------------------------------------------- trees
    Problem(
        slug="invert-binary-tree",
        title="Invert Binary Tree",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "DFS", "BFS"],
        companies=[G, M],
        statement=f"Mirror a binary tree (swap every node's left and right children) and return its root. {TREE_NOTE}",
        entry="invertTree",
        params=[("root", "Optional[TreeNode]")],
        returns="Optional[TreeNode]",
        examples=[{"args": [[4, 2, 7, 1, 3, 6, 9]]}, {"args": [[2, 1, 3]]}, {"args": [[]]}],
        constraints=["0 ≤ nodes ≤ 100"],
        hints=["Swap the children of the current node, then invert both subtrees."],
        reference="""
class Solution:
    def invertTree(self, root):
        st = [root]
        while st:
            n = st.pop()
            if n:
                n.left, n.right = n.right, n.left
                st += [n.left, n.right]
        return root
""",
        gen=lambda r: [[random_tree(r, ints(r, r.randint(0, 100), -100, 100))] for _ in range(20)],
    ),
    Problem(
        slug="maximum-depth-of-binary-tree",
        title="Maximum Depth of Binary Tree",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "DFS", "BFS"],
        companies=[G, M],
        statement=f"Return the number of nodes on the longest path from the root down to a leaf. {TREE_NOTE}",
        entry="maxDepth",
        params=[("root", "Optional[TreeNode]")],
        returns="int",
        examples=[{"args": [[3, 9, 20, None, None, 15, 7]]}, {"args": [[1, None, 2]]}],
        constraints=["0 ≤ nodes ≤ 10⁴"],
        hints=["depth(node) = 1 + max(depth(left), depth(right)); an empty tree has depth 0."],
        reference="""
class Solution:
    def maxDepth(self, root):
        d, q = 0, deque([root] if root else [])
        while q:
            d += 1
            for _ in range(len(q)):
                n = q.popleft()
                q.extend(c for c in (n.left, n.right) if c)
        return d
""",
        gen=lambda r: (
            [[[]]]
            + [[random_tree(r, ints(r, r.randint(1, 50), 0, 100))] for _ in range(18)]
            + [[random_tree(r, ints(r, 10_000, 0, 100))]]
        ),
    ),
    Problem(
        slug="same-tree",
        title="Same Tree",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "DFS", "BFS"],
        companies=[G, M],
        statement=f"Return `True` if the binary trees `p` and `q` have the same shape and the same values. {TREE_NOTE}",
        entry="isSameTree",
        params=[("p", "Optional[TreeNode]"), ("q", "Optional[TreeNode]")],
        returns="bool",
        examples=[{"args": [[1, 2, 3], [1, 2, 3]]}, {"args": [[1, 2], [1, None, 2]]}, {"args": [[1, 2, 1], [1, 1, 2]]}],
        constraints=["0 ≤ nodes ≤ 100"],
        hints=["Both empty → same. One empty or values differ → different. Otherwise compare both pairs of subtrees."],
        reference="""
class Solution:
    def isSameTree(self, p, q):
        st = [(p, q)]
        while st:
            a, b = st.pop()
            if a is None and b is None: continue
            if a is None or b is None or a.val != b.val: return False
            st += [(a.left, b.left), (a.right, b.right)]
        return True
""",
        gen=lambda r: [[[], []], [[1], []]] + [_tree_pair(r, r.randint(1, 30)) for _ in range(18)],
    ),
    Problem(
        slug="symmetric-tree",
        title="Symmetric Tree",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "DFS", "BFS"],
        companies=[G, M],
        statement=f"Return `True` if the binary tree is a mirror of itself around its centre. {TREE_NOTE}",
        entry="isSymmetric",
        params=[("root", "Optional[TreeNode]")],
        returns="bool",
        examples=[{"args": [[1, 2, 2, 3, 4, 4, 3]]}, {"args": [[1, 2, 2, None, 3, None, 3]]}],
        constraints=["1 ≤ nodes ≤ 1000"],
        hints=["Compare two subtrees at once: a.left mirrors b.right and a.right mirrors b.left."],
        reference="""
class Solution:
    def isSymmetric(self, root):
        st = [(root.left, root.right)]
        while st:
            a, b = st.pop()
            if a is None and b is None: continue
            if a is None or b is None or a.val != b.val: return False
            st += [(a.left, b.right), (a.right, b.left)]
        return True
""",
        gen=lambda r: [[[1]]] + [[_symmetric(r, r.randint(0, 25))] for _ in range(19)] + [[_symmetric(r, 499)]],
    ),
    Problem(
        slug="balanced-binary-tree",
        title="Balanced Binary Tree",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "DFS"],
        companies=[G, M],
        statement=f"A binary tree is height-balanced if, at every node, the heights of the left and right subtrees differ by at most 1. Return `True` if the tree is height-balanced. {TREE_NOTE}",
        entry="isBalanced",
        params=[("root", "Optional[TreeNode]")],
        returns="bool",
        examples=[
            {"args": [[3, 9, 20, None, None, 15, 7]]},
            {"args": [[1, 2, 2, 3, 3, None, None, 4, 4]]},
            {"args": [[]]},
        ],
        constraints=["0 ≤ nodes ≤ 5000"],
        hints=["Return each subtree's height upward, or −1 as soon as any subtree is unbalanced. That keeps it O(n)."],
        reference="""
class Solution:
    def isBalanced(self, root):
        h = {None: 0}; st = [(root, False)]
        while st:
            n, done = st.pop()
            if n is None: continue
            if done:
                a, b = h[n.left], h[n.right]
                if abs(a - b) > 1: return False
                h[n] = 1 + max(a, b)
            else:
                st += [(n, True), (n.left, False), (n.right, False)]
        return True
""",
        gen=lambda r: (
            [[[1, 2, None, 3]], [[1, 2, 3, 4, None, None, None, 5]]]
            + [[random_tree(r, ints(r, r.randint(0, 12), 0, 9))] for _ in range(14)]
            + [[level_order(_complete(n))] for n in (7, 20, 100, 5000)]
        ),
    ),
    Problem(
        slug="subtree-of-another-tree",
        title="Subtree of Another Tree",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "DFS", "String Matching", "Hash Function"],
        companies=[M, G],
        statement=f"Return `True` if `subRoot` matches some node of `root` together with **all** of that node's descendants. {TREE_NOTE}",
        entry="isSubtree",
        params=[("root", "Optional[TreeNode]"), ("subRoot", "Optional[TreeNode]")],
        returns="bool",
        examples=[
            {"args": [[3, 4, 5, 1, 2], [4, 1, 2]]},
            {"args": [[3, 4, 5, 1, 2, None, None, None, None, 0], [4, 1, 2]]},
        ],
        constraints=["1 ≤ nodes in root ≤ 2000", "1 ≤ nodes in subRoot ≤ 1000"],
        hints=["For each node in root, run Same Tree against subRoot. O(m · n) is fine here."],
        reference="""
class Solution:
    def isSubtree(self, root, subRoot):
        def same(a, b):
            st = [(a, b)]
            while st:
                x, y = st.pop()
                if x is None and y is None: continue
                if x is None or y is None or x.val != y.val: return False
                st += [(x.left, y.left), (x.right, y.right)]
            return True
        st = [root]
        while st:
            n = st.pop()
            if n:
                if same(n, subRoot): return True
                st += [n.left, n.right]
        return False
""",
        gen=lambda r: [_subtree_case(r, r.randint(1, 25)) for _ in range(20)] + [_subtree_case(r, 2000)],
    ),
    Problem(
        slug="path-sum",
        title="Path Sum",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "DFS", "BFS"],
        companies=[G, M],
        statement=f"Return `True` if the tree has a root-to-leaf path whose values add up to `targetSum`. A leaf has no children. {TREE_NOTE}",
        entry="hasPathSum",
        params=[("root", "Optional[TreeNode]"), ("targetSum", "int")],
        returns="bool",
        examples=[
            {"args": [[5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 22]},
            {"args": [[1, 2, 3], 5]},
            {"args": [[], 0]},
        ],
        constraints=["0 ≤ nodes ≤ 5000"],
        hints=["Subtract each node's value from the target on the way down; check for 0 only at leaves."],
        reference="""
class Solution:
    def hasPathSum(self, root, targetSum):
        st = [(root, targetSum)] if root else []
        while st:
            n, t = st.pop()
            t -= n.val
            if not n.left and not n.right and t == 0: return True
            st += [(c, t) for c in (n.left, n.right) if c]
        return False
""",
        gen=lambda r: (
            [[[1, 2], 1], [[1, 2], 3]]
            + [_path_target(r, r.randint(1, 20)) for _ in range(18)]
            + [_path_target(r, 5000)]
        ),
    ),
    Problem(
        slug="minimum-depth-of-binary-tree",
        title="Minimum Depth of Binary Tree",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "DFS", "BFS"],
        companies=[G, M],
        statement=f"Return the number of nodes on the shortest path from the root down to a **leaf** (a node with no children). {TREE_NOTE}",
        entry="minDepth",
        params=[("root", "Optional[TreeNode]")],
        returns="int",
        examples=[{"args": [[3, 9, 20, None, None, 15, 7]]}, {"args": [[2, None, 3, None, 4, None, 5, None, 6]]}],
        constraints=["0 ≤ nodes ≤ 10⁵"],
        hints=["BFS stops at the first leaf it meets. With DFS, a node with only one child is not a leaf."],
        reference="""
class Solution:
    def minDepth(self, root):
        q = deque([(root, 1)] if root else [])
        while q:
            n, d = q.popleft()
            if not n.left and not n.right: return d
            q.extend((c, d + 1) for c in (n.left, n.right) if c)
        return 0
""",
        gen=lambda r: (
            [[[]], [[1]]]
            + [[random_tree(r, ints(r, r.randint(1, 40), 0, 9))] for _ in range(18)]
            + [[random_tree(r, ints(r, 50_000, 0, 9))]]
        ),
    ),
    Problem(
        slug="range-sum-of-bst",
        title="Range Sum of BST",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "DFS", "Binary Search Tree"],
        companies=[M, G],
        statement=f"Return the sum of all values in the BST that lie in the inclusive range `[low, high]`. {TREE_NOTE}",
        entry="rangeSumBST",
        params=[("root", "Optional[TreeNode]"), ("low", "int"), ("high", "int")],
        returns="int",
        examples=[
            {"args": [[10, 5, 15, 3, 7, None, 18], 7, 15]},
            {"args": [[10, 5, 15, 3, 7, 13, 18, 1, None, 6], 6, 10]},
        ],
        constraints=["1 ≤ nodes ≤ 2 × 10⁴", "All values are unique"],
        hints=["Use the BST order to skip subtrees: if node.val < low, the whole left subtree is too small."],
        reference="""
class Solution:
    def rangeSumBST(self, root, low, high):
        total, st = 0, [root]
        while st:
            n = st.pop()
            if n:
                if low <= n.val <= high: total += n.val
                st += [n.left, n.right]
        return total
""",
        gen=lambda r: (
            [[random_bst(r, r.randint(1, 30), 0, 100), *sorted(ints(r, 2, 0, 100))] for _ in range(20)]
            + [[random_bst(r, 20_000, 0, 10**5), 20_000, 70_000]]
        ),
    ),
    Problem(
        slug="closest-binary-search-tree-value",
        title="Closest Binary Search Tree Value",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "Binary Search Tree", "Binary Search"],
        companies=[M, G],
        statement=f"Given a BST and a real number `target`, return the value in the tree closest to `target`. If two values are equally close, return the smaller. {TREE_NOTE}",
        entry="closestValue",
        params=[("root", "Optional[TreeNode]"), ("target", "float")],
        returns="int",
        examples=[{"args": [[4, 2, 5, 1, 3], 3.714286]}, {"args": [[1], 4.428571]}, {"args": [[4, 2, 5, 1, 3], 3.5]}],
        constraints=["1 ≤ nodes ≤ 10⁴", "All values are unique"],
        hints=["Walk down like a search: go left if target < node.val, else right, tracking the best value seen."],
        reference="""
class Solution:
    def closestValue(self, root, target):
        best, st = root.val, [root]
        while st:
            n = st.pop()
            if n:
                if (abs(n.val - target), n.val) < (abs(best - target), best): best = n.val
                st += [n.left, n.right]
        return best
""",
        gen=lambda r: (
            [
                [
                    random_bst(r, r.randint(1, 30), 0, 60),
                    r.choice([r.randint(-5, 65) + 0.5, round(r.uniform(-5, 65), 3)]),
                ]
                for _ in range(20)
            ]
            + [[random_bst(r, 10_000, 0, 10**6), 500_000.5]]
        ),
    ),
    Problem(
        slug="count-complete-tree-nodes",
        title="Count Complete Tree Nodes",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "Binary Search", "DFS"],
        companies=[G],
        statement=f"The tree is complete: every level is full except possibly the last, which is filled from the left. Return the number of nodes in less than O(n) time. {TREE_NOTE}",
        entry="countNodes",
        params=[("root", "Optional[TreeNode]")],
        returns="int",
        examples=[{"args": [[1, 2, 3, 4, 5, 6]]}, {"args": [[]]}, {"args": [[1]]}],
        constraints=["0 ≤ nodes ≤ 5 × 10⁴"],
        hints=[
            "If the leftmost and rightmost depths are equal, the subtree is perfect: 2^h − 1 nodes.",
            "Otherwise recurse into both children. Only one side is ever imperfect, so it's O(log² n).",
        ],
        reference="""
class Solution:
    def countNodes(self, root):
        c, st = 0, [root]
        while st:
            n = st.pop()
            if n: c += 1; st += [n.left, n.right]
        return c
""",
        gen=lambda r: [
            [list(range(1, n + 1))]
            for n in [0, 2, 3, 7, 8, 15, 16, 31] + [r.randint(1, 200) for _ in range(12)] + [50_000]
        ],
    ),
    Problem(
        slug="binary-tree-paths",
        title="Binary Tree Paths",
        difficulty="Easy",
        pattern="trees",
        topics=["Tree", "DFS", "Backtracking", "String"],
        companies=[G, M],
        statement=f'Return every root-to-leaf path as a string like `"1->2->5"`, in any order. {TREE_NOTE}',
        entry="binaryTreePaths",
        params=[("root", "Optional[TreeNode]")],
        returns="List[str]",
        examples=[{"args": [[1, 2, 3, None, 5]]}, {"args": [[1]]}],
        constraints=["1 ≤ nodes ≤ 100"],
        hints=["DFS carrying the path so far; at a leaf, join it with '->'."],
        reference="""
class Solution:
    def binaryTreePaths(self, root):
        out, st = [], [(root, str(root.val))]
        while st:
            n, p = st.pop()
            if not n.left and not n.right: out.append(p)
            st += [(c, f'{p}->{c.val}') for c in (n.left, n.right) if c]
        return out
""",
        gen=lambda r: [[random_tree(r, ints(r, r.randint(1, 100), -100, 100))] for _ in range(20)],
        compare="sorted",
    ),
    Problem(
        slug="lowest-common-ancestor-of-a-binary-search-tree",
        title="Lowest Common Ancestor of a Binary Search Tree",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "DFS", "Binary Search Tree"],
        companies=[M, G],
        statement=f"Given a BST and two of its nodes `p` and `q`, return their lowest common ancestor: the deepest node with both as descendants (a node is a descendant of itself). {TREE_NOTE}\n\nIn tests, `p` and `q` are given by value and the output shows the subtree rooted at the node you return.",
        entry="lowestCommonAncestor",
        params=[("root", "TreeNode"), ("p", "TreeNode@0"), ("q", "TreeNode@0")],
        returns="TreeNode",
        examples=[
            {"args": [[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 8]},
            {"args": [[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 4]},
        ],
        constraints=["2 ≤ nodes ≤ 10⁵", "All values are unique", "p ≠ q, both exist"],
        hints=[
            "If both values are smaller than the node, go left; both larger, go right. Otherwise this node splits them — it's the answer."
        ],
        reference="""
class Solution:
    def lowestCommonAncestor(self, root, p, q):
        lo, hi = sorted([p.val, q.val])
        while not lo <= root.val <= hi:
            root = root.left if hi < root.val else root.right
        return root
""",
        gen=lambda r: [_bst_pair(r, r.randint(2, 40)) for _ in range(20)] + [_bst_pair(r, 10_000)],
    ),
    Problem(
        slug="count-good-nodes-in-binary-tree",
        title="Count Good Nodes in Binary Tree",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "DFS", "BFS"],
        companies=[M, G],
        statement=f"A node is good if no node on the path from the root to it has a greater value. Return the number of good nodes. {TREE_NOTE}",
        entry="goodNodes",
        params=[("root", "TreeNode")],
        returns="int",
        examples=[{"args": [[3, 1, 4, 3, None, 1, 5]]}, {"args": [[3, 3, None, 4, 2]]}, {"args": [[1]]}],
        constraints=["1 ≤ nodes ≤ 10⁵", "−10⁴ ≤ Node.val ≤ 10⁴"],
        hints=["DFS passing down the maximum value seen on the path so far."],
        reference="""
class Solution:
    def goodNodes(self, root):
        c, st = 0, [(root, -inf)]
        while st:
            n, m = st.pop()
            if n.val >= m: c += 1
            st += [(x, max(m, n.val)) for x in (n.left, n.right) if x]
        return c
""",
        gen=lambda r: (
            [[random_tree(r, ints(r, r.randint(1, 40), 0, 10))] for _ in range(20)]
            + [[random_tree(r, ints(r, 100_000, -(10**4), 10**4))]]
        ),
    ),
    Problem(
        slug="kth-smallest-element-in-a-bst",
        title="Kth Smallest Element in a BST",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "DFS", "Binary Search Tree"],
        companies=[G, M],
        statement=f"Return the `k`-th smallest value (1-indexed) in a BST. {TREE_NOTE}",
        entry="kthSmallest",
        params=[("root", "Optional[TreeNode]"), ("k", "int")],
        returns="int",
        examples=[{"args": [[3, 1, 4, None, 2], 1]}, {"args": [[5, 3, 6, 2, 4, None, None, 1], 3]}],
        constraints=["1 ≤ k ≤ nodes ≤ 10⁴"],
        hints=["An in-order traversal visits BST values in sorted order. Stop at the k-th one."],
        reference="""
class Solution:
    def kthSmallest(self, root, k):
        vals, st = [], [root]
        while st:
            n = st.pop()
            if n: vals.append(n.val); st += [n.left, n.right]
        return sorted(vals)[k - 1]
""",
        gen=lambda r: (
            [(lambda n: [random_bst(r, n, -100, 100), r.randint(1, n)])(r.randint(1, 40)) for _ in range(20)]
            + [[random_bst(r, 10_000, 0, 10**5), 5000]]
        ),
    ),
    Problem(
        slug="construct-binary-tree-from-preorder-and-inorder-traversal",
        title="Construct Binary Tree from Preorder and Inorder Traversal",
        difficulty="Medium",
        pattern="trees",
        topics=["Array", "Hash Table", "Divide and Conquer", "Tree"],
        companies=[G, M],
        statement=f"Given the preorder and inorder traversals of a binary tree with unique values, rebuild the tree and return its root. {TREE_NOTE}",
        entry="buildTree",
        params=[("preorder", "List[int]"), ("inorder", "List[int]")],
        returns="Optional[TreeNode]",
        examples=[{"args": [[3, 9, 20, 15, 7], [9, 3, 15, 20, 7]]}, {"args": [[-1], [-1]]}],
        constraints=["1 ≤ nodes ≤ 3000", "Values are unique"],
        hints=[
            "preorder[0] is the root. Its position in inorder splits the left and right subtrees.",
            "A dict value → inorder index avoids O(n) searches.",
        ],
        reference="""
class Solution:
    def buildTree(self, preorder, inorder):
        pos = {v: i for i, v in enumerate(inorder)}
        it = iter(preorder)
        def build(lo, hi):
            if lo > hi: return None
            v = next(it); node = TreeNode(v)
            node.left = build(lo, pos[v] - 1)
            node.right = build(pos[v] + 1, hi)
            return node
        return build(0, len(inorder) - 1)
""",
        gen=lambda r: [_traversals(r, r.randint(1, 30)) for _ in range(20)] + [_traversals(r, 3000)],
    ),
    Problem(
        slug="binary-tree-zigzag-level-order-traversal",
        title="Binary Tree Zigzag Level Order Traversal",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "BFS"],
        companies=[M, G],
        statement=f"Return the node values level by level, alternating direction: left to right on the first level, right to left on the next, and so on. {TREE_NOTE}",
        entry="zigzagLevelOrder",
        params=[("root", "Optional[TreeNode]")],
        returns="List[List[int]]",
        examples=[{"args": [[3, 9, 20, None, None, 15, 7]]}, {"args": [[1]]}, {"args": [[]]}],
        constraints=["0 ≤ nodes ≤ 2000"],
        hints=["Normal BFS; reverse every other level before appending it."],
        reference="""
class Solution:
    def zigzagLevelOrder(self, root):
        res, q = [], deque([root] if root else [])
        while q:
            level = []
            for _ in range(len(q)):
                n = q.popleft(); level.append(n.val)
                q.extend(c for c in (n.left, n.right) if c)
            res.append(level[::-1] if len(res) % 2 else level)
        return res
""",
        gen=lambda r: (
            [[random_tree(r, ints(r, r.randint(0, 40), -100, 100))] for _ in range(18)]
            + [[random_tree(r, ints(r, 2000, -100, 100))]]
        ),
    ),
    Problem(
        slug="binary-tree-vertical-order-traversal",
        title="Binary Tree Vertical Order Traversal",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "BFS", "Hash Table"],
        companies=[M],
        statement=f"Return the node values column by column, from the leftmost column to the rightmost. The root is in column 0, a left child is one column left of its parent and a right child one column right.\n\nWithin a column, list values top to bottom; nodes in the same row and column go left to right. {TREE_NOTE}",
        entry="verticalOrder",
        params=[("root", "Optional[TreeNode]")],
        returns="List[List[int]]",
        examples=[
            {"args": [[3, 9, 20, None, None, 15, 7]]},
            {"args": [[3, 9, 8, 4, 0, 1, 7]]},
            {"args": [[1, 2, 3, 4, 10, 9, 11, None, 5, None, None, None, None, None, None, None, 6]]},
        ],
        constraints=["0 ≤ nodes ≤ 100"],
        hints=["BFS (not DFS) visits nodes top to bottom and left to right. Bucket values by column as you go."],
        reference="""
class Solution:
    def verticalOrder(self, root):
        cols = defaultdict(list); q = deque([(root, 0)] if root else [])
        while q:
            n, c = q.popleft(); cols[c].append(n.val)
            if n.left: q.append((n.left, c - 1))
            if n.right: q.append((n.right, c + 1))
        return [cols[c] for c in sorted(cols)]
""",
        gen=lambda r: [[random_tree(r, ints(r, r.randint(0, 100), 0, 50))] for _ in range(20)],
    ),
    Problem(
        slug="all-nodes-distance-k-in-binary-tree",
        title="All Nodes Distance K in Binary Tree",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "DFS", "BFS"],
        companies=[M, G],
        statement=f"Return the values of every node exactly `k` edges away from `target`, in any order. Values are unique; in tests `target` is given by value. {TREE_NOTE}",
        entry="distanceK",
        params=[("root", "TreeNode"), ("target", "TreeNode@0"), ("k", "int")],
        returns="List[int]",
        examples=[{"args": [[3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 2]}, {"args": [[1], 1, 3]}],
        constraints=["1 ≤ nodes ≤ 500", "0 ≤ k ≤ 1000"],
        hints=["Record each node's parent, then BFS from target treating the tree as an undirected graph."],
        reference="""
class Solution:
    def distanceK(self, root, target, k):
        adj = defaultdict(list); st = [root]
        while st:
            n = st.pop()
            for c in (n.left, n.right):
                if c: adj[n].append(c); adj[c].append(n); st.append(c)
        seen = {target}; frontier = [target]
        for _ in range(k):
            frontier = [m for n in frontier for m in adj[n] if m not in seen]
            seen.update(frontier)
        return [n.val for n in frontier]
""",
        gen=lambda r: (
            [
                (lambda v: [random_tree(r, v), r.choice(v), r.randint(0, 6)])(distinct(r, r.randint(1, 40), 0, 500))
                for _ in range(20)
            ]
            + [(lambda v: [random_tree(r, v), v[0], 10])(distinct(r, 500, 0, 500))]
        ),
        compare="sorted",
    ),
    Problem(
        slug="sum-root-to-leaf-numbers",
        title="Sum Root to Leaf Numbers",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "DFS"],
        companies=[M, G],
        statement=f"Every node holds a digit 0–9. Each root-to-leaf path spells a number (`1 → 2 → 3` is 123). Return the sum of all those numbers. {TREE_NOTE}",
        entry="sumNumbers",
        params=[("root", "Optional[TreeNode]")],
        returns="int",
        examples=[{"args": [[1, 2, 3]], "note": "12 + 13 = 25."}, {"args": [[4, 9, 0, 5, 1]]}],
        constraints=["1 ≤ nodes ≤ 1000", "0 ≤ Node.val ≤ 9"],
        hints=["Pass `number * 10 + node.val` down; add it to the total at each leaf."],
        reference="""
class Solution:
    def sumNumbers(self, root):
        total, st = 0, [(root, 0)]
        while st:
            n, x = st.pop()
            x = x * 10 + n.val
            if not n.left and not n.right: total += x
            st += [(c, x) for c in (n.left, n.right) if c]
        return total
""",
        gen=lambda r: (
            [[random_tree(r, ints(r, r.randint(1, 30), 0, 9))] for _ in range(20)]
            + [[random_tree(r, ints(r, 1000, 0, 9))]]
        ),
    ),
    Problem(
        slug="path-sum-ii",
        title="Path Sum II",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "DFS", "Backtracking"],
        companies=[G, M],
        statement=f"Return every root-to-leaf path whose values sum to `targetSum`, each as a list of values from root to leaf. Paths may be listed in any order. {TREE_NOTE}",
        entry="pathSum",
        params=[("root", "Optional[TreeNode]"), ("targetSum", "int")],
        returns="List[List[int]]",
        examples=[
            {"args": [[5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 22]},
            {"args": [[1, 2, 3], 5]},
            {"args": [[1, 2], 0]},
        ],
        constraints=["0 ≤ nodes ≤ 5000"],
        hints=["DFS with a path list: append on the way down, pop on the way back up (backtracking)."],
        reference="""
class Solution:
    def pathSum(self, root, targetSum):
        out, st = [], [(root, [root.val])] if root else []
        while st:
            n, p = st.pop()
            if not n.left and not n.right and sum(p) == targetSum: out.append(p)
            st += [(c, p + [c.val]) for c in (n.left, n.right) if c]
        return out
""",
        gen=lambda r: [[[], 0]] + [_path_target(r, r.randint(1, 25)) for _ in range(19)] + [_path_target(r, 1000)],
        compare="sorted",
    ),
    Problem(
        slug="path-sum-iii",
        title="Path Sum III",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "DFS", "Prefix Sum"],
        companies=[M, G],
        statement=f"Count the paths whose values sum to `targetSum`. A path must go downward (parent to child) but can start and end at any node. {TREE_NOTE}",
        entry="pathSum",
        params=[("root", "Optional[TreeNode]"), ("targetSum", "int")],
        returns="int",
        examples=[
            {"args": [[10, 5, -3, 3, 2, None, 11, 3, -2, None, 1], 8]},
            {"args": [[5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 22]},
        ],
        constraints=["0 ≤ nodes ≤ 1000", "−10⁹ ≤ Node.val ≤ 10⁹"],
        hints=[
            "Prefix sums on the root-to-node path: count earlier prefixes equal to current − target, like Subarray Sum Equals K. Undo the count when backtracking."
        ],
        reference="""
class Solution:
    def pathSum(self, root, targetSum):
        total, st = 0, [(root, [])] if root else []
        while st:
            n, sums = st.pop()
            sums = [s + n.val for s in sums] + [n.val]
            total += sums.count(targetSum)
            st += [(c, sums) for c in (n.left, n.right) if c]
        return total
""",
        gen=lambda r: (
            [[[], 0]]
            + [[random_tree(r, ints(r, r.randint(1, 40), -5, 5)), r.randint(-6, 6)] for _ in range(19)]
            + [[random_tree(r, ints(r, 1000, -3, 3)), 2]]
        ),
    ),
    Problem(
        slug="maximum-width-of-binary-tree",
        title="Maximum Width of Binary Tree",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "BFS", "DFS"],
        companies=[G, M],
        statement=f"The width of a level is the distance between its leftmost and rightmost non-null nodes, counting the missing nodes in between as if the tree were complete. Return the maximum width over all levels. {TREE_NOTE}",
        entry="widthOfBinaryTree",
        params=[("root", "Optional[TreeNode]")],
        returns="int",
        examples=[
            {"args": [[1, 3, 2, 5, 3, None, 9]]},
            {"args": [[1, 3, 2, 5, None, None, 9, 6, None, 7]]},
            {"args": [[1, 3, 2, 5]]},
        ],
        constraints=["1 ≤ nodes ≤ 3000"],
        hints=[
            "Number nodes like a heap: children of i are 2i and 2i + 1. Width = last − first + 1 on each BFS level."
        ],
        reference="""
class Solution:
    def widthOfBinaryTree(self, root):
        best, q = 0, [(root, 0)]
        while q:
            best = max(best, q[-1][1] - q[0][1] + 1)
            base = q[0][1]
            q = [(c, 2 * (i - base) + d) for n, i in q for d, c in ((0, n.left), (1, n.right)) if c]
        return best
""",
        gen=lambda r: (
            [[random_tree(r, ints(r, r.randint(1, 40), 0, 9))] for _ in range(20)]
            + [[random_tree(r, ints(r, 3000, 0, 9))]]
        ),
    ),
    Problem(
        slug="flatten-binary-tree-to-linked-list",
        title="Flatten Binary Tree to Linked List",
        difficulty="Medium",
        pattern="trees",
        topics=["Tree", "DFS", "Linked List", "Stack"],
        companies=[M, G],
        statement=f'Flatten the tree in place into a "linked list" that uses `right` pointers as `next` and sets every `left` to `None`. The nodes must appear in preorder. Return `root`. {TREE_NOTE}',
        entry="flatten",
        params=[("root", "Optional[TreeNode]")],
        returns="Optional[TreeNode]",
        examples=[{"args": [[1, 2, 5, 3, 4, None, 6]]}, {"args": [[]]}, {"args": [[0]]}],
        constraints=["0 ≤ nodes ≤ 2000"],
        hints=[
            "For each node with a left child: find the rightmost node of the left subtree, hang the right subtree there, move left to right."
        ],
        reference="""
class Solution:
    def flatten(self, root):
        order, st = [], [root]
        while st:
            n = st.pop()
            if n: order.append(n); st += [n.right, n.left]
        for a, b in zip(order, order[1:] + [None]):
            a.left, a.right = None, b
        return root
""",
        gen=lambda r: (
            [[random_tree(r, ints(r, r.randint(0, 30), -100, 100))] for _ in range(18)]
            + [[random_tree(r, ints(r, 2000, -100, 100))]]
        ),
    ),
    Problem(
        slug="binary-tree-maximum-path-sum",
        title="Binary Tree Maximum Path Sum",
        difficulty="Hard",
        pattern="trees",
        topics=["Tree", "DFS", "Dynamic Programming"],
        companies=[M, G],
        statement=f"A path is a sequence of nodes connected by edges, each node used at most once; it doesn't have to pass through the root. Return the maximum sum of values over all non-empty paths. {TREE_NOTE}",
        entry="maxPathSum",
        params=[("root", "Optional[TreeNode]")],
        returns="int",
        examples=[{"args": [[1, 2, 3]]}, {"args": [[-10, 9, 20, None, None, 15, 7]], "note": "15 → 20 → 7 = 42."}],
        constraints=["1 ≤ nodes ≤ 3 × 10⁴", "−1000 ≤ Node.val ≤ 1000"],
        hints=[
            "Each node returns the best downward path starting at it: val + max(0, left, right).",
            "The best path that bends at a node is val + max(0, left) + max(0, right); keep a global max of that.",
        ],
        reference="""
class Solution:
    def maxPathSum(self, root):
        best = -inf; down = {None: 0}; st = [(root, False)]
        while st:
            n, done = st.pop()
            if n is None: continue
            if done:
                l, r = max(0, down[n.left]), max(0, down[n.right])
                best = max(best, n.val + l + r); down[n] = n.val + max(l, r)
            else:
                st += [(n, True), (n.left, False), (n.right, False)]
        return best
""",
        gen=lambda r: (
            [[[-3]], [[-2, -1]]]
            + [[random_tree(r, ints(r, r.randint(1, 40), -10, 10))] for _ in range(18)]
            + [[random_tree(r, ints(r, 30_000, -1000, 1000))]]
        ),
    ),
]


# ---------------------------------------------------------------- private generator helpers
def _maybe_palindrome(r: random.Random, n: int) -> list[int]:
    half = ints(r, n // 2, 0, 9)
    vals = half + ints(r, n % 2, 0, 9) + half[::-1]
    if r.random() < 0.5:
        vals[r.randrange(n)] = r.randint(0, 9)
    return vals


def _digits(r: random.Random, n: int) -> list[int]:
    return [*ints(r, n - 1, 0, 9), r.randint(1, 9)] if n > 1 else [r.randint(0, 9)]


def _dup_case(r: random.Random, n: int) -> list[Any]:
    d = r.randint(1, n)
    nums = [*list(range(1, n + 1)), d]
    for i in range(n + 1):  # replace some other values with more copies of d
        if nums[i] != d and r.random() < 0.2:
            nums[i] = d
    r.shuffle(nums)
    return [nums]


def _parse(arr: list[Any]) -> dict[str, Any] | None:
    """Level-order list -> nested dict nodes {"v", "l", "r"} (the shape `level_order` reads)."""
    if not arr:
        return None
    root: dict[str, Any] = {"v": arr[0], "l": None, "r": None}
    q, i = deque([root]), 1
    while q and i < len(arr):
        node = q.popleft()
        for side in "lr":
            if i < len(arr) and arr[i] is not None:
                node[side] = {"v": arr[i], "l": None, "r": None}
                q.append(node[side])
            i += 1
    return root


def _nodes(root: dict[str, Any] | None) -> list[dict[str, Any]]:
    out, st = [], [root]
    while st:
        n = st.pop()
        if n:
            out.append(n)
            st += [n["r"], n["l"]]
    return out  # preorder


def _complete(n: int) -> dict[str, Any] | None:
    nodes: list[dict[str, Any]] = [{"v": i, "l": None, "r": None} for i in range(n)]
    for i in range(1, n):
        nodes[(i - 1) // 2]["lr"[(i - 1) % 2]] = nodes[i]
    return nodes[0] if nodes else None


def _tree_pair(r: random.Random, n: int) -> list[Any]:
    t = random_tree(r, ints(r, n, 0, 5))
    u = t[:]
    if r.random() < 0.5:
        idx = [i for i, v in enumerate(u) if v is not None]
        u[r.choice(idx)] = r.randint(0, 5)
    return [t, level_order(_parse(u))]


def _symmetric(r: random.Random, n: int) -> list[Any]:
    def mirror(node: dict[str, Any] | None) -> dict[str, Any] | None:
        return node and {"v": node["v"], "l": mirror(node["r"]), "r": mirror(node["l"])}

    half = _parse(random_tree(r, ints(r, n, 0, 3)))
    other = mirror(half)
    if other and r.random() < 0.4:
        r.choice(_nodes(other))["v"] += 1
    return level_order({"v": 1, "l": half, "r": other})


def _subtree_case(r: random.Random, n: int) -> list[Any]:
    root = _parse(random_tree(r, ints(r, n, 0, 3)))
    sub = r.choice(_nodes(root))
    sub_arr = level_order(sub)
    if r.random() < 0.4:
        sub_arr = [*sub_arr, r.randint(0, 3)] if r.random() < 0.5 else sub_arr[:-1] or [9]
    return [level_order(root), level_order(_parse(sub_arr))]


def _path_target(r: random.Random, n: int) -> list[Any]:
    arr = random_tree(r, ints(r, n, -5, 10))
    root = _parse(arr)
    if r.random() < 0.7:  # walk a random root-to-leaf path
        node, total = root, 0
        while node:
            total += node["v"]
            kids = [c for c in (node["l"], node["r"]) if c]
            node = r.choice(kids) if kids else None
        return [arr, total]
    return [arr, r.randint(-10, 30)]


def _bst_pair(r: random.Random, n: int) -> list[Any]:
    arr = random_bst(r, n, -(10**5), 10**5)
    return [arr, *r.sample([v for v in arr if v is not None], 2)]


def _traversals(r: random.Random, n: int) -> list[Any]:
    root = _parse(random_tree(r, distinct(r, n, -3000, 3000)))
    pre = [x["v"] for x in _nodes(root)]
    ino: list[int] = []
    st: list[dict[str, Any]] = []
    cur = root
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur["l"]
        cur = st.pop()
        ino.append(cur["v"])
        cur = cur["r"]
    return [pre, ino]
