#!/usr/bin/env python3
"""
Reference model for Facility Location Problem
Validates solution from stdin
"""

import json
import sys

def manhattan_distance(p1, p2):
    """Calculate Manhattan distance between two points"""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def validate_solution(solution):
    """Validate facility location solution"""

    # Customer locations
    customers = {
        1: (1, 1),
        2: (2, 4),
        3: (4, 2),
        4: (5, 5),
        5: (7, 1),
        6: (8, 3),
        7: (3, 6),
        8: (6, 4)
    }

    # Facility locations and costs
    facilities = {
        'A': {'pos': (2, 2), 'cost': 100},
        'B': {'pos': (4, 4), 'cost': 120},
        'C': {'pos': (6, 2), 'cost': 110},
        'D': {'pos': (3, 5), 'cost': 90},
        'E': {'pos': (7, 3), 'cost': 130}
    }

    coverage_radius = 3
    service_cost_per_unit = 5
    expected_optimal_cost = 380

    # Check feasible field
    if not solution.get('feasible', False):
        return {"valid": False, "message": "Solution is not marked as feasible"}

    # Check facilities field
    if 'facilities' not in solution:
        return {"valid": False, "message": "Missing 'facilities' field"}

    opened_facilities = solution['facilities']
    if not isinstance(opened_facilities, list):
        return {"valid": False, "message": "'facilities' must be a list"}

    # Check all opened facilities are valid
    for fid in opened_facilities:
        if fid not in facilities:
            return {"valid": False, "message": f"Invalid facility ID: {fid}"}

    # Check assignments field
    if 'assignments' not in solution:
        return {"valid": False, "message": "Missing 'assignments' field"}

    assignments = solution['assignments']
    if not isinstance(assignments, dict):
        return {"valid": False, "message": "'assignments' must be an object"}

    # Check all customers are assigned
    for cid in customers.keys():
        cid_str = str(cid)
        if cid_str not in assignments:
            return {"valid": False, "message": f"Customer {cid} is not assigned to any facility"}

    # Check all assignments are valid
    total_service_cost = 0
    for cid_str, fid in assignments.items():
        cid = int(cid_str)

        if cid not in customers:
            return {"valid": False, "message": f"Invalid customer ID: {cid}"}

        if fid not in facilities:
            return {"valid": False, "message": f"Invalid facility ID in assignment: {fid}"}

        # Check facility is opened
        if fid not in opened_facilities:
            return {"valid": False, "message": f"Customer {cid} is assigned to unopened facility {fid}"}

        # Check distance constraint
        cpos = customers[cid]
        fpos = facilities[fid]['pos']
        dist = manhattan_distance(cpos, fpos)

        if dist > coverage_radius:
            return {"valid": False, "message": f"Customer {cid} assigned to facility {fid} is outside coverage radius (distance {dist} > {coverage_radius})"}

        total_service_cost += dist * service_cost_per_unit

    # Calculate total cost
    opening_cost = sum(facilities[fid]['cost'] for fid in opened_facilities)
    computed_total_cost = opening_cost + total_service_cost

    # Check total_cost field
    if 'total_cost' not in solution:
        return {"valid": False, "message": "Missing 'total_cost' field"}

    reported_cost = solution['total_cost']
    if reported_cost != computed_total_cost:
        return {"valid": False, "message": f"Reported cost {reported_cost} does not match computed cost {computed_total_cost}"}

    # Check optimality
    if computed_total_cost != expected_optimal_cost:
        return {"valid": False, "message": f"Solution cost {computed_total_cost} is not optimal (expected {expected_optimal_cost})"}

    return {"valid": True, "message": f"Solution is valid and optimal with cost {computed_total_cost}"}

def main():
    try:
        data = sys.stdin.read().strip()
        if not data:
            print(json.dumps({"valid": False, "message": "No input provided"}))
            return

        solution = json.loads(data)
        result = validate_solution(solution)
        print(json.dumps(result))

    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {str(e)}"}))
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Validation error: {str(e)}"}))

if __name__ == "__main__":
    main()
