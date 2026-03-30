#!/usr/bin/env python3

import json
import sys

# Expected optimal value
EXPECTED_OPTIMAL_COST = 10

def get_graph_definition():
    """Defines the graph structure, vertex types, and costs."""
    vertices = set(range(1, 19))

    edges_list = [
        (1, 2), (1, 4), (1, 5),
        (2, 4), (2, 5),
        (3, 4), (3, 9),
        (4, 5), (4, 18),
        (6, 7), (6, 9), (6, 10),
        (7, 9),
        (8, 9), (8, 14),
        (9, 10),
        (11, 12), (11, 14),
        (12, 14),
        (13, 14), (13, 17),
        (15, 16), (15, 17),
        (16, 17),
        (17, 18)
    ]

    adj = {v: set() for v in vertices}
    for u, v in edges_list:
        adj[u].add(v)
        adj[v].add(u)

    types = {
        'c': {1, 5, 10, 15},
        's': {2, 6, 7, 11, 12, 16},
        'r': {3, 8, 13, 18}
    }

    costs = {
        4: 2, 9: 2, 14: 3, 17: 3,
        **{v: 5 for v in {1, 2, 3, 5, 6, 7, 8}},
        **{v: 8 for v in {10, 11, 12, 13, 15, 16, 18}}
    }

    return vertices, adj, types, costs

def validate_solution(solution_json):
    """Validates the dominating set solution."""
    try:
        data = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON format: {e}"}

    if not all(k in data for k in ["dominating_set", "total_cost"]):
        return {"valid": False, "message": "Missing 'dominating_set' or 'total_cost' key."}

    dom_set = set(data["dominating_set"])
    total_cost = data["total_cost"]

    vertices, adj, types, costs = get_graph_definition()

    # Verify vertices are valid
    if not dom_set.issubset(vertices):
        return {"valid": False, "message": f"Invalid vertex in dominating set: {dom_set - vertices}"}

    # Verify cost
    calculated_cost = sum(costs[v] for v in dom_set)
    if calculated_cost != total_cost:
        return {"valid": False, "message": f"Incorrect total_cost. Expected {calculated_cost}, got {total_cost}."}

    # Verify independent set constraint
    for u in dom_set:
        for v in dom_set:
            if u < v and v in adj[u]:
                return {"valid": False, "message": f"Dominating set is not independent. Edge exists between {u} and {v}."}

    # Verify domination for all vertices
    for v in vertices:
        if v in dom_set:
            continue  # Dominated by being in the set

        covering_nodes = {u for u in dom_set if v in adj[u]}
        num_covers = len(covering_nodes)

        v_type = None
        for t, v_set in types.items():
            if v in v_set:
                v_type = t
                break

        is_dominated = False
        if v_type in ['c', 's']:
            if num_covers >= 1:
                is_dominated = True
        elif v_type == 'r':
            if num_covers >= 2:
                is_dominated = True

        if not is_dominated:
            return {"valid": False, "message": f"Vertex {v} (type '{v_type}') is not dominated. Required covers not met (has {num_covers})."}

    # Check optimality
    if total_cost != EXPECTED_OPTIMAL_COST:
        return {"valid": False, "message": f"Not optimal: total_cost={total_cost}, expected {EXPECTED_OPTIMAL_COST}"}

    return {"valid": True, "message": f"Solution valid and optimal (total_cost={EXPECTED_OPTIMAL_COST})"}


if __name__ == "__main__":
    solution_str = sys.stdin.read()
    result = validate_solution(solution_str)
    print(json.dumps(result))
