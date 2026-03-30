#!/usr/bin/env python3
"""
Reference model for Graph Partitioning problem.
Validates balanced partitioning and cut size calculations.
"""

import json
import sys
from typing import List, Dict, Tuple


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
        "vertices": list(range(8)),
        "edges": [
            (0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (2, 6),
            (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)
        ],
        "target_partition_size": 4
    }


def calculate_cut_size(partition_1: List[int], partition_2: List[int], edges: List[Tuple[int, int]]) -> Tuple[int, List[Dict]]:
    """Calculate the cut size and cut edges"""

    set1 = set(partition_1)
    set2 = set(partition_2)

    cut_edges = []
    cut_size = 0

    for v1, v2 in edges:
        # Edge crosses partition boundary
        if (v1 in set1 and v2 in set2) or (v1 in set2 and v2 in set1):
            cut_edges.append({"from": min(v1, v2), "to": max(v1, v2)})
            cut_size += 1

    return cut_size, cut_edges


def validate_solution(solution: Dict) -> Tuple[bool, str]:
    """Validate the graph partitioning solution"""

    if not solution:
        return False, "No solution provided"

    required_fields = ["partition_1", "partition_2", "cut_size", "cut_edges", "balance"]
    for field in required_fields:
        if field not in solution:
            return False, f"Missing field: {field}"

    setup = get_problem_setup()
    all_vertices = set(setup["vertices"])
    edges = setup["edges"]
    target_size = setup["target_partition_size"]

    partition_1 = solution["partition_1"]
    partition_2 = solution["partition_2"]

    # Validate partition sizes
    if len(partition_1) != target_size:
        return False, f"Partition 1 has {len(partition_1)} vertices, expected {target_size}"

    if len(partition_2) != target_size:
        return False, f"Partition 2 has {len(partition_2)} vertices, expected {target_size}"

    # Validate partition vertices
    set1 = set(partition_1)
    set2 = set(partition_2)

    # Check for duplicates within partitions
    if len(set1) != len(partition_1):
        return False, "Partition 1 contains duplicate vertices"

    if len(set2) != len(partition_2):
        return False, "Partition 2 contains duplicate vertices"

    # Check partitions are disjoint
    if set1 & set2:
        return False, f"Partitions overlap: {sorted(set1 & set2)}"

    # Check all vertices are covered
    if set1 | set2 != all_vertices:
        missing = all_vertices - (set1 | set2)
        extra = (set1 | set2) - all_vertices
        return False, f"Vertex coverage error. Missing: {sorted(missing)}, Extra: {sorted(extra)}"

    # Validate balance information
    balance = solution["balance"]
    expected_balance = {
        "partition_1_size": len(partition_1),
        "partition_2_size": len(partition_2),
        "is_balanced": len(partition_1) == len(partition_2) == target_size
    }

    for key, expected_value in expected_balance.items():
        if balance.get(key) != expected_value:
            return False, f"Incorrect balance.{key}: expected {expected_value}, got {balance.get(key)}"

    # Calculate and validate cut size
    expected_cut_size, expected_cut_edges = calculate_cut_size(partition_1, partition_2, edges)

    if solution["cut_size"] != expected_cut_size:
        return False, f"Incorrect cut size: expected {expected_cut_size}, got {solution['cut_size']}"

    # Validate cut edges
    solution_cut_edges = sorted(solution["cut_edges"], key=lambda x: (x["from"], x["to"]))
    expected_cut_edges_sorted = sorted(expected_cut_edges, key=lambda x: (x["from"], x["to"]))

    if solution_cut_edges != expected_cut_edges_sorted:
        return False, f"Incorrect cut edges: expected {expected_cut_edges_sorted}, got {solution_cut_edges}"

    # Check for optimality (optimal cut size is 3)
    optimal_cut_size = 3
    if expected_cut_size != optimal_cut_size:
        return False, f"Suboptimal cut size: got {expected_cut_size}, optimal is {optimal_cut_size}"

    return True, f"Valid balanced partition with optimal cut size {optimal_cut_size}"


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
