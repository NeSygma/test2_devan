#!/usr/bin/env python3
"""
Reference model validator for 006_stable_marriage_extended_easy.md

Validates solutions from stdin for the extended stable marriage problem.
"""

import json
import sys
from typing import List, Dict, Set, Tuple

def validate_solution():
    """
    Validate a solution from stdin.

    Returns:
        dict: Validation result with 'valid' and 'message' fields
    """

    # Load solution from stdin
    try:
        data = sys.stdin.read().strip()
        if not data:
            return {"valid": False, "message": "No solution provided"}
        solution = json.loads(data)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    # Check required fields
    if "stable_matchings" not in solution:
        return {"valid": False, "message": "Missing 'stable_matchings' field"}
    if "count" not in solution:
        return {"valid": False, "message": "Missing 'count' field"}

    stable_matchings = solution["stable_matchings"]
    count = solution["count"]

    # Define problem instance
    men = ['m1', 'm2', 'm3', 'm4']
    women = ['w1', 'w2', 'w3', 'w4']

    # Men's preferences (acceptable partners only)
    men_prefs = {
        'm1': ['w1', 'w2', 'w3'],
        'm2': ['w2', 'w3', 'w4'],
        'm3': ['w3', 'w4', 'w1'],
        'm4': ['w4', 'w1', 'w2']
    }

    # Women's preferences (acceptable partners only)
    women_prefs = {
        'w1': ['m4', 'm1', 'm3'],
        'w2': ['m1', 'm2', 'm4'],
        'w3': ['m2', 'm3', 'm1'],
        'w4': ['m3', 'm4', 'm2']
    }

    # Create preference ranking dictionaries
    men_rank = {man: {woman: i for i, woman in enumerate(men_prefs[man])} for man in men}
    women_rank = {woman: {man: i for i, man in enumerate(women_prefs[woman])} for woman in women}

    def is_acceptable(man: str, woman: str) -> bool:
        """Check if a pair is mutually acceptable."""
        return woman in men_prefs[man] and man in women_prefs[woman]

    def is_stable(matching: List[List[str]]) -> bool:
        """Check if a matching is stable (no blocking pairs)."""
        # Convert to dictionaries for easier lookup
        man_to_woman = {pair[0]: pair[1] for pair in matching}
        woman_to_man = {pair[1]: pair[0] for pair in matching}

        # Check all possible pairs for blocking
        for man in men:
            for woman in women:
                # Skip if not acceptable
                if not is_acceptable(man, woman):
                    continue

                # Skip if already matched
                if man_to_woman.get(man) == woman:
                    continue

                # Check if this is a blocking pair
                current_man_partner = man_to_woman.get(man)
                current_woman_partner = woman_to_man.get(woman)

                # Would man prefer woman over current partner?
                man_prefers = True
                if current_man_partner is not None:
                    man_current_rank = men_rank[man].get(current_man_partner, float('inf'))
                    man_new_rank = men_rank[man].get(woman, float('inf'))
                    man_prefers = man_new_rank < man_current_rank

                # Would woman prefer man over current partner?
                woman_prefers = True
                if current_woman_partner is not None:
                    woman_current_rank = women_rank[woman].get(current_woman_partner, float('inf'))
                    woman_new_rank = women_rank[woman].get(man, float('inf'))
                    woman_prefers = woman_new_rank < woman_current_rank

                # If both prefer, it's a blocking pair
                if man_prefers and woman_prefers:
                    return False

        return True

    # Validate each matching
    if not isinstance(stable_matchings, list):
        return {"valid": False, "message": "stable_matchings must be a list"}

    for i, matching in enumerate(stable_matchings):
        if not isinstance(matching, list):
            return {"valid": False, "message": f"Matching {i} is not a list"}

        # Check format of pairs
        for pair in matching:
            if not isinstance(pair, list) or len(pair) != 2:
                return {"valid": False, "message": f"Invalid pair format in matching {i}: {pair}"}

            man, woman = pair
            if man not in men:
                return {"valid": False, "message": f"Invalid man '{man}' in matching {i}"}
            if woman not in women:
                return {"valid": False, "message": f"Invalid woman '{woman}' in matching {i}"}

            # Check acceptability
            if not is_acceptable(man, woman):
                return {"valid": False, "message": f"Unacceptable pair [{man}, {woman}] in matching {i}"}

        # Check uniqueness (each person matched at most once)
        matched_men = [pair[0] for pair in matching]
        matched_women = [pair[1] for pair in matching]

        if len(matched_men) != len(set(matched_men)):
            return {"valid": False, "message": f"Duplicate man in matching {i}"}
        if len(matched_women) != len(set(matched_women)):
            return {"valid": False, "message": f"Duplicate woman in matching {i}"}

        # Check stability
        if not is_stable(matching):
            return {"valid": False, "message": f"Matching {i} is not stable (has blocking pairs)"}

    # Check count matches
    if count != len(stable_matchings):
        return {"valid": False, "message": f"Count mismatch: count={count}, but {len(stable_matchings)} matchings provided"}

    # Check if all matchings are unique
    unique_matchings = set()
    for matching in stable_matchings:
        matching_tuple = tuple(tuple(pair) for pair in sorted(matching))
        if matching_tuple in unique_matchings:
            return {"valid": False, "message": "Duplicate matchings found"}
        unique_matchings.add(matching_tuple)

    # Success - found stable matchings
    return {"valid": True, "message": f"Solution correct: {count} stable matching(s) found"}

def main():
    """Main function to validate solution and output result."""
    result = validate_solution()
    print(json.dumps(result))

if __name__ == "__main__":
    main()
