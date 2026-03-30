#!/usr/bin/env python3
"""
Reference model for Nonogram Solver problem.
Validates solutions from stdin.
"""

import json
import sys


def verify_clue(line, clue):
    """
    Verify if a line satisfies the given clue.

    Args:
        line: list of integers (0 or 1)
        clue: list of integers representing consecutive black groups

    Returns:
        bool: True if line satisfies clue
    """
    if not clue:
        return all(cell == 0 for cell in line)

    # Find all groups of consecutive 1s
    groups = []
    current_group = 0

    for cell in line:
        if cell == 1:
            current_group += 1
        else:
            if current_group > 0:
                groups.append(current_group)
                current_group = 0

    if current_group > 0:
        groups.append(current_group)

    return groups == clue


def validate_solution(solution):
    """Validate nonogram solution from stdin."""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    # Check required fields
    if "grid" not in solution:
        return {"valid": False, "message": "Missing required field: grid"}
    if "valid" not in solution:
        return {"valid": False, "message": "Missing required field: valid"}

    grid = solution["grid"]

    # Validate grid structure
    if not isinstance(grid, list) or len(grid) != 5:
        return {"valid": False, "message": "Grid must be a 5x5 array"}

    for i, row in enumerate(grid):
        if not isinstance(row, list) or len(row) != 5:
            return {"valid": False, "message": f"Row {i} must have exactly 5 elements"}

        for j, cell in enumerate(row):
            if cell not in [0, 1]:
                return {"valid": False, "message": f"Cell [{i}][{j}] must be 0 or 1, got {cell}"}

    # Define the clues
    row_clues = [
        [2],     # Row 1
        [1],     # Row 2
        [3],     # Row 3
        [1, 1],  # Row 4
        [2]      # Row 5
    ]

    col_clues = [
        [1, 1],  # Column 1
        [1, 3],  # Column 2
        [2],     # Column 3
        [1],     # Column 4
        [1]      # Column 5
    ]

    # Check row constraints
    for i, (row, clue) in enumerate(zip(grid, row_clues)):
        if not verify_clue(row, clue):
            return {"valid": False, "message": f"Row {i+1} does not satisfy clue {clue}"}

    # Check column constraints
    for j in range(5):
        column = [grid[i][j] for i in range(5)]
        clue = col_clues[j]
        if not verify_clue(column, clue):
            return {"valid": False, "message": f"Column {j+1} does not satisfy clue {clue}"}

    return {"valid": True, "message": "Valid nonogram solution"}


if __name__ == "__main__":
    try:
        data = sys.stdin.read().strip()
        if not data:
            result = {"valid": False, "message": "No input provided"}
        else:
            solution = json.loads(data)
            result = validate_solution(solution)

        print(json.dumps(result))
        sys.exit(0 if result["valid"] else 1)
    except json.JSONDecodeError as e:
        result = {"valid": False, "message": f"Invalid JSON: {e}"}
        print(json.dumps(result))
        sys.exit(1)
