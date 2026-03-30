#!/usr/bin/env python3
"""
Reference Model (Validator): Car Sequencing Problem
====================================================
This script validates a car sequencing solution against the problem's constraints
by converting the solution into ASP facts and checking for constraint violations.
"""

import sys
import json
import clingo

def validate_solution(solution_json: str) -> dict:
    """
    Validates a car sequencing solution using an ASP checker model.

    Args:
        solution_json: A JSON string representing the solution.

    Returns:
        A dictionary with validation results.
    """
    try:
        solution_data = json.loads(solution_json)
        if not solution_data.get("solution_found"):
            return {"valid": False, "message": "Input indicates no solution was found."}
        sequence = solution_data.get("sequence")
        if not sequence or len(sequence) != 12:
            return {"valid": False, "message": f"Sequence must have 12 cars, but found {len(sequence) if sequence else 0}."}
    except json.JSONDecodeError:
        return {"valid": False, "message": "Invalid JSON input."}

    # Convert JSON sequence to ASP facts
    solution_facts = []
    seen_positions = set()
    try:
        for item in sequence:
            pos = item["position"]
            car_type = item["car_type"].lower()
            if not (1 <= pos <= 12 and car_type in ['a', 'b', 'c', 'd']):
                raise ValueError(f"Invalid position or car_type: {item}")
            if pos in seen_positions:
                raise ValueError(f"Duplicate position {pos} in sequence.")
            seen_positions.add(pos)
            solution_facts.append(f"assign({pos}, {car_type}).")
    except (ValueError, KeyError, AttributeError) as e:
        return {"valid": False, "message": f"Error parsing sequence data: {e}"}

    # ASP program with only constraints (checker)
    checker_program = """
    % --- Problem Definition ---
    pos(1..12).
    car_type(a;b;c;d).
    car_count(a,3). car_count(b,3). car_count(c,4). car_count(d,2).
    option(1..5).

    has_option(a,1).
    has_option(b,3). has_option(b,4).
    has_option(c,2).
    has_option(d,5).

    % --- Helper rules to interpret options ---
    car_has_option(P, O) :- assign(P, T), has_option(T, O).

    % Rule C1 (Hierarchical): Option 5 implies Option 1.
    % option_present/2 is the effective option for constraint checking.
    option_present(P, 1) :- car_has_option(P, 1).
    option_present(P, 1) :- car_has_option(P, 5).
    option_present(P, O) :- car_has_option(P, O), O != 1, O != 5.

    % --- Constraints to be Violated ---

    % Car count validation
    :- { assign(P, T) : pos(P) } != N, car_count(T, N).

    % Rule C2 (Positional Ban): No EV (Opt 4) in pos 1 or 12.
    :- option_present(1, 4).
    :- option_present(12, 4).

    % Rule C3 (Equipment Cooldown): Opt 2 requires a 2-slot gap.
    :- option_present(P, 2), option_present(P+1, 2), pos(P), pos(P+1).
    :- option_present(P, 2), option_present(P+2, 2), pos(P), pos(P+2).

    % Rule C4 (Standard Capacity): At most 2 sunroofs (Opt 1) in any 4 consecutive.
    :- pos(P), P <= 9, #count{ P1 : option_present(P1, 1), P <= P1, P1 < P+4 } > 2.

    % Rule C5 (Conditional Capacity): For Opt 3...
    % Helper: True if car at P-1 has EV powertrain.
    preceded_by_ev(P) :- P > 1, pos(P), option_present(P-1, 4).

    % Stricter rule: max 1 of Opt 3 in 4 if preceded by EV.
    :- preceded_by_ev(P), pos(P), P <= 9, #count{ P1 : option_present(P1, 3), P <= P1, P1 < P+4 } > 1.

    % Normal rule: max 2 of Opt 3 in 4 if NOT preceded by EV.
    :- not preceded_by_ev(P), pos(P), P <= 9, #count{ P1 : option_present(P1, 3), P <= P1, P1 < P+4 } > 2.
    """

    control = clingo.Control(["--warn=none"])
    control.add("base", [], "\n".join(solution_facts))
    control.add("base", [], checker_program)
    control.ground([("base", [])])

    solve_result = control.solve()

    if solve_result.satisfiable:
        return {"valid": True, "message": "Solution is valid and satisfies all constraints."}
    else:
        return {"valid": False, "message": "Solution is invalid; one or more constraints are violated."}


if __name__ == "__main__":
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        result = validate_solution(input_json)
        print(json.dumps(result))
    else:
        print(json.dumps({"valid": False, "message": "This script is a validator. Pipe a JSON solution to stdin."}))
