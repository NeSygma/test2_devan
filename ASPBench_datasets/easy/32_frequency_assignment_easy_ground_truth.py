#!/usr/bin/env python3

import json
import sys

def validate_solution(solution):
    """Validate a frequency assignment solution."""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    try:
        # Parse JSON if string
        if isinstance(solution, str):
            data = json.loads(solution)
        else:
            data = solution

        if "assignments" not in data:
            return {"valid": False, "message": "Missing 'assignments' key"}
        if "frequencies_used" not in data:
            return {"valid": False, "message": "Missing 'frequencies_used' key"}

        assignments = data["assignments"]
        frequencies_used = data["frequencies_used"]

        if not isinstance(assignments, list):
            return {"valid": False, "message": "assignments must be a list"}
        if not isinstance(frequencies_used, int):
            return {"valid": False, "message": "frequencies_used must be an integer"}

        if len(assignments) != 6:
            return {"valid": False, "message": f"Expected 6 assignments, got {len(assignments)}"}

        # Transmitters and interference graph
        transmitters = {"A", "B", "C", "D", "E", "F"}
        interference = {
            "A": {"B", "C"},
            "B": {"A", "D", "E"},
            "C": {"A", "D", "F"},
            "D": {"B", "C", "E"},
            "E": {"B", "D", "F"},
            "F": {"C", "E"}
        }

        available_frequencies = {1, 2, 3, 4, 5}

        # Check assignments format
        assigned_transmitters = set()
        frequency_map = {}

        for i, assignment in enumerate(assignments):
            if not isinstance(assignment, dict):
                return {"valid": False, "message": f"Assignment {i+1} must be an object"}

            required_fields = ["transmitter", "frequency"]
            for field in required_fields:
                if field not in assignment:
                    return {"valid": False, "message": f"Assignment {i+1} missing '{field}' field"}

            transmitter = assignment["transmitter"]
            frequency = assignment["frequency"]

            # Check valid values
            if transmitter not in transmitters:
                return {"valid": False, "message": f"Invalid transmitter: {transmitter}"}
            if frequency not in available_frequencies:
                return {"valid": False, "message": f"Invalid frequency: {frequency}"}

            # Check uniqueness
            if transmitter in assigned_transmitters:
                return {"valid": False, "message": f"Transmitter {transmitter} assigned multiple times"}

            assigned_transmitters.add(transmitter)
            frequency_map[transmitter] = frequency

        # Check all transmitters assigned
        if assigned_transmitters != transmitters:
            missing = transmitters - assigned_transmitters
            return {"valid": False, "message": f"Missing transmitter assignments: {missing}"}

        # Check interference constraints
        for tx1, neighbors in interference.items():
            freq1 = frequency_map[tx1]
            for tx2 in neighbors:
                freq2 = frequency_map[tx2]

                # Cannot use same frequency
                if freq1 == freq2:
                    return {"valid": False, "message": f"Transmitters {tx1} and {tx2} interfere and have same frequency {freq1}"}

                # Cannot use adjacent frequencies
                if abs(freq1 - freq2) == 1:
                    return {"valid": False, "message": f"Transmitters {tx1} and {tx2} interfere and have adjacent frequencies {freq1}, {freq2}"}

        # Check frequencies_used count
        used_freqs = set(frequency_map.values())
        actual_used = len(used_freqs)

        if frequencies_used != actual_used:
            return {"valid": False, "message": f"frequencies_used ({frequencies_used}) doesn't match actual count ({actual_used})"}

        # Check optimality (minimum is 3 frequencies for this instance)
        if actual_used != 3:
            return {"valid": False, "message": f"Solution uses {actual_used} frequencies, but optimal is 3"}

        return {"valid": True, "message": f"Solution is valid and optimal with {actual_used} frequencies"}

    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"valid": False, "message": f"Error validating solution: {e}"}

if __name__ == "__main__":
    solution_text = sys.stdin.read().strip()
    result = validate_solution(solution_text)
    print(json.dumps(result))
