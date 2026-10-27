## The idea in plain words

Every integer is a row of light switches: on (1) or off (0). Bit tricks flip and test those switches directly instead of doing arithmetic.

The single most useful fact: **XOR cancels pairs**. `x ^ x = 0` and `x ^ 0 = x`, and the order doesn't matter. So if you XOR a pile of numbers where everything appears twice except one, the pairs vanish and the loner is left. It's like pairing up socks: whatever has no partner is the answer.

## You'll know it's this pattern when…

- Everything appears **twice except one** value, or **one number is missing** from a range.
- The question is literally about **bits**: count them, reverse them, add without `+`.
- You're asked for **O(1) extra space** where a set would be the obvious answer.
- The input is a small set of choices you could encode as a **bitmask** (each bit = "is item i chosen?").

## Picture it

```text
operation   example (5 = 101, 3 = 011)   use it to…
a & b       101 & 011 = 001              test or keep bits
a | b       101 | 011 = 111              set bits
a ^ b       101 ^ 011 = 110              toggle; cancel pairs
n & (n-1)   110 & 101 = 100              clear the lowest 1 bit
n >> 1      101 >> 1  = 10               drop the last bit (÷ 2)
n & 1       101 & 1   = 1                read the last bit (odd?)
```

## Walk through an example

Single Number on `[4, 1, 2, 1, 2]`:

```text
start          0     000
^ 4            4     100
^ 1            5     101
^ 2            7     111
^ 1            6     110   ← the 1s cancelled
^ 2            4     100   ← the 2s cancelled
answer: 4
```

Missing Number uses the same trick: XOR every index `0..n` together with every value. Each present number meets its own index and cancels, so only the missing one survives.

## The code

```python
def single_number(nums):
    x = 0
    for v in nums:
        x ^= v
    return x


def count_ones(n):
    count = 0
    while n:
        n &= n - 1          # remove the lowest set bit
        count += 1
    return count


def count_bits(n):          # 1-bit counts for 0..n in O(n)
    ans = [0] * (n + 1)
    for i in range(1, n + 1):
        ans[i] = ans[i >> 1] + (i & 1)
    return ans
```

## How fast is it?

Each bitwise operation is O(1). Scanning the bits of a 32-bit number is at most 32 steps, so it's effectively O(1) too. XOR over an array is O(n) time with O(1) extra space.

## Common mistakes

- **Python integers never overflow.** Problems that assume 32 bits (Reverse Bits, Sum of Two Integers) need a mask like `& 0xFFFFFFFF`, and you convert back to a negative number when bit 31 is set.
- **Operator precedence.** `x & 1 == 0` means `x & (1 == 0)`. Write `(x & 1) == 0`.
- `n & (n - 1) == 0` (with parentheses!) tests for a power of two, but 0 also passes, so check `n > 0`.
- Reach for a bit trick only when the problem hints at it. A `Counter` that's clearly correct beats a clever trick you can't explain.
