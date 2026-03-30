#!/usr/bin/env python3
"""
Reference model for Nim Game Strategy problem.
Validates nim-sum calculations and strategy analysis.
"""

import json
import sys
from typing import List, Dict, Tuple


def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def calculate_nim_sum(piles: List[int]) -> int:
    """Calculate nim-sum (XOR) of all piles"""
    result = 0
    for pile in piles:
        result ^= pile
    return result


def get_problem_setup():
    """Get the problem setup"""
    return {
        "initial_piles": [3, 4, 5],
        "current_player": 1
    }


def validate_move(pile: int, stones: int, initial_piles: List[int], resulting_piles: List[int]) -> Tuple[bool, str]:
    """Validate a single move"""

    # Check pile index
    if pile < 1 or pile > len(initial_piles):
        return False, f"Invalid pile index: {pile}"

    pile_idx = pile - 1

    # Check stones to remove
    if stones <= 0:
        return False, f"Must remove at least 1 stone"

    if stones > initial_piles[pile_idx]:
        return False, f"Cannot remove {stones} stones from pile {pile} with only {initial_piles[pile_idx]} stones"

    # Check resulting piles
    expected_piles = initial_piles[:]
    expected_piles[pile_idx] -= stones

    if resulting_piles != expected_piles:
        return False, f"Incorrect resulting piles: expected {expected_piles}, got {resulting_piles}"

    return True, "Valid move"


def is_optimal_move(pile: int, stones: int, initial_piles: List[int], initial_nim_sum: int) -> bool:
    """Check if a move is optimal (makes nim-sum zero from winning position)"""

    if initial_nim_sum == 0:
        # In losing position, all moves are bad
        return False

    pile_idx = pile - 1
    resulting_piles = initial_piles[:]
    resulting_piles[pile_idx] -= stones

    resulting_nim_sum = calculate_nim_sum(resulting_piles)

    # Optimal move makes nim-sum zero
    return resulting_nim_sum == 0


def validate_solution(solution: Dict) -> Tuple[bool, str]:
    """Validate the nim game solution"""

    if not solution:
        return False, "No solution provided"

    required_fields = ["game_state", "optimal_moves", "nim_sum", "analysis"]
    for field in required_fields:
        if field not in solution:
            return False, f"Missing field: {field}"

    setup = get_problem_setup()
    initial_piles = setup["initial_piles"]

    # Validate nim-sum calculation
    expected_nim_sum = calculate_nim_sum(initial_piles)
    if solution["nim_sum"] != expected_nim_sum:
        return False, f"Incorrect nim-sum: expected {expected_nim_sum}, got {solution['nim_sum']}"

    # Validate game state
    is_winning_position = expected_nim_sum != 0
    expected_game_state = "winning" if is_winning_position else "losing"

    if solution["game_state"] != expected_game_state:
        return False, f"Incorrect game state: expected {expected_game_state}, got {solution['game_state']}"

    # Validate analysis
    if "analysis" not in solution:
        return False, "Missing analysis section"

    analysis = solution["analysis"]
    if analysis.get("is_winning_position") != is_winning_position:
        return False, f"Incorrect winning position analysis: expected {is_winning_position}"

    # Validate moves
    if not isinstance(solution["optimal_moves"], list):
        return False, "optimal_moves must be a list"

    if len(solution["optimal_moves"]) == 0:
        return False, "Must provide at least one move"

    for i, move in enumerate(solution["optimal_moves"]):
        required_move_fields = ["pile", "stones", "resulting_piles"]
        for field in required_move_fields:
            if field not in move:
                return False, f"Move {i+1} missing field: {field}"

        # Validate move
        is_valid, message = validate_move(
            move["pile"],
            move["stones"],
            initial_piles,
            move["resulting_piles"]
        )

        if not is_valid:
            return False, f"Move {i+1} invalid: {message}"

        # If in winning position, check if moves are optimal
        if is_winning_position:
            if not is_optimal_move(move["pile"], move["stones"], initial_piles, expected_nim_sum):
                return False, f"Move {i+1} is not optimal: should make nim-sum zero"

    # Validate after_optimal_move analysis
    if "after_optimal_move" in analysis:
        after_analysis = analysis["after_optimal_move"]

        if is_winning_position and solution["optimal_moves"]:
            # After optimal move from winning position, should be losing position
            if after_analysis.get("nim_sum") != 0:
                return False, "After optimal move, nim-sum should be 0"
            if after_analysis.get("position") != "losing":
                return False, "After optimal move from winning position, should be losing position"

    # Verify we found at least one optimal move from winning position
    if is_winning_position and len(solution["optimal_moves"]) == 0:
        return False, "No optimal moves found from winning position"

    return True, f"Valid nim game analysis with {len(solution['optimal_moves'])} optimal moves"


def main():
    """Main validation function"""
    solution = load_solution()

    if solution is None:
        result = {"valid": False, "message": "Invalid or missing JSON input"}
    else:
        is_valid, message = validate_solution(solution)
        result = {"valid": is_valid, "message": message}

    print(json.dumps(result))


if __name__ == "__main__":
    main()
