#!/usr/bin/env python3
"""
Reference model for Bin Packing Problem
Validates solution from stdin
"""

import json
import sys

def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def validate_solution(solution):
    """Validate the bin packing solution"""

    # Define problem instance
    items = {
        1: 4,
        2: 6,
        3: 2,
        4: 3,
        5: 7,
        6: 1,
        7: 5,
        8: 2,
        9: 4
    }
    bin_capacity = 10
    expected_optimal = 4

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    if not solution.get('feasible', False):
        return {"valid": False, "message": "Solution marked as infeasible"}

    # Check required fields
    if 'bins' not in solution or 'num_bins' not in solution:
        return {"valid": False, "message": "Missing required fields: bins or num_bins"}

    bins = solution['bins']
    num_bins = solution['num_bins']

    # Check num_bins matches actual bin count
    if num_bins != len(bins):
        return {"valid": False, "message": f"num_bins ({num_bins}) does not match bins array length ({len(bins)})"}

    # Track used items
    used_items = set()
    total_size_check = 0

    # Validate each bin
    for i, bin_data in enumerate(bins):
        # Check required fields
        if 'bin_id' not in bin_data or 'items' not in bin_data or 'total_size' not in bin_data:
            return {"valid": False, "message": f"Bin {i} missing required fields"}

        bin_id = bin_data['bin_id']
        items_in_bin = bin_data['items']
        reported_total = bin_data['total_size']

        # Check bin capacity
        actual_total = 0
        for item_id in items_in_bin:
            if item_id not in items:
                return {"valid": False, "message": f"Invalid item ID {item_id} in bin {bin_id}"}

            if item_id in used_items:
                return {"valid": False, "message": f"Item {item_id} assigned to multiple bins"}

            used_items.add(item_id)
            actual_total += items[item_id]
            total_size_check += items[item_id]

        # Verify reported total matches actual
        if actual_total != reported_total:
            return {"valid": False, "message": f"Bin {bin_id} reported total ({reported_total}) does not match actual ({actual_total})"}

        # Check capacity constraint
        if reported_total > bin_capacity:
            return {"valid": False, "message": f"Bin {bin_id} exceeds capacity: {reported_total} > {bin_capacity}"}

    # Check all items are used exactly once
    if len(used_items) != len(items):
        missing = set(items.keys()) - used_items
        return {"valid": False, "message": f"Not all items used. Missing: {missing}"}

    # Check total size
    expected_total = sum(items.values())
    if total_size_check != expected_total:
        return {"valid": False, "message": f"Total size mismatch: {total_size_check} != {expected_total}"}

    # Check optimality
    if num_bins > expected_optimal:
        return {"valid": False, "message": f"Solution uses {num_bins} bins, expected optimal is {expected_optimal}"}

    return {"valid": True, "message": f"Valid optimal solution using {num_bins} bins"}

if __name__ == "__main__":
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))
