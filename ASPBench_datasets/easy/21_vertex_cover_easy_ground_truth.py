#!/usr/bin/env python3
"""
Reference model for Vertex Cover problem
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
    required_fields = ["vertex_cover", "cover_size", "covered_edges"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    vertex_cover = solution["vertex_cover"]
    cover_size = solution["cover_size"]
    covered_edges = solution["covered_edges"]

    # Validate types
    if not isinstance(vertex_cover, list):
        return {"valid": False, "message": "vertex_cover must be an array"}
    if not isinstance(cover_size, int):
        return {"valid": False, "message": "cover_size must be an integer"}
    if not isinstance(covered_edges, list):
        return {"valid": False, "message": "covered_edges must be an array"}

    # Graph edges
    edges = {(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5), (1, 5)}

    # Validate vertices in cover
    for v in vertex_cover:
        if not isinstance(v, int):
            return {"valid": False, "message": f"Vertex {v} must be an integer"}
        if v not in range(6):
            return {"valid": False, "message": f"Invalid vertex {v}, must be 0-5"}

    # Check cover_size matches length
    if cover_size != len(vertex_cover):
        return {"valid": False, "message": f"cover_size {cover_size} doesn't match vertex_cover length {len(vertex_cover)}"}

    # Check no duplicates in vertex cover
    if len(vertex_cover) != len(set(vertex_cover)):
        return {"valid": False, "message": "Duplicate vertices in vertex_cover"}

    # Validate covered_edges format
    for i, edge in enumerate(covered_edges):
        if not isinstance(edge, list) or len(edge) != 2:
            return {"valid": False, "message": f"Edge {i} must be array of length 2"}
        u, v = edge
        if not isinstance(u, int) or not isinstance(v, int):
            return {"valid": False, "message": f"Edge {i} vertices must be integers"}
        if u >= v:
            return {"valid": False, "message": f"Edge {i} must be formatted as [min, max]: got {edge}"}

    # Convert covered_edges to set for comparison
    covered_edges_set = {(u, v) for u, v in covered_edges}

    # Check all edges are covered
    if covered_edges_set != edges:
        missing = edges - covered_edges_set
        extra = covered_edges_set - edges
        msg_parts = []
        if missing:
            msg_parts.append(f"Missing edges: {missing}")
        if extra:
            msg_parts.append(f"Extra edges: {extra}")
        return {"valid": False, "message": "; ".join(msg_parts)}

    # Verify that the vertex cover actually covers all edges
    vertex_set = set(vertex_cover)
    for u, v in edges:
        if u not in vertex_set and v not in vertex_set:
            return {"valid": False, "message": f"Edge ({u}, {v}) not covered by vertex cover"}

    # Check optimality - the minimum vertex cover size for this graph is 3
    optimal_size = 3

    if cover_size == optimal_size:
        return {"valid": True, "message": f"Valid and optimal vertex cover with {cover_size} vertices"}
    else:
        return {"valid": False, "message": f"Suboptimal solution: uses {cover_size} vertices, optimal is {optimal_size}"}

def main():
    """Main entry point for verification."""
    solution_json = sys.stdin.read().strip()

    if not solution_json:
        print(json.dumps({"valid": False, "message": "No input provided"}))
        return

    result = verify_solution(solution_json)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
