#!/usr/bin/env python3
"""
Reference model for the Bin Packing Problem.

This script reads a JSON solution from stdin, converts it to ASP facts,
and uses a simple clingo program to validate whether the solution adheres
to all problem constraints. It checks for feasibility only, not optimality.
"""

import json
import sys
import clingo

# The ground truth data for all 27 items.
ITEMS_DATA = {
    1: {'size': 9, 'category': 'electronics', 'fragility': 'fragile', 'priority': 'high'},
    2: {'size': 8, 'category': 'electronics', 'fragility': 'sturdy', 'priority': 'high'},
    3: {'size': 3, 'category': 'electronics', 'fragility': 'sturdy', 'priority': 'high'},
    4: {'size': 9, 'category': 'liquid', 'fragility': 'fragile', 'priority': 'high'},
    5: {'size': 7, 'category': 'liquid', 'fragility': 'sturdy', 'priority': 'high'},
    6: {'size': 4, 'category': 'liquid', 'fragility': 'sturdy', 'priority': 'high'},
    7: {'size': 10, 'category': 'electronics', 'fragility': 'fragile', 'priority': 'high'},
    8: {'size': 10, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'high'},
    9: {'size': 10, 'category': 'liquid', 'fragility': 'fragile', 'priority': 'high'},
    10: {'size': 10, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'high'},
    11: {'size': 8, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'high'},
    12: {'size': 7, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'high'},
    13: {'size': 5, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'low'},
    14: {'size': 8, 'category': 'standard', 'fragility': 'fragile', 'priority': 'low'},
    15: {'size': 6, 'category': 'standard', 'fragility': 'fragile', 'priority': 'low'},
    16: {'size': 6, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'low'},
    17: {'size': 8, 'category': 'standard', 'fragility': 'fragile', 'priority': 'low'},
    18: {'size': 6, 'category': 'standard', 'fragility': 'fragile', 'priority': 'low'},
    19: {'size': 6, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'low'},
    20: {'size': 7, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'low'},
    21: {'size': 7, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'low'},
    22: {'size': 6, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'low'},
    23: {'size': 7, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'low'},
    24: {'size': 5, 'category': 'standard', 'fragility': 'fragile', 'priority': 'low'},
    25: {'size': 5, 'category': 'standard', 'fragility': 'fragile', 'priority': 'low'},
    26: {'size': 3, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'low'},
    27: {'size': 5, 'category': 'standard', 'fragility': 'sturdy', 'priority': 'low'},
}


def validate_solution():
    """
    Reads a JSON solution from stdin and validates it against all problem constraints.
    """
    try:
        solution = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print(json.dumps({"valid": False, "message": "Invalid JSON format."}))
        return

    if not solution.get("feasible", False):
        print(json.dumps({"valid": True, "message": "Solution is marked as infeasible, which is a valid (though not useful) state."}))
        return

    # Generate ASP facts from the JSON solution
    asp_facts = []
    all_item_ids_in_solution = set()

    # Add ground truth item data
    for i, data in ITEMS_DATA.items():
        asp_facts.append(f"item_data({i}, {data['size']}, {data['category']}, {data['fragility']}, {data['priority']}).")

    if 'bins' not in solution or not isinstance(solution['bins'], list):
        print(json.dumps({"valid": False, "message": "Missing or invalid 'bins' array in solution."}))
        return

    for b in solution["bins"]:
        bin_id = b.get("bin_id")
        if bin_id is None:
            print(json.dumps({"valid": False, "message": "A bin is missing 'bin_id'."}))
            return

        if "items" not in b or not isinstance(b['items'], list):
            print(json.dumps({"valid": False, "message": f"Bin {bin_id} has missing or invalid 'items' array."}))
            return

        for item in b["items"]:
            item_id = item.get("item_id")
            if item_id is None:
                print(json.dumps({"valid": False, "message": f"An item in bin {bin_id} is missing 'item_id'."}))
                return

            if item_id in all_item_ids_in_solution:
                print(json.dumps({"valid": False, "message": f"Item {item_id} is assigned to multiple bins."}))
                return
            all_item_ids_in_solution.add(item_id)
            asp_facts.append(f"assign({item_id}, {bin_id}).")

    # Check if all items are packed
    if len(all_item_ids_in_solution) != len(ITEMS_DATA):
        print(json.dumps({"valid": False, "message": f"Incorrect number of items packed. Expected {len(ITEMS_DATA)}, got {len(all_item_ids_in_solution)}."}))
        return
    if all_item_ids_in_solution != set(ITEMS_DATA.keys()):
        print(json.dumps({"valid": False, "message": "The set of packed items does not match the required set of items."}))
        return


    # ASP program for validation
    asp_validator = """
    % Constants
    #const bin_capacity = 20.
    #const fragile_limit = 2.
    #const priority_bin_limit = 6.

    % --- CONSTRAINTS TO CHECK ---

    % 1. Bin capacity exceeded
    violation(capacity_exceeded, B) :-
        assign(_, B),
        #sum { S, I : assign(I, B), item_data(I, S, _, _, _) } > bin_capacity.

    % 2. Incompatible items in the same bin
    violation(incompatible_items, B) :-
        assign(I1, B), item_data(I1, _, electronics, _, _),
        assign(I2, B), item_data(I2, _, liquid, _, _).

    % 3. Fragility limit exceeded
    violation(fragile_limit_exceeded, B) :-
        assign(_, B),
        #count { I : assign(I, B), item_data(I, _, _, fragile, _) } > fragile_limit.

    % 4. High priority item in non-priority bin
    violation(priority_placement, I) :-
        assign(I, B), item_data(I, _, _, _, high), B > priority_bin_limit.

    % 5. Check if all items are assigned exactly once (already checked in Python)
    % An item is assigned to N bins. N should be 1.
    violation(multiple_assignment, I) :-
        item_data(I,_,_,_,_),
        #count { B : assign(I,B) } != 1.

    % --- FINAL VERDICT ---
    is_valid :- not violation(_, _).
    """

    ctl = clingo.Control()
    ctl.add("base", [], "\n".join(asp_facts))
    ctl.add("validator", [], asp_validator)
    ctl.ground([("base", []), ("validator", [])])

    is_valid = False
    violations = []

    def on_model(model):
        nonlocal is_valid
        for atom in model.symbols(shown=True):
            if atom.name == "is_valid":
                is_valid = True
            if atom.name == "violation":
                violations.append(str(atom))

    ctl.solve(on_model=on_model)

    if is_valid:
        print(json.dumps({"valid": True, "message": "Solution is valid."}))
    else:
        message = "Solution is invalid. Violations: " + ", ".join(violations)
        print(json.dumps({"valid": False, "message": message}))

if __name__ == "__main__":
    validate_solution()
