## Recognise it

Nested structure (brackets, expressions), or "for each element, find the **next greater / smaller** element".

## Core idea

A stack holds items still waiting for their match. A **monotonic stack** keeps them in sorted order. When a new element breaks the order, it's the answer for everything it pops.

## Templates

```python
def next_warmer(temps):                      # monotonic decreasing stack of indices
    ans, stack = [0] * len(temps), []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans

def calc(s):                                 # + - * / without parentheses
    stack, num, op = [], 0, "+"
    for ch in s + "+":
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch in "+-*/":
            if op == "+": stack.append(num)
            elif op == "-": stack.append(-num)
            elif op == "*": stack.append(stack.pop() * num)
            else: stack.append(int(stack.pop() / num))   # truncates toward zero
            num, op = 0, ch
    return sum(stack)
```

## Complexity

O(n): every element is pushed and popped at most once.

## Pitfalls

- Store **indices**, not values, when you need distances.
- Python's `//` floors toward −∞. Use `int(a / b)` or sign logic to truncate toward zero.
- Minimum Remove to Make Valid Parentheses needs two passes: drop unmatched `)` going forward, then leftover `(` indices.
