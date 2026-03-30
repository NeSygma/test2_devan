#!/usr/bin/env python3
"""
Reference model for Strategic Voting (Hard).
Validates coalition formation and manipulation success.
Also checks optimality (minimum coalition size = 2).
"""

import json
import sys

# Expected optimal value (minimum coalition size to achieve manipulation)
EXPECTED_OPTIMAL_COALITION_SIZE = 1


def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except (json.JSONDecodeError, EOFError) as e:
        print(json.dumps({"valid": False, "message": f"JSON parse error: {e}"}))
        sys.exit(0)


def validate_solution(solution):
    """Validate the strategic voting solution"""

    if not solution:
        return False, "No solution provided"

    # Check required fields
    required_fields = ["coalition", "strategic_votes", "original_election",
                       "manipulated_election", "manipulation_successful", "analysis"]
    for field in required_fields:
        if field not in solution:
            return False, f"Missing field: {field}"

    coalition = solution["coalition"]
    strategic_votes = solution["strategic_votes"]
    original = solution["original_election"]
    manipulated = solution["manipulated_election"]
    analysis = solution["analysis"]

    # Check coalition structure
    if "members" not in coalition or "size" not in coalition:
        return False, "Coalition must have 'members' and 'size' fields"

    if coalition["size"] != len(coalition["members"]):
        return False, f"Coalition size {coalition['size']} doesn't match members count {len(coalition['members'])}"

    # Check strategic votes match coalition
    if set(strategic_votes.keys()) != set(coalition["members"]):
        return False, "Strategic votes must be provided for exactly the coalition members"

    # Check original election format
    if "winner" not in original or "vote_counts" not in original:
        return False, "Original election must have 'winner' and 'vote_counts'"

    if "condorcet_winner" not in original:
        return False, "Original election must specify Condorcet winner"

    # Check manipulated election format
    if "winner" not in manipulated or "vote_counts" not in manipulated:
        return False, "Manipulated election must have 'winner' and 'vote_counts'"

    # Verify vote count changes are consistent with strategic votes
    original_counts = original["vote_counts"]
    manipulated_counts = manipulated["vote_counts"]

    # Total votes should remain constant
    original_total = sum(original_counts.values())
    manipulated_total = sum(manipulated_counts.values())
    if original_total != manipulated_total:
        return False, f"Total votes changed: {original_total} -> {manipulated_total}"

    # Check manipulation success
    if solution["manipulation_successful"]:
        # Winner must change to Condorcet winner
        if manipulated["winner"] != original["condorcet_winner"]:
            return False, "Successful manipulation must elect Condorcet winner"

        # Condorcet winner must beat original winner
        condorcet = original["condorcet_winner"]
        original_winner = original["winner"]
        if condorcet == original_winner:
            return False, "Condorcet winner already elected (no manipulation needed)"

        if manipulated_counts[condorcet] <= manipulated_counts[original_winner]:
            return False, f"Condorcet winner {condorcet} doesn't beat original winner {original_winner} in manipulated election"

    # Check analysis fields
    required_analysis = ["coalition_improved", "no_member_worse_off", "condorcet_winner_elected"]
    for field in required_analysis:
        if field not in analysis:
            return False, f"Analysis missing field: {field}"

    # If manipulation successful, Condorcet winner must be elected
    if solution["manipulation_successful"] and not analysis["condorcet_winner_elected"]:
        return False, "Successful manipulation must result in Condorcet winner elected"

    # Check optimality: coalition size should be minimal
    if coalition["size"] != EXPECTED_OPTIMAL_COALITION_SIZE:
        return False, f"Not optimal: coalition size={coalition['size']}, expected {EXPECTED_OPTIMAL_COALITION_SIZE}"

    return True, f"Solution valid and optimal (coalition size={EXPECTED_OPTIMAL_COALITION_SIZE})"


def main():
    """Main validation function"""
    solution = load_solution()

    if solution is None:
        result = {"valid": False, "message": "Invalid or missing JSON input"}
    else:
        is_valid, message = validate_solution(solution)
        result = {"valid": is_valid, "message": message}

    print(json.dumps(result))


if __name__ == "__main__":
    main()
