#!/usr/bin/env python3
"""
Reference model for Graph Coloring problem
Used for solution verification only.
"""

import json
import sys

def verify_solution(solution_json: str) -> dict:
    """
    Verify if the given solution satisfies all graph coloring constraints.

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
    if "num_colors" not in solution:
        return {"valid": False, "message": "Missing required field: num_colors"}
    if "coloring" not in solution:
        return {"valid": False, "message": "Missing required field: coloring"}

    num_colors = solution["num_colors"]
    coloring = solution["coloring"]

    # Validate num_colors
    if not isinstance(num_colors, int) or num_colors < 1:
        return {"valid": False, "message": f"Invalid num_colors: {num_colors}. Must be positive integer"}

    # Validate coloring array
    if len(coloring) != 6:
        return {"valid": False, "message": f"Coloring must have exactly 6 vertices, got {len(coloring)}"}

    # Graph structure (edges)
    edges = [
        (1, 2), (1, 3),
        (2, 3), (2, 4),
        (3, 4), (3, 5),
        (4, 5), (4, 6),
        (5, 6)
    ]

    # Build vertex color mapping
    vertex_colors = {}
    for item in coloring:
        if "vertex" not in item or "color" not in item:
            return {"valid": False, "message": "Each coloring item must have 'vertex' and 'color' fields"}

        v = item["vertex"]
        c = item["color"]

        # Validate vertex
        if v not in range(1, 7):
            return {"valid": False, "message": f"Invalid vertex: {v}. Must be 1-6"}

        # Validate color
        if c not in range(1, num_colors + 1):
            return {"valid": False, "message": f"Invalid color {c} for vertex {v}. Must be 1-{num_colors}"}

        if v in vertex_colors:
            return {"valid": False, "message": f"Vertex {v} appears multiple times"}

        vertex_colors[v] = c

    # Check all vertices are colored
    if len(vertex_colors) != 6:
        return {"valid": False, "message": "Not all vertices are colored"}

    # Check edge constraints: adjacent vertices must have different colors
    for v1, v2 in edges:
        if vertex_colors[v1] == vertex_colors[v2]:
            return {"valid": False, "message": f"Adjacent vertices {v1} and {v2} have the same color {vertex_colors[v1]}"}

    # Check symmetry: edges work both ways
    for v1, v2 in edges:
        if vertex_colors[v2] == vertex_colors[v1]:
            # Already checked above, but verify both directions
            pass

    # Check if optimal (chromatic number for this graph is 3)
    optimal = (num_colors == 3)

    if optimal:
        return {
            "valid": True,
            "message": f"Valid and optimal coloring with {num_colors} colors"
        }
    else:
        return {
            "valid": True,
            "message": f"Valid but suboptimal: uses {num_colors} colors (optimal is 3)"
        }

if __name__ == "__main__":
    solution_json = sys.stdin.read()
    result = verify_solution(solution_json)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)
