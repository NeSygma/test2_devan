#!/usr/bin/env python3
"""
Reference Model for the Composite Still Life Assembler problem.

This validator checks a solution on two criteria:
1. Global Stability: Verifies that the entire grid is a valid still life
   according to Conway's Game of Life rules.
2. Pattern Composition: Verifies that the grid contains exactly one Block,
   one Boat, and one Loaf, with no other live cells.
"""
import json
import sys

def load_solution():
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return None

def count_neighbors(grid, r, c, rows, cols):
    count = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                count += 1
    return count

def check_stability(grid):
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        for c in range(cols):
            neighbors = count_neighbors(grid, r, c, rows, cols)
            if grid[r][c] == 1:  # Live cell
                if neighbors not in [2, 3]:
                    return False, f"Live cell at ({r},{c}) is unstable with {neighbors} neighbors."
            else:  # Dead cell
                if neighbors == 3:
                    return False, f"Dead cell at ({r},{c}) becomes live with {neighbors} neighbors."
    return True, "Grid is a valid still life."

def find_patterns(grid):
    rows, cols = len(grid), len(grid[0])
    found_cells = set()
    patterns = []

    # Define pattern shapes relative to an anchor (r,c)
    # Note: anchor may be at a dead cell (e.g., loaf's anchor is dead at (0,0))
    shapes = {
        "block": {(0,0), (0,1), (1,0), (1,1)},
        "boat":  {(0,0), (0,1), (1,0), (1,2), (2,1)},
        "loaf":  {(0,1), (0,2), (1,0), (1,3), (2,1), (2,3), (3,2)}
    }

    # Try all possible anchor positions
    for r in range(rows):
        for c in range(cols):
            # Try each pattern type at this anchor position
            for name, shape_coords in shapes.items():
                is_match = True
                current_pattern_cells = set()

                # Check if all cells of this pattern exist and are live
                for dr, dc in shape_coords:
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1):
                        is_match = False
                        break
                    current_pattern_cells.add((nr, nc))

                # If pattern matches and cells aren't already claimed
                if is_match and len(current_pattern_cells) == len(shape_coords):
                    # Check if any of these cells are already in a found pattern
                    if not any(cell in found_cells for cell in current_pattern_cells):
                        # Check if this is not a subset of another pattern
                        is_subset = False
                        for p_cells in [p[1] for p in patterns]:
                            if current_pattern_cells.issubset(p_cells):
                                is_subset = True
                                break
                        if not is_subset:
                            patterns.append((name, current_pattern_cells))
                            found_cells.update(current_pattern_cells)

    return patterns, found_cells


def validate_solution(solution):
    if "grid" not in solution or not isinstance(solution["grid"], list):
        return False, "Invalid or missing 'grid' in solution."

    grid = solution["grid"]
    if len(grid) != 14 or any(len(row) != 14 for row in grid):
        return False, "Grid must be 14x14."

    is_stable, msg = check_stability(grid)
    if not is_stable:
        return False, msg

    found_patterns, found_cells = find_patterns(grid)

    total_live_cells = sum(row.count(1) for row in grid)
    if total_live_cells != len(found_cells):
        return False, "Grid contains unidentified live cells."

    expected_counts = {"block": 1, "boat": 1, "loaf": 1}
    actual_counts = {name: 0 for name in expected_counts}
    for name, _ in found_patterns:
        if name in actual_counts:
            actual_counts[name] += 1

    if actual_counts != expected_counts:
        return False, f"Incorrect pattern composition. Found: {actual_counts}"

    return True, "Solution is valid: stable grid with correct pattern composition."

def main():
    solution = load_solution()
    if solution is None:
        print(json.dumps({"valid": False, "message": "Invalid JSON input."}))
        return 1

    is_valid, message = validate_solution(solution)
    print(json.dumps({"valid": is_valid, "message": message}))
    return 0 if is_valid else 1

if __name__ == "__main__":
    sys.exit(main())
