#!/usr/bin/env python3
"""
Reference model for the Quantum Circuit Compilation problem.
Validates if a given schedule is feasible and checks optimality.
"""

import json
import sys
from typing import Dict, List, Set, Tuple

# Expected optimal values
EXPECTED_OPTIMAL_DEPTH = 3
EXPECTED_OPTIMAL_SWAPS = 1

def get_problem_instance() -> Dict:
    """Defines the fixed problem instance for this challenge."""
    instance = {
        "qubits": {f"q{i}" for i in range(8)},
        "adjacency": {
            ('q0', 'q1'), ('q1', 'q2'), ('q2', 'q3'),
            ('q4', 'q5'), ('q5', 'q6'), ('q6', 'q7'),
            ('q0', 'q4'), ('q1', 'q5'), ('q2', 'q6'), ('q3', 'q7')
        },
        "gates": {
            "h_q0": {"type": "1q", "lq": ["q0"]},
            "x_q1": {"type": "1q", "lq": ["q1"]},
            "cnot_q2_q3": {"type": "2q", "lq": ["q2", "q3"]},
            "cnot_q4_q5": {"type": "2q", "lq": ["q4", "q5"]},
            "cnot_q0_q2": {"type": "2q", "lq": ["q0", "q2"]},
            "toffoli_q5_q7_q6": {"type": "3q", "lq": ["q5", "q7", "q6"]} # c1, c2, t
        },
        "dependencies": [
            ("cnot_q4_q5", "toffoli_q5_q7_q6") # item 1 must be before item 2
        ]
    }
    # Make adjacency symmetric
    symmetric_adjacency = set()
    for q1, q2 in instance["adjacency"]:
        symmetric_adjacency.add(tuple(sorted((q1, q2))))
    instance["adjacency"] = symmetric_adjacency
    return instance

def validate_solution(solution: Dict, instance: Dict) -> Tuple[bool, str]:
    """Validates the proposed solution against the problem's constraints."""
    if not isinstance(solution, dict) or not all(k in solution for k in ["circuit_depth", "swaps_used", "gate_schedule"]):
        return False, "Invalid JSON structure: missing required keys."

    try:
        depth = solution["circuit_depth"]
        swaps_count = solution["swaps_used"]
        schedule = solution["gate_schedule"]
    except KeyError:
        return False, "Malformed solution object."

    # --- Simulation setup ---
    logical_to_physical = {q: q for q in instance["qubits"]}
    scheduled_mand_gates = set()
    all_scheduled_gates = {} # gate -> time
    total_swaps = 0

    if not schedule or schedule[-1]["time"] != depth:
        return False, f"Reported depth {depth} does not match max time in schedule."

    # --- Step-by-step simulation and validation ---
    for time_entry in sorted(schedule, key=lambda x: x['time']):
        time = time_entry["time"]
        gates_this_step = time_entry["gates"]

        physical_qubits_used = set()
        swaps_this_step = []

        for gate_name in gates_this_step:
            all_scheduled_gates[gate_name] = time

            # It's a SWAP gate
            if gate_name.startswith("swap_"):
                parts = gate_name.split('_')
                pq1, pq2 = parts[1], parts[2]
                if tuple(sorted((pq1, pq2))) not in instance["adjacency"]:
                    return False, f"Time {time}: Invalid SWAP({pq1},{pq2}). Qubits not adjacent."
                if pq1 in physical_qubits_used or pq2 in physical_qubits_used:
                    return False, f"Time {time}: Qubit conflict involving {gate_name}."
                physical_qubits_used.add(pq1)
                physical_qubits_used.add(pq2)
                swaps_this_step.append(tuple(sorted((pq1, pq2))))
                total_swaps += 1
                continue

            # It's a mandatory gate
            if gate_name not in instance["gates"]:
                return False, f"Time {time}: Unknown gate '{gate_name}'."
            if gate_name in scheduled_mand_gates:
                return False, f"Time {time}: Gate '{gate_name}' scheduled multiple times."

            scheduled_mand_gates.add(gate_name)
            gate_info = instance["gates"][gate_name]
            logical_qubits = gate_info["lq"]
            physical_qubits = [logical_to_physical[lq] for lq in logical_qubits]

            for pq in physical_qubits:
                if pq in physical_qubits_used:
                    return False, f"Time {time}: Qubit conflict on {pq} involving {gate_name}."
                physical_qubits_used.add(pq)

            # Check adjacency constraints
            if gate_info["type"] == "2q":
                pq1, pq2 = physical_qubits
                if tuple(sorted((pq1, pq2))) not in instance["adjacency"]:
                    return False, f"Time {time}: Adjacency violation for {gate_name}. Physical qubits {pq1},{pq2} not adjacent."
            elif gate_info["type"] == "3q": # toffoli_c1_c2_t
                pc1, pc2, pt = physical_qubits
                if tuple(sorted((pc1, pt))) not in instance["adjacency"]:
                    return False, f"Time {time}: Adjacency violation for {gate_name}. Control {pc1} not adjacent to target {pt}."
                if tuple(sorted((pc2, pt))) not in instance["adjacency"]:
                    return False, f"Time {time}: Adjacency violation for {gate_name}. Control {pc2} not adjacent to target {pt}."

        # Update qubit mapping based on swaps from THIS step
        physical_to_logical = {v: k for k, v in logical_to_physical.items()}
        for pq1, pq2 in swaps_this_step:
            lq1, lq2 = physical_to_logical[pq1], physical_to_logical[pq2]
            logical_to_physical[lq1], logical_to_physical[lq2] = pq2, pq1
            physical_to_logical[pq1], physical_to_logical[pq2] = lq2, lq1

    # --- Post-simulation checks ---
    if scheduled_mand_gates != set(instance["gates"].keys()):
        missing = set(instance["gates"].keys()) - scheduled_mand_gates
        return False, f"Not all mandatory gates were scheduled. Missing: {missing}"

    if total_swaps != swaps_count:
        return False, f"Reported swap count {swaps_count} does not match actual count {total_swaps}."

    for prereq, dep_gate in instance["dependencies"]:
        if prereq not in all_scheduled_gates or dep_gate not in all_scheduled_gates:
            return False, "A gate involved in a dependency was not scheduled."
        if all_scheduled_gates[prereq] >= all_scheduled_gates[dep_gate]:
            return False, f"Dependency violation: {dep_gate} must be after {prereq}."

    # Check optimality
    if depth != EXPECTED_OPTIMAL_DEPTH:
        return False, f"Not optimal: circuit_depth={depth}, expected {EXPECTED_OPTIMAL_DEPTH}"
    if swaps_count != EXPECTED_OPTIMAL_SWAPS:
        return False, f"Not optimal: swaps_used={swaps_count}, expected {EXPECTED_OPTIMAL_SWAPS}"

    return True, f"Solution valid and optimal (depth={EXPECTED_OPTIMAL_DEPTH}, swaps={EXPECTED_OPTIMAL_SWAPS})"

def main():
    try:
        solution = json.loads(sys.stdin.read())
        instance = get_problem_instance()
        is_valid, message = validate_solution(solution, instance)
    except (json.JSONDecodeError, EOFError, Exception) as e:
        is_valid = False
        message = f"Failed to parse or validate solution: {e}"

    result = {"valid": is_valid, "message": message}
    print(json.dumps(result))
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
