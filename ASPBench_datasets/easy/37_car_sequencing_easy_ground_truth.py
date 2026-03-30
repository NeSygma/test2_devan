#!/usr/bin/env python3
"""
Reference Model: Car Sequencing Problem
======================================
Validate car sequencing solution with capacity ratio constraints.
"""

import sys
import json
from typing import List, Dict, Tuple

def validate_solution(solution_data: dict) -> dict:
    """Validate the car sequencing solution."""

    # Check for error in solution
    if "error" in solution_data:
        return {"valid": False, "message": "Solution contains error"}

    # Extract sequence
    if "sequence" not in solution_data:
        return {"valid": False, "message": "Missing 'sequence' field"}

    sequence = solution_data["sequence"]

    # Check length
    if len(sequence) != 6:
        return {"valid": False, "message": f"Sequence length is {len(sequence)}, expected 6"}

    # Check car counts
    car_counts = {'A': 0, 'B': 0, 'C': 0}
    for car in sequence:
        if car not in car_counts:
            return {"valid": False, "message": f"Invalid car type: {car}"}
        car_counts[car] += 1

    expected_counts = {'A': 1, 'B': 2, 'C': 3}
    if car_counts != expected_counts:
        return {"valid": False, "message": f"Wrong car counts: got {car_counts}, expected {expected_counts}"}

    # Define car options
    car_options = {
        'A': [1, 2],  # sunroof + leather
        'B': [3],     # GPS only
        'C': [1]      # sunroof only
    }

    # Define capacity constraints: (option, max_in_window, window_size)
    capacity_constraints = [
        (1, 2, 3),  # Option 1: at most 2 in every 3 consecutive cars
        (2, 1, 2),  # Option 2: at most 1 in every 2 consecutive cars
        (3, 1, 2)   # Option 3: at most 1 in every 2 consecutive cars
    ]

    # Check capacity constraints
    for option, max_in_window, window_size in capacity_constraints:
        # Check each sliding window
        for start in range(len(sequence) - window_size + 1):
            window = sequence[start:start + window_size]
            option_count = sum(1 for car in window if option in car_options[car])

            if option_count > max_in_window:
                return {
                    "valid": False,
                    "message": f"Option {option} constraint violated at positions {start+1}-{start+window_size}: {window} has {option_count} cars with option {option}, max allowed is {max_in_window}"
                }

    return {"valid": True, "message": "Valid car sequence"}

if __name__ == "__main__":
    try:
        # Read solution from stdin
        input_data = sys.stdin.read().strip()

        if not input_data:
            print(json.dumps({"valid": False, "message": "No input provided"}))
            sys.exit(1)

        solution_data = json.loads(input_data)
        result = validate_solution(solution_data)
        print(json.dumps(result))

    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON input: {str(e)}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Verification error: {str(e)}"}))
        sys.exit(1)
