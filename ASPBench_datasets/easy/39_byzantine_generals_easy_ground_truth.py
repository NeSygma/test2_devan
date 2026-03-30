#!/usr/bin/env python3
"""
Reference Model: Byzantine Generals Problem
Validates consensus solution from stdin.
"""

import sys
import json

def validate_solution():
    """Validate Byzantine consensus solution from stdin."""
    try:
        # Read solution from stdin
        data = sys.stdin.read().strip()
        if not data:
            return {"valid": False, "message": "No solution provided"}

        solution = json.loads(data)

        # Check for error in solution
        if "error" in solution:
            return {"valid": False, "message": "Solution contains error"}

        # Check required fields
        if "consensus" not in solution:
            return {"valid": False, "message": "Missing 'consensus' field"}

        consensus = solution["consensus"]

        # Check that consensus is valid (0 or 1)
        if consensus not in [0, 1]:
            return {"valid": False, "message": f"Invalid consensus value: {consensus} (must be 0 or 1)"}

        # Problem setup: honest generals G1, G2, G3 have proposals 1, 1, 0
        # Majority is 2 votes for 1, so consensus should be 1
        honest_proposals = [1, 1, 0]  # G1, G2, G3
        count_0 = honest_proposals.count(0)
        count_1 = honest_proposals.count(1)

        expected = 1 if count_1 > count_0 else 0

        if consensus != expected:
            return {
                "valid": False,
                "message": f"Incorrect consensus: got {consensus}, expected {expected} (majority of honest generals)"
            }

        return {"valid": True, "message": "Correct Byzantine consensus achieved"}

    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON input: {str(e)}"}
    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}

if __name__ == "__main__":
    result = validate_solution()
    print(json.dumps(result))
