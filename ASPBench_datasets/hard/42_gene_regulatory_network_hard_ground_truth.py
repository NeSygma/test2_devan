#!/usr/bin/env python3
"""
Reference model for the Gene Regulatory Network problem.
Validates whether proposed steady states are correct based on a complex,
hierarchical rule set.
"""

import json
import sys
from typing import Dict, List

GENES = sorted(['master_reg', 'm1_g1', 'm1_g2', 'm1_g3', 'm2_g1', 'm2_g2', 'm2_g3', 'reporter'])
MODULE_1 = ['m1_g1', 'm1_g2', 'm1_g3']
MODULE_2 = ['m2_g1', 'm2_g2', 'm2_g3']

def compute_next_state(current_state: Dict[str, int]) -> Dict[str, int]:
    """Compute the next state based on the complex regulatory rules."""
    next_state = {}

    # --- Rule 1: master_reg ---
    m1_active_count = sum(current_state[g] for g in MODULE_1)
    m2_active_count = sum(current_state[g] for g in MODULE_2)
    next_state['master_reg'] = 1 if m1_active_count == m2_active_count else 0

    # --- Conditional Rules based on master_reg's CURRENT state ---
    if current_state['master_reg'] == 0:
        # --- Module 1 Rules when master_reg is inactive ---
        next_state['m1_g3'] = 1 # Constitutively active
        next_state['m1_g2'] = 1 if current_state['m1_g3'] == 0 else 0
        next_state['m1_g1'] = 1 if current_state['m1_g2'] == 0 else 0

        # --- Module 2 Rules when master_reg is inactive ---
        m1_active_count_for_m2 = sum(current_state[g] for g in MODULE_1)
        next_state['m2_g1'] = 1 if current_state['m1_g1'] == 0 and current_state['m1_g2'] == 0 else 0
        next_state['m2_g2'] = 1 if m1_active_count_for_m2 == 2 else 0
        next_state['m2_g3'] = 1 if current_state['m2_g1'] == 1 and current_state['m2_g2'] == 0 else 0

    else: # master_reg is active
        # --- Module 1 Rules when master_reg is active ---
        next_state['m1_g1'] = 0
        next_state['m1_g2'] = 0
        next_state['m1_g3'] = 0

        # --- Module 2 Rules when master_reg is active (repressive ring) ---
        next_state['m2_g1'] = 1 if current_state['m2_g2'] == 0 else 0
        next_state['m2_g2'] = 1 if current_state['m2_g3'] == 0 else 0
        next_state['m2_g3'] = 1 if current_state['m2_g1'] == 0 else 0

    # --- Rule 4: reporter ---
    m2_inactive_count = sum(1 for g in MODULE_2 if current_state[g] == 0)
    next_state['reporter'] = 1 if m2_inactive_count >= 2 else 0

    return next_state

def is_steady_state(state: Dict[str, int]) -> bool:
    """Check if a state is a steady state (fixed point)."""
    next_state = compute_next_state(state)
    return state == next_state

def find_all_steady_states() -> List[Dict[str, int]]:
    """Find all steady states by exhaustive search over the 2^8 state space."""
    steady_states = []
    num_genes = len(GENES)

    for i in range(2**num_genes):
        state = {}
        for j, gene in enumerate(GENES):
            state[gene] = (i >> j) & 1

        if is_steady_state(state):
            steady_states.append(state)

    return steady_states

def validate_solution(solution):
    """Validate the proposed solution from the user."""
    if not isinstance(solution, dict) or "steady_states" not in solution:
        return False, "Solution must be a JSON object with a 'steady_states' key."

    user_states = solution["steady_states"]
    if not isinstance(user_states, list):
        return False, "'steady_states' must be a list."

    # Validate each state provided by the user
    for i, state in enumerate(user_states):
        if not isinstance(state, dict):
            return False, f"State {i} is not a dictionary."
        if set(state.keys()) != set(GENES):
            return False, f"State {i} has incorrect gene keys. Expected: {GENES}"
        if not all(v in [0, 1] for v in state.values()):
            return False, f"State {i} contains values other than 0 or 1."
        if not is_steady_state(state):
            return False, f"State {json.dumps(state)} is not a valid steady state."

    # Compare user's states with the ground truth
    try:
        correct_states = find_all_steady_states()
    except Exception as e:
        return False, f"Internal validation error: {e}"

    def state_to_tuple(s):
        return tuple(sorted(s.items()))

    user_states_set = {state_to_tuple(s) for s in user_states}
    correct_states_set = {state_to_tuple(s) for s in correct_states}

    if len(user_states_set) != len(user_states):
        return False, "Duplicate steady states found in solution."

    if user_states_set != correct_states_set:
        return False, f"Incorrect set of steady states. Expected {len(correct_states_set)}, but got {len(user_states_set)}."

    return True, f"Solution is correct. Found {len(correct_states_set)} steady state(s)."

def main():
    """Load solution from stdin and validate it."""
    try:
        solution = json.loads(sys.stdin.read())
        is_valid, message = validate_solution(solution)
    except json.JSONDecodeError:
        is_valid, message = False, "Invalid JSON input."
    except Exception as e:
        is_valid, message = False, f"An unexpected error occurred: {e}"

    result = {"valid": is_valid, "message": message}
    print(json.dumps(result))
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
