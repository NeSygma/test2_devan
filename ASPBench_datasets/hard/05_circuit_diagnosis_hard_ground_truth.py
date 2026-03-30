#!/usr/bin/env python3
"""
Reference Model (Validation-Only) for Extreme Hard Circuit Diagnosis (006-EH)

This reference model does NOT optimize. It only validates whether given diagnoses
explain the observations across all tests. It also provides a small set of known
candidate diagnoses (including a witness) and reports which of them are valid.
"""

import json
from typing import Dict, List, Tuple
from itertools import product

# Expected optimal value (extracted from reference solution)
EXPECTED_OPTIMAL_COST = 3


class Circuit:
    def __init__(self):
        # Define the circuit structure
        self.components = {
            # Layer 1
            'and1': {'type': 'and', 'inputs': ['in1', 'in2'], 'output': 'w1'},
            'xor1': {'type': 'xor', 'inputs': ['in3', 'in4'], 'output': 'w2'},
            'or1':  {'type': 'or',  'inputs': ['in5', 'in6'], 'output': 'w3'},
            'and2': {'type': 'and', 'inputs': ['in7', 'in8'], 'output': 'w4'},
            'xor2': {'type': 'xor', 'inputs': ['in9', 'in10'], 'output': 'w5'},
            'not1': {'type': 'not', 'inputs': ['in1'],        'output': 'w6'},
            'or2':  {'type': 'or',  'inputs': ['in3', 'in5'], 'output': 'w7'},
            'and3': {'type': 'and', 'inputs': ['in4', 'in6'], 'output': 'w8'},

            # Layer 2
            'and4': {'type': 'and', 'inputs': ['w1', 'w2'],   'output': 'w9'},
            'or3':  {'type': 'or',  'inputs': ['w3', 'w4'],   'output': 'w10'},
            'xor4': {'type': 'xor', 'inputs': ['w5', 'w6'],   'output': 'w11'},
            'and5': {'type': 'and', 'inputs': ['w2', 'w7'],   'output': 'w12'},
            'or4':  {'type': 'or',  'inputs': ['w8', 'w5'],   'output': 'w13'},
            'not2': {'type': 'not', 'inputs': ['w7'],         'output': 'w14'},
            'xor5': {'type': 'xor', 'inputs': ['w6', 'w1'],   'output': 'w15'},
            'and6': {'type': 'and', 'inputs': ['w4', 'w8'],   'output': 'w16'},

            # Layer 3
            'xor6': {'type': 'xor', 'inputs': ['w9', 'w10'],  'output': 'w17'},
            'and7': {'type': 'and', 'inputs': ['w11', 'w12'], 'output': 'w18'},
            'or5':  {'type': 'or',  'inputs': ['w13', 'w14'], 'output': 'w19'},
            'xor7': {'type': 'xor', 'inputs': ['w15', 'w16'], 'output': 'w20'},
            'and8': {'type': 'and', 'inputs': ['w9', 'w13'],  'output': 'w21'},
            'or6':  {'type': 'or',  'inputs': ['w10', 'w12'], 'output': 'w22'},
            'not3': {'type': 'not', 'inputs': ['w11'],        'output': 'w23'},
            'xor8': {'type': 'xor', 'inputs': ['w14', 'w16'], 'output': 'w24'},

            # Layer 4
            'and9':  {'type': 'and', 'inputs': ['w17', 'w18'], 'output': 'w25'},
            'or7':   {'type': 'or',  'inputs': ['w19', 'w20'], 'output': 'w26'},
            'xor9':  {'type': 'xor', 'inputs': ['w21', 'w22'], 'output': 'w27'},
            'and10': {'type': 'and', 'inputs': ['w23', 'w24'], 'output': 'w28'},
            'or8':   {'type': 'or',  'inputs': ['w25', 'w26'], 'output': 'w29'},
            'xor10': {'type': 'xor', 'inputs': ['w27', 'w28'], 'output': 'w30'},
            'and11': {'type': 'and', 'inputs': ['w22', 'w24'], 'output': 'w31'},
            'or9':   {'type': 'or',  'inputs': ['w21', 'w23'], 'output': 'w32'},

            # Final stage
            'xor11': {'type': 'xor', 'inputs': ['w29', 'w30'], 'output': 'u1'},
            'and12': {'type': 'and', 'inputs': ['w31', 'w32'], 'output': 'u2'},
            'or10':  {'type': 'or',  'inputs': ['w17', 'w29'], 'output': 'u3'},
            'not4':  {'type': 'not', 'inputs': ['u2'],         'output': 'out2'},
            'or11':  {'type': 'or',  'inputs': ['u1', 'u3'],   'output': 'out1'},
            'xor12': {'type': 'xor', 'inputs': ['w30', 'w31'], 'output': 'out3'},
        }

        # Topological order respecting dependencies
        self.ordered_components = [
            # Layer 1
            'and1', 'xor1', 'or1', 'and2', 'xor2', 'not1', 'or2', 'and3',
            # Layer 2
            'and4', 'or3', 'xor4', 'and5', 'or4', 'not2', 'xor5', 'and6',
            # Layer 3
            'xor6', 'and7', 'or5', 'xor7', 'and8', 'or6', 'not3', 'xor8',
            # Layer 4
            'and9', 'or7', 'xor9', 'and10', 'or8', 'xor10', 'and11', 'or9',
            # Final stage
            'xor11', 'and12', 'or10', 'not4', 'or11', 'xor12'
        ]

        # Test input vectors (8 tests)
        self.tests: List[Dict[str, int]] = [
            {'in1':1,'in2':1,'in3':0,'in4':1,'in5':1,'in6':0,'in7':1,'in8':0,'in9':1,'in10':0},  # t1
            {'in1':0,'in2':1,'in3':1,'in4':0,'in5':1,'in6':1,'in7':0,'in8':1,'in9':1,'in10':1},  # t2
            {'in1':1,'in2':0,'in3':1,'in4':1,'in5':0,'in6':0,'in7':1,'in8':1,'in9':0,'in10':0},  # t3
            {'in1':0,'in2':0,'in3':0,'in4':1,'in5':1,'in6':1,'in7':1,'in8':0,'in9':0,'in10':1},  # t4
            {'in1':1,'in2':1,'in3':1,'in4':1,'in5':0,'in6':1,'in7':0,'in8':0,'in9':1,'in10':0},  # t5
            {'in1':0,'in2':1,'in3':0,'in4':0,'in5':1,'in6':0,'in7':1,'in8':1,'in9':0,'in10':1},  # t6
            {'in1':1,'in2':0,'in3':0,'in4':1,'in5':0,'in6':1,'in7':1,'in8':0,'in9':1,'in10':1},  # t7
            {'in1':0,'in2':0,'in3':1,'in4':0,'in5':1,'in6':0,'in7':0,'in8':1,'in9':1,'in10':0},  # t8
        ]

        # Observed outputs for each test (constant across tests here)
        self.observed: List[Dict[str, int]] = [
            {'out1': 0, 'out2': 1, 'out3': 0},  # t1
            {'out1': 0, 'out2': 1, 'out3': 0},  # t2
            {'out1': 0, 'out2': 1, 'out3': 0},  # t3
            {'out1': 0, 'out2': 1, 'out3': 0},  # t4
            {'out1': 0, 'out2': 1, 'out3': 0},  # t5
            {'out1': 0, 'out2': 1, 'out3': 0},  # t6
            {'out1': 0, 'out2': 1, 'out3': 0},  # t7
            {'out1': 0, 'out2': 1, 'out3': 0},  # t8
        ]

        # Fault modes and their costs (for info; not used for optimization here)
        self.modes = ['stuck0', 'stuck1', 'invert', 'open']
        self.mode_cost: Dict[str, int] = {'stuck0': 1, 'stuck1': 1, 'invert': 1, 'open': 2}

        # Global constraint
        self.max_faults = 3

        # A small set of known candidate diagnoses (witnesses) to validate
        # Each diagnosis is a dict: component -> mode
        self.known_candidates: List[Dict[str, str]] = [
            # Witness 1: one fault per output gate
            {'or11': 'stuck0', 'not4': 'stuck1', 'xor12': 'stuck0'},
            # Witness 2: alternative for out2 via its predecessor
            {'or11': 'stuck0', 'and12': 'stuck0', 'xor12': 'stuck0'},
        ]

    def evaluate_gate(self, gate_type: str, inputs: List[int]) -> int:
        if gate_type == 'and':
            return int(all(inputs))
        if gate_type == 'or':
            return int(any(inputs))
        if gate_type == 'not':
            return int(not inputs[0])
        if gate_type == 'xor':
            return int(inputs[0] != inputs[1])
        raise ValueError(f"Unknown gate type: {gate_type}")

    def simulate_one_test(self, test_inputs: Dict[str, int],
                          fault_modes: Dict[str, str],
                          open_values: Dict[str, int]) -> Dict[str, int]:
        """
        Simulate a single test with given fault modes.
        open_values holds per-component output for components with 'open' mode (for this test).
        """
        wires = dict(test_inputs)  # start with primary inputs

        # Pre-assign 'open' outputs
        for comp, mode in fault_modes.items():
            if mode == 'open':
                wires[self.components[comp]['output']] = open_values[comp]

        # Forward simulation respecting topological order
        for comp in self.ordered_components:
            info = self.components[comp]
            out = info['output']

            # Skip evaluation if 'open' is set (already assigned)
            if fault_modes.get(comp) == 'open':
                continue

            in_vals = [wires[sig] for sig in info['inputs']]  # all inputs must be ready

            mode = fault_modes.get(comp)
            if mode == 'stuck0':
                wires[out] = 0
            elif mode == 'stuck1':
                wires[out] = 1
            else:
                healthy = self.evaluate_gate(info['type'], in_vals)
                if mode == 'invert':
                    wires[out] = 1 - healthy
                else:
                    wires[out] = healthy  # healthy

        return wires

    def test_satisfiable(self, test_idx: int, fault_modes: Dict[str, str]) -> bool:
        """
        For a given test and fault assignment, check if there exists an assignment to all
        'open' component outputs making this test consistent with observations.
        """
        open_comps = [c for c, m in fault_modes.items() if m == 'open']
        for vals in product([0, 1], repeat=len(open_comps)):
            open_values = {c: v for c, v in zip(open_comps, vals)}
            wires = self.simulate_one_test(self.tests[test_idx], fault_modes, open_values)
            if all(wires[o] == self.observed[test_idx][o] for o in self.observed[test_idx]):
                return True
        return False

    def diagnosis_consistent(self, fault_modes: Dict[str, str]) -> bool:
        if len(fault_modes) > self.max_faults:
            return False
        return all(self.test_satisfiable(ti, fault_modes) for ti in range(len(self.tests)))

    def validate_known(self) -> List[Dict]:
        """
        Validate the built-in candidate diagnoses and report those that are consistent.
        This is validation-only; no search or optimization is performed.
        """
        valid = []
        for fm in self.known_candidates:
            if self.diagnosis_consistent(fm):
                faults_list = [{"component": comp, "mode": fm[comp]} for comp in sorted(fm.keys())]
                valid.append({
                    "faults": faults_list,
                    "cost": sum(self.mode_cost[m] for m in fm.values()),
                    "minimal": None  # Not asserted here
                })
        return valid

    def solve(self) -> Dict:
        valid = self.validate_known()
        return {
            "diagnoses": valid,
            "explanation": "Validation-only: reported known diagnoses that reproduce observations (no optimization or completeness guaranteed)."
        }


def main():
    """Validate a diagnosis solution from stdin."""
    import sys

    # Read solution from stdin
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            print(json.dumps({"valid": False, "message": "No solution provided"}))
            return

        solution = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {e}"}))
        return

    # Validate solution structure
    if "diagnoses" not in solution:
        print(json.dumps({"valid": False, "message": "Missing 'diagnoses' field"}))
        return

    diagnoses = solution["diagnoses"]
    if not isinstance(diagnoses, list) or len(diagnoses) == 0:
        print(json.dumps({"valid": False, "message": "No diagnoses provided"}))
        return

    # Create circuit and validate each diagnosis
    circuit = Circuit()
    min_cost_found = None

    for i, diag in enumerate(diagnoses):
        if "faults" not in diag:
            print(json.dumps({"valid": False, "message": f"Diagnosis {i} missing 'faults' field"}))
            return

        # Convert faults list to fault_modes dict
        fault_modes = {}
        diag_cost = 0
        for fault in diag["faults"]:
            if "component" not in fault or "mode" not in fault:
                print(json.dumps({"valid": False, "message": f"Invalid fault format in diagnosis {i}"}))
                return
            comp = fault["component"]
            mode = fault["mode"]
            if comp not in circuit.components:
                print(json.dumps({"valid": False, "message": f"Unknown component: {comp}"}))
                return
            if mode not in circuit.modes:
                print(json.dumps({"valid": False, "message": f"Unknown mode: {mode}"}))
                return
            fault_modes[comp] = mode
            diag_cost += circuit.mode_cost[mode]

        # Validate diagnosis consistency
        if not circuit.diagnosis_consistent(fault_modes):
            print(json.dumps({"valid": False, "message": f"Diagnosis {i} is inconsistent with observations"}))
            return

        # Track minimum cost
        if min_cost_found is None or diag_cost < min_cost_found:
            min_cost_found = diag_cost

    # Check optimality: at least one diagnosis must have the expected optimal cost
    if min_cost_found != EXPECTED_OPTIMAL_COST:
        print(json.dumps({"valid": False, "message": f"Not optimal: minimum cost found is {min_cost_found}, expected {EXPECTED_OPTIMAL_COST}"}))
        return

    # All diagnoses are valid and optimal
    print(json.dumps({"valid": True, "message": f"All {len(diagnoses)} diagnoses are consistent and optimal (min_cost={EXPECTED_OPTIMAL_COST})"}))


if __name__ == "__main__":
    main()


