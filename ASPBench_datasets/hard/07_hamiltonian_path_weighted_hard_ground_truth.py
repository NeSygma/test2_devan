#!/usr/bin/env python3
"""
Reference model (validation only) for Weighted Hamiltonian Path with forbidden edges.
Validates existence and structure of Hamiltonian paths from vertex 0 to vertex 99.
Enforces optimality - checks that path has minimal cost of 99.
"""

import json
import sys

# Expected optimal value
# The optimal path is the simple chain 0→1→2→...→99 (99 edges × weight 1 = 99)
EXPECTED_OPTIMAL_COST = 99

def validate_path_solution(solution):
    """Validate a Hamiltonian path solution from stdin."""
    # Check required fields
    if "paths" not in solution:
        return {"valid": False, "message": "Missing 'paths' field"}

    if "exists" not in solution:
        return {"valid": False, "message": "Missing 'exists' field"}

    paths = solution["paths"]
    exists = solution["exists"]

    # If exists is False, we expect empty paths
    if not exists:
        if len(paths) == 0:
            return {"valid": True, "message": "Correctly reported no path exists"}
        else:
            return {"valid": False, "message": "exists=False but paths provided"}

    # If exists is True, must have at least one path
    if len(paths) == 0:
        return {"valid": False, "message": "exists=True but no paths provided"}

    # Build the graph structure (edges and forbidden edges)
    edges = {}  # (x, y) -> weight

    # Chain edges (weight 1)
    for x in range(99):
        edges[(x, x+1)] = 1

    # Swap gadgets (weight 3)
    for n in range(24):
        b = 2 + 4*n
        edges[(b, b+2)] = 3
        edges[(b+2, b+1)] = 3
        edges[(b+1, b+3)] = 3

    # Skips of length 2 (weight 4)
    for n in range(25):
        s = 4*n
        if s + 2 <= 99:
            edges[(s, s+2)] = 4

    # Jumps of length 3 (weight 5)
    for n in range(24):
        t = 1 + 4*n
        edges[(t, t+3)] = 5

    # Long bridges (weight 6)
    for k in range(20):
        u = 5*k
        edges[(u, u+4)] = 6

    # Forbidden edges
    forbidden = set()
    forbidden.add((0, 2))
    forbidden.add((1, 3))

    for n in range(12):
        f = 2 + 8*n
        forbidden.add((f, f+2))

    for n in range(13):
        g = 8*n
        if g + 2 <= 99:
            forbidden.add((g, g+2))

    for n in range(12):
        h = 1 + 8*n
        forbidden.add((h, h+3))

    for m in range(10):
        l = 10*m + 5
        if l + 4 <= 99:
            forbidden.add((l, l+4))

    # Validate each path
    for i, path in enumerate(paths):
        # Check path length
        if len(path) != 100:
            return {"valid": False, "message": f"Path {i} has length {len(path)}, expected 100"}

        # Check start and end
        if path[0] != 0:
            return {"valid": False, "message": f"Path {i} doesn't start at vertex 0"}
        if path[-1] != 99:
            return {"valid": False, "message": f"Path {i} doesn't end at vertex 99"}

        # Check all vertices 0-99 appear exactly once
        if set(path) != set(range(100)):
            return {"valid": False, "message": f"Path {i} doesn't contain all vertices 0-99 exactly once"}

        # Check all edges are valid and not forbidden
        total_cost = 0
        for j in range(99):
            u, v = path[j], path[j+1]
            edge = (u, v)

            # Check edge exists
            if edge not in edges:
                return {"valid": False, "message": f"Path {i} contains invalid edge ({u}, {v})"}

            # Check edge not forbidden
            if edge in forbidden:
                return {"valid": False, "message": f"Path {i} uses forbidden edge ({u}, {v})"}

            total_cost += edges[edge]

        # Check optimality: path must have the expected optimal cost
        if total_cost != EXPECTED_OPTIMAL_COST:
            return {"valid": False, "message": f"Path {i} has cost {total_cost}, expected optimal cost {EXPECTED_OPTIMAL_COST}"}

    return {"valid": True, "message": f"All {len(paths)} Hamiltonian paths are valid and optimal (cost={EXPECTED_OPTIMAL_COST})"}


if __name__ == "__main__":
    # Read solution from stdin
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            print(json.dumps({"valid": False, "message": "No solution provided"}))
            sys.exit(0)

        solution = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {e}"}))
        sys.exit(0)

    # Validate solution
    result = validate_path_solution(solution)
    print(json.dumps(result))
