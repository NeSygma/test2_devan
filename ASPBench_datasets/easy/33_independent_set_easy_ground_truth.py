#!/usr/bin/env python3

import json
import sys

def validate_solution(solution):
    """Validate a maximum independent set solution."""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    try:
        # Parse JSON if it's a string
        if isinstance(solution, str):
            data = json.loads(solution)
        else:
            data = solution

        if "independent_set" not in data:
            return {"valid": False, "message": "Missing 'independent_set' key"}
        if "size" not in data:
            return {"valid": False, "message": "Missing 'size' key"}

        independent_set = data["independent_set"]
        size = data["size"]

        if not isinstance(independent_set, list):
            return {"valid": False, "message": "independent_set must be a list"}
        if not isinstance(size, int):
            return {"valid": False, "message": "size must be an integer"}

        # Graph definition
        vertices = {1, 2, 3, 4, 5, 6, 7, 8}
        edges = {
            (1, 2), (1, 3), (1, 4),
            (2, 1), (2, 5),
            (3, 1), (3, 6), (3, 7),
            (4, 1), (4, 8),
            (5, 2), (5, 6),
            (6, 3), (6, 5), (6, 7),
            (7, 3), (7, 6), (7, 8),
            (8, 4), (8, 7)
        }

        # Check vertices are valid
        ind_set = set(independent_set)

        for vertex in ind_set:
            if vertex not in vertices:
                return {"valid": False, "message": f"Invalid vertex in independent set: {vertex}"}

        # Check for duplicates
        if len(independent_set) != len(ind_set):
            return {"valid": False, "message": "Independent set contains duplicate vertices"}

        # Check size matches
        if size != len(independent_set):
            return {"valid": False, "message": f"Size ({size}) doesn't match independent set length ({len(independent_set)})"}

        # Check independence - no edges between vertices in the set
        for v1 in ind_set:
            for v2 in ind_set:
                if v1 != v2 and ((v1, v2) in edges or (v2, v1) in edges):
                    return {"valid": False, "message": f"Vertices {v1} and {v2} are connected, violating independence"}

        # Check optimality - the maximum independent set size is 3
        if size != 3:
            return {"valid": False, "message": f"Solution is not optimal. Expected size 3, got {size}"}

        return {"valid": True, "message": f"Solution is valid and optimal with size {size}"}

    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"valid": False, "message": f"Error validating solution: {e}"}

if __name__ == "__main__":
    # Read from stdin
    solution_text = sys.stdin.read().strip()

    if not solution_text:
        result = {"valid": False, "message": "No input provided"}
    else:
        result = validate_solution(solution_text)

    print(json.dumps(result))
