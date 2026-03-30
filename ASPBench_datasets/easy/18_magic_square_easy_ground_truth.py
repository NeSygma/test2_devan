#!/usr/bin/env python3
"""
Reference model for Magic Square problem.
Validates solution from stdin and outputs validation result.
"""
import json
import sys

def validate_solution(solution):
    """
    Validate a magic square solution.

    Args:
        solution: Dictionary with 'square', 'magic_sum', and 'valid' fields

    Returns:
        dict: Validation result with 'valid' and 'message' fields
    """
    if not solution:
        return {"valid": False, "message": "No solution provided"}

    # Check required fields
    if "square" not in solution:
        return {"valid": False, "message": "Missing 'square' field"}
    if "magic_sum" not in solution:
        return {"valid": False, "message": "Missing 'magic_sum' field"}
    if "valid" not in solution:
        return {"valid": False, "message": "Missing 'valid' field"}

    square = solution["square"]
    magic_sum = solution["magic_sum"]

    # Check if square is 3x3
    if not isinstance(square, list) or len(square) != 3:
        return {"valid": False, "message": "Square must be a 3x3 array"}

    for row in square:
        if not isinstance(row, list) or len(row) != 3:
            return {"valid": False, "message": "Square must be a 3x3 array"}

    # Check if magic_sum is 15
    if magic_sum != 15:
        return {"valid": False, "message": "Magic sum must be 15"}

    # Check if all numbers 1-9 are present exactly once
    numbers = []
    for row in square:
        for num in row:
            numbers.append(num)

    if sorted(numbers) != list(range(1, 10)):
        return {"valid": False, "message": "Square must contain numbers 1-9 exactly once"}

    # Check rows
    for i, row in enumerate(square):
        if sum(row) != magic_sum:
            return {"valid": False, "message": f"Row {i+1} sum is {sum(row)}, expected {magic_sum}"}

    # Check columns
    for col in range(3):
        col_sum = sum(square[row][col] for row in range(3))
        if col_sum != magic_sum:
            return {"valid": False, "message": f"Column {col+1} sum is {col_sum}, expected {magic_sum}"}

    # Check main diagonal
    main_diag_sum = sum(square[i][i] for i in range(3))
    if main_diag_sum != magic_sum:
        return {"valid": False, "message": f"Main diagonal sum is {main_diag_sum}, expected {magic_sum}"}

    # Check anti-diagonal
    anti_diag_sum = sum(square[i][2-i] for i in range(3))
    if anti_diag_sum != magic_sum:
        return {"valid": False, "message": f"Anti-diagonal sum is {anti_diag_sum}, expected {magic_sum}"}

    return {"valid": True, "message": "Valid magic square"}

def main():
    """Load solution from stdin and validate."""
    try:
        data = sys.stdin.read().strip()
        if not data:
            result = {"valid": False, "message": "No input provided"}
        else:
            solution = json.loads(data)
            result = validate_solution(solution)

        print(json.dumps(result))

    except json.JSONDecodeError as e:
        result = {"valid": False, "message": f"Invalid JSON: {str(e)}"}
        print(json.dumps(result))
        sys.exit(1)
    except Exception as e:
        result = {"valid": False, "message": f"Error: {str(e)}"}
        print(json.dumps(result))
        sys.exit(1)

if __name__ == "__main__":
    main()
