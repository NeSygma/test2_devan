# Problem Statement

Find a stable pattern in Conway's Game of Life by simulating the evolution of a 5x5 grid. A stable pattern is a cycle where the grid configuration repeats after a certain period (including period 1 for static patterns).

## Instance Data

Initial 5x5 grid configuration:
```
0 1 0 1 0
1 0 1 0 1
0 1 0 1 0
1 0 1 0 1
0 1 0 1 0
```

## Constraints

1. **Evolution rules**: Apply Conway's Game of Life rules for each generation:
   - Living cell with < 2 neighbors dies (underpopulation)
   - Living cell with 2-3 neighbors survives
   - Living cell with > 3 neighbors dies (overpopulation)
   - Dead cell with exactly 3 neighbors becomes alive (reproduction)

2. **Neighbor counting**: Each cell has up to 8 neighbors (orthogonal and diagonal)

3. **Cycle detection**: Simulate up to 10 time steps to detect when a state repeats, indicating a stable cycle

4. **Pattern extraction**: Once a cycle is found, extract **all** states in the cycle (from first occurrence to just before repetition)

## Objective

Find the first stable pattern (cycle) that emerges from the given initial configuration.

## Output Format

```json
{
  "stable_patterns": [
    {
      "pattern_id": 1,
      "period": 2,
      "states": [
        [[0, 1, ...], [1, 0, ...], ...],
        [[1, 0, ...], [0, 1, ...], ...],
        ...
      ]
    },
    ...
  ]
}
```

**Field descriptions:**
- `stable_patterns`: List of detected stable patterns (cycles)
- `pattern_id`: Integer identifier for the pattern (starting from 1)
- `period`: Number of generations in the cycle (1 = static, 2+ = oscillating)
- `states`: List of 5x5 grid states in the cycle (each state is a list of 5 lists of 5 integers)
