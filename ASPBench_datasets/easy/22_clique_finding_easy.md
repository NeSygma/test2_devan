# Problem Statement

Given an undirected graph, find the largest clique where every pair of vertices is connected by an edge.

## Instance Data

**Vertices:** {0, 1, 2, 3, 4, 5, 6}

**Edges:**
- (0, 1), (0, 2), (0, 3)
- (1, 2), (1, 3), (1, 4)
- (2, 3), (2, 5)
- (3, 4), (3, 5)
- (4, 5), (4, 6)
- (5, 6)

## Constraints

1. **All vertices** in the clique must be pairwise connected
2. For any two vertices u, v in the clique, edge (u, v) **must exist** in the graph

## Objective

Find a solution that **maximizes** the clique size.

**Expected optimal clique size:** 4

## Output Format

Return a JSON object with the following fields:

- `"clique"`: Array of integers - the vertices in the maximum clique (sorted)
- `"clique_size"`: Integer - number of vertices in the clique
- `"clique_edges"`: Array of [u, v] pairs - all edges within the clique where u < v (sorted)

**Example:**
```json
{
  "clique": [0, 1, 2, ...],
  "clique_size": 4,
  "clique_edges": [[0, 1], [0, 2], ...]
}
```

**Notes:**
- For a clique of size k, there should be k(k-1)/2 edges in clique_edges
- Multiple optimal solutions may exist with the same clique_size
