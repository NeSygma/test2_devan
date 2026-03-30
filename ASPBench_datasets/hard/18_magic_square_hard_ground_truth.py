#!/usr/bin/env python3
"""
Reference model for the Symmetrical Quadrant Magic Square problem.

This script reads a JSON solution from stdin, converts it into ASP facts,
and uses an ASP program with only integrity constraints to verify if all
problem constraints are met. It checks for feasibility only.
"""
import json
import sys
import clingo

def main():
    """
    Reads a JSON solution from stdin and verifies it.
    """
    try:
        solution_data = json.loads(sys.stdin.read())
        square = solution_data.get("square")
        if not isinstance(square, list) or len(square) != 4:
            invalid_exit("JSON 'square' must be a 4x4 list.")
    except (json.JSONDecodeError, AttributeError):
        invalid_exit("Invalid or malformed JSON input.")

    # Convert the solution square into ASP facts
    facts = []
    try:
        for r_idx, row in enumerate(square):
            if len(row) != 4:
                invalid_exit(f"Row {r_idx} must have 4 columns.")
            for c_idx, val in enumerate(row):
                facts.append(f"square({r_idx + 1}, {c_idx + 1}, {int(val)}).")
    except (TypeError, ValueError):
        invalid_exit("All square values must be integers.")

    asp_facts = "\n".join(facts)

    # ASP program with only integrity constraints for verification
    verifier_program = """
    % --- Domain Definitions ---
    row(1..4). col(1..4). val(1..16).
    small_prime(2;3;5;7).

    % --- Verification Constraints ---

    % Constraint 1: Grid and Values (Each number 1-16 used once)
    :- #count { R,C : square(R,C,V) } != 1, val(V).
    :- #count { V : square(R,C,V) } != 1, row(R), col(C).
    :- square(R,C,V), not val(V).

    % Constraint 2: Magic Sum (Rows, Columns, Diagonals must sum to 34)
    :- row(R), #sum { V,C : square(R,C,V) } != 34.
    :- col(C), #sum { V,R : square(R,C,V) } != 34.
    :- #sum { V,I : square(I,I,V) } != 34.
    :- #sum { V,I : square(I,5-I,V) } != 34.

    % Constraint 3: Symmetrical Pairs (Opposite cells must sum to 17)
    :- row(R), col(C), R <= 2, square(R,C,V1), square(5-R, 5-C, V2), V1+V2 != 17.

    % Constraint 4: Quadrant Sums (Each 2x2 quadrant must sum to 34)
    :- #sum { V,R,C : square(R,C,V), R<=2, C<=2 } != 34. % Top-Left
    :- #sum { V,R,C : square(R,C,V), R<=2, C>=3 } != 34. % Top-Right
    :- #sum { V,R,C : square(R,C,V), R>=3, C<=2 } != 34. % Bottom-Left
    :- #sum { V,R,C : square(R,C,V), R>=3, C>=3 } != 34. % Bottom-Right

    % Constraint 5: Prime Placement (Small primes not in corners)
    :- square(1,1,V), small_prime(V).
    :- square(1,4,V), small_prime(V).
    :- square(4,1,V), small_prime(V).
    :- square(4,4,V), small_prime(V).
    """

    # --- Run Clingo Verifier ---
    ctl = clingo.Control(['--models=1'])
    ctl.add("base", [], asp_facts)
    ctl.add("verifier", [], verifier_program)
    ctl.ground([("base", []), ("verifier", [])])

    with ctl.solve(yield_=True) as handle:
        model = handle.model()
        if model is None:
            # No model means a constraint was violated, so the solution is invalid.
            print(json.dumps({"valid": False, "message": "A constraint was violated."}))
        else:
            # A model was found, meaning no constraints were violated.
            print(json.dumps({"valid": True, "message": "All constraints satisfied."}))


def invalid_exit(message):
    """Prints an error message and exits."""
    print(json.dumps({"valid": False, "message": message}))
    sys.exit(1)

if __name__ == "__main__":
    main()
