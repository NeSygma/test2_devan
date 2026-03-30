#!/usr/bin/env python3
"""
Reference model for Clique Finding problem
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
    required_fields = ["clique", "clique_size", "clique_edges"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    clique = solution["clique"]
    clique_size = solution["clique_size"]
    clique_edges = solution["clique_edges"]

    # Validate types
    if not isinstance(clique, list):
        return {"valid": False, "message": "clique must be an array"}
    if not isinstance(clique_size, int):
        return {"valid": False, "message": "clique_size must be an integer"}
    if not isinstance(clique_edges, list):
        return {"valid": False, "message": "clique_edges must be an array"}

    # Graph edges (undirected, stored as (min, max))
    edges = {(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (1, 4), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5), (4, 6), (5, 6)}

    # Validate vertices in clique
    for v in clique:
        if not isinstance(v, int):
            return {"valid": False, "message": f"Vertex {v} must be an integer"}
        if v not in range(7):
            return {"valid": False, "message": f"Invalid vertex {v}, must be 0-6"}

    # Check clique_size matches length
    if clique_size != len(clique):
        return {"valid": False, "message": f"clique_size {clique_size} doesn't match clique length {len(clique)}"}

    # Check no duplicates in clique
    if len(clique) != len(set(clique)):
        return {"valid": False, "message": "Duplicate vertices in clique"}

    # Validate clique_edges format
    for i, edge in enumerate(clique_edges):
        if not isinstance(edge, list) or len(edge) != 2:
            return {"valid": False, "message": f"Edge {i} must be array of length 2"}
        u, v = edge
        if not isinstance(u, int) or not isinstance(v, int):
            return {"valid": False, "message": f"Edge {i} vertices must be integers"}
        if u >= v:
            return {"valid": False, "message": f"Edge {i} must be formatted as [min, max]: got {edge}"}

    # Expected number of edges in a clique of size k is k(k-1)/2
    expected_edge_count = clique_size * (clique_size - 1) // 2
    if len(clique_edges) != expected_edge_count:
        return {"valid": False, "message": f"Expected {expected_edge_count} edges for clique of size {clique_size}, got {len(clique_edges)}"}

    # Generate expected edges within the clique
    clique_set = set(clique)
    expected_clique_edges = set()
    for i, u in enumerate(clique):
        for v in clique[i+1:]:
            min_v, max_v = min(u, v), max(u, v)
            expected_clique_edges.add((min_v, max_v))

    # Convert clique_edges to set for comparison
    actual_clique_edges = {(u, v) for u, v in clique_edges}

    # Check that all clique edges are provided
    if actual_clique_edges != expected_clique_edges:
        missing = expected_clique_edges - actual_clique_edges
        extra = actual_clique_edges - expected_clique_edges
        msg_parts = []
        if missing:
            msg_parts.append(f"Missing clique edges: {missing}")
        if extra:
            msg_parts.append(f"Extra clique edges: {extra}")
        return {"valid": False, "message": "; ".join(msg_parts)}

    # Verify that all clique edges exist in the graph
    for u, v in actual_clique_edges:
        if (u, v) not in edges:
            return {"valid": False, "message": f"Edge ({u}, {v}) in clique but not in graph"}

    # Check optimality - the maximum clique size for this graph is 4
    # (vertices 0, 1, 2, 3 form a clique of size 4)
    optimal_size = 4
    is_optimal = clique_size == optimal_size

    if is_optimal:
        return {"valid": True, "message": f"Valid and optimal clique with {clique_size} vertices"}
    else:
        return {"valid": False, "message": f"Valid but suboptimal clique. Size {clique_size}, optimal is {optimal_size}"}

def main():
    """Main entry point for verification."""
    solution_json = sys.stdin.read()
    result = verify_solution(solution_json)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
