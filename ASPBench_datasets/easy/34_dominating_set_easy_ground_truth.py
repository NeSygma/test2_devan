#!/usr/bin/env python3

import json
import sys

def validate_solution(solution):
    """Validate a minimum dominating set solution."""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    try:
        # Check required keys
        if "dominating_set" not in solution:
            return {"valid": False, "message": "Missing 'dominating_set' key"}
        if "size" not in solution:
            return {"valid": False, "message": "Missing 'size' key"}

        dominating_set = solution["dominating_set"]
        size = solution["size"]

        if not isinstance(dominating_set, list):
            return {"valid": False, "message": "dominating_set must be a list"}
        if not isinstance(size, int):
            return {"valid": False, "message": "size must be an integer"}

        # Graph definition
        vertices = {1, 2, 3, 4, 5, 6, 7}
        edges = [
            (1, 2), (1, 3),
            (2, 1), (2, 3), (2, 4),
            (3, 1), (3, 2), (3, 5),
            (4, 2), (4, 6),
            (5, 3), (5, 6), (5, 7),
            (6, 4), (6, 5), (6, 7),
            (7, 5), (7, 6)
        ]

        # Create adjacency list
        adj = {v: set() for v in vertices}
        for u, v in edges:
            adj[u].add(v)

        # Check vertices are valid
        dom_set = set(dominating_set)

        for vertex in dom_set:
            if vertex not in vertices:
                return {"valid": False, "message": f"Invalid vertex in dominating set: {vertex}"}

        # Check for duplicates
        if len(dominating_set) != len(dom_set):
            return {"valid": False, "message": "Dominating set contains duplicate vertices"}

        # Check size matches
        if size != len(dominating_set):
            return {"valid": False, "message": f"Size ({size}) doesn't match dominating set length ({len(dominating_set)})"}

        # Check domination - every vertex must be in the set or adjacent to a vertex in the set
        for vertex in vertices:
            if vertex not in dom_set:
                # Check if vertex is adjacent to any vertex in dominating set
                if not any(neighbor in dom_set for neighbor in adj[vertex]):
                    return {"valid": False, "message": f"Vertex {vertex} is not dominated"}

        # Check optimality - expected minimum size is 2
        if size != 2:
            return {"valid": False, "message": f"Solution has size {size}, but optimal size is 2"}

        return {"valid": True, "message": "Solution correct - minimum dominating set with optimal size 2"}

    except Exception as e:
        return {"valid": False, "message": f"Error validating solution: {e}"}

if __name__ == "__main__":
    try:
        data = sys.stdin.read().strip()
        if not data:
            result = {"valid": False, "message": "No solution provided"}
        else:
            solution = json.loads(data)
            result = validate_solution(solution)
    except json.JSONDecodeError as e:
        result = {"valid": False, "message": f"Invalid JSON: {e}"}

    print(json.dumps(result))
