#!/usr/bin/env python3
"""
Reference model for Nontransitive Dice Design problem.
Validates whether proposed dice satisfy nontransitive properties.
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


def compute_win_probability(die1: List[int], die2: List[int]) -> float:
    """Compute probability that die1 beats die2"""
    wins = 0
    total = 0

    for face1 in die1:
        for face2 in die2:
            total += 1
            if face1 > face2:
                wins += 1

    return wins / total if total > 0 else 0.0


def validate_die(die: List[int], die_name: str) -> tuple:
    """Validate a single die"""
    if not isinstance(die, list):
        return False, f"Die {die_name} must be a list"

    if len(die) != 6:
        return False, f"Die {die_name} must have exactly 6 faces, has {len(die)}"

    for i, face in enumerate(die):
        if not isinstance(face, int):
            return False, f"Die {die_name} face {i} must be an integer, got {face}"

        if face < 0 or face > 6:
            return False, f"Die {die_name} face {i} must be between 0 and 6, got {face}"

    return True, ""


def validate_solution(solution):
    """Validate the proposed solution"""
    if not isinstance(solution, dict):
        return {"valid": False, "message": "Solution must be a JSON object"}

    if "dice" not in solution:
        return {"valid": False, "message": "Missing 'dice' field"}

    if "win_probabilities" not in solution:
        return {"valid": False, "message": "Missing 'win_probabilities' field"}

    dice = solution["dice"]
    win_probs = solution["win_probabilities"]

    if not isinstance(dice, dict):
        return {"valid": False, "message": "dice must be a dictionary"}

    if not isinstance(win_probs, dict):
        return {"valid": False, "message": "win_probabilities must be a dictionary"}

    # Check that we have exactly three dice A, B, C
    required_dice = {'A', 'B', 'C'}
    if set(dice.keys()) != required_dice:
        return {"valid": False, "message": f"Must have exactly dice A, B, C. Got: {set(dice.keys())}"}

    # Validate each die
    for die_name, die_faces in dice.items():
        is_valid, msg = validate_die(die_faces, die_name)
        if not is_valid:
            return {"valid": False, "message": msg}

    # Check win probability fields
    required_probs = {'A_beats_B', 'B_beats_C', 'C_beats_A'}
    if set(win_probs.keys()) != required_probs:
        return {"valid": False, "message": f"Must have exactly win probabilities: {required_probs}. Got: {set(win_probs.keys())}"}

    # Validate win probabilities
    for prob_name, prob_value in win_probs.items():
        if not isinstance(prob_value, (int, float)):
            return {"valid": False, "message": f"Win probability {prob_name} must be a number, got {prob_value}"}

        if prob_value < 0 or prob_value > 1:
            return {"valid": False, "message": f"Win probability {prob_name} must be between 0 and 1, got {prob_value}"}

    # Compute actual win probabilities and verify
    actual_a_beats_b = compute_win_probability(dice['A'], dice['B'])
    actual_b_beats_c = compute_win_probability(dice['B'], dice['C'])
    actual_c_beats_a = compute_win_probability(dice['C'], dice['A'])

    # Check if reported probabilities match computed ones (with small tolerance)
    tolerance = 0.01
    if abs(win_probs['A_beats_B'] - actual_a_beats_b) > tolerance:
        return {"valid": False, "message": f"A_beats_B probability mismatch: reported {win_probs['A_beats_B']}, actual {actual_a_beats_b:.3f}"}

    if abs(win_probs['B_beats_C'] - actual_b_beats_c) > tolerance:
        return {"valid": False, "message": f"B_beats_C probability mismatch: reported {win_probs['B_beats_C']}, actual {actual_b_beats_c:.3f}"}

    if abs(win_probs['C_beats_A'] - actual_c_beats_a) > tolerance:
        return {"valid": False, "message": f"C_beats_A probability mismatch: reported {win_probs['C_beats_A']}, actual {actual_c_beats_a:.3f}"}

    # Check nontransitive property (each win probability > 0.5)
    if actual_a_beats_b <= 0.5:
        return {"valid": False, "message": f"A must beat B with probability > 0.5, got {actual_a_beats_b:.3f}"}

    if actual_b_beats_c <= 0.5:
        return {"valid": False, "message": f"B must beat C with probability > 0.5, got {actual_b_beats_c:.3f}"}

    if actual_c_beats_a <= 0.5:
        return {"valid": False, "message": f"C must beat A with probability > 0.5, got {actual_c_beats_a:.3f}"}

    return {"valid": True, "message": f"Valid nontransitive dice with win probabilities A>B: {actual_a_beats_b:.3f}, B>C: {actual_b_beats_c:.3f}, C>A: {actual_c_beats_a:.3f}"}


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
