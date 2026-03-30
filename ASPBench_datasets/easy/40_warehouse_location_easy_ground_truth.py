#!/usr/bin/env python3
"""
Reference Model: Multi-Warehouse Location Problem
================================================
Validate warehouse location solutions from stdin.
"""

import sys
import json

def verify_solution(solution_data: dict) -> dict:
    """Verify warehouse location solution."""
    try:
        if "error" in solution_data:
            return {"valid": False, "message": "Solution contains error"}

        selected_warehouses = solution_data["selected_warehouses"]
        assignments = solution_data["assignments"]
        reported_cost = solution_data["total_cost"]

        # Problem data
        capacities = {'W1': 100, 'W2': 150, 'W3': 120}
        demands = {'C1': 25, 'C2': 30, 'C3': 20, 'C4': 35, 'C5': 15, 'C6': 25}
        distances = {
            ('W1', 'C1'): 10, ('W1', 'C2'): 15, ('W1', 'C3'): 25,
            ('W1', 'C4'): 20, ('W1', 'C5'): 30, ('W1', 'C6'): 12,
            ('W2', 'C1'): 18, ('W2', 'C2'): 8,  ('W2', 'C3'): 12,
            ('W2', 'C4'): 15, ('W2', 'C5'): 10, ('W2', 'C6'): 20,
            ('W3', 'C1'): 22, ('W3', 'C2'): 25, ('W3', 'C3'): 8,
            ('W3', 'C4'): 18, ('W3', 'C5'): 12, ('W3', 'C6'): 15
        }

        customers = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']

        # Check all customers assigned
        for customer in customers:
            if customer not in assignments:
                return {"valid": False, "message": f"Customer {customer} not assigned"}

        # Check capacity constraints
        warehouse_loads = {w: 0 for w in selected_warehouses}
        for customer, warehouse in assignments.items():
            if warehouse not in selected_warehouses:
                return {"valid": False, "message": f"Customer {customer} assigned to unselected warehouse {warehouse}"}
            warehouse_loads[warehouse] += demands[customer]

        for warehouse in selected_warehouses:
            if warehouse_loads[warehouse] > capacities[warehouse]:
                return {"valid": False, "message": f"Warehouse {warehouse} overloaded: {warehouse_loads[warehouse]} > {capacities[warehouse]}"}

        # Calculate actual cost
        actual_cost = 0
        for customer, warehouse in assignments.items():
            actual_cost += distances[(warehouse, customer)] * demands[customer]

        if abs(actual_cost - reported_cost) > 1e-6:
            return {"valid": False, "message": f"Cost mismatch: reported {reported_cost}, actual {actual_cost}"}

        # Check optimality (expected optimal cost is 1625)
        expected_optimal = 1625
        if actual_cost != expected_optimal:
            return {"valid": False, "message": f"Cost {actual_cost} does not match expected optimal cost {expected_optimal}"}

        return {"valid": True, "message": f"Valid solution with optimal cost {actual_cost}"}

    except KeyError as e:
        return {"valid": False, "message": f"Missing field in solution: {e}"}
    except Exception as e:
        return {"valid": False, "message": f"Verification error: {str(e)}"}

if __name__ == "__main__":
    try:
        input_data = sys.stdin.read().strip()

        if not input_data:
            result = {"valid": False, "message": "No input provided"}
        else:
            solution_data = json.loads(input_data)
            result = verify_solution(solution_data)

        print(json.dumps(result))

    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON input: {str(e)}"}))
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Unexpected error: {str(e)}"}))
