#!/usr/bin/env python3
"""
Reference model for DONALD + GERALD = ROBERT cryptarithmetic puzzle.
Validates a given solution from stdin.
"""

import json
import sys

def validate_solution():
    """
    Reads a solution from stdin and validates it.
    """
    try:
        solution = json.loads(sys.stdin.read())
        assignment = solution.get("assignment")

        if not assignment:
            print(json.dumps({"valid": False, "message": "Missing 'assignment' key in JSON."}))
            return

        letters = ['D', 'O', 'N', 'A', 'L', 'G', 'E', 'R', 'B', 'T']
        if len(assignment) != 10 or not all(l in assignment for l in letters):
            print(json.dumps({"valid": False, "message": f"Assignment must contain all 10 letters: {letters}"}))
            return

        # Check for unique digit assignments
        if len(set(assignment.values())) != 10:
            print(json.dumps({"valid": False, "message": "Digits assigned to letters are not unique."}))
            return

        D = assignment['D']
        O = assignment['O']
        N = assignment['N']
        A = assignment['A']
        L = assignment['L']
        G = assignment['G']
        E = assignment['E']
        R = assignment['R']
        B = assignment['B']
        T = assignment['T']

        # Check leading zero constraint
        if D == 0 or G == 0 or R == 0:
            print(json.dumps({"valid": False, "message": "Leading letters (D, G, R) cannot be zero."}))
            return

        # Calculate numeric values
        donald = 100000*D + 10000*O + 1000*N + 100*A + 10*L + D
        gerald = 100000*G + 10000*E + 1000*R + 100*A + 10*L + D
        robert = 100000*R + 10000*O + 1000*B + 100*E + 10*R + T

        # Validate the arithmetic
        if donald + gerald == robert:
            print(json.dumps({"valid": True, "message": "Solution is correct."}))
        else:
            message = f"Arithmetic is incorrect: {donald} + {gerald} != {robert}"
            print(json.dumps({"valid": False, "message": message}))

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON or missing keys. Error: {e}"}))

if __name__ == "__main__":
    validate_solution()
