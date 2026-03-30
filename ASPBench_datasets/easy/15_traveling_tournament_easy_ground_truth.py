#!/usr/bin/env python3
"""
Reference model for Traveling Tournament Problem (Easy).
Validates solution from stdin.
"""

import json
import sys
from math import sqrt


def validate_solution():
    """Validate traveling tournament solution from stdin."""

    # Load solution from stdin
    try:
        data = sys.stdin.read().strip()
        if not data:
            return {"valid": False, "message": "No solution provided"}
        solution = json.loads(data)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    # Check required fields
    if not isinstance(solution, dict):
        return {"valid": False, "message": "Solution must be a JSON object"}

    required_fields = ["schedule", "total_distance", "feasible"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    if not solution["feasible"]:
        return {"valid": False, "message": "Solution marked as infeasible"}

    schedule = solution["schedule"]
    total_distance = solution["total_distance"]

    # Team locations
    locations = {
        'A': (0, 0),
        'B': (3, 4),
        'C': (6, 0),
        'D': (2, 8)
    }
    teams = ['A', 'B', 'C', 'D']

    # Pre-compute distance matrix
    distances = {}
    for team1 in teams:
        for team2 in teams:
            if team1 != team2:
                x1, y1 = locations[team1]
                x2, y2 = locations[team2]
                distances[(team1, team2)] = sqrt((x2-x1)**2 + (y2-y1)**2)

    # Validate schedule structure
    if not isinstance(schedule, list) or len(schedule) != 6:
        return {"valid": False, "message": "Schedule must be a list of 6 rounds"}

    # Validate each round
    matches_played = set()
    for round_idx, round_matches in enumerate(schedule):
        if not isinstance(round_matches, list) or len(round_matches) != 2:
            return {"valid": False, "message": f"Round {round_idx+1} must have exactly 2 matches"}

        teams_in_round = set()
        for match in round_matches:
            if not isinstance(match, dict):
                return {"valid": False, "message": f"Match in round {round_idx+1} must be an object"}
            if "home" not in match or "away" not in match:
                return {"valid": False, "message": f"Match in round {round_idx+1} missing home or away field"}

            home = match["home"]
            away = match["away"]

            if home not in teams or away not in teams:
                return {"valid": False, "message": f"Invalid team in round {round_idx+1}: {home} vs {away}"}

            if home == away:
                return {"valid": False, "message": f"Team cannot play itself in round {round_idx+1}: {home}"}

            if home in teams_in_round or away in teams_in_round:
                return {"valid": False, "message": f"Team plays multiple times in round {round_idx+1}"}

            teams_in_round.add(home)
            teams_in_round.add(away)
            matches_played.add((home, away))

        if len(teams_in_round) != 4:
            return {"valid": False, "message": f"Round {round_idx+1} must include all 4 teams"}

    # Validate double round-robin (each pair plays twice: once home, once away)
    expected_matches = set()
    for i, team1 in enumerate(teams):
        for j, team2 in enumerate(teams):
            if i != j:
                expected_matches.add((team1, team2))

    if matches_played != expected_matches:
        missing = expected_matches - matches_played
        extra = matches_played - expected_matches
        msg = "Double round-robin constraint violated. "
        if missing:
            msg += f"Missing matches: {missing}. "
        if extra:
            msg += f"Extra matches: {extra}."
        return {"valid": False, "message": msg}

    # Validate consecutive home/away constraint (max 2 consecutive)
    for team in teams:
        home_away_sequence = []
        for round_matches in schedule:
            for match in round_matches:
                if match["home"] == team:
                    home_away_sequence.append('H')
                elif match["away"] == team:
                    home_away_sequence.append('A')

        # Check for 3 consecutive home or away games
        for i in range(len(home_away_sequence) - 2):
            if (home_away_sequence[i] == home_away_sequence[i+1] == home_away_sequence[i+2]):
                return {"valid": False, "message": f"Team {team} has 3+ consecutive {'home' if home_away_sequence[i] == 'H' else 'away'} games"}

    # Calculate and validate total distance
    calculated_distance = 0
    for round_matches in schedule:
        for match in round_matches:
            home = match["home"]
            away = match["away"]
            # Away team travels from their home to opponent's home
            calculated_distance += distances[(away, home)]

    calculated_distance_int = int(round(calculated_distance))

    if abs(total_distance - calculated_distance_int) > 1:
        return {"valid": False, "message": f"Total distance mismatch: reported {total_distance}, calculated {calculated_distance_int}"}

    # Check if optimal (expected optimal is 75)
    expected_optimal = 75
    if calculated_distance_int == expected_optimal:
        return {"valid": True, "message": f"Solution is optimal with total distance {calculated_distance_int}"}
    else:
        return {"valid": True, "message": f"Solution is valid (distance {calculated_distance_int}), but not optimal (expected {expected_optimal})"}


if __name__ == "__main__":
    result = validate_solution()
    print(json.dumps(result))
