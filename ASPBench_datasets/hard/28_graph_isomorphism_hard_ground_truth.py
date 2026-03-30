#!/usr/bin/env python3
"""
Reference model for the Graph Isomorphism problem.
Used for solution verification only.
"""

import json
import sys
from collections import defaultdict

def get_graphs():
    """Returns the definition of G1 and G2."""
    g1 = {
        "vertices": {str(i) for i in range(1, 9)},
        "colors": {"1": "red", "2": "red", "5": "red", "6": "red", "3": "blue", "4": "blue", "7": "blue", "8": "blue"},
        "special": {"1"},
        "edges": {
            ("1", "3", 10), ("1", "4", 20), ("2", "3", 20), ("2", "4", 10),
            ("5", "7", 10), ("5", "8", 20), ("6", "7", 20), ("6", "8", 10),
            ("1", "5", 30), ("2", "6", 30), ("3", "7", 40), ("4", "8", 40)
        }
    }
    g2 = {
        "vertices": {chr(ord('a') + i) for i in range(8)},
        "colors": {"a": "red", "b": "red", "e": "red", "f": "red", "c": "blue", "d": "blue", "g": "blue", "h": "blue"},
        "special": {"a"},
        "edges": {
            ("a", "c", 10), ("a", "d", 20), ("b", "c", 20), ("b", "d", 10),
            ("e", "g", 10), ("e", "h", 20), ("f", "g", 20), ("f", "h", 10),
            ("a", "e", 30), ("b", "f", 30), ("c", "g", 40), ("d", "h", 40)
        }
    }

    def normalize_edges(edges):
        return {tuple(sorted((u, v)) + [w]) for u, v, w in edges}

    g1["edges_norm"] = normalize_edges(g1["edges"])
    g2["edges_norm"] = normalize_edges(g2["edges"])

    # Adjacency list for G2 for cycle checking
    g2["adj"] = defaultdict(list)
    for u, v, w in g2["edges"]:
        g2["adj"][u].append((v, w))
        g2["adj"][v].append((u, w))

    return g1, g2

def verify_solution(solution_json: str) -> dict:
    """Verify if the given solution satisfies all problem constraints."""
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    g1, g2 = get_graphs()
    is_isomorphic = solution.get("is_isomorphic")
    mapping = solution.get("mapping")

    # For this problem, an isomorphism exists.
    if not is_isomorphic:
        return {"valid": False, "message": "Graphs are isomorphic, but is_isomorphic is false."}
    if not mapping:
        return {"valid": False, "message": "Graphs are isomorphic, but mapping is null."}

    # 1. Verify bijection
    if set(mapping.keys()) != g1["vertices"]:
        return {"valid": False, "message": f"Mapping keys must be G1 vertices. Got {set(mapping.keys())}"}
    if set(mapping.values()) != g2["vertices"]:
        return {"valid": False, "message": f"Mapping values must be G2 vertices. Got {set(mapping.values())}"}
    if len(set(mapping.values())) != len(g2["vertices"]):
        return {"valid": False, "message": "Mapping is not a bijection (values are not unique)."}

    # 2. Verify color preservation
    for v1, v2 in mapping.items():
        if g1["colors"][v1] != g2["colors"][v2]:
            return {"valid": False, "message": f"Color mismatch for mapping {v1}->{v2}. Expected {g1['colors'][v1]}, got {g2['colors'][v2]}."}

    # 3. Verify special vertex preservation
    for v1 in g1["vertices"]:
        is_special1 = v1 in g1["special"]
        is_special2 = mapping[v1] in g2["special"]
        if is_special1 != is_special2:
            return {"valid": False, "message": f"Special property mismatch for mapping {v1}->{mapping[v1]}."}

    # 4. Verify edge and weight preservation
    mapped_edges_norm = set()
    for u1, v1, w in g1["edges_norm"]:
        u2, v2 = mapping[u1], mapping[v1]
        mapped_edge = tuple(sorted((u2, v2)) + [w])
        if mapped_edge not in g2["edges_norm"]:
            return {"valid": False, "message": f"Edge ({u1},{v1},{w}) maps to ({u2},{v2},{w}), which does not exist in G2."}
        mapped_edges_norm.add(mapped_edge)

    if mapped_edges_norm != g2["edges_norm"]:
        return {"valid": False, "message": "Edge mapping is not complete. Not all G2 edges are covered."}

    # 5. Verify forbidden subgraph constraint
    special1_mapped = {mapping[s1] for s1 in g1["special"]}
    for s2 in special1_mapped:
        # Find 3-cycles involving s2 in G2
        for v2, w1 in g2["adj"][s2]:
            for u2, w2 in g2["adj"][v2]:
                if u2 == s2: continue # Avoid 2-cycles
                # Check if (u2, s2) is an edge to close the triangle
                for neighbor_of_u2, w3 in g2["adj"][u2]:
                    if neighbor_of_u2 == s2:
                        if w1 + w2 + w3 == 60:
                            return {"valid": False, "message": f"Forbidden 3-cycle {s2}-{v2}-{u2} found with total weight 60."}

    # 6. Verify preserved_weighted_edges format
    preserved_edges = solution.get("preserved_weighted_edges", [])
    expected_preserved = []
    for u1, v1, w in sorted(list(g1["edges_norm"])):
        u2, v2 = mapping[u1], mapping[v1]
        u2_s, v2_s = sorted((u2,v2))
        expected_preserved.append([[u1, v1, w], [u2_s, v2_s, w]])

    # Sort for comparison
    preserved_edges_sorted = sorted(preserved_edges, key=lambda x: (x[0][0], x[0][1]))

    if len(preserved_edges_sorted) != len(expected_preserved):
         return {"valid": False, "message": "Incorrect number of edges in preserved_weighted_edges."}

    if preserved_edges_sorted != expected_preserved:
        return {"valid": False, "message": "preserved_weighted_edges format or content is incorrect."}


    return {"valid": True, "message": "Valid isomorphism: bijection, color, special, and edge/weight preservation confirmed, and no forbidden subgraphs found."}

def main():
    """Main entry point for verification."""
    solution_json = sys.stdin.read()
    result = verify_solution(solution_json)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
