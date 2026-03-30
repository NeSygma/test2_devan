#!/usr/bin/env python3
"""
Reference model for Graph Isomorphism problem
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
    required_fields = ["is_isomorphic", "mapping", "preserved_edges"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    is_isomorphic = solution["is_isomorphic"]
    mapping = solution["mapping"]
    preserved_edges = solution["preserved_edges"]

    # Validate types
    if not isinstance(is_isomorphic, bool):
        return {"valid": False, "message": "is_isomorphic must be a boolean"}
    if mapping is not None and not isinstance(mapping, dict):
        return {"valid": False, "message": "mapping must be an object or null"}
    if not isinstance(preserved_edges, list):
        return {"valid": False, "message": "preserved_edges must be an array"}

    # Define graphs
    g1_vertices = {0, 1, 2, 3, 4}
    g1_edges = {(0, 1), (0, 2), (1, 3), (2, 4), (3, 4)}

    g2_vertices = {'a', 'b', 'c', 'd', 'e'}
    g2_edges = {('a', 'b'), ('a', 'c'), ('b', 'd'), ('c', 'e'), ('d', 'e')}

    # Normalize edges (smaller vertex first)
    def normalize_edge(u, v):
        return (min(u, v), max(u, v))

    g1_edges_norm = {normalize_edge(u, v) for u, v in g1_edges}
    g2_edges_norm = {normalize_edge(u, v) for u, v in g2_edges}

    # Check basic properties
    if len(g1_vertices) != len(g2_vertices):
        expected_iso = False
    elif len(g1_edges) != len(g2_edges):
        expected_iso = False
    else:
        # Check degree sequences
        def get_degree_sequence(vertices, edges):
            degrees = {}
            for v in vertices:
                degrees[v] = 0
            for u, v in edges:
                degrees[u] += 1
                degrees[v] += 1
            return sorted(degrees.values())

        g1_degrees = get_degree_sequence(g1_vertices, g1_edges)
        g2_degrees = get_degree_sequence(g2_vertices, g2_edges)
        expected_iso = g1_degrees == g2_degrees

    if not expected_iso:
        # Graphs are not isomorphic
        if is_isomorphic:
            return {"valid": False, "message": "Graphs are not isomorphic but is_isomorphic is true"}
        if mapping is not None:
            return {"valid": False, "message": "Graphs are not isomorphic but mapping is not null"}
        if preserved_edges:
            return {"valid": False, "message": "Graphs are not isomorphic but preserved_edges is not empty"}
        return {"valid": True, "message": "Correctly identified non-isomorphic graphs"}

    # Graphs should be isomorphic
    if not is_isomorphic:
        return {"valid": False, "message": "Graphs are isomorphic but is_isomorphic is false"}

    if mapping is None:
        return {"valid": False, "message": "Graphs are isomorphic but mapping is null"}

    # Validate mapping
    g1_str_vertices = {'0', '1', '2', '3', '4'}
    if set(mapping.keys()) != g1_str_vertices:
        return {"valid": False, "message": f"Mapping keys must be {g1_str_vertices}, got {set(mapping.keys())}"}

    if set(mapping.values()) != g2_vertices:
        return {"valid": False, "message": f"Mapping values must be {g2_vertices}, got {set(mapping.values())}"}

    # Check bijection
    if len(mapping.values()) != len(set(mapping.values())):
        return {"valid": False, "message": "Mapping is not a bijection (duplicate values)"}

    # Verify edge preservation
    mapped_edges = set()
    for u, v in g1_edges_norm:
        u_str, v_str = str(u), str(v)
        if u_str not in mapping or v_str not in mapping:
            return {"valid": False, "message": f"Edge ({u}, {v}) vertex not in mapping"}

        mapped_u, mapped_v = mapping[u_str], mapping[v_str]
        mapped_edge = normalize_edge(mapped_u, mapped_v)
        mapped_edges.add(mapped_edge)

    if mapped_edges != g2_edges_norm:
        return {"valid": False, "message": "Mapping does not preserve edges"}

    # Validate preserved_edges format
    # Normalize agent's output by parsing and sorting edge strings
    normalized_agent_edges = []
    for pair in preserved_edges:
        if not isinstance(pair, list) or len(pair) != 2:
            return {"valid": False, "message": "Each preserved_edge must be [g1_edge, g2_edge]"}

        g1_edge_str, g2_edge_str = pair

        # Parse and normalize G2 edge from agent output
        try:
            g2_parts = g2_edge_str.split(',')
            if len(g2_parts) != 2:
                return {"valid": False, "message": f"Invalid G2 edge format: {g2_edge_str}"}
            g2_u, g2_v = g2_parts[0].strip(), g2_parts[1].strip()
            # Normalize by sorting
            g2_normalized = f"{min(g2_u, g2_v)},{max(g2_u, g2_v)}"
        except Exception as e:
            return {"valid": False, "message": f"Error parsing G2 edge '{g2_edge_str}': {e}"}

        # Parse and normalize G1 edge
        try:
            g1_parts = g1_edge_str.split(',')
            if len(g1_parts) != 2:
                return {"valid": False, "message": f"Invalid G1 edge format: {g1_edge_str}"}
            g1_u, g1_v = g1_parts[0].strip(), g1_parts[1].strip()
            g1_normalized = f"{min(g1_u, g1_v)},{max(g1_u, g1_v)}"
        except Exception as e:
            return {"valid": False, "message": f"Error parsing G1 edge '{g1_edge_str}': {e}"}

        normalized_agent_edges.append([g1_normalized, g2_normalized])

    # Build expected edges with normalized format
    expected_preserved = []
    for u, v in sorted(g1_edges_norm):
        u_str, v_str = str(u), str(v)
        mapped_u, mapped_v = mapping[u_str], mapping[v_str]
        mapped_edge = normalize_edge(mapped_u, mapped_v)
        expected_preserved.append([f"{u},{v}", f"{mapped_edge[0]},{mapped_edge[1]}"])

    # Sort both for comparison
    expected_preserved.sort()
    normalized_agent_edges.sort()

    if normalized_agent_edges != expected_preserved:
        return {"valid": False, "message": f"preserved_edges incorrect. Expected {expected_preserved}, got {normalized_agent_edges}"}

    return {"valid": True, "message": "Valid graph isomorphism with correct mapping"}

def main():
    """Main entry point for verification."""
    solution_json = sys.stdin.read()

    result = verify_solution(solution_json)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
