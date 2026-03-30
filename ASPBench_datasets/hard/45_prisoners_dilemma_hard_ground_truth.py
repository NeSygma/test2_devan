#!/usr/bin/env python3
"""
Reference model for Problem 045 (Hard): Validator

This script validates that a given solution JSON conforms to the required output format.
It does NOT re-solve the problem. It only checks for structural integrity, correct
keys, data types, and logical consistency (e.g., winner matches top score).
"""

import json
import sys

# Expected optimal values (extracted from reference solution)
EXPECTED_BEST_STRATEGY = "DEFECT"
EXPECTED_BEST_SCORE = 48

def validate_solution(solution_json: str) -> dict:
    """
    Validates the JSON output from a solution.
    """
    try:
        data = json.loads(solution_json)
    except json.JSONDecodeError:
        return {"valid": False, "message": "Invalid JSON format."}

    # Check for required top-level keys
    required_keys = {"best_strategy_choice", "expected_scores"}
    if not required_keys.issubset(data.keys()):
        return {"valid": False, "message": f"Missing one or more top-level keys: {required_keys - set(data.keys())}"}

    # Validate 'best_strategy_choice'
    winner = data.get("best_strategy_choice")
    if not isinstance(winner, str):
        return {"valid": False, "message": "'best_strategy_choice' must be a string."}

    # Validate 'expected_scores'
    scores_list = data.get("expected_scores")
    if not isinstance(scores_list, list):
        return {"valid": False, "message": "'expected_scores' must be a list."}

    if not scores_list:
        return {"valid": False, "message": "'expected_scores' list cannot be empty."}

    # Check list entries
    found_strategies = set()
    previous_score = float('inf')
    for i, item in enumerate(scores_list):
        if not isinstance(item, dict):
            return {"valid": False, "message": f"Item at index {i} in 'expected_scores' is not an object."}

        item_keys = {"strategy", "expected_total_score"}
        if not item_keys.issubset(item.keys()):
            return {"valid": False, "message": f"Item at index {i} is missing keys: {item_keys - set(item.keys())}"}

        if not isinstance(item["strategy"], str) or not isinstance(item["expected_total_score"], int):
            return {"valid": False, "message": f"Item at index {i} has incorrect data types."}

        # Check for descending order
        current_score = item["expected_total_score"]
        if current_score > previous_score:
            return {"valid": False, "message": "List 'expected_scores' is not sorted in descending order."}
        previous_score = current_score

        found_strategies.add(item["strategy"])

    # Check if all required strategies are present
    EGO_STRATEGIES = {"COOP", "DEFECT", "TFT"}
    if found_strategies != EGO_STRATEGIES:
        return {"valid": False, "message": f"Expected strategies {EGO_STRATEGIES}, but found {found_strategies}."}

    # Check if winner matches the top of the sorted list
    if scores_list[0]["strategy"] != winner:
        return {"valid": False, "message": "'best_strategy_choice' does not match the strategy with the highest score."}

    # Check optimality
    if winner != EXPECTED_BEST_STRATEGY:
        return {"valid": False, "message": f"Not optimal: best_strategy_choice={winner}, expected {EXPECTED_BEST_STRATEGY}"}

    top_score = scores_list[0]["expected_total_score"]
    if top_score != EXPECTED_BEST_SCORE:
        return {"valid": False, "message": f"Not optimal: best strategy score={top_score}, expected {EXPECTED_BEST_SCORE}"}

    return {"valid": True, "message": f"Solution valid and optimal (strategy={EXPECTED_BEST_STRATEGY}, score={EXPECTED_BEST_SCORE})"}


if __name__ == "__main__":
    try:
        solution_output = sys.stdin.read()
        if not solution_output.strip():
            print(json.dumps({"valid": False, "message": "No solution provided on stdin."}), file=sys.stderr)
            sys.exit(1)

        validation_result = validate_solution(solution_output)
        print(json.dumps(validation_result))

    except Exception as e:
        print(json.dumps({"valid": False, "message": f"An unexpected error occurred during validation: {e}"}))
        sys.exit(1)
