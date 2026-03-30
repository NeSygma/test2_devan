#!/usr/bin/env python3
"""
Reference Model: Latin Square Completion Problem
===============================================
Validate a Latin square solution.
"""

import sys
import json
from typing import List

def validate_solution(solution_data: dict) -> dict:
    """Validate the Latin square solution."""

    # Check for error field
    if "error" in solution_data:
        return {"valid": False, "message": "Solution contains error"}

    # Extract grid
    if "grid" not in solution_data:
        return {"valid": False, "message": "Missing 'grid' field"}

    grid = solution_data["grid"]

    # Check dimensions
    if not grid or len(grid) != 5:
        return {"valid": False, "message": f"Grid must have 5 rows, got {len(grid)}"}

    for i, row in enumerate(grid):
        if len(row) != 5:
            return {"valid": False, "message": f"Row {i+1} must have 5 columns, got {len(row)}"}

    # Check row constraints
    for r in range(5):
        row_values = sorted(grid[r])
        if row_values != [1, 2, 3, 4, 5]:
            return {"valid": False, "message": f"Row {r+1} constraint violated: {grid[r]}"}

    # Check column constraints
    for c in range(5):
        col_values = sorted([grid[r][c] for r in range(5)])
        if col_values != [1, 2, 3, 4, 5]:
            return {"valid": False, "message": f"Column {c+1} constraint violated"}

    # Check initial constraints are preserved
    initial_constraints = [
        (0, 0, 1),
        (1, 2, 3),
        (2, 3, 4),
        (3, 4, 5),
        (4, 1, 2)
    ]

    for r, c, expected in initial_constraints:
        if grid[r][c] != expected:
            return {"valid": False, "message": f"Initial constraint violated at ({r+1},{c+1}): expected {expected}, got {grid[r][c]}"}

    return {"valid": True, "message": "Valid Latin square completion"}

if __name__ == "__main__":
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            print(json.dumps({"valid": False, "message": "No input provided"}))
            sys.exit(1)

        solution_data = json.loads(input_data)
        result = validate_solution(solution_data)
        print(json.dumps(result))

    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON input: {str(e)}"}))
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Verification error: {str(e)}"}))
