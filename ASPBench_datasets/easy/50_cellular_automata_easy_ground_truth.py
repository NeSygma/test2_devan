#!/usr/bin/env python3
"""
Reference model for Cellular Automata Pattern Detection problem.
Validates whether detected patterns follow Game of Life rules correctly.
"""

import json
import sys
from typing import List, Dict, Tuple


def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def get_initial_config():
    """Get the initial configuration"""
    return [
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0]
    ]


def count_neighbors(grid: List[List[int]], row: int, col: int) -> int:
    """Count living neighbors of a cell"""
    count = 0
    rows, cols = len(grid), len(grid[0])

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                count += grid[nr][nc]

    return count


def evolve_grid(grid: List[List[int]]) -> List[List[int]]:
    """Apply Game of Life rules to evolve grid one generation"""
    rows, cols = len(grid), len(grid[0])
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]

    for i in range(rows):
        for j in range(cols):
            neighbors = count_neighbors(grid, i, j)

            if grid[i][j] == 1:  # Living cell
                if neighbors < 2:
                    new_grid[i][j] = 0  # Dies from underpopulation
                elif neighbors in [2, 3]:
                    new_grid[i][j] = 1  # Survives
                else:
                    new_grid[i][j] = 0  # Dies from overpopulation
            else:  # Dead cell
                if neighbors == 3:
                    new_grid[i][j] = 1  # Becomes alive
                else:
                    new_grid[i][j] = 0  # Stays dead

    return new_grid


def grids_equal(grid1: List[List[int]], grid2: List[List[int]]) -> bool:
    """Check if two grids are equal"""
    if len(grid1) != len(grid2) or len(grid1[0]) != len(grid2[0]):
        return False

    for i in range(len(grid1)):
        for j in range(len(grid1[0])):
            if grid1[i][j] != grid2[i][j]:
                return False

    return True


def find_stable_patterns():
    """Find all stable patterns by simulation"""
    initial = get_initial_config()
    states = [initial]
    current = initial

    # Simulate up to 20 generations to find cycles
    for gen in range(20):
        next_state = evolve_grid(current)

        # Check if this state has appeared before
        for i, prev_state in enumerate(states):
            if grids_equal(next_state, prev_state):
                # Found a cycle
                cycle_start = i
                cycle_length = len(states) - i
                cycle_states = states[cycle_start:]

                return [{
                    "pattern_id": 1,
                    "period": cycle_length,
                    "states": cycle_states
                }]

        states.append(next_state)
        current = next_state

    # No cycle found, return empty
    return []


def validate_pattern(pattern: Dict) -> Tuple[bool, str]:
    """Validate a single pattern"""
    if not isinstance(pattern, dict):
        return False, "Pattern must be a dictionary"

    required_fields = ["pattern_id", "period", "states"]
    for field in required_fields:
        if field not in pattern:
            return False, f"Missing field: {field}"

    pattern_id = pattern["pattern_id"]
    period = pattern["period"]
    states = pattern["states"]

    if not isinstance(pattern_id, int) or pattern_id <= 0:
        return False, "pattern_id must be a positive integer"

    if not isinstance(period, int) or period <= 0:
        return False, "period must be a positive integer"

    if not isinstance(states, list):
        return False, "states must be a list"

    if len(states) != period:
        return False, f"Number of states ({len(states)}) must equal period ({period})"

    # Validate each state
    for i, state in enumerate(states):
        if not isinstance(state, list) or len(state) != 5:
            return False, f"State {i} must be a 5x5 grid"

        for j, row in enumerate(state):
            if not isinstance(row, list) or len(row) != 5:
                return False, f"State {i} row {j} must have 5 elements"

            for k, cell in enumerate(row):
                if cell not in [0, 1]:
                    return False, f"State {i} cell ({j},{k}) must be 0 or 1, got {cell}"

    # Verify state transitions follow Game of Life rules
    for i in range(len(states)):
        current_state = states[i]
        next_state = states[(i + 1) % len(states)]
        expected_next = evolve_grid(current_state)

        if not grids_equal(next_state, expected_next):
            return False, f"State transition {i} -> {(i+1)%len(states)} doesn't follow Game of Life rules"

    return True, ""


def validate_solution(solution):
    """Validate the proposed solution"""
    if not isinstance(solution, dict):
        return False, "Solution must be a JSON object"

    if "stable_patterns" not in solution:
        return False, "Missing 'stable_patterns' field"

    patterns = solution["stable_patterns"]

    if not isinstance(patterns, list):
        return False, "stable_patterns must be a list"

    # Find expected patterns
    expected_patterns = find_stable_patterns()

    if len(patterns) != len(expected_patterns):
        return False, f"Expected {len(expected_patterns)} patterns, got {len(patterns)}"

    # Validate each pattern
    for i, pattern in enumerate(patterns):
        is_valid, msg = validate_pattern(pattern)
        if not is_valid:
            return False, f"Pattern {i}: {msg}"

    return True, f"Found {len(patterns)} valid stable pattern(s)"


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
