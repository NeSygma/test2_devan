#!/usr/bin/env python3
"""
Reference model for Quantum Circuit Depth Optimization problem.
Validates whether proposed circuit schedule is correct and optimal.
"""

import json
import sys
from typing import Dict, Set


def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def get_problem_instance():
    """Define the problem instance"""
    qubits = {'q0', 'q1', 'q2', 'q3'}

    # Gates with their qubit dependencies
    gates = {
        'h_q0': {'q0'},
        'h_q1': {'q1'},
        'x_q2': {'q2'},
        'cnot_q0_q1': {'q0', 'q1'},
        'cnot_q1_q2': {'q1', 'q2'},
        'cnot_q0_q3': {'q0', 'q3'}
    }

    return qubits, gates


def compute_minimum_depth(gates: Dict[str, Set[str]]) -> int:
    """Compute the minimum possible circuit depth using greedy scheduling"""
    remaining_gates = set(gates.keys())
    time_step = 0

    while remaining_gates:
        time_step += 1
        # Find maximal set of gates that can be scheduled at this time step
        scheduled_this_step = set()
        used_qubits = set()

        for gate in list(remaining_gates):
            if gates[gate].isdisjoint(used_qubits):
                scheduled_this_step.add(gate)
                used_qubits.update(gates[gate])

        remaining_gates -= scheduled_this_step

    return time_step


def validate_solution(solution):
    """Validate the proposed solution"""
    if not isinstance(solution, dict):
        return {"valid": False, "message": "Solution must be a JSON object"}

    if "circuit_depth" not in solution:
        return {"valid": False, "message": "Missing 'circuit_depth' field"}

    if "gate_schedule" not in solution:
        return {"valid": False, "message": "Missing 'gate_schedule' field"}

    circuit_depth = solution["circuit_depth"]
    gate_schedule = solution["gate_schedule"]

    if not isinstance(circuit_depth, int) or circuit_depth <= 0:
        return {"valid": False, "message": "circuit_depth must be a positive integer"}

    if not isinstance(gate_schedule, list):
        return {"valid": False, "message": "gate_schedule must be a list"}

    qubits, gates = get_problem_instance()

    # Check that all time steps are present and valid
    scheduled_gates = set()
    max_time = 0

    for entry in gate_schedule:
        if not isinstance(entry, dict):
            return {"valid": False, "message": "Each schedule entry must be a dictionary"}

        if "time" not in entry or "gates" not in entry:
            return {"valid": False, "message": "Each schedule entry must have 'time' and 'gates' fields"}

        time_step = entry["time"]
        gates_at_time = entry["gates"]

        if not isinstance(time_step, int) or time_step <= 0:
            return {"valid": False, "message": f"Invalid time step: {time_step}"}

        if not isinstance(gates_at_time, list):
            return {"valid": False, "message": f"Gates at time {time_step} must be a list"}

        max_time = max(max_time, time_step)

        # Check that gates at this time step can be executed in parallel
        used_qubits = set()
        for gate in gates_at_time:
            if not isinstance(gate, str):
                return {"valid": False, "message": f"Gate names must be strings, got: {gate}"}

            if gate not in gates:
                return {"valid": False, "message": f"Unknown gate: {gate}"}

            if gate in scheduled_gates:
                return {"valid": False, "message": f"Gate {gate} is scheduled multiple times"}

            # Check for qubit conflicts
            gate_qubits = gates[gate]
            if gate_qubits & used_qubits:
                return {"valid": False, "message": f"Gate {gate} at time {time_step} conflicts with other gates (shared qubits)"}

            used_qubits.update(gate_qubits)
            scheduled_gates.add(gate)

    # Check that all gates are scheduled
    if scheduled_gates != set(gates.keys()):
        missing = set(gates.keys()) - scheduled_gates
        extra = scheduled_gates - set(gates.keys())
        msg = ""
        if missing:
            msg += f"Missing gates: {missing}. "
        if extra:
            msg += f"Extra gates: {extra}. "
        return {"valid": False, "message": msg}

    # Check that circuit_depth matches the schedule
    if max_time != circuit_depth:
        return {"valid": False, "message": f"circuit_depth ({circuit_depth}) doesn't match schedule max time ({max_time})"}

    # Check if the solution is optimal
    optimal_depth = compute_minimum_depth(gates)
    if circuit_depth != optimal_depth:
        return {"valid": False, "message": f"Solution is not optimal. Expected depth {optimal_depth}, got {circuit_depth}"}

    return {"valid": True, "message": f"Valid optimal schedule with depth {circuit_depth}"}


def main():
    solution = load_solution()

    if solution is None:
        result = {"valid": False, "message": "Invalid JSON input"}
    else:
        result = validate_solution(solution)

    print(json.dumps(result))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
