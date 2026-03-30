#!/usr/bin/env python3
"""
Reference model for the Escape Room Design problem.
Validates a given solution against all complex constraints.
"""
import json
import sys

def load_solution():
    """Loads solution from stdin."""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return None

def validate_solution(solution):
    """Validates the entire escape room design."""
    if not solution:
        return False, "No solution provided or empty."

    required_fields = ["puzzle_order", "puzzle_details"]
    for field in required_fields:
        if field not in solution:
            return False, f"Missing required field: {field}"

    p_order = solution["puzzle_order"]
    p_details = solution["puzzle_details"]

    if len(p_order) != 18:
        return False, f"Expected 18 puzzles in order, but got {len(p_order)}."
    if len(p_details) != 18:
        return False, f"Expected 18 puzzle details, but got {len(p_details)}."
    if len(set(p_order)) != 18:
        return False, "Puzzle order contains duplicates."

    details_map = {p["puzzle_id"]: p for p in p_details}
    if set(p_order) != set(details_map.keys()):
        return False, "Mismatch between puzzle_order and puzzle_details IDs."

    completed_puzzles = set()
    inventory = set()
    current_room = None

    for i, puzzle_id in enumerate(p_order):
        puzzle = details_map[puzzle_id]

        # Initialize first room
        if i == 0:
            current_room = puzzle["room"]

        # 1. Room Adjacency Constraint
        next_room = puzzle["room"]
        room1_num = int(current_room[1])
        room2_num = int(next_room[1])
        if abs(room1_num - room2_num) > 1:
            return False, f"Invalid move at step {i+1}: Cannot move from {current_room} to {next_room} for puzzle {puzzle_id}."
        current_room = next_room

        # 2. Prerequisite Constraint
        if not set(puzzle.get("prerequisites", [])).issubset(completed_puzzles):
            return False, f"Prerequisite fail at step {i+1} for puzzle {puzzle_id}. Needs {puzzle['prerequisites']}, completed: {completed_puzzles}"

        # 3. Item Requirement Constraint
        if not set(puzzle.get("requires", [])).issubset(inventory):
            return False, f"Item requirement fail at step {i+1} for puzzle {puzzle_id}. Needs {puzzle['requires']}, inventory: {inventory}"

        if i > 0:
            prev_puzzle_id = p_order[i-1]
            prev_puzzle = details_map[prev_puzzle_id]

            # 4. Theme Balance Constraint
            if puzzle["theme"] == prev_puzzle["theme"]:
                return False, f"Theme violation at step {i+1}: Puzzle {puzzle_id} has same theme '{puzzle['theme']}' as previous puzzle {prev_puzzle_id}."

            # 5. Difficulty Curve Constraint
            diff_jump = abs(puzzle["difficulty"] - prev_puzzle["difficulty"])
            if diff_jump > 1:
                return False, f"Difficulty jump violation at step {i+1}: Puzzle {puzzle_id} (diff {puzzle['difficulty']}) and prev {prev_puzzle_id} (diff {prev_puzzle['difficulty']}) have jump > 1."

        # Update state
        completed_puzzles.add(puzzle_id)
        inventory.update(puzzle.get("yields", []))

    return True, "Solution satisfies all constraints."

def main():
    """Main validation function."""
    solution = load_solution()
    is_valid, message = validate_solution(solution)
    print(json.dumps({"valid": is_valid, "message": message}))

if __name__ == "__main__":
    main()