#!/usr/bin/env python3
"""
Reference Model: Latin Square Problem Validator
================================================
This script validates a solution for the Latin Square problem
read from standard input. It does not solve the problem, only verifies
that a given solution adheres to all specified constraints.
"""

import sys
import json
from typing import List, Dict, Any

def verify_solution(solution: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """
    Verifies a given solution grid against all problem constraints.
    """
    try:
        grid = solution["grid"]
        n = 8
    except (KeyError, TypeError):
        return {"valid": False, "message": "Invalid JSON format: 'grid' key not found or incorrect type."}

    # --- Constraint Verification ---

    # 0. Initial clues must be preserved (1-indexed in description, 0-indexed in array)
    initial_clues = {
        (0, 0): 1, (0, 7): 8, (1, 1): 6, (2, 2): 4, (3, 3): 5,
        (4, 4): 7, (5, 5): 4, (6, 6): 6, (7, 7): 3, (7, 0): 8
    }
    for (r, c), val in initial_clues.items():
        if grid[r][c] != val:
            msg = f"Initial clue at ({r+1},{c+1}) is incorrect. Expected {val}, found {grid[r][c]}."
            if verbose: print(f"✗ {msg}")
            return {"valid": False, "message": msg}
    if verbose: print("✓ Initial clues preserved.")

    # 1. Latin Square Constraint
    for i in range(n):
        # Check row i
        if sorted(grid[i]) != list(range(1, n + 1)):
            msg = f"Row {i+1} is not a valid permutation of 1-8."
            if verbose: print(f"✗ {msg}")
            return {"valid": False, "message": msg}
        # Check column i
        col = [grid[r][i] for r in range(n)]
        if sorted(col) != list(range(1, n + 1)):
            msg = f"Column {i+1} is not a valid permutation of 1-8."
            if verbose: print(f"✗ {msg}")
            return {"valid": False, "message": msg}
    if verbose: print("✓ Latin Square constraint satisfied.")

    # 2. Adjacent Pair Sum Constraint
    for r in range(n):
        for c in range(n - 1):
            if grid[r][c] + grid[r][c+1] <= 5:
                msg = f"Adjacent pair sum violated at ({r+1},{c+1}) and ({r+1},{c+2}): {grid[r][c]} + {grid[r][c+1]} <= 5."
                if verbose: print(f"✗ {msg}")
                return {"valid": False, "message": msg}
    if verbose: print("✓ Adjacent pair sum constraint satisfied.")

    # 3. Quadrant Parity Constraint
    # Top-left quadrant
    tl_even_count = 0
    for r in range(n // 2):
        for c in range(n // 2):
            if grid[r][c] % 2 == 0:
                tl_even_count += 1
    if tl_even_count != 8:
        msg = f"Top-left quadrant has {tl_even_count} even numbers, but expected 8."
        if verbose: print(f"✗ {msg}")
        return {"valid": False, "message": msg}

    # Bottom-right quadrant
    br_odd_count = 0
    for r in range(n // 2, n):
        for c in range(n // 2, n):
            if grid[r][c] % 2 != 0:
                br_odd_count += 1
    if br_odd_count != 8:
        msg = f"Bottom-right quadrant has {br_odd_count} odd numbers, but expected 8."
        if verbose: print(f"✗ {msg}")
        return {"valid": False, "message": msg}
    if verbose: print("✓ Quadrant parity constraint satisfied.")

    # 4. Partial Sum Constraint
    # First row partial sum
    row1_p_sum = sum(grid[0][c] for c in range(n // 2))
    if row1_p_sum != 14:
        msg = f"Sum of first 4 cells in row 1 is {row1_p_sum}, but expected 14."
        if verbose: print(f"✗ {msg}")
        return {"valid": False, "message": msg}

    # First column partial sum
    col1_p_sum = sum(grid[r][0] for r in range(n // 2))
    if col1_p_sum != 10:
        msg = f"Sum of first 4 cells in column 1 is {col1_p_sum}, but expected 10."
        if verbose: print(f"✗ {msg}")
        return {"valid": False, "message": msg}
    if verbose: print("✓ Partial sum constraint satisfied.")

    return {"valid": True, "message": "All constraints satisfied. Solution is valid."}

if __name__ == "__main__":
    try:
        input_data = sys.stdin.read()
        solution_json = json.loads(input_data)
        result = verify_solution(solution_json, verbose=False)
    except json.JSONDecodeError:
        result = {"valid": False, "message": "Invalid JSON input."}
    except Exception as e:
        result = {"valid": False, "message": f"An unexpected error occurred during verification: {e}"}

    print(json.dumps(result))
