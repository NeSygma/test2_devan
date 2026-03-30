#!/usr/bin/env python3
"""
Reference model for the Weighted Vertex Cover problem.
Validates solution from stdin and checks optimality.
"""

import clingo
import json
import sys

# Expected optimal value
EXPECTED_OPTIMAL_COST = 12

def get_problem_definition():
    """Returns the ASP facts and constraints defining the problem."""
    return """
    % --- Problem Instance Definition ---

    % Vertices
    vertex(0..15).

    % Vertex Costs
    high_cost(2). high_cost(10). high_cost(14).
    cost(V, 3) :- high_cost(V).
    cost(V, 1) :- vertex(V), not high_cost(V).

    % Standard Edges
    edge(1,3). edge(1,4). edge(2,6). edge(3,7). edge(4,8).
    edge(5,11). edge(6,7). edge(7,12). edge(8,12). edge(11,13).
    edge(12,13). edge(13,14).

    % Heavy Edges
    heavy_edge(0,5). heavy_edge(9,10). heavy_edge(14,15).

    % Master Vertices
    master(0). master(15).

    % Antagonistic Pairs
    pair(1,2). pair(8,9).

    % --- CONSTRAINTS FOR VALIDATION (NO CHOICE RULES) ---

    % 1. Standard edge coverage
    :- edge(U,V), not in_cover(U), not in_cover(V).

    % 2. Antagonistic pair constraint
    :- pair(U,V), in_cover(U), in_cover(V).

    % 3. Heavy edge coverage constraint with master vertex exception
    % A heavy edge is covered if both endpoints are in, OR if a master endpoint is in.
    is_covered_heavy(U,V) :- heavy_edge(U,V), in_cover(U), in_cover(V).
    is_covered_heavy(U,V) :- heavy_edge(U,V), master(U), in_cover(U).
    is_covered_heavy(U,V) :- heavy_edge(U,V), master(V), in_cover(V).
    :- heavy_edge(U,V), not is_covered_heavy(U,V).
    """

def verify_solution(solution_data: dict) -> dict:
    """
    Verifies the solution against the problem's constraints using ASP.
    """
    if not all(k in solution_data for k in ["vertex_cover", "total_cost"]):
        return {"valid": False, "message": "Missing 'vertex_cover' or 'total_cost' key."}

    vertex_cover = solution_data["vertex_cover"]
    total_cost = solution_data["total_cost"]

    # --- Convert solution to ASP facts ---
    asp_solution_facts = ""
    for v in vertex_cover:
        asp_solution_facts += f"in_cover({v}).\n"

    # --- Check total_cost matches the provided cover ---
    high_cost_nodes = {2, 10, 14}
    calculated_cost = 0
    for v in vertex_cover:
        if v in high_cost_nodes:
            calculated_cost += 3
        else:
            calculated_cost += 1

    if calculated_cost != total_cost:
        return {
            "valid": False,
            "message": f"Incorrect total_cost. Provided: {total_cost}, Calculated: {calculated_cost}."
        }

    # --- Use Clingo to check for constraint violations ---
    program = get_problem_definition() + asp_solution_facts

    ctl = clingo.Control(["--warn=none"])
    try:
        ctl.add("base", [], program)
        ctl.ground([("base", [])])
    except RuntimeError as e:
        return {"valid": False, "message": f"ASP grounding error: {e}"}

    is_sat = ctl.solve().satisfiable

    if not is_sat:
        return {"valid": False, "message": "Solution is invalid. One or more constraints were violated."}

    # Check optimality
    if calculated_cost != EXPECTED_OPTIMAL_COST:
        return {"valid": False, "message": f"Not optimal: total_cost={calculated_cost}, expected {EXPECTED_OPTIMAL_COST}"}

    return {"valid": True, "message": f"Solution is valid and optimal (total_cost={EXPECTED_OPTIMAL_COST})"}

def main():
    """Main entry point for verification."""
    try:
        solution_json = sys.stdin.read()
        solution_data = json.loads(solution_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON input: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Error reading solution: {e}"}))
        sys.exit(1)

    result = verify_solution(solution_data)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
