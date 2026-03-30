# Problem Statement

Find a minimum set of vertices whose removal makes a directed graph acyclic. This is the classical feedback vertex set problem in graph theory, crucial for breaking cycles in circuits and dependencies.

## Instance Data

**Directed graph:**
- **Vertices:** {1, 2, 3, 4, 5, 6}
- **Edges:**
  - 1 → 2, 1 → 3
  - 2 → 4, 2 → 5
  - 3 → 4, 3 → 6
  - 4 → 2, 4 → 5
  - 5 → 3, 5 → 6
  - 6 → 1, 6 → 4

## Constraints

1. **All** removed vertices must eliminate all directed cycles
2. **No** directed cycles can remain in the graph after removal
3. When a vertex is removed, **all** its incident edges (both incoming and outgoing) are also removed

## Objective

Find a solution that **minimizes** the number of removed vertices.

**Expected optimal size:** 2

## Output Format

Return a JSON object with the following fields:
- `feedback_set`: List of vertex numbers in the minimum feedback vertex set (e.g., `[2, 5, ...]`)
- `size`: Integer representing the number of vertices in the feedback set
- `remaining_vertices`: List of vertices remaining after removal (e.g., `[1, 3, ...]`)

Example:
```json
{
  "feedback_set": [2, 5, ...],
  "size": 2,
  "remaining_vertices": [1, 3, ...]
}
```
