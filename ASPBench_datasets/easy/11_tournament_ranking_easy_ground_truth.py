#!/usr/bin/env python3
"""
Reference model for Tournament Ranking problem.
Validates solution from stdin.
"""

import json
import sys

def validate_solution():
    """
    Validate a tournament ranking solution.
    """
    # Load solution from stdin
    try:
        data = sys.stdin.read().strip()
        if not data:
            return {"valid": False, "message": "No solution provided"}
        solution = json.loads(data)
    except json.JSONDecodeError:
        return {"valid": False, "message": "Invalid JSON format"}

    # Check required fields
    if "ranking" not in solution or "violations" not in solution:
        return {"valid": False, "message": "Missing required fields (ranking, violations)"}

    ranking = solution["ranking"]
    violations = solution["violations"]

    # Tournament results: beat(winner, loser)
    matches = [
        ("A", "B"),  # A beat B
        ("B", "C"),  # B beat C
        ("C", "A"),  # C beat A (creates a cycle)
        ("A", "D"),  # A beat D
        ("D", "E"),  # D beat E
        ("E", "C"),  # E beat C
        ("B", "E"),  # B beat E
        ("D", "C"),  # D beat C
        ("A", "E"),  # A beat E
        ("B", "D"),  # B beat D
    ]

    teams = ["A", "B", "C", "D", "E"]

    # Validate ranking
    if not isinstance(ranking, list):
        return {"valid": False, "message": "Ranking must be a list"}

    if len(ranking) != 5:
        return {"valid": False, "message": f"Ranking must contain exactly 5 teams, got {len(ranking)}"}

    if sorted(ranking) != sorted(teams):
        return {"valid": False, "message": "Ranking must contain each team exactly once"}

    # Count violations
    position = {team: i for i, team in enumerate(ranking)}
    actual_violations = 0

    for winner, loser in matches:
        # Violation if winner's position > loser's position (winner ranked lower)
        if position[winner] > position[loser]:
            actual_violations += 1

    # Check if violations count is correct
    if actual_violations != violations:
        return {
            "valid": False,
            "message": f"Violation count incorrect: reported {violations}, actual {actual_violations}"
        }

    # Check if this is the optimal solution (minimum violations = 1)
    optimal_violations = 1
    if violations != optimal_violations:
        return {
            "valid": False,
            "message": f"Solution is not optimal: got {violations} violations, optimal is {optimal_violations}"
        }

    return {
        "valid": True,
        "message": f"Solution correct with {violations} violations (optimal)"
    }

if __name__ == "__main__":
    result = validate_solution()
    print(json.dumps(result))
