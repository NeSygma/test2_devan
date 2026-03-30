# Problem Statement

In this grid puzzle, robots move one step at a time on a grid with obstacles. Robot A must reach its target position by coordinating with Robot B to clear the path.

## Instance Data

**Grid Size:** 4x4 (coordinates 0-3 for rows and columns)

**Robots:**
- Robot A: starts at (0, 1)
- Robot B: starts at (1, 1)

**Target:** Robot A must reach position (2, 1)

**Walls (vertical barriers):**
- Column 2 right side: rows 0-1 (creates corridor)

**Visual Grid:**
```
  0   1   2   3
0 .   A   |   .
1 .   B   |   .
2 .   T   .   .
3 .   .   .   .
```
Legend: `|` = wall, `A/B` = robots, `T` = target position (B blocks A's direct path down)

## Constraints

1. **Single-step movement**: Each move must be exactly one cell in a cardinal direction (Manhattan distance = 1)
2. **No collisions**: Multiple robots cannot occupy the same cell at the same time
3. **Wall blocking**: Robots cannot move through walls
4. **Valid positions**: All movements must stay within grid bounds (0-3 for both row and column)
5. **Sequential execution**: Moves are executed one at a time in sequence order

## Objective

Find a solution that **minimizes** the number of moves required to reach the goal.

**Expected minimum moves:** 3

## Output Format

```json
{
  "solution_found": true,
  "moves": 3,
  "sequence": [
    {"robot": "B", "from": [1, 1], "to": [1, 0]},
    {"robot": "A", "from": [0, 1], "to": [1, 1]},
    {"robot": "A", "from": [1, 1], "to": [2, 1]}
  ],
  "final_positions": {
    "A": [2, 1],
    "B": [1, 0]
  }
}
```

**Field Descriptions:**
- `solution_found` (boolean): Whether a valid solution was found
- `moves` (integer): Total number of moves in the sequence
- `sequence` (array): Ordered list of move objects, each containing:
  - `robot` (string): Robot identifier ("A" or "B")
  - `from` (array): Starting position [row, col]
  - `to` (array): Ending position [row, col] (must be exactly 1 step away)
- `final_positions` (object): Final positions of all robots after all moves, with robot names as keys and [row, col] arrays as values
