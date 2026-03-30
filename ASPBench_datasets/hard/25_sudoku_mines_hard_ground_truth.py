#!/usr/bin/env python3
"""
Reference model for Sudoku Mines problem.
Used for solution verification only.
"""

import json
import sys

def verify_solution(solution_json: str) -> dict:
    """Verifies the Sudoku Mines solution."""
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    # --- Field and Type Validation ---
    required_fields = {
        "grid": list, "mines": list, "is_valid_sudoku": bool,
        "sudoku_clues_preserved": bool, "mine_clues_satisfied": bool
    }
    for field, field_type in required_fields.items():
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}
        if not isinstance(solution[field], field_type):
            return {"valid": False, "message": f"Field '{field}' has incorrect type"}

    grid = solution["grid"]

    # --- Grid Structure Validation ---
    if len(grid) != 9 or not all(isinstance(r, list) and len(r) == 9 for r in grid):
        return {"valid": False, "message": "Grid must be a 9x9 array of arrays."}
    if not all(isinstance(c, int) and 1 <= c <= 9 for r in grid for c in r):
        return {"valid": False, "message": "Grid cells must be integers from 1 to 9."}

    # --- Sudoku Clue Data ---
    sudoku_clues = {
        (0,0): 5, (0,4): 7, (0,8): 2,
        (4,0): 4, (4,4): 5, (4,8): 1,
        (8,0): 3, (8,4): 8, (8,8): 9,
    }

    # --- Mine-Count Clue Data (corrected to 3 clues) ---
    mine_clue_locs = [(0,1), (3,1), (5,7)]

    # --- Verification 1: Sudoku Validity ---
    def check_sudoku_validity(g):
        for i in range(9):
            if len(set(g[i])) != 9:
                return False, f"Row {i} has duplicate values."
        for j in range(9):
            if len(set(g[i][j] for i in range(9))) != 9:
                return False, f"Column {j} has duplicate values."
        for box_r in range(3):
            for box_c in range(3):
                box = [g[box_r*3+i][box_c*3+j] for i in range(3) for j in range(3)]
                if len(set(box)) != 9:
                    return False, f"Box at ({box_r},{box_c}) has duplicates."
        return True, "Valid Sudoku"

    actual_is_valid_sudoku, msg = check_sudoku_validity(grid)
    if solution["is_valid_sudoku"] != actual_is_valid_sudoku:
        return {"valid": False, "message": f"is_valid_sudoku flag is incorrect. Expected {actual_is_valid_sudoku}, got {solution['is_valid_sudoku']}. Reason: {msg}"}
    if not actual_is_valid_sudoku:
        return {"valid": False, "message": f"Grid is not a valid Sudoku: {msg}"}

    # --- Verification 2: Sudoku Clues Preserved ---
    actual_clues_preserved = True
    for (r, c), val in sudoku_clues.items():
        if grid[r][c] != val:
            actual_clues_preserved = False
            break
    if solution["sudoku_clues_preserved"] != actual_clues_preserved:
        return {"valid": False, "message": f"sudoku_clues_preserved flag is incorrect. Expected {actual_clues_preserved}, got {solution['sudoku_clues_preserved']}."}

    # --- Verification 3: Mine Locations ---
    actual_mines = sorted([[r, c] for r in range(9) for c in range(9) if grid[r][c] % 2 == 0])
    submitted_mines = sorted(solution["mines"])
    if submitted_mines != actual_mines:
        return {"valid": False, "message": "The 'mines' field does not correctly list all cells with even numbers."}

    # --- Verification 4: Mine-Count Clues Satisfied ---
    actual_mine_clues_satisfied = True
    for r_clue, c_clue in mine_clue_locs:
        neighbor_mine_count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = r_clue + dr, c_clue + dc
                if 0 <= r < 9 and 0 <= c < 9:
                    if grid[r][c] % 2 == 0:
                        neighbor_mine_count += 1
        if grid[r_clue][c_clue] != neighbor_mine_count:
            actual_mine_clues_satisfied = False
            break

    if solution["mine_clues_satisfied"] != actual_mine_clues_satisfied:
        return {"valid": False, "message": f"mine_clues_satisfied flag is incorrect. Expected {actual_mine_clues_satisfied}, got {solution['mine_clues_satisfied']}."}
    if not actual_mine_clues_satisfied:
        return {"valid": False, "message": "A mine-count clue is incorrect."}

    return {"valid": True, "message": "Solution is valid and satisfies all constraints."}

def main():
    """Main entry point for verification."""
    try:
        solution_json = sys.stdin.read()
        result = verify_solution(solution_json)
    except Exception as e:
        result = {"valid": False, "message": f"An unexpected error occurred: {e}"}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
