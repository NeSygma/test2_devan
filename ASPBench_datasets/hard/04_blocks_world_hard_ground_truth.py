#!/usr/bin/env python3
"""
Reference model for the Weighted Blocks World - Hard (feasibility validation only).

Validates solutions by checking action sequences, constraints, and goal achievement.
Does NOT check optimality - any valid plan is accepted.
"""

import json
import sys
from typing import Dict, List

BLOCKS = [chr(c) for c in range(ord('A'), ord('L') + 1)]  # A..L (12 blocks)
WEIGHT = {chr(ord('A') + i): i + 1 for i in range(12)}    # A=1 .. L=12
TABLE_LIMIT = 6  # Relaxed from 5 to 6 for solvability
MAX_HEIGHT = 5  # Relaxed from 4 to 5 for solvability

# Initial state mapping: on[X] = Y (Y in BLOCKS or 'table')
INITIAL_ON = {
    # Stack 1 (light)
    'A': 'B', 'B': 'C', 'C': 'D', 'D': 'table',
    # Stack 2 (mid)
    'E': 'F', 'F': 'G', 'G': 'H', 'H': 'table',
    # Stack 3 (heavy)
    'I': 'J', 'J': 'K', 'K': 'L', 'L': 'table'
}

# Goal mapping
GOAL_ON = {
    # Tower 1: L (table) <- I <- F <- C
    'C': 'F', 'F': 'I', 'I': 'L', 'L': 'table',
    # Tower 2: K (table) <- H <- E <- B
    'B': 'E', 'E': 'H', 'H': 'K', 'K': 'table',
    # Tower 3: J (table) <- G <- D <- A
    'A': 'D', 'D': 'G', 'G': 'J', 'J': 'table'
}

def verify_solution(solution_json: str) -> dict:
    """
    Verify if the given solution correctly solves the blocks world problem.
    Checks validity step-by-step under constraints and verifies the goal is reached.
    Does NOT check optimality - any valid plan is accepted.

    Input JSON keys:
      - plan_length: int
      - actions: list of {step, action, block, from, to}
    """
    # Parse input
    try:
        sol = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    actions = sol.get("actions")
    if not isinstance(actions, list):
        return {"valid": False, "message": "Missing or invalid 'actions' list"}

    # Working state
    on: Dict[str, str] = dict(INITIAL_ON)

    def is_clear(block: str) -> bool:
        for x, y in on.items():
            if y == block:
                return False
        return True

    def table_count() -> int:
        return sum(1 for b in BLOCKS if on[b] == 'table')

    def depth_of(block: str) -> int:
        d = 1
        current = on[block]
        seen = {block}
        while current != 'table':
            if current in seen:
                return MAX_HEIGHT + 1  # cycle guard
            seen.add(current)
            d += 1
            current = on[current]
        return d

    def check_height_ok() -> bool:
        return all(depth_of(b) <= MAX_HEIGHT for b in BLOCKS)

    # Validate and simulate
    for i, act in enumerate(actions):
        step = act.get('step', i + 1)
        block = act.get('block')
        src = act.get('from')
        dst = act.get('to')

        # Basic format checks
        if block not in BLOCKS or src not in (BLOCKS + ['table']) or dst not in (BLOCKS + ['table']):
            return {"valid": False, "message": f"Step {step}: Invalid block/from/to"}
        if act.get('action') != 'move':
            return {"valid": False, "message": f"Step {step}: Invalid action type"}
        if block == dst:
            return {"valid": False, "message": f"Step {step}: Cannot place {block} on itself"}
        if on[block] != src:
            return {"valid": False, "message": f"Step {step}: Block {block} is on {on[block]}, not {src}"}
        if not is_clear(block):
            return {"valid": False, "message": f"Step {step}: Block {block} is not clear"}
        if dst != 'table' and not is_clear(dst):
            return {"valid": False, "message": f"Step {step}: Destination {dst} is not clear"}

        # Weight constraint
        if dst != 'table' and WEIGHT[block] > WEIGHT[dst]:
            return {"valid": False, "message": f"Step {step}: Cannot place heavier {block} on lighter {dst}"}

        # Apply the move
        on[block] = dst

        # Global constraints after the move
        if table_count() > TABLE_LIMIT:
            return {"valid": False, "message": f"Step {step}: Table stack limit exceeded (> {TABLE_LIMIT})"}
        if not check_height_ok():
            return {"valid": False, "message": f"Step {step}: Stack height limit exceeded (> {MAX_HEIGHT})"}

    # Verify goal state
    if on != GOAL_ON:
        return {"valid": False, "message": f"Goal not reached. Final state does not match goal"}

    # Valid solution found (no optimality check)
    return {"valid": True, "message": f"Valid solution with {len(actions)} moves"}

def main():
    try:
        solution_json = sys.stdin.read()
        result = verify_solution(solution_json)
        print(json.dumps(result, indent=2))
    except Exception as e:
        result = {"valid": False, "message": f"Error: {str(e)}"}
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
