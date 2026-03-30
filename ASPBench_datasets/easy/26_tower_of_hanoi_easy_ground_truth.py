#!/usr/bin/env python3
"""
Reference model for Tower of Hanoi problem
Used for solution verification only.
"""

import json
import sys

def verify_solution(solution_json: str) -> dict:
    """
    Verify if the given solution satisfies all problem constraints.

    Args:
        solution_json: JSON string containing the solution

    Returns:
        dict with keys:
        - valid: bool (True if solution is valid)
        - message: str (explanation)
    """

    # Parse solution
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    # Check required fields
    required_fields = ["moves", "total_moves", "is_optimal"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    moves = solution["moves"]
    total_moves = solution["total_moves"]
    is_optimal = solution["is_optimal"]

    # Validate types
    if not isinstance(moves, list):
        return {"valid": False, "message": "moves must be an array"}
    if not isinstance(total_moves, int):
        return {"valid": False, "message": "total_moves must be an integer"}
    if not isinstance(is_optimal, bool):
        return {"valid": False, "message": "is_optimal must be a boolean"}

    # Check total_moves consistency
    if total_moves != len(moves):
        return {"valid": False, "message": f"total_moves {total_moves} doesn't match moves length {len(moves)}"}

    # Initialize state: peg -> list of disks (bottom to top)
    state = {
        "A": [4, 3, 2, 1],  # All disks start on peg A
        "B": [],
        "C": []
    }

    # Validate and simulate each move
    for i, move in enumerate(moves):
        if not isinstance(move, dict):
            return {"valid": False, "message": f"Move {i+1} must be an object"}

        required_move_fields = ["step", "disk", "from_peg", "to_peg"]
        for field in required_move_fields:
            if field not in move:
                return {"valid": False, "message": f"Move {i+1} missing field: {field}"}

        step = move["step"]
        disk = move["disk"]
        from_peg = move["from_peg"]
        to_peg = move["to_peg"]

        # Validate move fields
        if not isinstance(step, int) or step != i + 1:
            return {"valid": False, "message": f"Move {i+1} has invalid step {step}, expected {i+1}"}
        if not isinstance(disk, int) or disk not in [1, 2, 3, 4]:
            return {"valid": False, "message": f"Move {i+1} has invalid disk {disk}, must be 1-4"}
        if from_peg not in ["A", "B", "C"]:
            return {"valid": False, "message": f"Move {i+1} has invalid from_peg {from_peg}"}
        if to_peg not in ["A", "B", "C"]:
            return {"valid": False, "message": f"Move {i+1} has invalid to_peg {to_peg}"}
        if from_peg == to_peg:
            return {"valid": False, "message": f"Move {i+1} has same from_peg and to_peg"}

        # Check if move is legal
        if not state[from_peg]:
            return {"valid": False, "message": f"Move {i+1}: Peg {from_peg} is empty"}

        top_disk = state[from_peg][-1]  # Top disk on from_peg
        if top_disk != disk:
            return {"valid": False, "message": f"Move {i+1}: Disk {disk} is not on top of peg {from_peg}"}

        # Check if placement is legal
        if state[to_peg] and state[to_peg][-1] < disk:
            return {"valid": False, "message": f"Move {i+1}: Cannot place disk {disk} on smaller disk {state[to_peg][-1]}"}

        # Execute move
        moved_disk = state[from_peg].pop()
        state[to_peg].append(moved_disk)

    # Check final state
    goal_state = {"A": [], "B": [], "C": [4, 3, 2, 1]}
    if state != goal_state:
        return {"valid": False, "message": f"Final state {state} doesn't match goal {goal_state}"}

    # Check optimality - minimum moves for 4 disks is 2^4 - 1 = 15
    optimal_moves = 15
    actual_optimal = total_moves == optimal_moves

    if is_optimal != actual_optimal:
        return {"valid": False, "message": f"is_optimal mismatch: expected {actual_optimal}, got {is_optimal}"}

    if actual_optimal:
        return {"valid": True, "message": f"Valid and optimal Tower of Hanoi solution with {total_moves} moves"}
    else:
        return {"valid": True, "message": f"Valid but suboptimal solution. Uses {total_moves} moves, optimal is {optimal_moves}"}

def main():
    """Main entry point for verification."""
    solution_json = sys.stdin.read()

    if not solution_json.strip():
        print(json.dumps({"valid": False, "message": "No input provided"}))
        return

    result = verify_solution(solution_json)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
