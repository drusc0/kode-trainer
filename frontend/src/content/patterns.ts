export interface Pattern {
  slug: string;
  title: string;
  summary: string;
  signals: string[];
}

export const PATTERNS: Pattern[] = [
  {
    slug: "arrays-hashing",
    title: "Arrays & hashing",
    summary: "Trade memory for speed: remember what you've seen in a dict or set so each lookup is O(1).",
    signals: [
      "find a pair, duplicate or complement",
      "counting or grouping",
      "an O(n²) brute force that re-scans the array",
    ],
  },
  {
    slug: "two-pointers",
    title: "Two pointers",
    summary: "Walk two indices toward each other, or in the same direction, over a sorted array or a string.",
    signals: ["sorted input", "palindromes", "pairs or triplets with a target sum", "in-place partitioning"],
  },
  {
    slug: "sliding-window",
    title: "Sliding window",
    summary: "Keep a contiguous window and a summary of it; grow the right edge, shrink the left when a rule breaks.",
    signals: ["longest or shortest contiguous substring/subarray", "“at most k” constraints", "all-positive values"],
  },
  {
    slug: "prefix-sum",
    title: "Prefix sums",
    summary: "Precompute running totals so any range sum is one subtraction; add a hash map to count ranges.",
    signals: ["range sums", "subarray sums with negative numbers", "“everything except i”"],
  },
  {
    slug: "stack",
    title: "Stack & monotonic stack",
    summary:
      "Process items last-in-first-out: matching brackets, evaluating expressions, finding the next greater element.",
    signals: ["nested structure", "next greater or smaller element", "undo the most recent thing"],
  },
  {
    slug: "binary-search",
    title: "Binary search",
    summary: "Halve the search space each step, over indices or over the answer itself when feasibility is monotonic.",
    signals: ["sorted or rotated input", "an O(log n) requirement", "“minimum k such that …”"],
  },
  {
    slug: "linked-list",
    title: "Linked lists",
    summary: "Pointer manipulation with dummy heads, fast/slow runners and in-place reversal.",
    signals: ["ListNode input", "cycle detection", "middle or k-th from the end", "reversal or reordering"],
  },
  {
    slug: "trees",
    title: "Trees: DFS & BFS",
    summary: "Recursive DFS returns information upward; BFS processes level by level with a queue.",
    signals: ["TreeNode input", "depth, height or diameter", "level-by-level views", "BST ordering"],
  },
  {
    slug: "heap",
    title: "Heaps & top-k",
    summary: "A priority queue returns the smallest item in O(log n): ideal for top-k, k-way merges and scheduling.",
    signals: [
      "k largest, smallest, closest or most frequent",
      "merging k sorted sources",
      "always process the cheapest next",
    ],
  },
  {
    slug: "graphs",
    title: "Graphs: BFS, DFS & topological sort",
    summary:
      "Model the problem as nodes and edges: BFS for fewest steps, DFS for connectivity, Kahn's algorithm for dependencies.",
    signals: ["grids", "minimum steps or moves", "dependencies or prerequisites", "connected components"],
  },
  {
    slug: "backtracking",
    title: "Backtracking",
    summary:
      "Build a candidate step by step, recurse, then undo the choice to enumerate subsets, permutations and paths.",
    signals: ["“return all …”", "combinations, permutations, subsets", "small n (≤ 20)", "path search in a grid"],
  },
  {
    slug: "dynamic-programming",
    title: "Dynamic programming",
    summary: "Define a state, write how states relate, then fill a table bottom-up or memoize top-down.",
    signals: ["“number of ways”", "minimum or maximum cost", "choices at each step with overlapping subproblems"],
  },
  {
    slug: "intervals-greedy",
    title: "Intervals & greedy",
    summary: "Sort by start or end, then sweep once keeping only the state that matters.",
    signals: [
      "intervals, meetings or ranges",
      "minimum rooms, arrows or removals",
      "reachability decided by local choices",
    ],
  },
  {
    slug: "design",
    title: "Design problems",
    summary:
      "Combine data structures so each operation meets its complexity target, such as a hash map plus a linked list.",
    signals: ["a class with several methods", "O(1) get/put requirements", "time-versioned or cached data"],
  },
  {
    slug: "trie",
    title: "Tries",
    summary: "A prefix tree stores strings character by character, so prefix queries cost O(length).",
    signals: ["prefix search or autocomplete", "many lookups against one dictionary", "word games on grids"],
  },
  {
    slug: "math-geometry",
    title: "Math & geometry",
    summary:
      "Walk a matrix with careful index rules, or turn paper arithmetic into loops: rotations, spirals, fast powers.",
    signals: [
      "rotate, spiral or update a matrix in place",
      "neighbour-based cell updates",
      "arithmetic without built-ins",
    ],
  },
  {
    slug: "bit-manipulation",
    title: "Bit manipulation",
    summary:
      "Treat integers as rows of switches: XOR cancels pairs, n & (n − 1) drops the lowest bit, masks encode sets.",
    signals: ["everything appears twice except one", "a missing number in a range", "count, reverse or add bits"],
  },
];

const bodies = import.meta.glob("./patterns/*.md", { query: "?raw", import: "default", eager: true }) as Record<
  string,
  string
>;

export const patternBody = (slug: string): string => bodies[`./patterns/${slug}.md`] ?? "";
export const APPROACH_GUIDE: string = bodies["./patterns/_approach.md"] ?? "";
export const patternTitle = (slug: string): string => PATTERNS.find((p) => p.slug === slug)?.title ?? slug;
