#!/usr/bin/env python3
"""
Reference model for Steiner Tree problem.
Validates tree structure and weight calculations.
"""

import json
import sys
from typing import List, Dict, Set, Tuple


def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def get_problem_setup():
    """Get the problem setup"""
    return {
        "vertices": list(range(7)),
        "edges": [
            (0, 1, 3), (0, 2, 5), (1, 3, 2), (1, 4, 4),
            (2, 3, 1), (2, 5, 6), (3, 4, 3), (3, 5, 3),
            (3, 6, 2), (4, 5, 2), (5, 6, 4)
        ],
        "terminals": [0, 5, 6]
    }


def build_adjacency_list(edges: List[Tuple[int, int, int]]) -> Dict[int, List[Tuple[int, int]]]:
    """Build adjacency list from edges"""
    adj = {}
    for v1, v2, weight in edges:
        if v1 not in adj:
            adj[v1] = []
        if v2 not in adj:
            adj[v2] = []
        adj[v1].append((v2, weight))
        adj[v2].append((v1, weight))
    return adj


def is_connected(vertices: Set[int], tree_edges: List[Dict]) -> bool:
    """Check if the given vertices form a connected component via tree edges"""
    if not vertices:
        return True

    if len(vertices) == 1:
        return True

    # Build adjacency from tree edges
    adj = {}
    for edge in tree_edges:
        v1, v2 = edge["from"], edge["to"]
        if v1 not in adj:
            adj[v1] = []
        if v2 not in adj:
            adj[v2] = []
        adj[v1].append(v2)
        adj[v2].append(v1)

    # DFS from any vertex in the set
    start = next(iter(vertices))
    visited = set()
    stack = [start]

    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v)

        if v in adj:
            for neighbor in adj[v]:
                if neighbor in vertices and neighbor not in visited:
                    stack.append(neighbor)

    return visited == vertices


def validate_tree_structure(tree_edges: List[Dict], vertices: Set[int]) -> Tuple[bool, str]:
    """Validate that edges form a tree"""

    n_vertices = len(vertices)
    n_edges = len(tree_edges)

    # Tree must have n-1 edges for n vertices
    if n_edges != n_vertices - 1:
        return False, f"Tree must have {n_vertices-1} edges for {n_vertices} vertices, got {n_edges}"

    # Check connectivity
    if not is_connected(vertices, tree_edges):
        return False, "Edges do not form a connected tree"

    return True, "Valid tree structure"


def validate_solution(solution: Dict) -> Tuple[bool, str]:
    """Validate the Steiner tree solution"""

    if not solution:
        return False, "No solution provided"

    required_fields = ["total_weight", "tree_edges", "steiner_vertices", "terminals", "connected_components"]
    for field in required_fields:
        if field not in solution:
            return False, f"Missing field: {field}"

    setup = get_problem_setup()
    all_edges = setup["edges"]
    terminals = setup["terminals"]

    # Build edge weight lookup
    edge_weights = {}
    for v1, v2, weight in all_edges:
        edge_weights[(min(v1, v2), max(v1, v2))] = weight

    # Validate tree edges
    tree_edges = solution["tree_edges"]
    used_vertices = set()
    total_weight = 0

    for edge in tree_edges:
        if not isinstance(edge, dict) or "from" not in edge or "to" not in edge or "weight" not in edge:
            return False, "Invalid edge format"

        v1, v2, weight = edge["from"], edge["to"], edge["weight"]
        edge_key = (min(v1, v2), max(v1, v2))

        # Check if edge exists in graph
        if edge_key not in edge_weights:
            return False, f"Edge ({v1}, {v2}) does not exist in the graph"

        # Check weight
        if weight != edge_weights[edge_key]:
            return False, f"Edge ({v1}, {v2}) has incorrect weight: expected {edge_weights[edge_key]}, got {weight}"

        used_vertices.add(v1)
        used_vertices.add(v2)
        total_weight += weight

    # Check total weight
    if solution["total_weight"] != total_weight:
        return False, f"Incorrect total weight: expected {total_weight}, got {solution['total_weight']}"

    # Check for optimal weight
    EXPECTED_OPTIMAL = 10
    if total_weight != EXPECTED_OPTIMAL:
        return False, f"Solution is not optimal: expected weight {EXPECTED_OPTIMAL}, got {total_weight}"

    # Check that all terminals are included
    for terminal in terminals:
        if terminal not in used_vertices:
            return False, f"Terminal {terminal} not included in the tree"

    # Validate steiner vertices
    expected_steiner = sorted([v for v in used_vertices if v not in terminals])
    if sorted(solution["steiner_vertices"]) != expected_steiner:
        return False, f"Incorrect Steiner vertices: expected {expected_steiner}, got {sorted(solution['steiner_vertices'])}"

    # Validate terminals
    if sorted(solution["terminals"]) != sorted(terminals):
        return False, f"Incorrect terminals: expected {sorted(terminals)}, got {sorted(solution['terminals'])}"

    # Validate tree structure
    is_valid_tree, tree_message = validate_tree_structure(tree_edges, used_vertices)
    if not is_valid_tree:
        return False, f"Invalid tree structure: {tree_message}"

    # Validate connected components
    if len(solution["connected_components"]) != 1:
        return False, "Steiner tree should have exactly one connected component"

    component = solution["connected_components"][0]
    if sorted(component["vertices"]) != sorted(list(used_vertices)):
        return False, "Connected component vertices do not match tree vertices"

    return True, f"Valid Steiner tree with optimal weight {total_weight}"


def main():
    """Main validation function"""
    solution = load_solution()

    if solution is None:
        result = {"valid": False, "message": "Invalid or missing JSON input"}
    else:
        is_valid, message = validate_solution(solution)
        result = {"valid": is_valid, "message": message}

    print(json.dumps(result))


if __name__ == "__main__":
    main()
