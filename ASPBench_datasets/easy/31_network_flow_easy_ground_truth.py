#!/usr/bin/env python3

import json
import sys

def validate_solution(solution):
    """Validate a network flow solution."""

    try:
        # Parse JSON
        if not solution:
            return {"valid": False, "message": "No solution provided"}

        data = json.loads(solution)

        if "max_flow" not in data:
            return {"valid": False, "message": "Missing 'max_flow' key"}
        if "flows" not in data:
            return {"valid": False, "message": "Missing 'flows' key"}

        max_flow = data["max_flow"]
        flows = data["flows"]

        if not isinstance(max_flow, (int, float)):
            return {"valid": False, "message": "max_flow must be a number"}
        if not isinstance(flows, list):
            return {"valid": False, "message": "flows must be a list"}

        # Network definition
        edges = [
            (1, 2, 10), (1, 3, 8), (2, 3, 5), (2, 4, 7),
            (3, 4, 3), (3, 5, 9), (4, 6, 8), (5, 6, 6)
        ]

        nodes = {1, 2, 3, 4, 5, 6}
        source = 1
        sink = 6

        # Check flows format
        if len(flows) != len(edges):
            return {"valid": False, "message": f"Expected {len(edges)} flows, got {len(flows)}"}

        flow_dict = {}
        for i, flow_entry in enumerate(flows):
            if not isinstance(flow_entry, dict):
                return {"valid": False, "message": f"Flow {i+1} must be an object"}

            required_fields = ["from", "to", "flow"]
            for field in required_fields:
                if field not in flow_entry:
                    return {"valid": False, "message": f"Flow {i+1} missing '{field}' field"}

            from_node = flow_entry["from"]
            to_node = flow_entry["to"]
            flow_val = flow_entry["flow"]

            if not isinstance(flow_val, (int, float)):
                return {"valid": False, "message": f"Flow value must be a number in flow {i+1}"}

            flow_dict[(from_node, to_node)] = flow_val

        # Check all edges are present with correct capacities
        for from_node, to_node, capacity in edges:
            if (from_node, to_node) not in flow_dict:
                return {"valid": False, "message": f"Missing flow for edge ({from_node}, {to_node})"}

            flow_val = flow_dict[(from_node, to_node)]

            # Check capacity constraint
            if flow_val < 0:
                return {"valid": False, "message": f"Flow on edge ({from_node}, {to_node}) cannot be negative: {flow_val}"}
            if flow_val > capacity:
                return {"valid": False, "message": f"Flow on edge ({from_node}, {to_node}) exceeds capacity: {flow_val} > {capacity}"}

        # Check flow conservation
        for node in nodes:
            if node == source or node == sink:
                continue

            inflow = sum(flow_dict.get((u, node), 0) for u, v, _ in edges if v == node)
            outflow = sum(flow_dict.get((node, v), 0) for u, v, _ in edges if u == node)

            if abs(inflow - outflow) > 1e-9:  # Allow small floating point errors
                return {"valid": False, "message": f"Flow conservation violated at node {node}: inflow={inflow}, outflow={outflow}"}

        # Check max flow value
        source_outflow = sum(flow_dict.get((source, v), 0) for u, v, _ in edges if u == source)
        sink_inflow = sum(flow_dict.get((u, sink), 0) for u, v, _ in edges if v == sink)

        if abs(source_outflow - sink_inflow) > 1e-9:
            return {"valid": False, "message": f"Source outflow ({source_outflow}) != sink inflow ({sink_inflow})"}

        if abs(max_flow - source_outflow) > 1e-9:
            return {"valid": False, "message": f"Declared max_flow ({max_flow}) != actual flow ({source_outflow})"}

        # Check optimality: the optimal max flow for this instance is 14
        expected_optimal = 14
        if max_flow < expected_optimal:
            return {"valid": False, "message": f"Solution is suboptimal: max_flow={max_flow}, expected optimal={expected_optimal}"}

        return {"valid": True, "message": f"Solution is valid and optimal with max_flow={max_flow}"}

    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"valid": False, "message": f"Error validating solution: {e}"}

if __name__ == "__main__":
    solution = sys.stdin.read().strip()
    result = validate_solution(solution)
    print(json.dumps(result))
