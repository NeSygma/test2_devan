#!/usr/bin/env python3
"""
Reference model for Strategic Voting problem.
Validates voting analysis and manipulation detection.
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
    except json.JSONDecodeError as e:
        return None


def validate_solution(solution):
    """Validate the strategic voting solution"""

    if not solution:
        return False, "No solution provided"

    # Check required top-level fields
    required_fields = ["election_result", "strategic_opportunities", "is_manipulation_proof", "analysis"]
    for field in required_fields:
        if field not in solution:
            return False, f"Missing required field: {field}"

    # Validate election_result structure
    election_result = solution["election_result"]
    if not isinstance(election_result, dict):
        return False, "election_result must be a dictionary"

    if "winner" not in election_result:
        return False, "election_result missing 'winner' field"
    if "vote_counts" not in election_result:
        return False, "election_result missing 'vote_counts' field"
    if "total_votes" not in election_result:
        return False, "election_result missing 'total_votes' field"

    # Validate vote_counts
    vote_counts = election_result["vote_counts"]
    if not isinstance(vote_counts, dict):
        return False, "vote_counts must be a dictionary"

    # Check total_votes consistency
    total_votes = sum(vote_counts.values())
    if election_result["total_votes"] != total_votes:
        return False, f"Total votes mismatch: sum of vote_counts is {total_votes}, but total_votes is {election_result['total_votes']}"

    # Check that we have exactly 4 votes (per instance data)
    if total_votes != 4:
        return False, f"Expected 4 total votes, got {total_votes}"

    # Check winner is correct (highest vote count)
    max_votes = max(vote_counts.values())
    candidates_with_max = [c for c, v in vote_counts.items() if v == max_votes]

    if election_result["winner"] not in candidates_with_max:
        return False, f"Winner '{election_result['winner']}' does not have the highest vote count"

    # Validate strategic_opportunities structure
    strategic_opps = solution["strategic_opportunities"]
    if not isinstance(strategic_opps, list):
        return False, "strategic_opportunities must be a list"

    for opp in strategic_opps:
        if not isinstance(opp, dict):
            return False, "Each strategic opportunity must be a dictionary"
        required_opp_fields = ["voter", "true_preference", "strategic_vote", "manipulation_detected", "benefit"]
        for field in required_opp_fields:
            if field not in opp:
                return False, f"Strategic opportunity missing field: {field}"

    # Validate analysis structure
    analysis = solution["analysis"]
    if not isinstance(analysis, dict):
        return False, "analysis must be a dictionary"

    required_analysis_fields = ["condorcet_winner", "strategic_voting_present", "voting_paradox", "min_coalition_size"]
    for field in required_analysis_fields:
        if field not in analysis:
            return False, f"analysis missing field: {field}"

    # Check min_coalition_size is the expected optimal value
    min_coalition = analysis["min_coalition_size"]
    if not isinstance(min_coalition, int) or min_coalition < 0:
        return False, f"min_coalition_size must be a non-negative integer, got {min_coalition}"

    # Expected optimal coalition size is 2
    if min_coalition != 2:
        return False, f"Expected optimal min_coalition_size of 2, got {min_coalition}"

    return True, "Solution valid. Strategic voting analysis correct with min_coalition_size=2."


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
