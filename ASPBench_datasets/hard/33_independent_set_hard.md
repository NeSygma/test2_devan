# Problem Statement

Find the maximum independent set in a graph where vertices have attributes and must satisfy additional constraints. An independent set is a set of vertices with no edges between them. Each vertex has a **type** ('core', 'support', or 'peripheral') and a **zone** (1, 2, or 3).

## Instance Data

**Vertices:** 1 through 24

**Zones:**
- Zone 1: vertices 1-8
- Zone 2: vertices 9-16
- Zone 3: vertices 17-24

**Types:**
- Core vertices: 1, 9, 17
- Support vertices: 2, 3, 10, 11, 18, 19
- Peripheral vertices: 4, 5, 6, 7, 8, 12, 13, 14, 15, 16, 20, 21, 22, 23, 24

**Edges:**
(1,2), (1,4), (1,10), (1,17), (2,5), (2,9), (3,6), (4,7), (5,8), (6,7), (8,16), (8,24), (9,10), (9,12), (9,17), (10,14), (11,15), (12,16), (13,14), (16,24), (17,18), (17,20), (18,19), (18,21), (19,22), (20,23), (21,24)

## Constraints

1. **Standard Independence:** No two vertices in the set can be connected by an edge.
2. **Core Count Limit:** The set can contain **at most** two core vertices.
3. **Core-Support Dependency:** For every core vertex included in the set, **at least** one support vertex from the **same zone** must also be included.
4. **Conditional Zone Exclusion:** If the set contains any peripheral vertex from zone 1, then it **cannot** contain any vertex from zone 3.
5. **Peripheral Headcount Rule:** The total number of peripheral vertices in the set **must not exceed** the total number of core vertices in the set.

## Objective

Find a solution that **maximizes** the size of the independent set.

**Expected maximum size: 7**

## Output Format

The solution must be a JSON object with the following structure:

```json
{
  "independent_set": [1, 3, 9, 11, 13],
  "size": 5,
  "core_vertices": [1, 9],
  "support_vertices": [3, 11],
  "peripheral_vertices": [13],
  "core_count": 2,
  "support_count": 2,
  "peripheral_count": 1
}
```

### Field Descriptions

- `independent_set`: Array of vertex numbers in the independent set (sorted)
- `size`: Total number of vertices in the set
- `core_vertices`: Array of core vertices in the set (sorted)
- `support_vertices`: Array of support vertices in the set (sorted)
- `peripheral_vertices`: Array of peripheral vertices in the set (sorted)
- `core_count`: Number of core vertices in the set
- `support_count`: Number of support vertices in the set
- `peripheral_count`: Number of peripheral vertices in the set
