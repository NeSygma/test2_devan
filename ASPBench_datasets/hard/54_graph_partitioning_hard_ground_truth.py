#!/usr/bin/env python3
"""
Reference model for Graph Partitioning problem.
Validates a weighted, 4-way balanced partition for a 16-vertex graph.
Checks optimality against expected optimal value.
"""

import json
import sys
from typing import List, Dict, Tuple

# Expected optimal value
EXPECTED_OPTIMAL_CUT_WEIGHT = 13

def get_problem_setup():
    """Defines the graph structure and problem parameters."""
    # Intra-partition cliques (weight 10)
    edges = []
    for i in range(4):
        base = i * 4
        clique_nodes = range(base, base + 4)
        for u in clique_nodes:
            for v in clique_nodes:
                if u < v:
                    edges.append((u, v, 10))

    # Inter-partition "cut" edges (low weights)
    cut_edges_spec = [
        (3, 4, 1), (7, 8, 2), (11, 12, 3), (15, 0, 1),
        (1, 6, 2), (5, 10, 3), (9, 14, 1)
    ]
    edges.extend(cut_edges_spec)

    return {
        "vertices": list(range(16)),
        "edges": edges,
        "num_partitions": 4,
        "target_partition_size": 4
    }

def load_solution():
    """Load solution from stdin"""
    try:
        return json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return None

def calculate_cut(partitions: Dict[str, List[int]], edges: List[Tuple[int, int, int]]) -> Tuple[int, List[Dict]]:
    """Calculate the cut weight and cut edges for a given partitioning."""

    # Create a reverse map from vertex to partition index (1-4)
    vertex_to_partition = {}
    for i in range(1, 5):
        part_key = f"partition_{i}"
        for vertex in partitions.get(part_key, []):
            vertex_to_partition[vertex] = i

    cut_edges_list = []
    total_weight = 0

    for u, v, weight in edges:
        # Edge crosses partition boundary if vertices are in different partitions
        if u in vertex_to_partition and v in vertex_to_partition and vertex_to_partition[u] != vertex_to_partition[v]:
            cut_edges_list.append({"from": min(u, v), "to": max(u, v), "weight": weight})
            total_weight += weight

    return total_weight, cut_edges_list

def validate_solution(solution: Dict) -> Tuple[bool, str]:
    """Validate the graph partitioning solution."""

    if not solution:
        return False, "No solution provided or JSON is invalid"

    setup = get_problem_setup()

    # Check for required fields
    required_fields = ["partition_1", "partition_2", "partition_3", "partition_4", "cut_weight", "cut_edges", "balance"]
    for field in required_fields:
        if field not in solution:
            return False, f"Missing field: {field}"

    # Collect all partitions from solution
    partitions = {}
    all_partitioned_vertices = set()
    for i in range(1, setup["num_partitions"] + 1):
        part_key = f"partition_{i}"
        part_list = solution[part_key]
        partitions[part_key] = part_list

        # Validate partition size
        if len(part_list) != setup["target_partition_size"]:
            return False, f"{part_key} has size {len(part_list)}, expected {setup['target_partition_size']}"

        # Check for duplicates within a partition
        if len(set(part_list)) != len(part_list):
            return False, f"{part_key} contains duplicate vertices"

        all_partitioned_vertices.update(part_list)

    # Check for disjointness and coverage
    all_problem_vertices = set(setup["vertices"])
    if len(all_partitioned_vertices) != len(setup["vertices"]):
        return False, "Partitions are not disjoint or do not cover all vertices"

    if all_partitioned_vertices != all_problem_vertices:
        missing = all_problem_vertices - all_partitioned_vertices
        extra = all_partitioned_vertices - all_problem_vertices
        return False, f"Vertex coverage error. Missing: {sorted(list(missing))}, Extra: {sorted(list(extra))}"

    # Validate balance information
    balance_info = solution["balance"]
    if not balance_info.get("is_balanced"):
        return False, "Solution claims to be unbalanced in 'balance.is_balanced'"
    for i in range(1, setup["num_partitions"] + 1):
        if balance_info.get(f"partition_{i}_size") != setup["target_partition_size"]:
            return False, f"Incorrect balance info for partition_{i}_size"

    # Recalculate and validate cut weight
    expected_weight, expected_edges = calculate_cut(partitions, setup["edges"])

    if solution["cut_weight"] != expected_weight:
        return False, f"Incorrect cut weight: expected {expected_weight}, got {solution['cut_weight']}"

    # Validate that the reported cut_edges list is consistent with the partitioning
    if len(solution["cut_edges"]) != len(expected_edges):
        return False, f"Cut edges count mismatch: expected {len(expected_edges)} edges, got {len(solution['cut_edges'])}"

    # Verify the reported cut edges sum to the reported cut weight
    reported_cut_total = sum(e["weight"] for e in solution["cut_edges"])
    if reported_cut_total != solution["cut_weight"]:
        return False, f"Cut edges weight sum {reported_cut_total} doesn't match reported cut_weight {solution['cut_weight']}"

    # Check optimality
    if expected_weight != EXPECTED_OPTIMAL_CUT_WEIGHT:
        return False, f"Not optimal: cut_weight={expected_weight}, expected {EXPECTED_OPTIMAL_CUT_WEIGHT}"

    return True, f"Solution valid and optimal (cut_weight={EXPECTED_OPTIMAL_CUT_WEIGHT})"

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
