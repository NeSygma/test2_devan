# Problem Statement

The Blocks World consists of blocks that can be stacked on top of each other or placed on a table. Find the shortest sequence of moves to transform an initial configuration into a goal configuration. Only clear blocks (with nothing on top) can be moved, and only one block can be moved at a time.

## Instance Data

**Blocks:** A, B, C

**Initial State:**
- Block A is on the table
- Block B is on the table
- Block C is on top of block A

**Goal State:**
- Block A is on top of block B
- Block B is on top of block C
- Block C is on the table

## Constraints

1. **Only clear blocks** can be moved (blocks with nothing on top of them)
2. **Exactly one** block can be moved per time step
3. **Each block** can only be in one position at each time
4. **At most one** block can be on top of another block (except the table)
5. **No block** can be placed on itself

## Objective

Find a sequence of moves that **minimizes** the number of actions to reach the goal state.

**Expected optimal plan length:** 3 moves

## Output Format

```json
{
  "plan_length": <number>,
  "actions": [
    {
      "step": 1,
      "action": "move",
      "block": "<block_name>",
      "from": "<source_position>",
      "to": "<target_position>"
    },
    ...
  ]
}
```

**Fields:**
- `plan_length`: Total number of moves in the plan
- `actions`: List of move actions in order
- `step`: Sequential step number (1, 2, 3, ...)
- `action`: Always "move" for this problem
- `block`: Name of block being moved (A, B, or C)
- `from`: Source position ("table" or block name)
- `to`: Target position ("table" or block name)
