#!/usr/bin/env python3

import json
import sys

# Expected optimal value
EXPECTED_OPTIMAL_MAX_FLOW = 12

def validate_solution(solution_str):
    """Validate a solution for the Network Flow problem."""
    try:
        data = json.loads(solution_str)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON format: {e}"}

    # Basic structure validation
    if "max_flow" not in data or "flows" not in data:
        return {"valid": False, "message": "Missing 'max_flow' or 'flows' key."}

    max_flow_val = data["max_flow"]
    flows = data["flows"]

    if not isinstance(max_flow_val, int):
        return {"valid": False, "message": "max_flow must be an integer."}
    if not isinstance(flows, list):
        return {"valid": False, "message": "flows must be a list."}

    # Instance definition
    nodes = set(range(1, 9))
    source, sink = 1, 8
    budget = 100
    priority_nodes = {3, 5}
    edges = {
        (1, 2): {'cap': 10, 'cost': 2, 'type': 'standard'},
        (1, 3): {'cap': 12, 'cost': 4, 'type': 'premium'},
        (2, 4): {'cap': 8, 'cost': 1, 'type': 'standard'},
        (2, 5): {'cap': 4, 'cost': 3, 'type': 'premium'},
        (3, 4): {'cap': 5, 'cost': 3, 'type': 'standard'},
        (3, 6): {'cap': 10, 'cost': 5, 'type': 'premium'},
        (4, 7): {'cap': 10, 'cost': 2, 'type': 'standard'},
        (5, 7): {'cap': 7, 'cost': 4, 'type': 'premium'},
        (6, 8): {'cap': 12, 'cost': 2, 'type': 'premium'},
        (7, 8): {'cap': 15, 'cost': 1, 'type': 'standard'}
    }

    if len(flows) != len(edges):
        return {"valid": False, "message": f"Expected {len(edges)} flows, but got {len(flows)}."}

    flow_dict = {}
    for flow_entry in flows:
        if not all(k in flow_entry for k in ["from", "to", "flow"]):
            return {"valid": False, "message": f"Flow entry is missing a required key: {flow_entry}"}

        u, v, f = flow_entry["from"], flow_entry["to"], flow_entry["flow"]
        if (u, v) not in edges:
            return {"valid": False, "message": f"Invalid edge in solution: ({u}, {v})"}
        if not isinstance(f, int) or f < 0:
            return {"valid": False, "message": f"Flow must be a non-negative integer: {f}"}

        # Constraint 1: Capacity
        if f > edges[(u, v)]['cap']:
            return {"valid": False, "message": f"Flow {f} on edge ({u},{v}) exceeds capacity {edges[(u,v)]['cap']}."}
        flow_dict[(u, v)] = f

    if len(flow_dict) != len(edges):
        return {"valid": False, "message": "Solution does not contain a flow for every edge."}

    # Constraint 2: Flow Conservation
    for n in nodes:
        if n in [source, sink]:
            continue
        inflow = sum(flow_dict.get((u, v), 0) for u, v in flow_dict if v == n)
        outflow = sum(flow_dict.get((u, v), 0) for u, v in flow_dict if u == n)
        if inflow != outflow:
            return {"valid": False, "message": f"Flow conservation violated at node {n}: inflow={inflow}, outflow={outflow}"}

    # Constraint 3: Budget
    total_cost = sum(f * edges[(u, v)]['cost'] for (u, v), f in flow_dict.items())
    if total_cost > budget:
        return {"valid": False, "message": f"Total cost {total_cost} exceeds budget {budget}."}

    # Constraint 4: Priority Node Rule
    for n in priority_nodes:
        inflow = sum(flow_dict.get((u, v), 0) for u, v in flow_dict if v == n)
        premium_outflow = sum(f for (u, v), f in flow_dict.items() if u == n and edges[(u, v)]['type'] == 'premium')
        if inflow > 0 and premium_outflow * 100 < inflow * 75:
            return {"valid": False, "message": f"Priority node {n} rule violated: premium outflow {premium_outflow} is less than 75% of inflow {inflow}."}

    # Constraint 5: Flow Balancing
    total_standard_flow = sum(f for (u, v), f in flow_dict.items() if edges[(u, v)]['type'] == 'standard')
    total_premium_flow = sum(f for (u, v), f in flow_dict.items() if edges[(u, v)]['type'] == 'premium')
    if total_standard_flow * 10 < total_premium_flow * 5:
        return {"valid": False, "message": f"Flow balancing rule violated: standard flow {total_standard_flow} is less than 50% of premium flow {total_premium_flow}."}

    # Check max_flow value consistency
    source_outflow = sum(flow_dict.get((u, v), 0) for u, v in flow_dict if u == source)
    if source_outflow != max_flow_val:
        return {"valid": False, "message": f"Declared max_flow {max_flow_val} does not match actual source outflow {source_outflow}."}

    # Check optimality
    if max_flow_val != EXPECTED_OPTIMAL_MAX_FLOW:
        return {"valid": False, "message": f"Not optimal: max_flow={max_flow_val}, expected {EXPECTED_OPTIMAL_MAX_FLOW}"}

    return {"valid": True, "message": f"Solution is valid and optimal (max_flow={EXPECTED_OPTIMAL_MAX_FLOW})"}

if __name__ == "__main__":
    solution_str = sys.stdin.read()
    result = validate_solution(solution_str)
    print(json.dumps(result))
