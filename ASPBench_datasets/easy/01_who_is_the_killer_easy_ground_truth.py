#!/usr/bin/env python3
"""
Reference model for Who Killed Agatha problem
Used for solution verification only.
"""

import clingo
import json
import sys

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

    # Parse solution
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    # Check required fields
    if "killer" not in solution:
        return {"valid": False, "message": "Missing required field: killer"}
    if "killer_name" not in solution:
        return {"valid": False, "message": "Missing required field: killer_name"}

    killer = solution["killer"]
    killer_name = solution["killer_name"]

    # Validate killer index
    if killer not in [0, 1, 2]:
        return {"valid": False, "message": f"Invalid killer index: {killer}. Must be 0, 1, or 2"}

    # Validate name matches index
    names = ["Agatha", "Butler", "Charles"]
    if killer_name != names[killer]:
        return {"valid": False, "message": f"Name mismatch: index {killer} should be {names[killer]}, got {killer_name}"}

    # Create clingo control
    ctl = clingo.Control()

    # Base ASP program with problem constraints
    program = f"""
    % Domain
    person(0..2).  % 0=Agatha, 1=Butler, 2=Charles
    #const agatha=0.
    #const butler=1.
    #const charles=2.
    #const victim=0.  % Agatha is the victim

    % Given solution
    killer({killer}).

    % Define hates and richer predicates
    {{ hates(X,Y) }} :- person(X), person(Y).
    {{ richer(X,Y) }} :- person(X), person(Y).

    % Constraint 1: A killer always hates their victim
    :- killer(K), not hates(K, victim).

    % Constraint 2: A killer is no richer than their victim
    :- killer(K), richer(K, victim).

    % Constraint 3: Charles hates no one that Agatha hates
    :- hates(agatha, X), hates(charles, X).

    % Constraint 4: Agatha hates everybody except the butler
    :- person(X), X != butler, not hates(agatha, X).
    :- hates(agatha, butler).

    % Constraint 5: The butler hates everyone not richer than Aunt Agatha
    :- person(X), not richer(X, agatha), not hates(butler, X).

    % Constraint 6: The butler hates everyone whom Agatha hates
    :- hates(agatha, X), not hates(butler, X).

    % Constraint 7: No one hates everyone
    :- person(X), hates(X, 0), hates(X, 1), hates(X, 2).

    % Logical constraint: no one is richer than themselves
    :- richer(X, X).

    % Transitive and antisymmetric properties of richer
    :- richer(X, Y), richer(Y, X), X != Y.
    """

    # Add program and ground
    ctl.add("base", [], program)
    ctl.ground([("base", [])])

    # Check satisfiability
    sat = False
    def on_model(model):
        nonlocal sat
        sat = True

    ctl.solve(on_model=on_model)

    if sat:
        return {"valid": True, "message": f"Solution is valid: {killer_name} is the killer"}
    else:
        return {"valid": False, "message": f"Solution violates logical constraints for killer={killer_name}"}

if __name__ == "__main__":
    # Read solution from stdin
    solution_json = sys.stdin.read()

    result = verify_solution(solution_json)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)
