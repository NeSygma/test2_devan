#!/usr/bin/env python3
"""
Reference model for the Nim Game problem.
Validates solutions from stdin and checks optimality.
"""

import json
import sys
from typing import List, Dict, Tuple, Any

# --- Problem Constants ---
INITIAL_PILES = [6, 7, 10, 13]
CURRENT_PLAYER = 1
POWERS = {1: "split", 2: "merge"}

# Expected optimal value
EXPECTED_OPTIMAL_MOVES_COUNT = 3

def calculate_nim_sum(piles: List[int]) -> int:
    """Calculates the bitwise XOR sum of a list of numbers."""
    result = 0
    for p in piles:
        result ^= p
    return result

def is_state_valid(piles: List[int]) -> bool:
    """Checks if a state is valid (no two piles of the same size)."""
    return len(piles) == len(set(piles))

def validate_solution(solution: Dict[str, Any]) -> Tuple[bool, str]:
    """Validates the provided solution JSON."""

    required_fields = ["initial_nim_sum", "is_winning_position", "optimal_moves", "analysis"]
    for field in required_fields:
        if field not in solution:
            return False, f"Missing required top-level field: '{field}'"

    # 1. Validate initial state analysis
    expected_nim_sum = calculate_nim_sum(INITIAL_PILES)
    if solution["initial_nim_sum"] != expected_nim_sum:
        return False, f"Incorrect initial_nim_sum. Expected {expected_nim_sum}, got {solution['initial_nim_sum']}."

    is_winning = expected_nim_sum != 0
    if solution["is_winning_position"] != is_winning:
        return False, f"Incorrect is_winning_position. Expected {is_winning}."

    if not is_winning:
        # If starting in a losing position, any move is fine. We just check for one valid move.
        if not solution["optimal_moves"]:
             return False, "Must provide at least one move, even from a losing position."
        # Further validation for losing positions is omitted for this problem.
        return True, "Valid analysis for a losing position."

    # 2. Validate optimal moves from a winning position
    if not isinstance(solution["optimal_moves"], list):
        return False, "Field 'optimal_moves' must be a list."

    if not solution["optimal_moves"]:
        return False, "A winning position must have at least one optimal move."

    for i, move in enumerate(solution["optimal_moves"]):
        move_valid, msg = validate_move(move, i)
        if not move_valid:
            return False, msg

    # Check optimality: must find the expected number of optimal moves
    if len(solution["optimal_moves"]) != EXPECTED_OPTIMAL_MOVES_COUNT:
        return False, f"Not optimal: found {len(solution['optimal_moves'])} moves, expected {EXPECTED_OPTIMAL_MOVES_COUNT}"

    return True, f"Solution valid and optimal ({EXPECTED_OPTIMAL_MOVES_COUNT} optimal moves found)"

def validate_move(move: Dict[str, Any], move_index: int) -> Tuple[bool, str]:
    """Validates a single move from the solution."""

    move_type = move.get("move_type")
    pile_idx = move.get("pile_index")

    if pile_idx is None or not (0 <= pile_idx < len(INITIAL_PILES)):
        return False, f"Move {move_index}: Invalid pile_index: {pile_idx}."

    original_pile_size = INITIAL_PILES[pile_idx]

    resulting_piles = []

    if move_type == "standard":
        stones_removed = move.get("stones_removed")
        if stones_removed is None or not (0 < stones_removed <= original_pile_size):
            return False, f"Move {move_index}: Invalid stones_removed: {stones_removed}."

        new_piles = INITIAL_PILES[:pile_idx] + INITIAL_PILES[pile_idx+1:]
        if original_pile_size - stones_removed > 0:
            new_piles.append(original_pile_size - stones_removed)
        resulting_piles = sorted(new_piles)

    elif move_type == "power_split":
        if original_pile_size % 2 != 0:
            return False, f"Move {move_index}: Split power can only be used on even piles. Pile {pile_idx} has {original_pile_size} stones."

        split_into = move.get("split_into")
        if not (isinstance(split_into, list) and len(split_into) == 2 and all(s > 0 for s in split_into)):
            return False, f"Move {move_index}: 'split_into' must be a list of two positive integers."

        if sum(split_into) != original_pile_size:
            return False, f"Move {move_index}: Split piles {split_into} do not sum to original pile size {original_pile_size}."

        new_piles = INITIAL_PILES[:pile_idx] + INITIAL_PILES[pile_idx+1:]
        new_piles.extend(split_into)
        resulting_piles = sorted(new_piles)

    else:
        return False, f"Move {move_index}: Unknown move_type: '{move_type}'."

    # Validate resulting state
    if "resulting_piles" not in move or sorted(move["resulting_piles"]) != resulting_piles:
        return False, f"Move {move_index}: Incorrect resulting_piles. Expected {resulting_piles}, got {move.get('resulting_piles')}."

    if not is_state_valid(resulting_piles):
        return False, f"Move {move_index}: Resulting state {resulting_piles} is unstable (contains duplicate pile sizes)."

    # Validate optimality
    resulting_nim_sum = calculate_nim_sum(resulting_piles)
    if resulting_nim_sum != 0:
        return False, f"Move {move_index}: Move is not optimal. Resulting nim-sum is {resulting_nim_sum}, should be 0."

    return True, "Valid optimal move."

def main():
    """Main validation function."""
    try:
        solution_json = sys.stdin.read()
        if not solution_json:
            print(json.dumps({"valid": False, "message": "Empty input."}))
            return
        solution = json.loads(solution_json)
        is_valid, message = validate_solution(solution)
        print(json.dumps({"valid": is_valid, "message": message}))
    except json.JSONDecodeError:
        print(json.dumps({"valid": False, "message": "Invalid JSON format."}))
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"An unexpected error occurred: {e}"}))

if __name__ == "__main__":
    main()
