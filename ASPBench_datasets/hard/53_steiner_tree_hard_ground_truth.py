#!/usr/bin/env python3
"""
Reference model for the Hierarchical Steiner Tree with Resource Constraints problem.
Validates solution from stdin and checks optimality.
"""
import json
import sys
from typing import Dict, Any

# Expected optimal value
EXPECTED_OPTIMAL_WEIGHT = 13

def get_problem_setup():
    """Returns the hardcoded problem instance."""
    base_edges = {
        (0,2): (5,"fiber"), (1,3): (4,"fiber"), (2,3): (3,"fiber"), (2,4): (6,"copper"),
        (2,6): (2,"copper"), (3,5): (2,"fiber"), (3,7): (8,"copper"), (4,8): (5,"fiber"),
        (5,9): (4,"copper"), (5,10): (3,"fiber"), (6,7): (1,"copper"), (9,10): (7,"fiber"),
        (10,11): (2,"copper")
    }
    # Make edges symmetric for lookup
    edges = {}
    for (u, v), (w, t) in base_edges.items():
        edges[(min(u,v), max(u,v))] = (w, t)

    return {
        "levels": {0:2, 1:2, 2:1, 3:1, 4:1, 5:1, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0},
        "costs": {0:10, 1:10, 2:8, 3:5, 4:7, 5:6, 6:2, 7:2, 8:3, 9:3, 10:4, 11:4},
        "edges": edges,
        "terminals": {"A": {6, 7}, "B": {10, 11}},
        "resource_budget": 20,
        "copper_limit": 3
    }

def validate_solution(solution: Dict[str, Any]) -> (bool, str):
    """Validates a given solution against all problem constraints."""
    setup = get_problem_setup()

    # 1. Basic Structure and Field Validation
    required_fields = ["total_weight", "tree_edges", "steiner_vertices", "terminals", "gateways", "copper_edge_count", "steiner_resource_cost", "connected_components"]
    for field in required_fields:
        if field not in solution:
            return False, f"Missing field: {field}"

    tree_edges = solution["tree_edges"]
    all_terminals = set(t for group in setup["terminals"].values() for t in group)

    used_vertices = set()
    calculated_weight = 0
    for edge in tree_edges:
        u, v = edge["from"], edge["to"]
        used_vertices.add(u)
        used_vertices.add(v)
        calculated_weight += edge["weight"]

    # 2. Tree Validity (Edges, Vertices, Connectivity)
    if len(tree_edges) != len(used_vertices) - 1:
        return False, f"Invalid tree structure: {len(used_vertices)} vertices but {len(tree_edges)} edges."

    # Check connectivity of the whole tree
    if used_vertices:
        start_vertex = next(iter(used_vertices))
        q = [start_vertex]
        visited = {start_vertex}
    else:
        q = []
        visited = set()

    adj = {v: [] for v in used_vertices}
    for edge in tree_edges:
        adj[edge["from"]].append(edge["to"])
        adj[edge["to"]].append(edge["from"])
    head = 0
    while head < len(q):
        u = q[head]
        head += 1
        for v_neighbor in adj[u]:
            if v_neighbor not in visited:
                visited.add(v_neighbor)
                q.append(v_neighbor)
    if visited != used_vertices:
        return False, "The tree is not connected."

    # 3. Terminals and Steiner vertices
    if any(t not in used_vertices for t in all_terminals):
        return False, "Not all terminals are included in the tree."

    calculated_steiner = sorted([v for v in used_vertices if v not in all_terminals])
    if calculated_steiner != sorted(solution["steiner_vertices"]):
        return False, f"Steiner vertices mismatch. Expected {calculated_steiner}, got {solution['steiner_vertices']}"

    # 4. Hierarchy Constraint
    for s in calculated_steiner:
        for edge in tree_edges:
            if edge["from"] == s:
                neighbor = edge["to"]
                if setup["levels"][neighbor] > setup["levels"][s]:
                    return False, f"Hierarchy violation: Steiner {s} (L{setup['levels'][s]}) connected to higher L{setup['levels'][neighbor]} vertex {neighbor}."
            elif edge["to"] == s:
                neighbor = edge["from"]
                if setup["levels"][neighbor] > setup["levels"][s]:
                    return False, f"Hierarchy violation: Steiner {s} (L{setup['levels'][s]}) connected to higher L{setup['levels'][neighbor]} vertex {neighbor}."

    # 5. Resource Budget
    calculated_resource_cost = sum(setup["costs"][v] for v in calculated_steiner)
    if calculated_resource_cost != solution["steiner_resource_cost"]:
        return False, f"Steiner resource cost mismatch. Calculated {calculated_resource_cost}, got {solution['steiner_resource_cost']}"
    if calculated_resource_cost > setup["resource_budget"]:
        return False, f"Steiner resource budget exceeded. Used {calculated_resource_cost}, budget {setup['resource_budget']}."

    # 6. Edge Type Limit
    calculated_copper_count = 0
    for edge in tree_edges:
        u, v = min(edge["from"], edge["to"]), max(edge["from"], edge["to"])
        _, edge_type = setup["edges"][(u,v)]
        if edge_type == 'copper':
            calculated_copper_count += 1
    if calculated_copper_count != solution["copper_edge_count"]:
        return False, f"Copper edge count mismatch. Calculated {calculated_copper_count}, got {solution['copper_edge_count']}"
    if calculated_copper_count > setup["copper_limit"]:
        return False, f"Copper edge limit exceeded. Used {calculated_copper_count}, limit {setup['copper_limit']}."

    # 7. Gateway Constraints
    all_gateways = set()
    for group, terminals in setup["terminals"].items():
        if group not in solution["gateways"] or not solution["gateways"][group]:
            return False, f"Missing gateway for terminal group '{group}'."

        group_gateways = set(solution["gateways"][group])
        all_gateways.update(group_gateways)

        is_gateway_for_group = False
        for g_node in group_gateways:
            if g_node not in calculated_steiner:
                return False, f"Gateway {g_node} is not a valid Steiner vertex."
            for edge in tree_edges:
                if (edge["from"] == g_node and edge["to"] in terminals) or \
                   (edge["to"] == g_node and edge["from"] in terminals):
                    is_gateway_for_group = True
                    break
            if not is_gateway_for_group:
                 return False, f"Gateway {g_node} for group {group} does not connect to any terminal in that group."

    # Gateway connectivity check
    if all_gateways:
        steiner_adj = {s: [] for s in calculated_steiner}
        for edge in tree_edges:
            u, v = edge["from"], edge["to"]
            if u in calculated_steiner and v in calculated_steiner:
                steiner_adj[u].append(v)
                steiner_adj[v].append(u)

        first_gateway = next(iter(all_gateways))
        g_q = [first_gateway]
        g_visited = {first_gateway}
        g_head = 0
        while g_head < len(g_q):
            u = g_q[g_head]; g_head += 1
            if u in steiner_adj:
                for v_neighbor in steiner_adj[u]:
                    if v_neighbor not in g_visited:
                        g_visited.add(v_neighbor)
                        g_q.append(v_neighbor)

        if not all_gateways.issubset(g_visited):
            return False, "Gateways are not connected to each other via Steiner vertices."

    # Check optimality
    if solution['total_weight'] != EXPECTED_OPTIMAL_WEIGHT:
        return False, f"Not optimal: total_weight={solution['total_weight']}, expected {EXPECTED_OPTIMAL_WEIGHT}"

    return True, f"Solution valid and optimal (total_weight={EXPECTED_OPTIMAL_WEIGHT})"

def main():
    try:
        solution = json.load(sys.stdin)
        is_valid, message = validate_solution(solution)
    except (json.JSONDecodeError, EOFError, TypeError) as e:
        is_valid = False
        message = f"Invalid or missing JSON input: {e}"
    except Exception as e:
        import traceback
        is_valid = False
        message = f"An unexpected error occurred during validation: {e}\n{traceback.format_exc()}"

    print(json.dumps({"valid": is_valid, "message": message}))

if __name__ == "__main__":
    main()
