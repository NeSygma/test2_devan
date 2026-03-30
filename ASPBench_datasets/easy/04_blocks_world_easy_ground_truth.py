#!/usr/bin/env python3
"""
Reference model for Blocks World Planning Problem
Validates solutions by checking action sequences and goal achievement.
"""

import json
import sys
from typing import Dict, Any

def verify_solution(solution: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify if the given solution correctly solves the blocks world problem.

    Initial State: A on table, B on table, C on A
    Goal State: A on B, B on C, C on table

    Args:
        solution: Dictionary containing plan_length and actions

    Returns:
        dict with keys 'valid' (bool) and 'message' (str)
    """

    # Check required fields
    if "actions" not in solution:
        return {"valid": False, "message": "Missing required field: actions"}

    if "plan_length" not in solution:
        return {"valid": False, "message": "Missing required field: plan_length"}

    actions = solution["actions"]
    plan_length = solution["plan_length"]

    # Verify plan_length matches actions count
    if len(actions) != plan_length:
        return {
            "valid": False,
            "message": f"plan_length ({plan_length}) does not match actions count ({len(actions)})"
        }

    # Initialize state
    # on[block] = what it's on ('table' or another block)
    on = {'A': 'table', 'B': 'table', 'C': 'A'}
    # clear[block] = True if nothing on top
    clear = {'A': False, 'B': True, 'C': True}

    # Goal state
    goal_on = {'A': 'B', 'B': 'C', 'C': 'table'}

    # Helper function to check if a block is clear
    def is_clear(block):
        return clear.get(block, block == 'table')

    # Helper function to update clear status
    def update_clear():
        nonlocal clear
        clear = {'A': True, 'B': True, 'C': True}
        for block in ['A', 'B', 'C']:
            for other in ['A', 'B', 'C']:
                if other != block and on[other] == block:
                    clear[block] = False
                    break

    # Execute plan
    for i, action in enumerate(actions):
        if not isinstance(action, dict):
            return {
                "valid": False,
                "message": f"Step {i+1}: Invalid action format (not a dict)"
            }

        # Extract action details
        step = action.get('step')
        action_type = action.get('action')
        block = action.get('block')
        from_pos = action.get('from')
        to_pos = action.get('to')

        # Validate action format
        if step != i + 1:
            return {
                "valid": False,
                "message": f"Action {i+1}: step number should be {i+1}, got {step}"
            }

        if action_type != 'move':
            return {
                "valid": False,
                "message": f"Step {step}: action should be 'move', got '{action_type}'"
            }

        if not all([block, from_pos is not None, to_pos is not None]):
            return {
                "valid": False,
                "message": f"Step {step}: Missing required fields (block, from, to)"
            }

        # Check if block exists
        if block not in ['A', 'B', 'C']:
            return {
                "valid": False,
                "message": f"Step {step}: Invalid block '{block}'"
            }

        # Check current position matches 'from'
        if on[block] != from_pos:
            return {
                "valid": False,
                "message": f"Step {step}: Block {block} is on {on[block]}, not {from_pos}"
            }

        # Check if block is clear (can be moved)
        if not is_clear(block):
            return {
                "valid": False,
                "message": f"Step {step}: Block {block} is not clear (has something on top)"
            }

        # Check if destination is clear (unless it's table)
        if to_pos != 'table' and not is_clear(to_pos):
            return {
                "valid": False,
                "message": f"Step {step}: Destination {to_pos} is not clear"
            }

        # Check if destination exists
        if to_pos not in ['A', 'B', 'C', 'table']:
            return {
                "valid": False,
                "message": f"Step {step}: Invalid destination '{to_pos}'"
            }

        # Can't place a block on itself
        if block == to_pos:
            return {
                "valid": False,
                "message": f"Step {step}: Cannot place block {block} on itself"
            }

        # Apply the move
        on[block] = to_pos
        update_clear()

    # Check if goal is reached
    if on != goal_on:
        return {
            "valid": False,
            "message": f"Goal not reached. Final state: {on}, expected: {goal_on}"
        }

    # Check optimality - for this problem, 3 steps is optimal
    if plan_length == 3:
        message = f"Valid and optimal solution with {plan_length} moves"
    else:
        message = f"Valid solution with {plan_length} moves (optimal is 3)"

    return {
        "valid": True,
        "message": message
    }

def main():
    """Read solution from stdin and validate it."""
    try:
        data = sys.stdin.read().strip()
        if not data:
            print(json.dumps({"valid": False, "message": "No input provided"}))
            return

        solution = json.loads(data)
        result = verify_solution(solution)
        print(json.dumps(result))
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {e}"}))
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Error: {str(e)}"}))

if __name__ == "__main__":
    main()
