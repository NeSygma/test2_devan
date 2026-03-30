#!/usr/bin/env python3
"""
Reference model for Escape Room Design problem.
Validates puzzle ordering and dependencies.
"""

import json
import sys


def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def validate_solution(solution):
    """Validate the escape room design solution"""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    required_fields = ["puzzle_order", "difficulty_progression", "dependencies_satisfied", "puzzle_details"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing field: {field}"}

    puzzle_order = solution["puzzle_order"]
    puzzle_details = solution["puzzle_details"]

    # Check puzzle count
    if len(puzzle_order) != 6:
        return {"valid": False, "message": f"Should have 6 puzzles, got {len(puzzle_order)}"}

    if len(puzzle_details) != 6:
        return {"valid": False, "message": f"Should have 6 puzzle details, got {len(puzzle_details)}"}

    # Check all puzzles present
    if set(puzzle_order) != {1, 2, 3, 4, 5, 6}:
        return {"valid": False, "message": "Puzzle order should contain puzzles 1-6"}

    # Build dependency map
    dependencies = {}
    for detail in puzzle_details:
        puzzle_id = detail["puzzle_id"]
        prerequisites = detail["prerequisites"]
        dependencies[puzzle_id] = prerequisites

    # Check dependencies are satisfied in order
    completed = set()
    for puzzle_id in puzzle_order:
        for prereq in dependencies.get(puzzle_id, []):
            if prereq not in completed:
                return {"valid": False, "message": f"Puzzle {puzzle_id} requires puzzle {prereq} which hasn't been completed yet"}
        completed.add(puzzle_id)

    return {"valid": True, "message": "Valid escape room design"}


def main():
    """Main validation function"""
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
