#!/usr/bin/env python3
"""
Reference model for SEND + MORE = MONEY cryptarithmetic puzzle.
Validates solution from stdin.
"""

import json
import sys

def validate_solution():
    """
    Validate SEND + MORE = MONEY solution from stdin.
    Returns {"valid": true/false, "message": "..."}.
    """
    try:
        # Read solution from stdin
        data = sys.stdin.read().strip()
        if not data:
            return {"valid": False, "message": "No solution provided"}

        solution = json.loads(data)

        # Check required fields
        if "assignment" not in solution:
            return {"valid": False, "message": "Missing 'assignment' field"}

        assignment = solution["assignment"]

        # Check all required letters present
        required_letters = {'S', 'E', 'N', 'D', 'M', 'O', 'R', 'Y'}
        if set(assignment.keys()) != required_letters:
            return {"valid": False, "message": f"Expected letters {required_letters}, got {set(assignment.keys())}"}

        # Extract values
        S = assignment['S']
        E = assignment['E']
        N = assignment['N']
        D = assignment['D']
        M = assignment['M']
        O = assignment['O']
        R = assignment['R']
        Y = assignment['Y']

        # Validate all digits are 0-9
        values = [S, E, N, D, M, O, R, Y]
        if not all(isinstance(v, int) and 0 <= v <= 9 for v in values):
            return {"valid": False, "message": "All values must be digits 0-9"}

        # Check all different
        if len(set(values)) != 8:
            return {"valid": False, "message": "All letters must map to different digits"}

        # Check no leading zeros
        if S == 0:
            return {"valid": False, "message": "Leading letter S cannot be 0"}
        if M == 0:
            return {"valid": False, "message": "Leading letter M cannot be 0"}

        # Verify arithmetic equation
        send = 1000*S + 100*E + 10*N + D
        more = 1000*M + 100*O + 10*R + E
        money = 10000*M + 1000*O + 100*N + 10*E + Y

        if send + more != money:
            return {"valid": False, "message": f"Equation does not hold: {send} + {more} = {send+more}, expected {money}"}

        # All checks passed
        return {"valid": True, "message": f"Solution correct: {send} + {more} = {money}"}

    except json.JSONDecodeError:
        return {"valid": False, "message": "Invalid JSON"}
    except KeyError as e:
        return {"valid": False, "message": f"Missing key: {e}"}
    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}

if __name__ == "__main__":
    result = validate_solution()
    print(json.dumps(result))
