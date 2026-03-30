#!/usr/bin/env python3

import json
import sys

def validate_solution(solution):
    """Validate a team formation solution."""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    if "teams" not in solution:
        return {"valid": False, "message": "Missing 'teams' key"}

    teams = solution["teams"]

    if len(teams) != 2:
        return {"valid": False, "message": f"Expected 2 teams, got {len(teams)}"}

    # Check team sizes
    for i, team in enumerate(teams):
        if not isinstance(team, list):
            return {"valid": False, "message": f"Team {i+1} must be a list"}
        if len(team) != 4:
            return {"valid": False, "message": f"Team {i+1} must have exactly 4 people, got {len(team)}"}

    # People and their skills
    people_skills = {
        "Alice": {"Programming", "Design"},
        "Bob": {"Programming", "Testing"},
        "Carol": {"Design", "Management"},
        "Dave": {"Testing", "Management"},
        "Eve": {"Programming", "Documentation"},
        "Frank": {"Design", "Documentation"},
        "Grace": {"Testing", "Documentation"},
        "Henry": {"Management", "Documentation"}
    }

    all_people = set(people_skills.keys())
    all_skills = {"Programming", "Design", "Testing", "Management"}

    # Check that all people are assigned exactly once
    assigned_people = set()
    for i, team in enumerate(teams):
        for person in team:
            if person not in all_people:
                return {"valid": False, "message": f"Unknown person: {person}"}
            if person in assigned_people:
                return {"valid": False, "message": f"Person {person} assigned to multiple teams"}
            assigned_people.add(person)

    if len(assigned_people) != 8:
        return {"valid": False, "message": f"Expected 8 people assigned, got {len(assigned_people)}"}

    if assigned_people != all_people:
        missing = all_people - assigned_people
        return {"valid": False, "message": f"Missing people: {missing}"}

    # Check skill coverage for each team
    for i, team in enumerate(teams):
        team_skills = set()
        for person in team:
            team_skills.update(people_skills[person])

        if not all_skills.issubset(team_skills):
            missing_skills = all_skills - team_skills
            return {"valid": False, "message": f"Team {i+1} missing required skills: {missing_skills}"}

    return {"valid": True, "message": "Solution is valid"}

if __name__ == "__main__":
    try:
        data = sys.stdin.read().strip()
        if not data:
            result = {"valid": False, "message": "No input provided"}
        else:
            solution = json.loads(data)
            result = validate_solution(solution)
    except json.JSONDecodeError as e:
        result = {"valid": False, "message": f"Invalid JSON: {e}"}
    except Exception as e:
        result = {"valid": False, "message": f"Error validating solution: {e}"}

    print(json.dumps(result))
