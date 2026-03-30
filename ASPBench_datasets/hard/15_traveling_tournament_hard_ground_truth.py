#!/usr/bin/env python3
"""
Reference model for Traveling Tournament Problem (Hard).

This script validates a given schedule in JSON format against all problem constraints.
It reads a JSON solution from stdin, converts it to ASP facts, and uses a clingo-based
validator to check for feasibility.
"""
import json
import sys
import clingo
from math import sqrt

def validate_schedule(solution):
    """
    Validates the tournament schedule using an ASP model.

    Args:
        solution (dict): A dictionary containing the schedule.

    Returns:
        dict: A dictionary with 'valid' status and a 'message'.
    """
    if not solution or "schedule" not in solution:
        return {"valid": False, "message": "Invalid input format: 'schedule' key missing."}

    schedule = solution["schedule"]

    # Generate ASP facts from the solution
    facts = []
    if isinstance(schedule, list):
        for r, round_matches in enumerate(schedule, 1):
            if isinstance(round_matches, list):
                for match in round_matches:
                    if isinstance(match, dict) and "home" in match and "away" in match:
                        h = match["home"].lower()
                        a = match["away"].lower()
                        facts.append(f"match({h},{a},{r}).")

    # ASP program for validation
    validator_program = """
    % --- Base Facts & Rules ---
    team(a;b;c;d;e;f).
    round(1..10).

    % --- Constraint 1: Double Round-Robin ---
    % Each pair plays exactly once with a specific home/away assignment.
    :- team(T1), team(T2), T1 < T2, #count{ R : match(T1,T2,R) } != 1.
    :- team(T1), team(T2), T1 < T2, #count{ R : match(T2,T1,R) } != 1.

    % --- Constraint 2: Round Structure ---
    % Each team plays exactly once per round (home or away).
    plays(T,R) :- match(T,_,R).
    plays(T,R) :- match(_,T,R).
    :- team(T), round(R), not plays(T,R).
    :- team(T), round(R), match(T,A1,R), match(T,A2,R), A1 != A2.
    :- team(T), round(R), match(H1,T,R), match(H2,T,R), H1 != H2.
    :- team(T), round(R), match(T,_,R), match(_,T,R).
    % Each round has exactly 3 matches.
    :- round(R), #count{ H,A : match(H,A,R) } != 3.
    % Exactly 10 rounds with matches.
    :- #count{ R : round(R), match(_,_,R) } != 10.

    % --- Constraint 3: Stateful Travel (Setup) ---
    location_id(a). location_id(b). location_id(c). location_id(d). location_id(e). location_id(f).
    distance(a,b,100). distance(a,c,94). distance(a,d,150). distance(a,e,180). distance(a,f,170).
    distance(b,c,94). distance(b,d,180). distance(b,e,150). distance(b,f,94).
    distance(c,d,86). distance(c,e,86). distance(c,f,100).
    distance(d,e,100). distance(d,f,170).
    distance(e,f,94).
    distance(X,Y,D) :- distance(Y,X,D), team(X), team(Y).

    location(T, 0, T) :- team(T).
    location(T, R, T) :- match(T, _, R).
    location(T, R, H) :- match(H, T, R), H != T.

    % --- Constraint 4: Consecutive Game Limit (max 3) ---
    :- team(T), round(R), R <= 7, match(T,_,R), match(T,_,R+1), match(T,_,R+2), match(T,_,R+3).
    :- team(T), round(R), R <= 7, match(_,T,R), match(_,T,R+1), match(_,T,R+2), match(_,T,R+3).

    % --- Constraint 5: Rivalry Constraint ---
    :- match(a,b,1); match(b,a,1).
    :- match(c,d,1); match(d,c,1).

    % --- Constraint 6: Mandatory Break ---
    % Each team must have at least one H-H sequence.
    :- team(T), not #count{ R : match(T,_,R), match(T,_,R+1), R < 10 } >= 1.

    % --- Constraint 7: Travel Fatigue ---
    travel(T, R, D) :- match(H, T, R), location(T, R-1, PrevLoc), distance(PrevLoc, H, D).
    % If travel > 140 (14.0), must be home next round.
    :- travel(T, R, D), D > 140, match(_, T, R+1).

    % --- Main validation rule ---
    holds :- not violated.
    violated :- team(T1), team(T2), T1 < T2, #count{ R : match(T1,T2,R) } != 1.
    violated :- team(T1), team(T2), T1 < T2, #count{ R : match(T2,T1,R) } != 1.
    violated :- team(T), round(R), not plays(T,R).
    violated :- team(T), round(R), match(T,A1,R), match(T,A2,R), A1 != A2.
    violated :- team(T), round(R), match(H1,T,R), match(H2,T,R), H1 != H2.
    violated :- team(T), round(R), match(T,_,R), match(_,T,R).
    violated :- round(R), #count{ H,A : match(H,A,R) } != 3.
    violated :- #count{ R : round(R), match(_,_,R) } != 10.
    violated :- team(T), round(R), R <= 7, match(T,_,R), match(T,_,R+1), match(T,_,R+2), match(T,_,R+3).
    violated :- team(T), round(R), R <= 7, match(_,T,R), match(_,T,R+1), match(_,T,R+2), match(_,T,R+3).
    violated :- match(a,b,1); match(b,a,1).
    violated :- match(c,d,1); match(d,c,1).
    violated :- team(T), not #count{ R : match(T,_,R), match(T,_,R+1), R < 10 } >= 1.
    violated :- travel(T, R, D), D > 140, match(_, T, R+1).
    """

    control = clingo.Control(["--warn=none"])
    control.add("base", [], "\n".join(facts))
    control.add("validator", [], validator_program)

    control.ground([("base", []), ("validator", [])])

    holds = False
    with control.solve(yield_=True) as handle:
        for model in handle:
            if model.contains(clingo.Function("holds")):
                holds = True
                break

    if holds:
        return {"valid": True, "message": "All constraints are satisfied."}
    else:
        return {"valid": False, "message": "One or more constraints are violated."}


if __name__ == "__main__":
    try:
        solution_json = json.loads(sys.stdin.read())
        result = validate_schedule(solution_json)
    except json.JSONDecodeError:
        result = {"valid": False, "message": "Failed to decode JSON from stdin."}
    except Exception as e:
        result = {"valid": False, "message": f"An unexpected error occurred: {e}"}

    print(json.dumps(result))
