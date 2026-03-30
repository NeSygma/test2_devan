#!/usr/bin/env python3
"""
Reference model for the Hierarchical Argumentation Framework problem.
This script validates a given solution by checking it against the ground truth,
which is determined by exhaustively checking all possible subsets of arguments.
"""

import json
import sys
from itertools import combinations
from typing import Dict, List, Set, Tuple

def get_problem_instance() -> Tuple[Set[str], Dict[str, int], Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    """Defines the hardcoded problem instance."""
    arguments = {f'a{i}' for i in range(1, 17)}
    levels = {
        **{f'a{i}': 1 for i in range(1, 7)},
        **{f'a{i}': 2 for i in range(7, 13)},
        **{f'a{i}': 3 for i in range(13, 17)},
    }
    strong_attacks = {
        ('a2', 'a1'), ('a9', 'a8'), ('a14', 'a13'), ('a15', 'a16'),
        ('a1', 'a14'), ('a16', 'a15'), ('a1', 'a3'), ('a1', 'a4'),
        ('a13', 'a7'), ('a13', 'a10'), ('a3', 'a5'), ('a5', 'a3')
    }
    weak_attacks = {
        ('a8', 'a2'), ('a13', 'a9'), ('a8', 'a5'), ('a8', 'a6'),
        ('a16', 'a11'), ('a16', 'a12'), ('a2', 'a7'), ('a10', 'a13')
    }
    return arguments, levels, strong_attacks, weak_attacks

def is_successful_attack(
    attacker: str, target: str,
    levels: Dict[str, int],
    strong_attacks: Set[Tuple[str, str]],
    weak_attacks: Set[Tuple[str, str]]
) -> bool:
    """Check if an attack from attacker to target is successful."""
    if (attacker, target) in strong_attacks:
        return True
    if (attacker, target) in weak_attacks and levels[attacker] > levels[target]:
        return True
    return False

def check_properties(
    extension: Set[str],
    arguments: Set[str],
    levels: Dict[str, int],
    strong_attacks: Set[Tuple[str, str]],
    weak_attacks: Set[Tuple[str, str]]
) -> bool:
    """Check if a given set of arguments is a hierarchical stable extension."""
    # 1. Conflict-Free
    for arg1 in extension:
        for arg2 in extension:
            if is_successful_attack(arg1, arg2, levels, strong_attacks, weak_attacks):
                return False

    # 2. Self-Defending
    for member in extension:
        attackers = {arg for arg in arguments if is_successful_attack(arg, member, levels, strong_attacks, weak_attacks)}
        for attacker in attackers:
            if not any(is_successful_attack(defender, attacker, levels, strong_attacks, weak_attacks) for defender in extension):
                return False

    # 3. Maximal
    outsiders = arguments - extension
    for outsider in outsiders:
        if not any(is_successful_attack(attacker, outsider, levels, strong_attacks, weak_attacks) for attacker in extension):
            return False

    return True

def find_all_correct_extensions(
    arguments: Set[str],
    levels: Dict[str, int],
    strong_attacks: Set[Tuple[str, str]],
    weak_attacks: Set[Tuple[str, str]]
) -> List[List[str]]:
    """Find all hierarchical stable extensions by exhaustive search."""
    correct_extensions = []
    for r in range(len(arguments) + 1):
        for subset in combinations(arguments, r):
            extension_set = set(subset)
            if check_properties(extension_set, arguments, levels, strong_attacks, weak_attacks):
                correct_extensions.append(sorted(list(extension_set)))
    return sorted(correct_extensions)

def main():
    """Main validation logic."""
    try:
        solution = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({"valid": False, "message": "Invalid or empty JSON input."}))
        return 1

    if "hierarchical_stable_extensions" not in solution:
        print(json.dumps({"valid": False, "message": "Missing 'hierarchical_stable_extensions' key in solution."}))
        return 1

    proposed_extensions = solution["hierarchical_stable_extensions"]

    # Sort inner lists for consistent comparison
    try:
        proposed_extensions_sorted = sorted([sorted(ext) for ext in proposed_extensions])
    except (TypeError, AttributeError):
        print(json.dumps({"valid": False, "message": "'hierarchical_stable_extensions' must be a list of lists of strings."}))
        return 1

    arguments, levels, strong_attacks, weak_attacks = get_problem_instance()

    correct_extensions = find_all_correct_extensions(arguments, levels, strong_attacks, weak_attacks)

    if proposed_extensions_sorted == correct_extensions:
        print(json.dumps({"valid": True, "message": "Solution is correct."}))
        return 0
    else:
        msg = (f"Solution is incorrect. Expected {len(correct_extensions)} extensions, found {len(proposed_extensions_sorted)}. "
               f"Expected: {correct_extensions}, Got: {proposed_extensions_sorted}")
        print(json.dumps({"valid": False, "message": msg}))
        return 1

if __name__ == "__main__":
    sys.exit(main())
