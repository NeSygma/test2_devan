# Problem Statement

Given a weighted graph and a set of terminal vertices, find a minimum-weight tree that connects all terminals. The tree may include additional non-terminal vertices (called Steiner vertices) to reduce the total weight.

## Instance Data

**Graph:**
- Vertices: 0, 1, 2, 3, 4, 5, 6
- Edges with weights:
  - (0,1): 3, (0,2): 5
  - (1,3): 2, (1,4): 4
  - (2,3): 1, (2,5): 6
  - (3,4): 3, (3,5): 3, (3,6): 2
  - (4,5): 2
  - (5,6): 4

**Terminal Vertices:** 0, 5, 6

## Constraints

1. **All terminals must be connected**: Every terminal vertex must be included in the tree
2. **Tree structure**: The edges must form a valid tree (no cycles, connected)
3. **Valid edges**: Only edges from the graph can be used
4. **Correct weights**: Edge weights must match the graph

## Objective

Find a solution that **minimizes** the total weight of the tree connecting all terminals.

**Expected optimal weight: 10**

## Output Format

```json
{
  "total_weight": <integer, total weight of tree edges>,
  "tree_edges": [
    {"from": <integer>, "to": <integer>, "weight": <integer>},
    ...
  ],
  "steiner_vertices": [<integer>, ...],
  "terminals": [<integer>, ...],
  "connected_components": [
    {"component": <integer>, "vertices": [<integer>, ...]}
  ]
}
```

Where:
- `total_weight`: Sum of all edge weights in the tree
- `tree_edges`: List of edges in the Steiner tree
- `steiner_vertices`: Non-terminal vertices included in the tree
- `terminals`: The required terminal vertices
- `connected_components`: List of connected components (should be exactly 1)
