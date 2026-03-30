#!/usr/bin/env python3
"""
Reference model for Set Cover problem
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
    required_fields = ["selected_sets", "total_sets", "covered_elements"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    selected_sets = solution["selected_sets"]
    total_sets = solution["total_sets"]
    covered_elements = solution["covered_elements"]

    # Validate types
    if not isinstance(selected_sets, list):
        return {"valid": False, "message": "selected_sets must be an array"}
    if not isinstance(total_sets, int):
        return {"valid": False, "message": "total_sets must be an integer"}
    if not isinstance(covered_elements, list):
        return {"valid": False, "message": "covered_elements must be an array"}

    # Set definitions
    universe = {1, 2, 3, 4, 5, 6, 7, 8}
    sets_data = [
        {1, 2, 3},      # Set 0
        {2, 4, 5},      # Set 1
        {3, 6, 7},      # Set 2
        {1, 4, 8},      # Set 3
        {5, 6, 7, 8},   # Set 4
        {1, 2, 6}       # Set 5
    ]

    # Validate selected sets
    for s in selected_sets:
        if not isinstance(s, int):
            return {"valid": False, "message": f"Set index {s} must be an integer"}
        if s not in range(6):
            return {"valid": False, "message": f"Invalid set index {s}, must be 0-5"}

    # Check total_sets matches length
    if total_sets != len(selected_sets):
        return {"valid": False, "message": f"total_sets {total_sets} doesn't match selected_sets length {len(selected_sets)}"}

    # Check no duplicates in selected sets
    if len(selected_sets) != len(set(selected_sets)):
        return {"valid": False, "message": "Duplicate sets in selected_sets"}

    # Calculate actual coverage
    actual_covered = set()
    for s in selected_sets:
        actual_covered.update(sets_data[s])

    # Check covered elements
    expected_covered = sorted(list(actual_covered))
    if sorted(covered_elements) != expected_covered:
        return {"valid": False, "message": f"covered_elements mismatch. Expected: {expected_covered}, got: {sorted(covered_elements)}"}

    # Verify complete coverage
    if actual_covered != universe:
        missing = universe - actual_covered
        return {"valid": False, "message": f"Not all elements covered. Missing: {missing}"}

    # Check optimality
    optimal_size = 3
    if len(selected_sets) != optimal_size:
        return {"valid": False, "message": f"Solution is not optimal. Uses {len(selected_sets)} sets, optimal is {optimal_size}"}

    return {"valid": True, "message": f"Valid and optimal set cover with {len(selected_sets)} sets"}

def main():
    """Main entry point for verification."""
    content = sys.stdin.read().strip()

    if not content:
        print(json.dumps({"valid": False, "message": "No input provided"}))
        return

    result = verify_solution(content)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
