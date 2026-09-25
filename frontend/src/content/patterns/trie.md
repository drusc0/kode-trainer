## Recognise it

Prefix queries, autocomplete, or many lookups against the same dictionary of words (Word Break, Word Search II).

## Core idea

Each node maps a character to a child node and marks whether a word ends there. Insert and lookup both cost O(length of the word).

## Template

```python
class TrieNode:
    __slots__ = ("children", "end")
    def __init__(self):
        self.children = {}
        self.end = False

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

## Complexity

O(L) per operation. Space is O(total characters inserted).

## Pitfalls

- `search` must check `end`. `"app"` isn't a word just because `"apple"` was inserted.
- For grid word games, prune trie nodes once a word is found so later searches get faster.
