## The idea in plain words

A trie (pronounced "try") is how a **phone's autocomplete** thinks. Words that start the same way **share the same path**: "car", "cat" and "cart" all walk through `c → a`, then branch. To check a word or a prefix, you follow one letter at a time. The cost depends on the **word's length**, not on how many words are stored.

Each node is a small dict of `letter → child node` plus a flag that says "a word ends here".

## You'll know it's this pattern when…

- The question involves **prefixes**: autocomplete, "starts with", or the longest common prefix.
- You look up many words against the **same dictionary** (Word Break, Word Search II).
- You play word games on a grid.

## Picture it

The words `car`, `cat`, `cart` and `dog` (★ marks the end of a word):

```text
          (root)
          /    \
         c      d
         |      |
         a      o
        / \     |
       r★  t★   g★
       |
       t★
```

`search("ca")` walks c → a and the path exists, but there's no ★, so it isn't a word. `startsWith("ca")` is true.

## Walk through an example

Insert `"cart"` into a trie that already holds `"car"`:

1. Start at the root. `c` exists, so step into it.
2. `a` exists, so step in. `r` exists, so step in.
3. `t` doesn't exist, so create it.
4. Mark the `t` node with ★.

Only one new node was needed, because the prefix `car` was shared.

## The code

```python
class TrieNode:
    __slots__ = ("children", "end")
    def __init__(self):
        self.children = {}            # letter -> TrieNode
        self.end = False              # does a word end here?

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.end = True

    def _walk(self, s):
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.end

    def startsWith(self, prefix):
        return self._walk(prefix) is not None
```

## How fast is it?

O(L) per operation, where L is the length of the word. Space is O(total characters inserted), less when prefixes are shared.

## Common mistakes

- `search` must check `end`: `"app"` isn't a word just because `"apple"` was inserted.
- For grid word games, remove trie nodes once a word is found, so later searches get faster and don't report duplicates.
