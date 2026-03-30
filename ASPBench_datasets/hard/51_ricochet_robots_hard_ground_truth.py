#!/usr/bin/env python3
"""
Reference model for the Ricochet Robots - Narrow Bridge problem.
Validates single-step movements and checks optimality (expected 7 moves).
"""

import json
import sys
from typing import List, Dict, Tuple

# Expected optimal value
EXPECTED_OPTIMAL_MOVES = 7

def get_problem_setup():
    """Defines the specific instance of the Narrow Bridge puzzle."""
    return {
        "grid_size": [5, 5],
        "initial_positions": {"A": [0, 1], "B": [1, 1], "C": [3, 1]},
        "target_robot": "A",
        "target_pos": [2, 3],
        "h_walls": [],
        # v_wall(col, r_start, r_end) is a wall to the *right* of the given col
        "v_walls": [
            {"col": 0, "r_start": 0, "r_end": 4}, # Left wall of the starting corridor
            {"col": 1, "r_start": 0, "r_end": 1}, # Wall with opening for bridge
            {"col": 1, "r_start": 3, "r_end": 4}, # Wall with opening for bridge
            {"col": 2, "r_start": 0, "r_end": 1}, # Wall with opening for bridge
            {"col": 2, "r_start": 3, "r_end": 4}, # Wall with opening for bridge
        ]
    }

def check_barrier(pos_from: List[int], pos_to: List[int], setup: Dict) -> bool:
    """Checks if a move crosses a barrier. Note: positions are [row, col]."""
    r1, c1 = pos_from
    r2, c2 = pos_to

    # Check horizontal walls
    for wall in setup["h_walls"]:
        wr, wc_start, wc_end = wall["row"], wall["c_start"], wall["c_end"]
        # Moving down across a wall
        if r1 == wr and r2 == wr + 1 and c1 >= wc_start and c1 <= wc_end:
            return True
        # Moving up across a wall
        if r2 == wr and r1 == wr + 1 and c1 >= wc_start and c1 <= wc_end:
            return True

    # Check vertical walls (wall is to the right of column 'wc')
    for wall in setup["v_walls"]:
        wc, wr_start, wr_end = wall["col"], wall["r_start"], wall["r_end"]
        # Moving right across a wall
        if c1 == wc and c2 == wc + 1 and r1 >= wr_start and r1 <= wr_end:
            return True
        # Moving left across a wall
        if c2 == wc and c1 == wc + 1 and r1 >= wr_start and r1 <= wr_end:
            return True

    return False

def validate_solution(solution: Dict) -> Tuple[bool, str]:
    """Validates the entire move sequence."""
    if not solution or "sequence" not in solution:
        return False, "Invalid or missing JSON input with 'sequence' field."

    if not solution.get("solution_found", False):
        return True, "Solution correctly reports no solution was found."

    setup = get_problem_setup()
    positions = {k: v[:] for k, v in setup["initial_positions"].items()}

    sequence = solution["sequence"]

    if solution.get("moves") != len(sequence):
        return False, f"Move count mismatch: claimed {solution.get('moves')}, but sequence has {len(sequence)} moves."

    for i, move in enumerate(sequence):
        # Validate move format
        if not all(k in move for k in ["robot", "from", "to"]):
            return False, f"Move {i+1} is missing required keys."

        robot, pos_from, pos_to = move["robot"], move["from"], move["to"]

        # Check if robot exists
        if robot not in positions:
            return False, f"Move {i+1}: Robot '{robot}' is not a valid robot."

        # Check if from position is correct
        if positions[robot] != pos_from:
            return False, f"Move {i+1}: Robot {robot} starts at {positions[robot]}, not {pos_from}."

        # Check for valid single-step move
        dr, dc = abs(pos_to[0] - pos_from[0]), abs(pos_to[1] - pos_from[1])
        if not ((dr == 1 and dc == 0) or (dr == 0 and dc == 1)):
            return False, f"Move {i+1}: Move from {pos_from} to {pos_to} is not a single cardinal step."

        # Check bounds
        if not (0 <= pos_to[0] < setup["grid_size"][0] and 0 <= pos_to[1] < setup["grid_size"][1]):
            return False, f"Move {i+1}: Move to {pos_to} is out of bounds."

        # Check for collisions with other robots
        for r, pos in positions.items():
            if r != robot and pos == pos_to:
                return False, f"Move {i+1}: Robot {robot} collides with robot {r} at {pos_to}."

        # Check for barrier crossings
        if check_barrier(pos_from, pos_to, setup):
             return False, f"Move {i+1}: Robot {robot} move from {pos_from} to {pos_to} crosses a barrier."

        # Update position
        positions[robot] = pos_to

    # Check final state
    if positions[setup["target_robot"]] != setup["target_pos"]:
        return False, f"Target not reached. Robot {setup['target_robot']} ended at {positions[setup['target_robot']]}, not {setup['target_pos']}."

    if solution["final_positions"] != positions:
        return False, f"Final positions mismatch. Expected {positions}, got {solution['final_positions']}."

    # Check optimality
    if len(sequence) != EXPECTED_OPTIMAL_MOVES:
        return False, f"Not optimal: moves={len(sequence)}, expected {EXPECTED_OPTIMAL_MOVES}"

    return True, f"Solution valid and optimal (moves={EXPECTED_OPTIMAL_MOVES})"

def main():
    try:
        solution_json = sys.stdin.read()
        solution = json.loads(solution_json)
        is_valid, message = validate_solution(solution)
        print(json.dumps({"valid": is_valid, "message": message}))
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({"valid": False, "message": "Invalid or missing JSON input."}))
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"An unexpected error occurred: {e}"}))

if __name__ == "__main__":
    main()
