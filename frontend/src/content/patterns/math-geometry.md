## The idea in plain words

Some questions aren't about a clever data structure at all. They ask you to **move around a grid carefully** or to **do arithmetic the way you learned it at school**.

Think of rotating a photo on your phone. You don't redraw it pixel by pixel from scratch. You notice a rule: the top row becomes the right column. Matrix problems are about finding that rule and then walking the indices without falling off the edge.

Arithmetic problems (multiply two huge numbers, compute xⁿ) work the same way: write down how you'd do it on paper, then turn each step into a loop.

## You'll know it's this pattern when…

- The input is a **matrix** and you must rotate, spiral through, or update it **in place**.
- A cell's new value depends on its **neighbours** (Game of Life, Set Matrix Zeroes).
- You're asked to compute something **without** the obvious built-in: no `**`, no `int()` on the whole string.
- Numbers are too big for normal integers in other languages, so they come as strings.

## Picture it

Rotating a matrix 90° clockwise is two easy moves:

```text
 original        transpose        reverse each row
 1 2 3           1 4 7            7 4 1
 4 5 6    ──►    2 5 8    ──►     8 5 2
 7 8 9           3 6 9            9 6 3
```

Spiral order is four walls that close in:

```text
 top    → 1  2  3  4
            ┌──────┐
 left   ↑ 5 │6  7  │8 ↓ right
            └──────┘
 bottom ← 9 10 11 12

 1 2 3 4 → 8 12 → 11 10 9 → 5 → 6 7
```

## Walk through an example

Compute `2¹³` with fast exponentiation. 13 in binary is `1101`, so 2¹³ = 2⁸ · 2⁴ · 2¹.

```text
n (binary)   lowest bit   result          x (squared each step)
1101         1            1 · 2   = 2     2  → 4
110          0            2               4  → 16
11           1            2 · 16  = 32    16 → 256
1            1            32 · 256 = 8192 256 → …
                                    done: 8192
```

Four steps instead of thirteen multiplications. For n = 2³¹ it's 31 steps instead of two billion.

## The code

```python
def rotate(matrix):                 # n × n, in place
    n = len(matrix)
    for i in range(n):              # transpose
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:              # mirror left ↔ right
        row.reverse()


def my_pow(x, n):
    if n < 0:
        x, n = 1 / x, -n
    result = 1.0
    while n:
        if n & 1:                   # this power of two is part of n
            result *= x
        x *= x
        n >>= 1
    return result
```

## How fast is it?

Matrix walks are O(rows × cols): every cell is touched a constant number of times. Fast exponentiation is O(log n). Grade-school multiplication of two strings is O(m × n).

## Common mistakes

- **Updating cells you still need to read.** In Game of Life or Set Matrix Zeroes, decide everything first (or encode the new state in spare bits), then write.
- **Spiral on non-square matrices.** After walking the top row and right column, check the walls haven't crossed before walking back, or you'll repeat a row.
- **Negative exponents.** `x⁻ⁿ = 1 / xⁿ`. Flip once at the start.
- **Multiplying strings:** digit `i` times digit `j` lands at position `i + j + 1` of the result. Add everything, carry once at the end, then strip leading zeros (but keep a lone `"0"`).
