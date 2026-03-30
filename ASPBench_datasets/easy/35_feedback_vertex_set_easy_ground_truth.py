#!/usr/bin/env python3
"""
Reference Model: Feedback Vertex Set Problem
===========================================
Validate solution from stdin.
"""

import sys
import json
from typing import Set, List, Tuple, Dict

def has_cycle_dfs(adj_list: Dict[int, List[int]], vertices: Set[int]) -> bool:
    """Check if graph has cycles using DFS with three colors."""
    # 0 = white (unvisited), 1 = gray (in current path), 2 = black (finished)
    color = {v: 0 for v in vertices}

    def dfs(v: int) -> bool:
        if color[v] == 1:  # Back edge found - cycle detected
            return True
        if color[v] == 2:  # Already processed
            return False

        color[v] = 1  # Mark as being processed

        # Visit all neighbors that still exist
        for neighbor in adj_list.get(v, []):
            if neighbor in vertices and dfs(neighbor):
                return True

        color[v] = 2  # Mark as finished
        return False

    # Check each unvisited vertex
    for v in vertices:
        if color[v] == 0 and dfs(v):
            return True
    return False

def find_minimum_feedback_set() -> int:
    """Compute minimum feedback set size."""
    vertices = {1, 2, 3, 4, 5, 6}
    edges = [
        (1, 2), (1, 3),
        (2, 4), (2, 5),
        (3, 4), (3, 6),
        (4, 2), (4, 5),
        (5, 3), (5, 6),
        (6, 1), (6, 4)
    ]

    # Build adjacency list
    adj_list = {}
    for u, v in edges:
        if u not in adj_list:
            adj_list[u] = []
        adj_list[u].append(v)

    # Try removing vertex sets of increasing size
    from itertools import combinations

    for k in range(len(vertices) + 1):
        for removal_set in combinations(vertices, k):
            remaining_vertices = vertices - set(removal_set)

            if not has_cycle_dfs(adj_list, remaining_vertices):
                return k

    return len(vertices)

def validate_solution():
    """Validate solution from stdin."""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return {"valid": False, "message": "No solution provided"}

        solution = json.loads(data)

        if "error" in solution:
            return {"valid": False, "message": "Solution contains error"}

        # Extract feedback set
        if "feedback_set" not in solution:
            return {"valid": False, "message": "Missing 'feedback_set' field"}

        feedback_set = set(solution["feedback_set"])

        # Problem instance
        vertices = {1, 2, 3, 4, 5, 6}
        edges = [
            (1, 2), (1, 3),
            (2, 4), (2, 5),
            (3, 4), (3, 6),
            (4, 2), (4, 5),
            (5, 3), (5, 6),
            (6, 1), (6, 4)
        ]

        # Check that all feedback vertices are valid
        if not feedback_set.issubset(vertices):
            return {"valid": False, "message": "Invalid vertex in feedback set"}

        # Build adjacency list
        adj_list = {}
        for u, v in edges:
            if u not in adj_list:
                adj_list[u] = []
            adj_list[u].append(v)

        # Check if removal makes graph acyclic
        remaining_vertices = vertices - feedback_set
        has_cycles = has_cycle_dfs(adj_list, remaining_vertices)

        if has_cycles:
            return {"valid": False, "message": "Remaining graph still contains cycles"}

        # Check optimality
        optimal_size = find_minimum_feedback_set()
        if len(feedback_set) != optimal_size:
            return {
                "valid": False,
                "message": f"Solution is not optimal: size {len(feedback_set)}, expected {optimal_size}"
            }

        return {
            "valid": True,
            "message": f"Solution is correct and optimal with size {len(feedback_set)}"
        }

    except json.JSONDecodeError:
        return {"valid": False, "message": "Invalid JSON input"}
    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}

if __name__ == "__main__":
    result = validate_solution()
    print(json.dumps(result))
