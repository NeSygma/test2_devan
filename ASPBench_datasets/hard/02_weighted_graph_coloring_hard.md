# Problem Statement

The task is to color the vertices of a given graph using colors from the set {1, 2, 3, 4, 5}. The coloring must satisfy two main conditions:
1. No two adjacent vertices can share the same color.
2. The total weighted coloring cost, calculated as the sum over all vertices of (color_index × vertex_weight), must be less than or equal to 850.

You must find a valid coloring that meets these requirements.

## Instance Data

**Vertices:** 1 through 36

**Colors:** 1 through 5 (exactly 5 colors available)

**Weights:**
- Vertices 1-5: weight = 10
- Vertices 6-15: weight = 3
- Vertices 16-25: weight = 5
- Vertices 26-36: weight = 7

**Graph Structure:**

The graph consists of a core clique and three connected clusters.

**Core Clique (K5):**
- Vertices 1, 2, 3, 4, 5 form a complete graph (all 10 pairs connected)
- This forces the use of all 5 colors

**Cluster A (vertices 6-15):**
- Ring structure: edges (6,7), (7,8), (8,9), (9,10), (10,11), (11,12), (12,13), (13,14), (14,15), (15,6)
- Diagonal chords: edges (6,9), (7,10), (8,11), (9,12), (10,13), (11,14), (12,15), (13,6), (14,7), (15,8)
- Connections to core:
  - Vertex 6 connects to vertices 1, 2
  - Vertex 9 connects to vertices 2, 3
  - Vertex 12 connects to vertices 3, 4
  - Vertex 15 connects to vertices 4, 5

**Cluster B (vertices 16-25):**
- Grid structure: arranged as 2 rows × 5 columns
  - Row 1: vertices 16-20
  - Row 2: vertices 21-25
- Horizontal edges: (16,17), (17,18), (18,19), (19,20), (21,22), (22,23), (23,24), (24,25)
- Vertical edges: (16,21), (17,22), (18,23), (19,24), (20,25)
- Diagonal edges: (16,22), (17,23), (18,24), (19,25)
- Connections to core:
  - Vertex 16 connects to vertex 1
  - Vertex 20 connects to vertex 5
- Connections to Cluster A:
  - Vertex 18 connects to vertex 8
  - Vertex 23 connects to vertex 13

**Cluster C (vertices 26-36):**
- Vertices 26-36 arranged in an 11-cycle with chords
- Cycle edges: (26,27), (27,28), (28,29), (29,30), (30,31), (31,32), (32,33), (33,34), (34,35), (35,36), (36,26)
- Chord edges connecting vertices 3 steps apart: (26,29), (27,30), (28,31), (29,32), (30,33), (31,34), (32,35), (33,36), (34,26), (35,27), (36,28)
- Connections to core:
  - Vertex 26 connects to vertices 1, 5
  - Vertex 31 connects to vertex 3
- Connections to Cluster B:
  - Vertex 28 connects to vertex 19
  - Vertex 33 connects to vertex 24

## Constraints

1. **Every vertex** must be assigned exactly one color from {1, 2, 3, 4, 5}
2. **No two adjacent vertices** can have the same color
3. Due to the K5 core, **all 5 colors must be used**
4. Colors must be positive integers from 1 to 5
5. **Weighted cost bound**: weighted_cost ≤ 850, where weighted_cost = sum over all vertices v of (color(v) × weight(v))

## Objective

Find **any** valid 5-coloring that satisfies all 5 constraints listed. This is a **satisfaction problem**, not an optimization problem. The goal is to find a feasible solution that meets the cost bound, not to find the solution with the absolute minimum cost. Your solution will be considered correct if it meets all adjacency constraints and the calculated `weighted_cost` is 850 or less.

## Output Format

Output a JSON object with the following fields:

- **num_colors** (integer): Number of distinct colors used (must be 5)
- **weighted_cost** (integer): Sum of color(v) × weight(v) over all 36 vertices
- **coloring** (array): Array of 36 objects, each with:
  - **vertex** (integer): Vertex number (1-36)
  - **color** (integer): Color assigned (1-5)

**Example structure:**
```json
{
  "num_colors": 5,
  "weighted_cost": 600,
  "coloring": [
    {"vertex": 1, "color": 1},
    {"vertex": 2, "color": 2},
    {"vertex": 3, "color": 3},
    {"vertex": 4, "color": 4},
    {"vertex": 5, "color": 5},
    {"vertex": 6, "color": 1},
    ...
    {"vertex": 36, "color": 2}
  ]
}
```

**Requirements:**
- The coloring array must contain exactly 36 entries (one per vertex)
- Vertices should be listed in order from 1 to 36
- All colors must be in range [1, 5]
- The weighted_cost must match the sum calculated from the coloring
