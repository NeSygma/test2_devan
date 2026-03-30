#!/usr/bin/env python3
"""
Reference model for the Nontransitive Dice problem.
Validates a given JSON solution against all problem constraints.
"""

import json
import sys
from typing import Dict, List, Any, Tuple

def compute_wins(die1: List[int], die2: List[int]) -> int:
    """Computes the number of times die1 wins against die2."""
    wins = 0
    for v1 in die1:
        for v2 in die2:
            if v1 > v2:
                wins += 1
    return wins

def validate_solution(solution: Dict[str, Any]) -> Tuple[bool, str]:
    """Validates a solution against all problem constraints."""
    # Basic structure
    if not isinstance(solution, dict) or "dice" not in solution or "analysis" not in solution:
        return False, "Solution must be a dict with 'dice' and 'analysis' keys."

    dice = solution.get("dice", {})
    analysis = solution.get("analysis", {})

    # Constraint 1 & 2: Four dice, four faces each
    required_dice = {'A', 'B', 'C', 'D'}
    if set(dice.keys()) != required_dice:
        return False, f"Must have exactly dice A, B, C, D. Got: {set(dice.keys())}"

    for name, faces in dice.items():
        if not isinstance(faces, list) or len(faces) != 4:
            return False, f"Die {name} must be a list of 4 integers."

    # Constraint 3: Values in [1, 8]
    # Note: We sort faces internally for validation - presentation order doesn't affect correctness
    for name, faces in dice.items():
        for val in faces:
            if not isinstance(val, int) or not (1 <= val <= 8):
                return False, f"Die {name} has face value {val} outside [1, 8]."
        # Sort faces in place for validation
        dice[name] = sorted(faces)

    # Constraint 5: Equal Sum
    sums = {name: sum(faces) for name, faces in dice.items()}
    first_sum = sums['A']
    if not all(s == first_sum for s in sums.values()):
        return False, f"Sum of faces must be equal for all dice. Got sums: {sums}"

    reported_sum = analysis.get("common_sum")
    if reported_sum != first_sum:
        return False, f"Reported common_sum {reported_sum} does not match actual sum {first_sum}."

    # Constraint 6: Unique Value Sets
    value_sets = [frozenset(faces) for name, faces in dice.items()]
    if len(set(value_sets)) != 4:
        return False, f"The sets of unique values used on each die must be distinct. Got sets: {[sorted(list(s)) for s in value_sets]}"

    # Constraint 4: Nontransitive Cycle
    win_threshold = (4 * 4) / 2
    actual_win_counts = {
        "A_beats_B": compute_wins(dice['A'], dice['B']),
        "B_beats_C": compute_wins(dice['B'], dice['C']),
        "C_beats_D": compute_wins(dice['C'], dice['D']),
        "D_beats_A": compute_wins(dice['D'], dice['A']),
    }

    reported_win_counts = analysis.get("win_counts", {})
    if actual_win_counts != reported_win_counts:
        return False, f"Reported win_counts do not match actual ones. Actual: {actual_win_counts}, Reported: {reported_win_counts}"

    for pair, wins in actual_win_counts.items():
        if wins <= win_threshold:
            return False, f"Dominance failed for {pair}. Win count is {wins}, must be > {win_threshold}."

    return True, "Solution is valid."

def main():
    """Loads a JSON solution from stdin and validates it."""
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            is_valid, message = False, "No input provided."
        else:
            solution = json.loads(input_data)
            is_valid, message = validate_solution(solution)
    except json.JSONDecodeError as e:
        is_valid, message = False, f"Invalid JSON input: {e}"
    except Exception as e:
        is_valid, message = False, f"An unexpected error occurred: {e}"

    result = {"valid": is_valid, "message": message}
    print(json.dumps(result))
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
