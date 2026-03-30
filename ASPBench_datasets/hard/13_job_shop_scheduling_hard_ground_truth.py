#!/usr/bin/env python3
"""
Reference Validator for Job Shop Scheduling Problem.

This script reads a JSON solution from stdin, converts it to ASP facts,
and uses clingo to verify that all hard constraints are satisfied.
It also checks that the makespan matches the expected optimal value.
"""
import json
import sys
import clingo

# Expected optimal value
EXPECTED_OPTIMAL_MAKESPAN = 24

def get_problem_instance_facts():
    """Returns the hard-coded problem instance as a string of ASP facts."""
    return """
    % --- Problem Instance Facts ---
    job(1..4).
    machine(1..4).
    op_count(1,3). op_count(2,4). op_count(3,3). op_count(4,4).
    operation(J, 1..N) :- job(J), op_count(J, N).

    % Operation data: op_data(Job, Op, Machine, Duration)
    op_data(1, 1, 1, 4). op_data(1, 2, 3, 5). op_data(1, 3, 2, 3).
    op_data(2, 1, 2, 6). op_data(2, 2, 4, 4). op_data(2, 3, 1, 2). op_data(2, 4, 3, 3).
    op_data(3, 1, 4, 7). op_data(3, 2, 1, 6). op_data(3, 3, 3, 2).
    op_data(4, 1, 3, 2). op_data(4, 2, 2, 5). op_data(4, 3, 4, 3). op_data(4, 4, 1, 4).

    % Special requirements
    master_op_req(1, 2).
    master_op_req(3, 1).
    master_op_req(4, 4).

    % Machine maintenance: maintenance(Machine, StartTime, EndTime)
    % Note: EndTime is exclusive, so [Start, End-1] is the down period.
    maintenance(2, 10, 12).
    maintenance(4, 15, 17).
    """

def get_integrity_constraints():
    """Returns the hard constraints as a string of ASP integrity rules."""
    return """
    % --- Hard Constraint Verification ---

    % 1. Precedence constraints within a job
    :- operation(J, O), O > 1, start(J, O-1, T1), start(J, O, T2), op_data(J, O-1, _, D1), T2 < T1 + D1.

    % 2. Resource constraint: one operation per machine at a time
    :- start(J1, O1, T1), start(J2, O2, T2), op_data(J1, O1, M, D1), op_data(J2, O2, M, _), (J1,O1) != (J2,O2), T1 <= T2, T2 < T1 + D1.

    % 3. Resource constraint: master operator can only do one task at a time
    :- start(J1, O1, T1), start(J2, O2, T2), master_op_req(J1, O1), master_op_req(J2, O2), op_data(J1, O1, _, D1), (J1,O1) != (J2,O2), T1 <= T2, T2 < T1 + D1.

    % 4. Maintenance constraint: operations cannot overlap with maintenance windows
    :- start(J, O, T), op_data(J, O, M, D), maintenance(M, TM_start, TM_end), T < TM_end, T+D > TM_start.

    % 5. All operations must be scheduled.
    :- operation(J, O), not start(J, O, _).
    """

def validate_solution(solution_json: str):
    """Validates the given solution against all hard constraints."""
    try:
        solution = json.loads(solution_json)
        if not solution.get("feasible", False):
            return {"valid": False, "message": "Input solution marked as infeasible."}

        schedule = solution.get("schedule", [])
        if not schedule:
            return {"valid": False, "message": "Schedule is empty."}

    except json.JSONDecodeError:
        return {"valid": False, "message": "Invalid JSON format."}

    # Convert schedule to ASP facts and compute makespan
    solution_facts = ""
    makespan = 0
    for op in schedule:
        solution_facts += f"start({op['job']}, {op['operation']}, {op['start']}).\n"
        # Extract operation duration from problem data to compute makespan
        job, operation, start = op['job'], op['operation'], op['start']
        duration = op.get('duration', 0)
        completion = start + duration
        if completion > makespan:
            makespan = completion

    # Combine all parts of the ASP program
    asp_program = get_problem_instance_facts() + solution_facts + get_integrity_constraints()

    # Run clingo to check for constraint violations
    ctl = clingo.Control(['--warn=none'])
    ctl.add("base", [], asp_program)
    ctl.ground([("base", [])])

    is_valid = False
    message = "Solution violates constraints (UNSAT)."

    with ctl.solve(yield_=True) as handle:
        model = handle.model()
        if model:
            is_valid = True
            message = "Solution is valid and satisfies all hard constraints."

    # Check optimality
    if is_valid and makespan != EXPECTED_OPTIMAL_MAKESPAN:
        return {"valid": False, "message": f"Not optimal: makespan={makespan}, expected {EXPECTED_OPTIMAL_MAKESPAN}"}

    if is_valid:
        message = f"Solution is valid and optimal (makespan={EXPECTED_OPTIMAL_MAKESPAN})"

    return {"valid": is_valid, "message": message}

def main():
    """Main function to read from stdin, validate, and print result."""
    try:
        solution_json = sys.stdin.read()
        result = validate_solution(solution_json)
    except Exception as e:
        result = {"valid": False, "message": f"An unexpected error occurred: {e}"}

    print(json.dumps(result))

if __name__ == "__main__":
    main()
