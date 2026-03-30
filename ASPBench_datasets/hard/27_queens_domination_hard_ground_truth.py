#!/usr/bin/env python3
"""
Reference model for Queens Domination problem on 9x9 board.
Validates that all 81 squares are dominated by the given queen positions.
"""

import json
import sys

# Expected optimal value
EXPECTED_OPTIMAL_QUEENS = 5

def verify_solution(solution_json: str) -> dict:
    """
    Verify if the given solution satisfies all problem constraints.
    """
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    if "queens" not in solution:
        return {"valid": False, "message": "Missing required field: queens"}

    queens = solution["queens"]

    if not isinstance(queens, list):
        return {"valid": False, "message": "queens must be an array"}

    # Validate queen positions
    queen_positions = set()
    for i, queen in enumerate(queens):
        if not (isinstance(queen, list) and len(queen) == 2 and
                isinstance(queen[0], int) and isinstance(queen[1], int) and
                0 <= queen[0] <= 8 and 0 <= queen[1] <= 8):
            return {"valid": False, "message": f"Invalid queen format or position at index {i}"}
        pos = tuple(queen)
        if pos in queen_positions:
            return {"valid": False, "message": f"Duplicate queen position at {pos}"}
        queen_positions.add(pos)

    # Calculate dominated squares
    dominated = set()

    for r_q, c_q in queens:
        # Queen covers its own square
        dominated.add((r_q, c_q))

        # Horizontal and vertical (rook moves)
        for i in range(9):
            dominated.add((r_q, i))  # Row
            dominated.add((i, c_q))  # Column

        # Diagonals (bishop moves)
        for i in range(-8, 9):
            # Main diagonal (top-left to bottom-right)
            r, c = r_q + i, c_q + i
            if 0 <= r <= 8 and 0 <= c <= 8:
                dominated.add((r, c))

            # Anti-diagonal (top-right to bottom-left)
            r, c = r_q + i, c_q - i
            if 0 <= r <= 8 and 0 <= c <= 8:
                dominated.add((r, c))

    # Check if all 81 squares are dominated
    all_squares = {(r, c) for r in range(9) for c in range(9)}
    if len(dominated) != 81:
        missing = sorted(list(all_squares - dominated))
        return {
            "valid": False,
            "message": f"Not all 81 squares are dominated. Missing {len(missing)} squares: {missing[:10]}"
        }

    # Check optimality
    if len(queens) != EXPECTED_OPTIMAL_QUEENS:
        return {
            "valid": False,
            "message": f"Not optimal: {len(queens)} queens used, expected {EXPECTED_OPTIMAL_QUEENS}"
        }

    return {
        "valid": True,
        "message": f"Valid and optimal solution with {EXPECTED_OPTIMAL_QUEENS} queens dominating all 81 squares on 9x9 board"
    }

def main():
    """Main entry point for verification."""
    solution_json = sys.stdin.read()
    result = verify_solution(solution_json)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
