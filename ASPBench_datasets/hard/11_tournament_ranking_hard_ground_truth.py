#!/usr/bin/env python3
"""
Reference model for Tournament Ranking Problem (Hard Variant)
Reads a solution from stdin and validates feasibility only (no optimality check).

Validates:
- All teams ranked (1-30)
- No duplicate rankings
- All hard constraints satisfied
- Computes violations (but doesn't check if optimal)

Outputs JSON: {"valid": true/false, "message": "..."}
"""

import json
import sys


def get_problem_data():
    """Returns the problem constraints and data."""
    n = 30
    teams = [f"T{i:02d}" for i in range(1, n+1)]

    # Generate match results (same pattern as code)
    import random
    random.seed(42)
    W = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            w = random.randint(1,5)
            if (i+j)%2==0: W[i][j]=w
            else: W[j][i]=w

    seeds = {f"T{i:02d}" for i in range(1,11)}
    expected = {f"T{i:02d}":i for i in range(1,n+1)}

    must_above = [(f"T{a:02d}",f"T{b:02d}") for a,b in [
        (5,18),(10,11),(7,28),(8,19),(2,27),(4,21),(3,12),(6,17),(9,25),(1,30),
        (13,29),(14,20),(15,16),(22,8),(23,3),(24,7),(26,5),(25,14),(20,22),(28,15)
    ]]

    banned_adj = {frozenset([f"T{a:02d}",f"T{b:02d}"]) for a,b in [
        (2,3),(4,5),(6,7),(8,9),(10,11),(12,13),(14,15),(16,17),(18,19),(20,21),
        (22,23),(24,25),(26,27),(28,29),(1,30)
    ]}

    forbid_top = {f"T{i:02d}":k for i,k in [
        (27,3),(14,5),(18,4),(21,2),(22,6),(19,8),(16,7),(29,10)
    ]}

    forbid_block = {f"T{i:02d}":(k1,k2) for i,k1,k2 in [
        (14,11,15),(20,5,9),(23,13,17),(2,21,25),(9,26,30)
    ]}

    # Groups (6 groups of 5)
    group = {}
    for i in range(n):
        group[f"T{i+1:02d}"] = "ABCDEF"[i//5]

    return {
        "n": n,
        "teams": teams,
        "W": W,
        "seeds": seeds,
        "expected": expected,
        "must_above": must_above,
        "banned_adj": banned_adj,
        "forbid_top": forbid_top,
        "forbid_block": forbid_block,
        "group": group
    }


def validate_solution(solution):
    """Validate a tournament ranking solution from stdin."""
    data = get_problem_data()

    # Check solution structure
    if not isinstance(solution, dict):
        return {"valid": False, "message": "Solution must be a JSON object"}

    if not solution.get("valid", False):
        return {"valid": False, "message": "Solution marked as invalid"}

    if "ranking" not in solution:
        return {"valid": False, "message": "Missing 'ranking' field"}

    ranking = solution["ranking"]
    if not isinstance(ranking, list):
        return {"valid": False, "message": "'ranking' must be a list"}

    if len(ranking) != data["n"]:
        return {"valid": False, "message": f"Ranking must have {data['n']} teams, got {len(ranking)}"}

    # Check all teams present and no duplicates
    ranking_set = set(ranking)
    if len(ranking_set) != data["n"]:
        return {"valid": False, "message": "Ranking contains duplicate teams"}

    if ranking_set != set(data["teams"]):
        return {"valid": False, "message": "Ranking doesn't contain all teams"}

    # Build position map
    pos = {team: i+1 for i, team in enumerate(ranking)}

    # Validate constraints
    # 1. Must-above constraints
    for x, y in data["must_above"]:
        if pos[x] >= pos[y]:
            return {"valid": False, "message": f"Must-above constraint violated: {x} must rank above {y}"}

    # 2. Adjacency constraints
    for i in range(data["n"]-1):
        pair = frozenset([ranking[i], ranking[i+1]])
        if pair in data["banned_adj"]:
            return {"valid": False, "message": f"Adjacency constraint violated: {ranking[i]} and {ranking[i+1]} cannot be adjacent"}

    # 3. Forbid-top constraints
    for t, k in data["forbid_top"].items():
        if pos[t] <= k:
            return {"valid": False, "message": f"Forbid-top constraint violated: {t} cannot be in top {k}"}

    # 4. Forbid-block constraints
    for t, (k1, k2) in data["forbid_block"].items():
        if k1 <= pos[t] <= k2:
            return {"valid": False, "message": f"Forbid-block constraint violated: {t} cannot be in positions {k1}-{k2}"}

    # 5. Diversity constraint (no more than 2 from same group in any window of 5)
    for i in range(data["n"]-4):
        window = ranking[i:i+5]
        cnt = {}
        for team in window:
            g = data["group"][team]
            cnt[g] = cnt.get(g, 0) + 1
            if cnt[g] > 2:
                return {"valid": False, "message": f"Diversity constraint violated at position {i+1}: too many from group {g}"}

    # 6. Seed quota (at least 6 seeds in top 10)
    top10 = sum(1 for t in data["seeds"] if pos[t] <= 10)
    if top10 < 6:
        return {"valid": False, "message": f"Seed quota violated: only {top10} seeds in top 10 (need 6)"}

    # Compute violations and check bound
    violations = 0
    for i in range(data["n"]):
        for j in range(i+1, data["n"]):
            team_i_idx = data["teams"].index(ranking[i])
            team_j_idx = data["teams"].index(ranking[j])
            if data["W"][team_j_idx][team_i_idx] > 0:
                violations += data["W"][team_j_idx][team_i_idx]

    # 7. Violation bound constraint
    MAX_VIOLATIONS = 650
    if violations > MAX_VIOLATIONS:
        return {"valid": False, "message": f"Violation bound exceeded: {violations} > {MAX_VIOLATIONS}"}

    return {"valid": True, "message": f"Valid tournament ranking (violations={violations}, bound={MAX_VIOLATIONS})"}


def main():
    try:
        solution_json = sys.stdin.read().strip()
        if not solution_json:
            print(json.dumps({"valid": False, "message": "No solution provided"}))
            sys.exit(1)

        solution = json.loads(solution_json)
        result = validate_solution(solution)
        print(json.dumps(result))
        sys.exit(0 if result["valid"] else 1)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Validation error: {e}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
