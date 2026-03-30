#!/usr/bin/env python3

import json
import sys

# Expected optimal value
EXPECTED_OPTIMAL_SIZE = 7

def get_instance_data():
    """Defines the problem instance (graph, attributes)."""
    zones = {v: 1 for v in range(1, 9)}
    zones.update({v: 2 for v in range(9, 17)})
    zones.update({v: 3 for v in range(17, 25)})

    types = {v: 'peripheral' for v in range(1, 25)}
    types.update({v: 'core' for v in [1, 9, 17]})
    types.update({v: 'support' for v in [2, 3, 10, 11, 18, 19]})

    edge_list = [
        (1, 2), (1, 4), (1, 10), (1, 17), (2, 5), (2, 9), (3, 6), (4, 7),
        (5, 8), (6, 7), (8, 16), (8, 24), (9, 10), (9, 12), (9, 17),
        (10, 14), (11, 15), (12, 16), (13, 14), (16, 24), (17, 18),
        (17, 20), (18, 19), (18, 21), (19, 22), (20, 23), (21, 24)
    ]
    edges = set()
    for u, v in edge_list:
        edges.add(tuple(sorted((u, v))))

    return zones, types, edges

def validate_solution(solution):
    """Validate solution - check feasibility and optimality."""
    try:
        data = json.loads(solution)
        zones, types, edges = get_instance_data()

        required_keys = [
            "independent_set", "size", "core_vertices", "support_vertices",
            "peripheral_vertices", "core_count", "support_count", "peripheral_count"
        ]
        for key in required_keys:
            if key not in data:
                return {"valid": False, "message": f"Missing required key: {key}"}

        ind_set = set(data["independent_set"])

        # Check counts and lists match the main set
        if data["size"] != len(ind_set):
            return {"valid": False, "message": "Size field does not match length of independent_set"}
        if len(data["independent_set"]) != len(ind_set):
             return {"valid": False, "message": "Duplicate vertices in independent_set"}

        # Verify derived lists and counts
        cores = {v for v in ind_set if types[v] == 'core'}
        supports = {v for v in ind_set if types[v] == 'support'}
        peripherals = {v for v in ind_set if types[v] == 'peripheral'}

        if set(data["core_vertices"]) != cores: return {"valid": False, "message": "core_vertices list is incorrect."}
        if set(data["support_vertices"]) != supports: return {"valid": False, "message": "support_vertices list is incorrect."}
        if set(data["peripheral_vertices"]) != peripherals: return {"valid": False, "message": "peripheral_vertices list is incorrect."}
        if data["core_count"] != len(cores): return {"valid": False, "message": "core_count is incorrect."}
        if data["support_count"] != len(supports): return {"valid": False, "message": "support_count is incorrect."}
        if data["peripheral_count"] != len(peripherals): return {"valid": False, "message": "peripheral_count is incorrect."}

        # Constraint 1: Standard Independence
        for v1 in ind_set:
            for v2 in ind_set:
                if v1 < v2 and tuple(sorted((v1, v2))) in edges:
                    return {"valid": False, "message": f"Edge violation: vertices {v1} and {v2} are connected."}

        # Constraint 2: Core Count Limit
        if len(cores) > 2:
            return {"valid": False, "message": f"Core count violation: {len(cores)} cores found, max is 2."}

        # Constraint 3: Core-Support Dependency
        for core_v in cores:
            core_zone = zones[core_v]
            if not any(zones[support_v] == core_zone for support_v in supports):
                return {"valid": False, "message": f"Core-support violation: core vertex {core_v} in zone {core_zone} lacks a support vertex from the same zone."}

        # Constraint 4: Conditional Zone Exclusion
        peripheral_z1_present = any(zones[p_v] == 1 for p_v in peripherals)
        if peripheral_z1_present:
            if any(zones[v] == 3 for v in ind_set):
                return {"valid": False, "message": "Zone exclusion violation: peripheral from zone 1 selected, but vertices from zone 3 are also in the set."}

        # Constraint 5: Peripheral Headcount Rule
        if len(peripherals) > len(cores):
            return {"valid": False, "message": f"Peripheral headcount violation: {len(peripherals)} peripherals > {len(cores)} cores."}

        # Check optimality
        if data["size"] != EXPECTED_OPTIMAL_SIZE:
            return {"valid": False, "message": f"Not optimal: size={data['size']}, expected {EXPECTED_OPTIMAL_SIZE}"}

        return {"valid": True, "message": f"Solution valid and optimal (size={EXPECTED_OPTIMAL_SIZE})"}

    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"valid": False, "message": f"Error validating solution: {e}"}

if __name__ == "__main__":
    solution_str = sys.stdin.read().strip()
    if not solution_str:
        print(json.dumps({"valid": False, "message": "Empty input received."}))
    else:
        result = validate_solution(solution_str)
        print(json.dumps(result))
