#!/usr/bin/env python3
"""
Reference model for Queens Domination problem
Validates solutions from stdin only.
"""

import json
import sys

def verify_solution(solution: dict) -> dict:
    """
    Verify if the given solution satisfies all problem constraints.

    Args:
        solution: Parsed JSON solution dictionary

    Returns:
        dict with keys:
        - valid: bool (True if solution is valid)
        - message: str (explanation)
    """

    # Check required fields
    required_fields = ["queens", "num_queens", "dominated_squares"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    queens = solution["queens"]
    num_queens = solution["num_queens"]
    dominated_squares = solution["dominated_squares"]

    # Validate types
    if not isinstance(queens, list):
        return {"valid": False, "message": "queens must be an array"}
    if not isinstance(num_queens, int):
        return {"valid": False, "message": "num_queens must be an integer"}
    if not isinstance(dominated_squares, list):
        return {"valid": False, "message": "dominated_squares must be an array"}

    # Check num_queens consistency
    if num_queens != len(queens):
        return {"valid": False, "message": f"num_queens {num_queens} doesn't match queens length {len(queens)}"}

    # Validate queen positions
    queen_positions = set()
    for i, queen in enumerate(queens):
        if not isinstance(queen, list) or len(queen) != 2:
            return {"valid": False, "message": f"Queen {i} must be array of length 2"}

        row, col = queen
        if not isinstance(row, int) or not isinstance(col, int):
            return {"valid": False, "message": f"Queen {i} coordinates must be integers"}
        if row not in range(8) or col not in range(8):
            return {"valid": False, "message": f"Queen {i} position ({row}, {col}) out of bounds"}

        pos = (row, col)
        if pos in queen_positions:
            return {"valid": False, "message": f"Duplicate queen at position ({row}, {col})"}
        queen_positions.add(pos)

    # Calculate actual dominated squares
    def get_dominated_squares(queen_positions):
        dominated = set()
        for row, col in queen_positions:
            # Add queen's own square
            dominated.add((row, col))

            # Add row
            for c in range(8):
                dominated.add((row, c))

            # Add column
            for r in range(8):
                dominated.add((r, col))

            # Add diagonals
            # Main diagonal (top-left to bottom-right)
            for i in range(-7, 8):
                r, c = row + i, col + i
                if 0 <= r < 8 and 0 <= c < 8:
                    dominated.add((r, c))

            # Anti-diagonal (top-right to bottom-left)
            for i in range(-7, 8):
                r, c = row + i, col - i
                if 0 <= r < 8 and 0 <= c < 8:
                    dominated.add((r, c))

        return dominated

    actual_dominated = get_dominated_squares(queen_positions)

    # Validate dominated_squares format
    dominated_squares_set = set()
    for i, square in enumerate(dominated_squares):
        if not isinstance(square, list) or len(square) != 2:
            return {"valid": False, "message": f"Dominated square {i} must be array of length 2"}

        row, col = square
        if not isinstance(row, int) or not isinstance(col, int):
            return {"valid": False, "message": f"Dominated square {i} coordinates must be integers"}
        if row not in range(8) or col not in range(8):
            return {"valid": False, "message": f"Dominated square {i} position ({row}, {col}) out of bounds"}

        dominated_squares_set.add((row, col))

    # Check if all squares are dominated
    all_squares = {(r, c) for r in range(8) for c in range(8)}
    if actual_dominated != all_squares:
        missing = all_squares - actual_dominated
        return {"valid": False, "message": f"Not all squares dominated. Missing: {sorted(list(missing))[:10]}"}

    # Check if dominated_squares matches actual domination
    if dominated_squares_set != actual_dominated:
        return {"valid": False, "message": "dominated_squares doesn't match actual domination pattern"}

    # Check optimality - minimum domination number for 8x8 is 5
    optimal_num_queens = 5

    if num_queens == optimal_num_queens:
        return {"valid": True, "message": f"Valid and optimal solution with {num_queens} queens"}
    else:
        return {"valid": True, "message": f"Valid but suboptimal: {num_queens} queens (optimal is {optimal_num_queens})"}

def main():
    """Main entry point for verification."""
    try:
        solution_json = sys.stdin.read().strip()
        if not solution_json:
            print(json.dumps({"valid": False, "message": "No input provided"}))
            return

        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {e}"}))
        return

    result = verify_solution(solution)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
