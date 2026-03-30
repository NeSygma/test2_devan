#!/usr/bin/env python3

import json
import sys
from collections import defaultdict

# Expected optimal value (extracted from reference solution)
EXPECTED_OPTIMAL_SYNERGY = 11

def get_problem_spec():
    """Returns the static data for the problem instance."""
    spec = {
        "people": {
            "Alex": {"level": "Senior", "skills": {"Programming", "Security"}},
            "Ben": {"level": "Senior", "skills": {"Programming", "DevOps"}},
            "Chloe": {"level": "Senior", "skills": {"Design", "Management"}},
            "David": {"level": "Senior", "skills": {"Testing", "DataScience"}},
            "Grace": {"level": "Senior", "skills": {"Management", "DataScience"}},
            "Harry": {"level": "Senior", "skills": {"DevOps", "Security"}},
            "Eva": {"level": "Junior", "skills": {"Programming", "Cloud"}},
            "Frank": {"level": "Junior", "skills": {"Design", "Testing"}},
            "Ivy": {"level": "Junior", "skills": {"Design", "Cloud"}},
            "Jack": {"level": "Junior", "skills": {"Testing", "Programming"}},
            "Kate": {"level": "Junior", "skills": {"Management", "DevOps"}},
            "Leo": {"level": "Junior", "skills": {"DataScience", "Security"}},
        },
        "projects": {
            "Alpha": {"req": "Security"},
            "Beta": {"req": "Cloud"},
            "Gamma": {"req": None},
        },
        "primary_skills": {"Programming", "Design", "Testing", "Management", "DataScience", "DevOps"},
        "incompatibilities": {("Alex", "Ben"), ("Chloe", "Grace"), ("David", "Harry")},
        "synergies": {
            frozenset(["Programming", "DevOps"]),
            frozenset(["Design", "DataScience"]),
            frozenset(["Management", "Testing"]),
            frozenset(["Security", "Cloud"]),
        }
    }
    return spec

def validate_solution(solution_json, spec):
    """Validates a solution against the problem's constraints."""
    try:
        data = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    # Basic structure validation
    if "teams" not in data or "total_synergy" not in data:
        return {"valid": False, "message": "Missing 'teams' or 'total_synergy' key."}
    if len(data["teams"]) != 3:
        return {"valid": False, "message": f"Expected 3 teams, found {len(data['teams'])}."}

    all_personnel = set(spec["people"].keys())
    assigned_personnel = set()
    assigned_projects = set()
    team_leaders = []

    for team in data["teams"]:
        # Team structure
        if not all(k in team for k in ["team_id", "project", "leader", "members", "synergy_score"]):
            return {"valid": False, "message": "Each team object is missing required keys."}
        if len(team["members"]) != 4:
            return {"valid": False, "message": f"Team {team['team_id']} must have 4 members, has {len(team['members'])}."}

        # Uniqueness checks
        for person in team["members"]:
            if person not in all_personnel:
                return {"valid": False, "message": f"Unknown person '{person}' in team {team['team_id']}."}
            if person in assigned_personnel:
                return {"valid": False, "message": f"Person '{person}' assigned to multiple teams."}
            assigned_personnel.add(person)

        if team["project"] in assigned_projects:
            return {"valid": False, "message": f"Project '{team['project']}' assigned to multiple teams."}
        assigned_projects.add(team["project"])

        # Leadership validation
        leader = team["leader"]
        if leader not in team["members"]:
            return {"valid": False, "message": f"Leader '{leader}' is not a member of team {team['team_id']}."}
        if spec["people"][leader]["level"] != "Senior":
            return {"valid": False, "message": f"Leader '{leader}' of team {team['team_id']} is not a Senior."}
        team_leaders.append(leader)

        # Incompatibility validation
        for p1 in team["members"]:
            for p2 in team["members"]:
                if p1 < p2 and (p1, p2) in spec["incompatibilities"]:
                    return {"valid": False, "message": f"Incompatible pair ({p1}, {p2}) in team {team['team_id']}."}

        # Project requirement validation
        team_skills = set().union(*(spec["people"][p]["skills"] for p in team["members"]))
        proj_req = spec["projects"].get(team["project"], {}).get("req")
        if proj_req and proj_req not in team_skills:
            return {"valid": False, "message": f"Team {team['team_id']} on project '{team['project']}' is missing required skill '{proj_req}'."}

        # Synergy score validation
        achieved_synergies = 0
        for s_pair in spec["synergies"]:
            if s_pair.issubset(team_skills):
                achieved_synergies += 1
        if team["synergy_score"] != achieved_synergies:
            return {"valid": False, "message": f"Team {team['team_id']} has incorrect synergy score. Stated: {team['synergy_score']}, Calculated: {achieved_synergies}."}

    # Global validation
    if assigned_personnel != all_personnel:
        return {"valid": False, "message": f"Not all personnel were assigned. Missing: {all_personnel - assigned_personnel}."}
    if assigned_projects != set(spec["projects"].keys()):
        return {"valid": False, "message": f"Not all projects were assigned. Missing: {set(spec['projects'].keys()) - assigned_projects}."}

    # Leader skill diversity validation
    leader_primary_skills = defaultdict(list)
    for leader in team_leaders:
        for skill in spec["people"][leader]["skills"]:
            if skill in spec["primary_skills"]:
                leader_primary_skills[skill].append(leader)
    for skill, leaders in leader_primary_skills.items():
        if len(leaders) > 1:
            return {"valid": False, "message": f"Leaders {leaders} clash on primary skill '{skill}'."}

    # Total synergy validation
    total_synergy_calculated = sum(t["synergy_score"] for t in data["teams"])
    if data["total_synergy"] != total_synergy_calculated:
        return {"valid": False, "message": f"Total synergy is incorrect. Stated: {data['total_synergy']}, Calculated: {total_synergy_calculated}."}

    # Check optimality
    if total_synergy_calculated != EXPECTED_OPTIMAL_SYNERGY:
        return {"valid": False, "message": f"Not optimal: total_synergy={total_synergy_calculated}, expected {EXPECTED_OPTIMAL_SYNERGY}"}

    return {"valid": True, "message": f"Solution is valid and optimal (total_synergy={EXPECTED_OPTIMAL_SYNERGY})"}

if __name__ == "__main__":
    try:
        solution_str = sys.stdin.read()
        problem_spec = get_problem_spec()
        result = validate_solution(solution_str, problem_spec)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"An unexpected error occurred: {e}"}))
