## The idea in plain words

A stack is a **pile of plates**: you only add to the top and take from the top (last in, first out). It's the right tool whenever the most recent unfinished thing is the one you'll deal with next. An opening bracket waits on the pile until its closing bracket arrives.

A **monotonic stack** is a pile that stays sorted. Picture people in a queue for a concert, each waiting to see someone taller than themselves. When a tall person arrives, everyone shorter at the back of the queue has their answer, so they leave.

## You'll know it's this pattern when…

- There's **nested** structure: brackets, expressions, folders inside folders.
- The question says "for each element, find the **next greater / smaller** element" (or how far away it is).
- You need to **undo** the most recent thing.

## Picture it

Daily temperatures: how many days until a warmer day? `[73, 74, 75, 71, 69, 72, 76]`

```text
day temp   stack (days still waiting)   who gets an answer
0   73     [0]
1   74     [1]                          day 0 → 1 day
2   75     [2]                          day 1 → 1 day
3   71     [2, 3]
4   69     [2, 3, 4]
5   72     [2, 5]                       day 4 → 1, day 3 → 2
6   76     [6]                          day 5 → 1, day 2 → 4
```

The stack always reads from warmest to coolest, top to bottom. A warmer day pops everything cooler.

## Walk through an example

Valid parentheses: `"([]{})"`

1. `(` opens, so push it. Stack: `(`
2. `[` opens, so push it. Stack: `( [`
3. `]` closes. The top is `[`, a match, so pop. Stack: `(`
4. `{` opens, so push it. Stack: `( {`
5. `}` matches `{`, so pop. Stack: `(`
6. `)` matches `(`, so pop. The stack is empty, so the string is valid.

## The code

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

## How fast is it?

O(n). The inner `while` looks scary, but every element is pushed once and popped at most once, so the total work is at most 2n.

## Common mistakes

- Store **indices**, not values, when you need distances.
- Python's `//` rounds toward −∞. Use `int(a / b)` to round toward zero, as most calculator problems expect.
- Minimum Remove to Make Valid Parentheses needs two passes: drop unmatched `)` going forward, then drop the leftover `(` indices.
