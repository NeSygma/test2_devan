#!/usr/bin/env python3
"""
Reference Model: Hierarchical Warehouse Network Design (Validation)
===================================================================
This script validates a given solution for the Hierarchical Warehouse Network
Design problem. It checks feasibility against all constraints and verifies
optimality.
"""

import sys
import json
import clingo

# Expected optimal value
EXPECTED_OPTIMAL_COST = 5215

def get_problem_instance_asp():
    """Returns the ASP facts for the problem instance."""
    return """
    % Entities
    hub(h1; h2).
    regional_warehouse(r1; r2; r3; r4).
    customer(c1; c2; c3; c4; c5; c6).
    time(1..4).

    % Costs
    hub_cost(h1, 1000). hub_cost(h2, 1200).
    regional_cost(r1, 200). regional_cost(r2, 250). regional_cost(r3, 220). regional_cost(r4, 180).

    % Capacities
    hub_capacity(h1, 400). hub_capacity(h2, 350).
    regional_capacity(r1, 70). regional_capacity(r2, 80). regional_capacity(r3, 60). regional_capacity(r4, 90).

    % Trucks per hub
    hub_trucks(h1, 2). hub_trucks(h2, 1).

    % Customer demand and time windows
    demand(c1, 20). window(c1, 2, 3).
    demand(c2, 30). window(c2, 1, 2).
    demand(c3, 15). window(c3, 3, 4).
    demand(c4, 25). window(c4, 1, 4).
    demand(c5, 35). window(c5, 2, 4).
    demand(c6, 10). window(c6, 1, 1).

    % Transport costs (per demand unit)
    h_r_cost(h1, r1, 5). h_r_cost(h1, r2, 6).
    h_r_cost(h2, r3, 5). h_r_cost(h2, r4, 6).
    r_c_cost(r1, c1, 10). r_c_cost(r1, c2, 12).
    r_c_cost(r2, c2, 13). r_c_cost(r2, c3, 15).
    r_c_cost(r3, c4, 9). r_c_cost(r3, c5, 11).
    r_c_cost(r4, c5, 14). r_c_cost(r4, c6, 7).

    % Connectivity constraints
    can_supply(h1, r1). can_supply(h1, r2).
    can_supply(h2, r3). can_supply(h2, r4).
    can_serve(r1, c1). can_serve(r1, c2).
    can_serve(r2, c2). can_serve(r2, c3).
    can_serve(r3, c4). can_serve(r3, c5).
    can_serve(r4, c5). can_serve(r4, c6).

    % Maintenance schedules
    maintenance(r2, 2).
    maintenance(h1, 4).
    """

def get_validation_rules():
    """Returns the ASP integrity constraints for validation."""
    return """
    % --- CONSTRAINTS ---

    % 1. Hierarchy & Opening Prerequisites
    :- delivery(_, R, _), not open_regional(R).
    :- supply_link(H, R), not open_hub(H).
    :- supply_link(H, R), not open_regional(R).
    :- delivery(C, R, _), not supply_link(_, R).

    % 2. Assignment Uniqueness
    :- customer(C), #count{ R, T : delivery(C, R, T) } != 1.
    :- regional_warehouse(R), open_regional(R), #count{ H : supply_link(H, R) } != 1.

    % 3. Connectivity
    :- supply_link(H, R), not can_supply(H, R).
    :- delivery(C, R, _), not can_serve(R, C).

    % 4. Time Windows
    valid_time(C, T) :- delivery(C, _, T), window(C, T_start, T_end), T >= T_start, T <= T_end.
    :- delivery(C, _, T), not valid_time(C, T).

    % 5. Maintenance
    :- delivery(_, R, T), maintenance(R, T).
    :- delivery(C, R, T), supply_link(H, R), maintenance(H, T).

    % 6. Capacity Constraints
    % Regional capacity
    :- open_regional(R), #sum{ D, C : delivery(C, R, _), demand(C, D) } > Cap, regional_capacity(R, Cap).
    % Hub capacity
    :- open_hub(H), #sum{ D, C, R : delivery(C, R, _), demand(C, D), supply_link(H, R) } > Cap, hub_capacity(H, Cap).

    % 7. Truck Resource Limits
    :- hub(H), time(T), #count{ C, R : delivery(C, R, T), supply_link(H, R) } > Trucks, hub_trucks(H, Trucks).
    """

def verify_solution(solution_data):
    """Verify a given solution JSON."""
    solution_facts = []
    try:
        for hub in solution_data.get("open_hubs", []):
            solution_facts.append(f'open_hub({hub.lower()}).')
        for regional in solution_data.get("open_regionals", []):
            solution_facts.append(f'open_regional({regional.lower()}).')
        for regional, hub in solution_data.get("hub_assignments", {}).items():
            solution_facts.append(f'supply_link({hub.lower()}, {regional.lower()}).')
        for delivery in solution_data.get("customer_deliveries", []):
            cust, reg, time = delivery['customer'], delivery['regional_warehouse'], delivery['time_slot']
            solution_facts.append(f'delivery({cust.lower()}, {reg.lower()}, {time}).')

        solution_facts.append(f'total_cost({solution_data.get("total_cost", -1)}).')

        asp_program = get_problem_instance_asp() + "\n" + "\n".join(solution_facts) + "\n" + get_validation_rules()

        control = clingo.Control(['--warn=none'])
        control.add("base", [], asp_program)
        control.ground([("base", [])])

        result = control.solve()

        is_valid = result.satisfiable
        if not is_valid:
            message = "Solution violates one or more constraints."
            return {"valid": False, "message": message}

        # Check optimality
        total_cost = solution_data.get("total_cost", -1)
        if total_cost != EXPECTED_OPTIMAL_COST:
            return {"valid": False, "message": f"Not optimal: total_cost={total_cost}, expected {EXPECTED_OPTIMAL_COST}"}

        message = f"Solution valid and optimal (total_cost={EXPECTED_OPTIMAL_COST})"

    except Exception as e:
        is_valid = False
        message = f"Error during validation: {e}"
        return {"valid": is_valid, "message": message}

    return {"valid": True, "message": message}

if __name__ == "__main__":
    if not sys.stdin.isatty():
        try:
            input_json = sys.stdin.read()
            solution_data = json.loads(input_json)
            result = verify_solution(solution_data)
        except json.JSONDecodeError:
            result = {"valid": False, "message": "Invalid JSON input."}
        except Exception as e:
            result = {"valid": False, "message": f"An unexpected error occurred: {str(e)}"}
        print(json.dumps(result))
    else:
        print(json.dumps({"valid": False, "message": "This script is for validation and expects a JSON solution via stdin."}))
