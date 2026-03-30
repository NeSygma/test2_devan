#!/usr/bin/env python3
"""
Reference model for Sudoku problem
Used for solution verification only.
"""

import json
import sys

def verify_solution(solution_json: str) -> dict:
    """
    Verify if the given solution satisfies all problem constraints.

    Args:
        solution_json: JSON string containing the solution

    Returns:
        dict with keys:
        - valid: bool (True if solution is valid)
        - message: str (explanation)
    """

    # Parse solution
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    # Check required fields
    required_fields = ["grid", "is_valid", "clues_preserved"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    grid = solution["grid"]
    is_valid = solution["is_valid"]
    clues_preserved = solution["clues_preserved"]

    # Validate types
    if not isinstance(grid, list):
        return {"valid": False, "message": "grid must be an array"}
    if not isinstance(is_valid, bool):
        return {"valid": False, "message": "is_valid must be a boolean"}
    if not isinstance(clues_preserved, bool):
        return {"valid": False, "message": "clues_preserved must be a boolean"}

    # Check grid structure
    if len(grid) != 9:
        return {"valid": False, "message": f"Grid must have 9 rows, got {len(grid)}"}

    for i, row in enumerate(grid):
        if not isinstance(row, list):
            return {"valid": False, "message": f"Row {i} must be an array"}
        if len(row) != 9:
            return {"valid": False, "message": f"Row {i} must have 9 columns, got {len(row)}"}
        for j, cell in enumerate(row):
            if not isinstance(cell, int) or cell not in range(1, 10):
                return {"valid": False, "message": f"Cell [{i}][{j}] must be integer 1-9, got {cell}"}

    # Original clues (0-indexed, 0 means empty)
    original_clues = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    # Check clues preservation
    actual_clues_preserved = True
    for i in range(9):
        for j in range(9):
            if original_clues[i][j] != 0 and grid[i][j] != original_clues[i][j]:
                actual_clues_preserved = False
                break
        if not actual_clues_preserved:
            break

    if clues_preserved != actual_clues_preserved:
        return {"valid": False, "message": f"clues_preserved mismatch: expected {actual_clues_preserved}, got {clues_preserved}"}

    if not actual_clues_preserved:
        return {"valid": False, "message": "Original clues were modified"}

    # Check sudoku constraints
    def check_valid_sudoku(grid):
        # Check rows
        for i in range(9):
            if len(set(grid[i])) != 9:
                return False, f"Row {i} has duplicate values"

        # Check columns
        for j in range(9):
            col = [grid[i][j] for i in range(9)]
            if len(set(col)) != 9:
                return False, f"Column {j} has duplicate values"

        # Check 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                box_values = []
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_col * 3 + j
                        box_values.append(grid[row][col])
                if len(set(box_values)) != 9:
                    return False, f"3x3 box at ({box_row}, {box_col}) has duplicate values"

        return True, "Valid Sudoku"

    actual_valid, validation_msg = check_valid_sudoku(grid)

    if is_valid != actual_valid:
        return {"valid": False, "message": f"is_valid mismatch: expected {actual_valid}, got {is_valid}"}

    if not actual_valid:
        return {"valid": False, "message": f"Invalid Sudoku: {validation_msg}"}

    return {"valid": True, "message": "Valid and complete Sudoku solution"}

def main():
    """Main entry point for verification."""
    # Read from stdin
    solution_json = sys.stdin.read()

    result = verify_solution(solution_json)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
