#!/usr/bin/env python3
"""
Reference Model for Circuit Diagnosis Problem
Validates solution from stdin
"""

import json
import sys
from typing import List, Dict, Set, Tuple
from itertools import combinations

class Circuit:
    def __init__(self):
        # Define the circuit structure
        self.components = {
            'and1': {'type': 'and', 'inputs': ['in1', 'in2'], 'output': 'w1'},
            'or1': {'type': 'or', 'inputs': ['w1', 'in3'], 'output': 'w2'},
            'notgate1': {'type': 'not', 'inputs': ['w2'], 'output': 'out1'},
            'xor1': {'type': 'xor', 'inputs': ['in1', 'in4'], 'output': 'w3'},
            'and2': {'type': 'and', 'inputs': ['w3', 'in2'], 'output': 'out2'}
        }

        # Test case
        self.inputs = {'in1': 1, 'in2': 0, 'in3': 1, 'in4': 1}
        self.expected_outputs = {'out1': 0, 'out2': 0}
        self.observed_outputs = {'out1': 1, 'out2': 0}

    def evaluate_gate(self, gate_type: str, input_values: List[int]) -> int:
        """Evaluate a logic gate given its inputs"""
        if gate_type == 'and':
            return int(all(input_values))
        elif gate_type == 'or':
            return int(any(input_values))
        elif gate_type == 'not':
            return int(not input_values[0])
        elif gate_type == 'xor':
            return int(input_values[0] != input_values[1])
        else:
            raise ValueError(f"Unknown gate type: {gate_type}")

    def is_consistent_diagnosis(self, faulty_components: Set[str]) -> bool:
        """Check if a set of faulty components can explain the observations"""
        if not faulty_components:
            # No faults - check if normal simulation matches observations
            wire_values = self.simulate_circuit(set())
            return all(wire_values.get(out, None) == self.observed_outputs[out]
                      for out in self.observed_outputs)

        # Try all possible output combinations for faulty components
        faulty_outputs = [self.components[comp_name]['output']
                         for comp_name in faulty_components]

        # Generate all possible output combinations for faulty components
        for fault_output_combo in self.generate_output_combinations(len(faulty_outputs)):
            if self.check_scenario(faulty_components, faulty_outputs, fault_output_combo):
                return True

        return False

    def simulate_circuit(self, faulty_components: Set[str]) -> Dict[str, int]:
        """Simulate the circuit with given faulty components"""
        wire_values = self.inputs.copy()
        ordered_components = ['and1', 'xor1', 'or1', 'and2', 'notgate1']

        for comp_name in ordered_components:
            comp = self.components[comp_name]

            if comp_name in faulty_components:
                continue

            input_vals = [wire_values[inp] for inp in comp['inputs']]
            output_val = self.evaluate_gate(comp['type'], input_vals)
            wire_values[comp['output']] = output_val

        return wire_values

    def generate_output_combinations(self, num_faulty: int):
        """Generate all possible output combinations for faulty components"""
        if num_faulty == 0:
            return [()]

        combos = []
        for i in range(2 ** num_faulty):
            combo = [(i >> j) & 1 for j in range(num_faulty)]
            combos.append(tuple(combo))
        return combos

    def check_scenario(self, faulty_components: Set[str], faulty_outputs: List[str],
                      fault_values: Tuple[int, ...]) -> bool:
        """Check if a specific fault scenario produces the observed outputs"""
        wire_values = self.inputs.copy()

        for i, output_wire in enumerate(faulty_outputs):
            wire_values[output_wire] = fault_values[i]

        ordered_components = ['and1', 'xor1', 'or1', 'and2', 'notgate1']

        for comp_name in ordered_components:
            if comp_name in faulty_components:
                continue

            comp = self.components[comp_name]

            if all(inp in wire_values for inp in comp['inputs']):
                input_vals = [wire_values[inp] for inp in comp['inputs']]
                output_val = self.evaluate_gate(comp['type'], input_vals)
                wire_values[comp['output']] = output_val

        return all(wire_values.get(out) == self.observed_outputs[out]
                  for out in self.observed_outputs)

    def find_all_diagnoses(self) -> List[Set[str]]:
        """Find all possible diagnoses"""
        diagnoses = []
        component_names = list(self.components.keys())

        for r in range(len(component_names) + 1):
            for combo in combinations(component_names, r):
                fault_set = set(combo)
                if self.is_consistent_diagnosis(fault_set):
                    diagnoses.append(fault_set)

        return diagnoses

    def is_minimal_diagnosis(self, diagnosis: Set[str], all_diagnoses: List[Set[str]]) -> bool:
        """Check if a diagnosis is minimal"""
        for other in all_diagnoses:
            if other != diagnosis and other.issubset(diagnosis):
                return False
        return True

def validate_solution(solution: Dict) -> Dict:
    """Validate the solution from stdin"""
    if not solution:
        return {"valid": False, "message": "No solution provided"}

    if "diagnoses" not in solution:
        return {"valid": False, "message": "Missing 'diagnoses' field"}

    diagnoses = solution["diagnoses"]

    if not isinstance(diagnoses, list):
        return {"valid": False, "message": "'diagnoses' must be a list"}

    if len(diagnoses) == 0:
        return {"valid": False, "message": "No diagnoses provided"}

    # Compute the correct minimal diagnoses
    circuit = Circuit()
    all_diagnoses = circuit.find_all_diagnoses()
    expected_minimal = []

    for diagnosis in all_diagnoses:
        if circuit.is_minimal_diagnosis(diagnosis, all_diagnoses):
            expected_minimal.append(set(diagnosis))

    # Extract provided diagnoses
    provided_diagnoses = []
    for d in diagnoses:
        if not isinstance(d, dict):
            return {"valid": False, "message": "Each diagnosis must be a dict"}

        if "components" not in d:
            return {"valid": False, "message": "Missing 'components' field in diagnosis"}

        if not isinstance(d["components"], list):
            return {"valid": False, "message": "'components' must be a list"}

        provided_diagnoses.append(set(d["components"]))

    # Check if all provided diagnoses are valid
    for diag in provided_diagnoses:
        if not circuit.is_consistent_diagnosis(diag):
            return {"valid": False,
                   "message": f"Diagnosis {sorted(list(diag))} is not consistent with observations"}

        if not circuit.is_minimal_diagnosis(diag, all_diagnoses):
            return {"valid": False,
                   "message": f"Diagnosis {sorted(list(diag))} is not minimal"}

    # Check if all expected minimal diagnoses are present
    provided_set = set(frozenset(d) for d in provided_diagnoses)
    expected_set = set(frozenset(d) for d in expected_minimal)

    if provided_set != expected_set:
        missing = expected_set - provided_set
        extra = provided_set - expected_set

        msg = []
        if missing:
            msg.append(f"Missing diagnoses: {[sorted(list(d)) for d in missing]}")
        if extra:
            msg.append(f"Extra diagnoses: {[sorted(list(d)) for d in extra]}")

        return {"valid": False, "message": "; ".join(msg)}

    return {"valid": True,
            "message": f"All {len(expected_minimal)} minimal diagnoses correctly identified"}

def main():
    try:
        data = sys.stdin.read().strip()
        if not data:
            result = {"valid": False, "message": "No input provided"}
        else:
            solution = json.loads(data)
            result = validate_solution(solution)
    except json.JSONDecodeError as e:
        result = {"valid": False, "message": f"Invalid JSON: {str(e)}"}
    except Exception as e:
        result = {"valid": False, "message": f"Error: {str(e)}"}

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
