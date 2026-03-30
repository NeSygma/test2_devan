# Problem Statement

Design a complete, valid Metroidvania-style game world with complex mechanics. The level must be fully solvable without soft-locks and must satisfy advanced design constraints including special room types, item-based traversal abilities, one-way paths, and item acquisition prerequisites.

## Instance Data

**Rooms:** 12 fixed rooms: `Start`, `R1`, `R2`, `R3`, `R4`, `R5`, `R6`, `R7`, `R8`, `R9`, `R10`, `Goal`.

**Items:** 6 items to be placed:
- 4 Keys: `RedKey`, `BlueKey`, `GreenKey`, `YellowKey`
- 2 Equipment: `Boots` (for flooded rooms), `Grapple` (for chasms)

**Special Room Types:** Two rooms from `R1-R10` must be assigned special types: one `Flooded` and one `Chasm`.

## Constraints

1. **Item Placement:** All 6 items must be placed in rooms `R1-R10`. The `Start` and `Goal` rooms cannot contain items or have special types.
2. **Connections:** The level graph must have 10-15 bidirectional connections and exactly one one-way connection **(this is in addition to the mandatory one-way path to the `Goal` room, for a total of two one-way edges in the final graph)**. For each pair of rooms connected bidirectionally, if any connection in one direction requires a key, there **must exist** at least one connection in the return direction that is keyless (`requires: null`). The `Goal` room must have exactly one incoming connection and no outgoing connections.

   **Example:**
   ```json
   // VALID: A key-required path has a corresponding keyless return path.
   {"from": "R1", "to": "R2", "requires": "RedKey"},
   {"from": "R2", "to": "R1", "requires": null}

   // INVALID: A key-required path's return path also requires a key.
   {"from": "R3", "to": "R4", "requires": "BlueKey"},
   {"from": "R4", "to": "R3", "requires": "GreenKey"}
   ```
3. **Traversal Rules:**
   - Key-locked doors require the corresponding key
   - To **enter** a `Flooded` room, player must possess `Boots`
   - To **enter** a `Chasm` room, player must possess `Grapple`
   - An equipment item cannot be placed in a room of the type it enables (e.g., `Boots` cannot be in the `Flooded` room)
4. **Item Prerequisites:** The `YellowKey` must be located in the `Chasm` room, creating a hard dependency: player must acquire `Grapple` before acquiring `YellowKey`.
5. **Reachability & Progression:**
   - All 12 rooms must be reachable from `Start`
   - The `Goal` room must be the **last** new room the player can reach. All other 11 rooms must be accessible before the path to `Goal` is open.

## Objective

Find any valid solution that satisfies all constraints.

## Output Format

The solution must be a JSON object with the following structure:

```json
{
  "special_room_types": {
    "Flooded": "R5",
    "Chasm": "R9"
  },
  "item_locations": {
    "RedKey": "R1",
    "Boots": "R2",
    "BlueKey": "R4",
    "Grapple": "R6",
    "GreenKey": "R8",
    "YellowKey": "R9"
  },
  "connections": [
    {"from": "Start", "to": "R1", "requires": null},
    {"from": "R1", "to": "Start", "requires": null},
    {"from": "R1", "to": "R2", "requires": "RedKey"},
    {"from": "R2", "to": "R1", "requires": null},
    {"from": "R1", "to": "R3", "requires": null},
    {"from": "R3", "to": "R1", "requires": null},
    {"from": "R3", "to": "R4", "requires": "RedKey"},
    {"from": "R4", "to": "R3", "requires": null},
    {"from": "R2", "to": "R5", "requires": null},
    {"from": "R5", "to": "R2", "requires": null},
    {"from": "R5", "to": "R6", "requires": "BlueKey"},
    {"from": "R6", "to": "R5", "requires": null},
    {"from": "R6", "to": "R7", "requires": null},
    {"from": "R7", "to": "R6", "requires": null},
    {"from": "R7", "to": "R8", "requires": "Grapple"},
    {"from": "R8", "to": "R7", "requires": null},
    {"from": "R8", "to": "R10", "requires": "GreenKey"},
    {"from": "R10", "to": "R8", "requires": null},
    {"from": "R9", "to": "R10", "requires": null},
    {"from": "R10", "to": "R9", "requires": null},
    {"from": "R7", "to": "R9", "requires": "Grapple"},
    {"from": "R10", "to": "Goal", "requires": "YellowKey"}
  ],
  "solution_validity": {
    "all_rooms_reachable": true,
    "goal_is_last": true
  }
}
```

**Field Descriptions:**
- `special_room_types`: Object mapping special type names to room names
- `item_locations`: Object mapping item names to room names
- `connections`: Array of connection objects, each with `from`, `to`, and `requires` fields
- `solution_validity`: Object with boolean flags for reachability and goal timing
