#!/usr/bin/env python3
"""
Reference model for the Tower of Hanoi problem.
This script validates a given JSON solution against all problem constraints.
Validates both feasibility and optimality (25 moves).
"""

import json
import sys

# Expected optimal value
EXPECTED_OPTIMAL_MOVES = 19

def verify_solution(solution_json: str) -> dict:
    """
    Verifies if the provided solution for the Tower of Hanoi is valid.

    Args:
        solution_json: A JSON string containing the solution.

    Returns:
        A dictionary with 'valid' (bool) and 'message' (str) keys.
    """
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON format: {e}"}

    # === Basic Structure Validation ===
    if "moves" not in solution or "total_moves" not in solution:
        return {"valid": False, "message": "Missing 'moves' or 'total_moves' field."}

    moves = solution["moves"]
    total_moves = solution["total_moves"]

    if not isinstance(moves, list):
        return {"valid": False, "message": "'moves' must be a list."}
    if not isinstance(total_moves, int):
        return {"valid": False, "message": "'total_moves' must be an integer."}
    if len(moves) != total_moves:
        return {"valid": False, "message": f"Mismatch between total_moves ({total_moves}) and actual move count ({len(moves)})."}

    # === Simulation and Constraint Checking ===
    pegs = {
        "A": [4, 3, 2, 1],
        "B": [],
        "C": [],
        "D": []
    }

    # For the Pilgrim's Journey rule
    disk_visits = {i: set() for i in range(1, 5)}

    for i, move in enumerate(moves):
        step = i + 1

        # Move structure validation
        expected_fields = {"step", "disk", "from_peg", "to_peg"}
        if not all(field in move for field in expected_fields):
            return {"valid": False, "message": f"Move {step} is missing required fields."}
        if move["step"] != step:
            return {"valid": False, "message": f"Move {step} has incorrect step number {move['step']}."}

        disk, from_peg, to_peg = move["disk"], move["from_peg"], move["to_peg"]

        # --- Rule 1: Standard Movement ---
        if from_peg not in pegs or to_peg not in pegs or from_peg == to_peg:
            return {"valid": False, "message": f"Move {step}: Invalid peg selection ('{from_peg}' to '{to_peg}')."}
        if not pegs[from_peg]:
            return {"valid": False, "message": f"Move {step}: Cannot move from empty peg {from_peg}."}
        if pegs[from_peg][-1] != disk:
            return {"valid": False, "message": f"Move {step}: Disk {disk} is not on top of peg {from_peg}."}

        # --- Rule 2: Larger on Smaller ---
        if pegs[to_peg] and pegs[to_peg][-1] < disk:
            return {"valid": False, "message": f"Move {step}: Cannot place disk {disk} on smaller disk {pegs[to_peg][-1]}."}

        # If all checks pass, execute the move
        pegs[from_peg].pop()
        pegs[to_peg].append(disk)

        # --- Rule 4: Pilgrim's Journey ---
        if to_peg in ['B', 'C']:
            disk_visits[disk].add(to_peg)

    # === Final State Validation ===
    goal_pegs = {
        "A": [],
        "B": [],
        "C": [],
        "D": [4, 3, 2, 1]
    }
    if pegs != goal_pegs:
        return {"valid": False, "message": f"Final state is incorrect. Expected {goal_pegs}, but got {pegs}."}

    # --- Final check for Pilgrim's Journey ---
    for disk_num, visited_pegs in disk_visits.items():
        if 'B' not in visited_pegs:
            return {"valid": False, "message": f"Pilgrim's Journey failed: Disk {disk_num} never landed on peg B."}
        if 'C' not in visited_pegs:
            return {"valid": False, "message": f"Pilgrim's Journey failed: Disk {disk_num} never landed on peg C."}

    # Check optimality
    if total_moves != EXPECTED_OPTIMAL_MOVES:
        return {"valid": False, "message": f"Not optimal: total_moves={total_moves}, expected {EXPECTED_OPTIMAL_MOVES}"}

    return {"valid": True, "message": f"Solution is valid and optimal (total_moves={EXPECTED_OPTIMAL_MOVES})"}


def main():
    """Reads solution from stdin and verifies it."""
    try:
        solution_str = sys.stdin.read()
        result = verify_solution(solution_str)
    except Exception as e:
        result = {"valid": False, "message": f"An unexpected error occurred during verification: {e}"}

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
