#!/usr/bin/env python3
"""
Reference model for Gene Regulatory Network problem.
Validates whether proposed steady states are correct.
"""

import json
import sys
from typing import Dict, List


def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def get_regulatory_rules():
    """Define the regulatory rules for the gene network"""
    def g1_next_state(state):
        """g1 is active if g2 is not active"""
        return state['g2'] == 0

    def g2_next_state(state):
        """g2 is active if g1 is not active"""
        return state['g1'] == 0

    def g3_next_state(state):
        """g3 is active if g4 is active and g5 is active"""
        return state['g4'] == 1 and state['g5'] == 1

    def g4_next_state(state):
        """g4 is active always (constitutive)"""
        return True

    def g5_next_state(state):
        """g5 is active always (constitutive)"""
        return True

    return {
        'g1': g1_next_state,
        'g2': g2_next_state,
        'g3': g3_next_state,
        'g4': g4_next_state,
        'g5': g5_next_state
    }


def compute_next_state(current_state: Dict[str, int], rules: Dict) -> Dict[str, int]:
    """Compute the next state given current state and regulatory rules"""
    next_state = {}
    for gene in current_state:
        next_state[gene] = 1 if rules[gene](current_state) else 0
    return next_state


def is_steady_state(state: Dict[str, int], rules: Dict) -> bool:
    """Check if a state is a steady state (fixed point)"""
    next_state = compute_next_state(state, rules)
    return state == next_state


def get_all_steady_states() -> List[Dict[str, int]]:
    """Find all steady states by exhaustive search"""
    genes = ['g1', 'g2', 'g3', 'g4', 'g5']
    rules = get_regulatory_rules()
    steady_states = []

    # Check all possible states (2^5 = 32 states)
    for i in range(32):
        state = {}
        for j, gene in enumerate(genes):
            state[gene] = (i >> j) & 1

        if is_steady_state(state, rules):
            steady_states.append(state)

    return steady_states


def validate_solution(solution):
    """Validate the proposed solution"""
    if not isinstance(solution, dict):
        return {"valid": False, "message": "Solution must be a JSON object"}

    if "steady_states" not in solution:
        return {"valid": False, "message": "Missing 'steady_states' field"}

    states = solution["steady_states"]
    if not isinstance(states, list):
        return {"valid": False, "message": "steady_states must be a list"}

    genes = {'g1', 'g2', 'g3', 'g4', 'g5'}
    rules = get_regulatory_rules()

    # Validate each proposed state
    for i, state in enumerate(states):
        if not isinstance(state, dict):
            return {"valid": False, "message": f"State {i} must be a dictionary"}

        # Check that all genes are present
        if set(state.keys()) != genes:
            return {"valid": False, "message": f"State {i} must contain exactly genes: {sorted(genes)}"}

        # Check that all values are 0 or 1
        for gene, value in state.items():
            if value not in [0, 1]:
                return {"valid": False, "message": f"State {i}: gene {gene} must have value 0 or 1, got {value}"}

        # Check that it's actually a steady state
        if not is_steady_state(state, rules):
            return {"valid": False, "message": f"State {i} is not a valid steady state"}

    # Get the correct steady states
    correct_states = get_all_steady_states()

    # Convert to sets for comparison (order doesn't matter)
    def state_to_tuple(state):
        return tuple(sorted(state.items()))

    proposed_set = set(state_to_tuple(state) for state in states)
    correct_set = set(state_to_tuple(state) for state in correct_states)

    if len(proposed_set) != len(states):
        return {"valid": False, "message": "Duplicate steady states found"}

    if proposed_set != correct_set:
        return {"valid": False, "message": f"Expected {len(correct_states)} steady states, found different ones"}

    return {"valid": True, "message": f"All {len(states)} steady states are correct"}


def main():
    solution = load_solution()

    if solution is None:
        result = {"valid": False, "message": "No solution provided"}
    else:
        result = validate_solution(solution)

    print(json.dumps(result))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
