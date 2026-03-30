#!/usr/bin/env python3
"""
Reference model for Knights and Knaves puzzle verification.

This module verifies that a given solution satisfies all logical constraints
of the Knights and Knaves puzzle without generating solutions.
"""

import json
import sys
from typing import Dict


def verify_solution(solution: Dict[str, str]) -> Dict[str, any]:
    """
    Verify that a solution satisfies all constraints of the Knights and Knaves puzzle.

    Args:
        solution: Dictionary with keys 'alice', 'bob', 'charlie' and values 'knight' or 'knave'

    Returns:
        Dictionary with 'valid' (bool) and 'message' (str)
    """

    # Check solution format
    required_keys = {'alice', 'bob', 'charlie'}
    if not isinstance(solution, dict):
        return {"valid": False, "message": "Solution must be a dictionary"}

    if set(solution.keys()) != required_keys:
        return {"valid": False, "message": f"Solution must have exactly these keys: {required_keys}"}

    valid_values = {'knight', 'knave'}
    for person, type_val in solution.items():
        if type_val not in valid_values:
            return {"valid": False, "message": f"{person} must be 'knight' or 'knave', got '{type_val}'"}

    # Extract assignments
    alice_type = solution['alice']
    bob_type = solution['bob']
    charlie_type = solution['charlie']

    # Verify logical consistency

    # Alice says: "Bob is a knave"
    alice_statement = (bob_type == 'knave')
    if alice_type == 'knight':
        # Knights tell the truth
        if not alice_statement:
            return {"valid": False, "message": "Alice is a knight but her statement 'Bob is a knave' is false"}
    else:  # alice_type == 'knave'
        # Knaves lie
        if alice_statement:
            return {"valid": False, "message": "Alice is a knave but her statement 'Bob is a knave' is true"}

    # Bob says: "Alice and Charlie are of the same type"
    bob_statement = (alice_type == charlie_type)
    if bob_type == 'knight':
        # Knights tell the truth
        if not bob_statement:
            return {"valid": False, "message": "Bob is a knight but his statement 'Alice and Charlie are of the same type' is false"}
    else:  # bob_type == 'knave'
        # Knaves lie
        if bob_statement:
            return {"valid": False, "message": "Bob is a knave but his statement 'Alice and Charlie are of the same type' is true"}

    # Charlie says: "Alice is a knight"
    charlie_statement = (alice_type == 'knight')
    if charlie_type == 'knight':
        # Knights tell the truth
        if not charlie_statement:
            return {"valid": False, "message": "Charlie is a knight but his statement 'Alice is a knight' is false"}
    else:  # charlie_type == 'knave'
        # Knaves lie
        if charlie_statement:
            return {"valid": False, "message": "Charlie is a knave but his statement 'Alice is a knight' is true"}

    return {"valid": True, "message": "Solution is valid"}


def main():
    """Main function to verify a JSON solution from stdin."""

    try:
        data = sys.stdin.read().strip()
        if not data:
            result = {"valid": False, "message": "No input provided"}
            print(json.dumps(result))
            sys.exit(1)

        solution = json.loads(data)
    except json.JSONDecodeError as e:
        result = {"valid": False, "message": f"Invalid JSON: {e}"}
        print(json.dumps(result))
        sys.exit(1)

    result = verify_solution(solution)
    print(json.dumps(result))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
