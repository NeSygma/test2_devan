#!/usr/bin/env python3
"""
Reference Model: Weighted Feedback Vertex Set
==============================================
Validates solutions for weighted feedback vertex set with protection,
groups, and conditional edges.
"""

import sys
import json
from typing import Set, List, Tuple, Dict

# Expected optimal value
EXPECTED_OPTIMAL_COST = 18

def load_solution():
    """Load solution from stdin."""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError as e:
        return None
    except Exception as e:
        return None

def has_cycle_dfs(adj_list: Dict[int, List[int]], vertices: Set[int]) -> bool:
    """Check if graph has cycles using DFS with three colors."""
    color = {v: 0 for v in vertices}

    def dfs(v: int) -> bool:
        if color[v] == 1:  # Back edge - cycle detected
            return True
        if color[v] == 2:  # Already processed
            return False

        color[v] = 1  # Mark as being processed

        for neighbor in adj_list.get(v, []):
            if neighbor in vertices and dfs(neighbor):
                return True

        color[v] = 2  # Mark as finished
        return False

    for v in vertices:
        if color[v] == 0 and dfs(v):
            return True
    return False

def validate_solution(solution: dict) -> dict:
    """Validate the feedback vertex set solution."""

    if solution is None:
        return {"valid": False, "message": "No solution provided"}

    if "error" in solution:
        return {"valid": False, "message": "Solution contains error"}

    # Extract solution
    try:
        feedback_set = set(solution["feedback_set"])
        costs = solution["costs"]
        total_cost = solution["total_cost"]
        remaining_vertices_sol = set(solution["remaining_vertices"])
    except KeyError as e:
        return {"valid": False, "message": f"Missing required field: {e}"}

    # Problem data
    all_vertices = set(range(1, 16))
    protected = {1, 15}

    vertex_costs = {
        1: 10, 2: 4, 3: 5, 4: 6, 5: 7, 6: 9, 7: 8,
        8: 2, 9: 4, 10: 3, 11: 5, 12: 7, 13: 6, 14: 6, 15: 12
    }

    groups = [
        {2, 3, 4},   # Group A
        {5, 6, 7},   # Group B
        {8, 9, 10},  # Group C
        {11, 12, 13}, # Group D
        {14}         # Group E
    ]

    # Core edges (always present)
    core_edges = [
        (1, 2), (1, 5), (1, 8),
        (2, 3), (3, 4), (4, 2),  # Cycle in group A
        (5, 6), (6, 7), (7, 5),  # Cycle in group B
        (8, 9), (9, 10), (10, 8), # Cycle in group C
        (11, 12), (12, 13), (13, 11), # Cycle in group D
        (2, 11), (4, 14), (7, 14), (10, 15),
        (14, 1)
    ]

    # Check 1: Protected vertices not removed
    if feedback_set & protected:
        return {"valid": False, "message": f"Protected vertices cannot be removed: {feedback_set & protected}"}

    # Check 2: At most one vertex per group removed
    for i, group in enumerate(groups):
        removed_from_group = feedback_set & group
        if len(removed_from_group) > 1:
            return {"valid": False, "message": f"Group {chr(65+i)} has {len(removed_from_group)} vertices removed (max 1): {removed_from_group}"}

    # Check 3: Cost calculation
    # Costs should match the feedback_set order
    expected_costs = [vertex_costs[v] for v in solution["feedback_set"]]
    if costs != expected_costs:
        return {"valid": False, "message": f"Costs mismatch: expected {expected_costs} for vertices {solution['feedback_set']}, got {costs}"}

    expected_total = sum(vertex_costs[v] for v in feedback_set)
    if total_cost != expected_total:
        return {"valid": False, "message": f"Total cost mismatch: expected {expected_total}, got {total_cost}"}

    # Check 4: Remaining vertices correct
    expected_remaining = all_vertices - feedback_set
    if remaining_vertices_sol != expected_remaining:
        return {"valid": False, "message": f"Remaining vertices mismatch"}

    # Check 5: Build remaining graph with conditional edges
    remaining = all_vertices - feedback_set

    # Start with core edges
    adj_list = {}
    for u, v in core_edges:
        if u in remaining and v in remaining:
            if u not in adj_list:
                adj_list[u] = []
            adj_list[u].append(v)

    # Add conditional edges (only if source vertex remains)
    conditional_edges = [
        (3, 7), (3, 11),   # If 3 remains
        (6, 10), (6, 13),  # If 6 remains
        (9, 13), (9, 14),  # If 9 remains
        (12, 4), (12, 7)   # If 12 remains
    ]

    for u, v in conditional_edges:
        if u in remaining and v in remaining:
            if u not in adj_list:
                adj_list[u] = []
            adj_list[u].append(v)

    # Check 6: Remaining graph is acyclic
    if has_cycle_dfs(adj_list, remaining):
        return {"valid": False, "message": "Remaining graph still contains cycles"}

    # Check optimality
    if total_cost != EXPECTED_OPTIMAL_COST:
        return {"valid": False, "message": f"Not optimal: total_cost={total_cost}, expected {EXPECTED_OPTIMAL_COST}"}

    return {
        "valid": True,
        "message": f"Solution valid and optimal (total_cost={EXPECTED_OPTIMAL_COST})"
    }

if __name__ == "__main__":
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))
