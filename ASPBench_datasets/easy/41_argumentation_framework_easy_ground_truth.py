#!/usr/bin/env python3
"""
Reference model for Abstract Argumentation Framework problem.
Validates whether proposed stable extensions are correct.
"""

import json
import sys
from typing import List, Set, Tuple


def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def get_problem_instance():
    """Define the problem instance"""
    arguments = {'a', 'b', 'c', 'd', 'e', 'f'}
    attacks = {
        ('a', 'b'),
        ('b', 'c'),
        ('c', 'd'),
        ('d', 'e'),
        ('e', 'f'),
        ('f', 'a'),
        ('b', 'f'),
        ('d', 'b')
    }
    return arguments, attacks


def is_conflict_free(extension: Set[str], attacks: Set[Tuple[str, str]]) -> bool:
    """Check if extension is conflict-free"""
    for attacker, target in attacks:
        if attacker in extension and target in extension:
            return False
    return True


def is_defending(extension: Set[str], arguments: Set[str], attacks: Set[Tuple[str, str]]) -> bool:
    """Check if extension defends all its arguments"""
    for arg in extension:
        # Find all attackers of this argument
        attackers = {attacker for attacker, target in attacks if target == arg}

        # For each attacker, there must be a defender in the extension
        for attacker in attackers:
            defenders = {defender for defender, target in attacks if target == attacker and defender in extension}
            if not defenders:
                return False
    return True


def is_attacking_outside(extension: Set[str], arguments: Set[str], attacks: Set[Tuple[str, str]]) -> bool:
    """Check if extension attacks every argument not in the extension (maximality)"""
    outside_args = arguments - extension

    for outside_arg in outside_args:
        # Check if any argument in extension attacks this outside argument
        attackers_from_extension = {attacker for attacker, target in attacks
                                  if target == outside_arg and attacker in extension}
        if not attackers_from_extension:
            return False
    return True


def is_stable_extension(extension: Set[str], arguments: Set[str], attacks: Set[Tuple[str, str]]) -> bool:
    """Check if a set of arguments forms a stable extension"""
    return (is_conflict_free(extension, attacks) and
            is_defending(extension, arguments, attacks) and
            is_attacking_outside(extension, arguments, attacks))


def get_all_stable_extensions(arguments: Set[str], attacks: Set[Tuple[str, str]]) -> List[Set[str]]:
    """Find all stable extensions by exhaustive search"""
    stable_extensions = []

    # Check all possible subsets of arguments
    from itertools import combinations

    for r in range(len(arguments) + 1):
        for subset in combinations(arguments, r):
            extension = set(subset)
            if is_stable_extension(extension, arguments, attacks):
                stable_extensions.append(extension)

    return stable_extensions


def validate_solution(solution):
    """Validate the proposed solution"""
    if not isinstance(solution, dict):
        return False, "Solution must be a JSON object"

    if "stable_extensions" not in solution:
        return False, "Missing 'stable_extensions' field"

    extensions = solution["stable_extensions"]
    if not isinstance(extensions, list):
        return False, "stable_extensions must be a list"

    arguments, attacks = get_problem_instance()

    # Convert string extensions to sets
    proposed_extensions = []
    for ext in extensions:
        if not isinstance(ext, list):
            return False, "Each extension must be a list of arguments"

        for arg in ext:
            if not isinstance(arg, str):
                return False, "Each argument must be a string"
            if arg not in arguments:
                return False, f"Unknown argument: {arg}"

        proposed_extensions.append(set(ext))

    # Get the correct stable extensions
    correct_extensions = get_all_stable_extensions(arguments, attacks)

    # Check if proposed extensions match correct ones (order doesn't matter)
    if len(proposed_extensions) != len(correct_extensions):
        return False, f"Expected {len(correct_extensions)} stable extensions, got {len(proposed_extensions)}"

    # Convert to sets for comparison
    proposed_set = set(frozenset(ext) for ext in proposed_extensions)
    correct_set = set(frozenset(ext) for ext in correct_extensions)

    if proposed_set != correct_set:
        return False, "Proposed extensions do not match the correct stable extensions"

    # Validate each proposed extension individually
    for i, ext in enumerate(proposed_extensions):
        if not is_stable_extension(ext, arguments, attacks):
            ext_list = sorted(list(ext))
            return False, f"Extension {ext_list} is not a valid stable extension"

    return True, "All stable extensions are correct"


def main():
    solution = load_solution()

    if solution is None:
        result = {"valid": False, "message": "Invalid JSON input"}
    else:
        is_valid, message = validate_solution(solution)
        result = {"valid": is_valid, "message": message}

    print(json.dumps(result))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
