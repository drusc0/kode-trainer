## The idea in plain words

Imagine a party where you're looking for someone whose age plus yours makes 50. The slow way is to walk up to every guest and ask. The fast way is to keep a **notebook** of everyone you've already met: when a new person arrives, you check the notebook for "50 minus their age" and get an instant answer.

In Python the notebook is a `dict` or a `set`. Looking something up takes the same tiny amount of time (O(1)) however big it gets. You spend a little memory to avoid scanning the array again and again.

## You'll know it's this pattern when…

- The question is "have I **seen** X before?": a matching pair, a duplicate, a complement.
- You need to **count** things or **group** things that look alike.
- Your first idea is two nested loops (O(n²)) where the inner loop just searches for something.

## Picture it

Two Sum with `nums = [2, 7, 11, 15]`, `target = 9`. At each step ask the notebook: "have I seen `9 - x`?"

```text
step  x    need (9 - x)   notebook before       found?
 0    2    7              {}                    no  → write 2:0
 1    7    2              {2:0}                 YES → answer [0, 1]

notebook = { value → index where we saw it }
```

One pass and done. The brute force would compare every pair: 4 numbers make 6 pairs, and 10,000 numbers make about 50 million.

## Walk through an example

Group anagrams: `["eat", "tea", "tan", "ate", "nat"]`.

1. Words that are anagrams contain the same letters, so sorting the letters gives the same **key**: `"eat" → "aet"`, `"tea" → "aet"`.
2. Use that key as the notebook entry and append each word to its group:

```text
"aet" → [eat, tea, ate]
"ant" → [tan, nat]
```

3. The answer is the list of groups.

## The code

```python
def two_sum(nums, target):
    seen = {}                      # value -> index
    for i, x in enumerate(nums):
        if target - x in seen:     # complement already seen?
            return [seen[target - x], i]
        seen[x] = i                # insert AFTER checking, so x doesn't pair with itself

def group(words):
    groups = defaultdict(list)
    for w in words:
        groups[key(w)].append(w)   # choose a canonical key, e.g. ''.join(sorted(w))
    return list(groups.values())
```

## How fast is it?

O(n) time: each element is looked at once and each lookup is O(1). O(n) space for the notebook. Sorting-based keys add O(k log k) per word of length k.

## Common mistakes

- Check before you insert, or an element pairs with itself (`[3]`, target 6).
- Lists aren't hashable. Convert keys to a `tuple` or a string.
- "Longest consecutive sequence": only start counting from the first number of a run (`x - 1 not in s`), or you recount the same run many times and lose O(n).
