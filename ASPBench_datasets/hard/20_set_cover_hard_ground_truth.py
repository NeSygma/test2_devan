#!/usr/bin/env python3
"""
Reference model for the Set Cover with Costs and Complex Constraints problem.
Validates solution from stdin and checks optimality.
"""

import json
import sys
from collections import Counter

# Expected optimal value
EXPECTED_OPTIMAL_COST = 5

def verify_solution(solution_json: str) -> dict:
    """
    Verify if the given solution satisfies all problem constraints.

    Args:
        solution_json: JSON string containing the solution

    Returns:
        dict with keys:
        - valid: bool (True if solution is valid)
        - message: str (explanation)
    """
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    required_fields = ["selected_sets", "total_sets", "covered_elements", "base_cost", "redundancy_penalty", "total_cost"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    # Problem Definition
    universe = set(range(1, 21))
    sets_data = [
        {1, 2, 3, 4, 5}, {1, 6, 11, 16}, {2, 7, 12, 17}, {3, 8, 13, 18},
        {4, 9, 14, 19}, {5, 10, 15, 20}, {6, 7, 8, 9, 10}, {1, 3, 5, 7, 9},
        {2, 4, 6, 8, 10}, {1, 2, 3, 4, 5, 6, 7}, {11, 12, 13, 14, 15},
        {8, 9, 10}, {1, 5, 10, 15}, {16, 17, 18, 19, 20}
    ]
    costs = {i: 1 for i in range(9)}
    costs.update({i: 4 for i in range(9, 14)})

    categories = {
        'a': {0, 1, 2}, 'b': {3, 4, 5}, 'c': {6, 7, 8}
    }
    specialized_sets = set(range(9, 14))

    selected_sets = solution["selected_sets"]

    # Validate selected_sets format
    if not isinstance(selected_sets, list) or not all(isinstance(i, int) for i in selected_sets):
        return {"valid": False, "message": "selected_sets must be an array of integers."}
    if len(selected_sets) != len(set(selected_sets)):
        return {"valid": False, "message": "Duplicate sets in selected_sets."}

    # Constraint 1: Full Coverage
    actual_covered = set()
    for s_idx in selected_sets:
        if not 0 <= s_idx < len(sets_data):
            return {"valid": False, "message": f"Invalid set index {s_idx}."}
        actual_covered.update(sets_data[s_idx])

    if actual_covered != universe:
        missing = sorted(list(universe - actual_covered))
        return {"valid": False, "message": f"Not all elements covered. Missing: {missing}"}
    if sorted(solution["covered_elements"]) != sorted(list(universe)):
        return {"valid": False, "message": "covered_elements field does not match all universe elements."}

    # Constraint 2: Prerequisites
    if 9 in selected_sets and 0 not in selected_sets:
        return {"valid": False, "message": "Constraint violated: Set 9 selected without prerequisite Set 0."}
    if 11 in selected_sets and 6 not in selected_sets:
        return {"valid": False, "message": "Constraint violated: Set 11 selected without prerequisite Set 6."}

    # Constraint 3: Mutual Exclusion
    if 12 in selected_sets and 13 in selected_sets:
        return {"valid": False, "message": "Constraint violated: Mutually exclusive sets 12 and 13 are both selected."}

    # Constraint 4: Category Balancing
    is_any_specialized_selected = any(s in specialized_sets for s in selected_sets)
    if is_any_specialized_selected:
        selected_categories = {cat for cat, s_indices in categories.items() if any(s in s_indices for s in selected_sets)}
        if len(selected_categories) < 3:
            missing_cats = {'A', 'B', 'C'} - {c.upper() for c in selected_categories}
            return {"valid": False, "message": f"Constraint violated: Specialized set selected, but missing sets from standard categories: {sorted(list(missing_cats))}"}

    # Constraint 5 & 6: Cost Calculation
    # Base Cost
    calculated_base_cost = sum(costs[s] for s in selected_sets)
    if calculated_base_cost != solution["base_cost"]:
        return {"valid": False, "message": f"base_cost mismatch. Expected: {calculated_base_cost}, got: {solution['base_cost']}"}

    # Redundancy Penalty
    coverage_counts = Counter()
    for s_idx in selected_sets:
        coverage_counts.update(sets_data[s_idx])

    calculated_penalty = 0
    for element, count in coverage_counts.items():
        if count > 3:
            calculated_penalty += 2

    if calculated_penalty != solution["redundancy_penalty"]:
        return {"valid": False, "message": f"redundancy_penalty mismatch. Expected: {calculated_penalty}, got: {solution['redundancy_penalty']}"}

    # Total Cost
    calculated_total_cost = calculated_base_cost + calculated_penalty
    if calculated_total_cost != solution["total_cost"]:
        return {"valid": False, "message": f"total_cost mismatch. Expected: {calculated_total_cost}, got: {solution['total_cost']}"}

    # Other field checks
    if len(selected_sets) != solution["total_sets"]:
        return {"valid": False, "message": "total_sets does not match the length of selected_sets."}

    # Check optimality
    if calculated_total_cost != EXPECTED_OPTIMAL_COST:
        return {"valid": False, "message": f"Not optimal: total_cost={calculated_total_cost}, expected {EXPECTED_OPTIMAL_COST}"}

    return {"valid": True, "message": f"Solution is valid and optimal (total_cost={EXPECTED_OPTIMAL_COST})"}

def main():
    """Main entry point for verification."""
    try:
        solution_json = sys.stdin.read()
        result = verify_solution(solution_json)
    except Exception as e:
        result = {"valid": False, "message": f"An unexpected error occurred: {e}"}

    print(json.dumps(result))

if __name__ == "__main__":
    main()
