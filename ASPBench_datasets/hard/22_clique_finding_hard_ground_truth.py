#!/usr/bin/env python3
"""
Reference model for Extreme Hard Clique Finding problem.
UPDATED: Now enforces optimality - checks that clique has maximal size.
"""

import json
import sys
from collections import Counter

# Expected optimal value (extracted from reference solution)
# Maximum clique size with constraints is 6
EXPECTED_OPTIMAL_SIZE = 6

# --- Ground Truth Data ---
VERTICES = {
    v: {'type': t, 'weight': w} for v, t, w in [
        (0, 'alpha', 20), (1, 'alpha', 20), (2, 'alpha', 15), (3, 'alpha', 20),
        (4, 'beta', 30), (5, 'alpha', 15), (6, 'beta', 30), (7, 'beta', 30),
        (8, 'beta', 18), (9, 'delta', 10), (10, 'delta', 10), (11, 'beta', 12),
        (12, 'gamma', 25), (13, 'gamma', 25), (14, 'gamma', 20), (15, 'delta', 5),
        (16, 'delta', 5), (17, 'gamma', 19), (18, 'alpha', 40), (19, 'beta', 40)
    ]
}

EDGES = {
    (2, 5), (2, 8), (2, 11), (2, 14), (2, 17), (5, 8), (5, 11), (5, 14), (5, 17),
    (8, 11), (8, 14), (8, 17), (11, 14), (11, 17), (14, 17),
    (0, 1), (0, 3), (0, 4), (0, 6), (0, 7), (0, 9), (1, 3), (1, 4), (1, 6),
    (1, 7), (1, 9), (3, 4), (3, 6), (3, 7), (3, 9), (4, 6), (4, 7), (4, 9),
    (6, 7), (6, 9), (7, 9),
    (2, 18), (5, 19), (12, 13), (15, 16), (0, 10)
}

# --- Constraint Constants ---
MAX_WEIGHT = 100
MAX_PER_TYPE = 2

def verify_solution(solution_json: str) -> dict:
    """
    Verify if the given solution satisfies all problem constraints.
    Checks for feasibility only, not optimality.
    """
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    required_fields = ["clique", "clique_size", "clique_edges", "clique_total_weight", "clique_type_distribution"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    clique = solution["clique"]
    clique_size = solution["clique_size"]
    clique_edges = solution["clique_edges"]
    total_weight = solution["clique_total_weight"]
    type_dist = solution["clique_type_distribution"]

    # --- Basic Validation ---
    if not isinstance(clique, list) or clique_size != len(clique):
        return {"valid": False, "message": "clique_size does not match length of clique array"}
    if len(clique) != len(set(clique)):
        return {"valid": False, "message": "Duplicate vertices in clique"}

    # --- Property Calculation and Verification ---
    # Recalculate properties from the ground truth to verify solution's claims
    try:
        actual_weight = sum(VERTICES[v]['weight'] for v in clique)
        actual_type_dist = Counter(VERTICES[v]['type'] for v in clique)
    except KeyError as e:
        return {"valid": False, "message": f"Invalid vertex {e} found in clique"}

    if total_weight != actual_weight:
        return {"valid": False, "message": f"Incorrect clique_total_weight. Stated: {total_weight}, actual: {actual_weight}"}

    if dict(actual_type_dist) != type_dist:
        return {"valid": False, "message": f"Incorrect clique_type_distribution. Stated: {type_dist}, actual: {dict(actual_type_dist)}"}

    # --- Constraint Checking ---
    # 1. Weight Constraint
    if total_weight > MAX_WEIGHT:
        return {"valid": False, "message": f"Weight limit exceeded. Limit: {MAX_WEIGHT}, got: {total_weight}"}

    # 2. Type Diversity Constraint
    for type_name, count in type_dist.items():
        if count > MAX_PER_TYPE:
            return {"valid": False, "message": f"Type diversity violated for '{type_name}'. Limit: {MAX_PER_TYPE}, got: {count}"}

    # 3. Clique Property Constraint
    for i in range(len(clique)):
        for j in range(i + 1, len(clique)):
            u, v = clique[i], clique[j]
            if tuple(sorted((u, v))) not in EDGES:
                return {"valid": False, "message": f"Clique property violated. Edge ({u}, {v}) is missing from the graph."}

    # 4. Edge List Correctness
    expected_edge_count = clique_size * (clique_size - 1) // 2
    if len(clique_edges) != expected_edge_count:
        return {"valid": False, "message": f"Incorrect number of edges. Expected {expected_edge_count}, got {len(clique_edges)}"}

    expected_edges = set()
    for i in range(len(clique)):
        for j in range(i + 1, len(clique)):
            expected_edges.add(tuple(sorted((clique[i], clique[j]))))

    actual_edges = {tuple(sorted(edge)) for edge in clique_edges}

    if expected_edges != actual_edges:
        return {"valid": False, "message": "Field 'clique_edges' does not match the edges implied by 'clique'"}

    # Check optimality
    if clique_size != EXPECTED_OPTIMAL_SIZE:
        return {"valid": False, "message": f"Not optimal: clique_size={clique_size}, expected {EXPECTED_OPTIMAL_SIZE}"}

    return {"valid": True, "message": f"Solution is valid and optimal (clique_size={EXPECTED_OPTIMAL_SIZE})"}


def main():
    """Main entry point for verification."""
    try:
        solution_json = sys.stdin.read()
        result = verify_solution(solution_json)
    except Exception as e:
        result = {"valid": False, "message": f"An unexpected error occurred: {e}"}

    print(json.dumps(result))

if __name__ == "__main__":
    main()
