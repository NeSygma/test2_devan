#!/usr/bin/env python3
"""
Reference model for Colored Nonogram with Diagonal Constraints (24x24)
- Verifies solutions
- Can output a known valid solution (--find)
- Validation only (no optimality checks)
"""

import json
import sys

PALETTE = {0: "white", 1: "red", 2: "green", 3: "blue"}
N = 24

# Row clues: list of rows; each row is list of (color, length)
ROW_CLUES = [
    [(1,10), (2,4), (1,10)],                      # Row 1
    [(1,10), (2,4), (1,10)],                      # Row 2
    [(1,2), (2,4), (1,2)],                        # Row 3
    [(1,2), (2,4), (1,2)],                        # Row 4
    [(1,2), (2,4), (1,2)],                        # Row 5
    [(1,2), (2,4), (1,2)],                        # Row 6
    [(1,2), (2,4), (1,2)],                        # Row 7
    [(1,2), (2,4), (1,2)],                        # Row 8
    [(1,2), (3,8), (1,2)],                        # Row 9
    [(1,2), (3,8), (1,2)],                        # Row 10
    [(1,2), (2,6), (3,8), (2,6), (1,2)],          # Row 11
    [(1,2), (2,6), (3,8), (2,6), (1,2)],          # Row 12
    [(1,2), (2,6), (3,8), (2,6), (1,2)],          # Row 13
    [(1,2), (2,6), (3,8), (2,6), (1,2)],          # Row 14
    [(1,2), (3,8), (1,2)],                        # Row 15
    [(1,2), (3,8), (1,2)],                        # Row 16
    [(1,2), (2,4), (1,2)],                        # Row 17
    [(1,2), (2,4), (1,2)],                        # Row 18
    [(1,2), (2,4), (1,2)],                        # Row 19
    [(1,2), (2,4), (1,2)],                        # Row 20
    [(1,2), (2,4), (1,2)],                        # Row 21
    [(1,2), (2,4), (1,2)],                        # Row 22
    [(1,10), (2,4), (1,10)],                      # Row 23
    [(1,10), (2,4), (1,10)],                      # Row 24
]

# Column clues: list of columns; each column is list of (color, length)
COL_CLUES = [
    [(1,24)],                                     # Col 1
    [(1,24)],                                     # Col 2
    [(1,2), (2,4), (1,2)],                        # Col 3
    [(1,2), (2,4), (1,2)],                        # Col 4
    [(1,2), (2,4), (1,2)],                        # Col 5
    [(1,2), (2,4), (1,2)],                        # Col 6
    [(1,2), (2,4), (1,2)],                        # Col 7
    [(1,2), (2,4), (1,2)],                        # Col 8
    [(1,2), (3,8), (1,2)],                        # Col 9
    [(1,2), (3,8), (1,2)],                        # Col 10
    [(2,8), (3,8), (2,8)],                        # Col 11
    [(2,8), (3,8), (2,8)],                        # Col 12
    [(2,8), (3,8), (2,8)],                        # Col 13
    [(2,8), (3,8), (2,8)],                        # Col 14
    [(1,2), (3,8), (1,2)],                        # Col 15
    [(1,2), (3,8), (1,2)],                        # Col 16
    [(1,2), (2,4), (1,2)],                        # Col 17
    [(1,2), (2,4), (1,2)],                        # Col 18
    [(1,2), (2,4), (1,2)],                        # Col 19
    [(1,2), (2,4), (1,2)],                        # Col 20
    [(1,2), (2,4), (1,2)],                        # Col 21
    [(1,2), (2,4), (1,2)],                        # Col 22
    [(1,24)],                                     # Col 23
    [(1,24)],                                     # Col 24
]

# Exact diagonal patterns (cell-by-cell)
MAIN_DIAG = [1, 1, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 1, 1]
ANTI_DIAG = [1, 1, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 1, 1]

def verify_color_clue(line, clue):
    """
    Verify a colored line (list of ints in {0,1,2,3}) against a clue list of (color,length).
    Whites (0) are ignored; adjacencies of different colors are allowed; two runs of the same
    color are separated by at least one non-same-color cell by definition of runs.
    """
    groups = []
    cur_color = 0
    cur_len = 0
    for v in line:
        if v == 0:
            if cur_len > 0:
                groups.append((cur_color, cur_len))
                cur_color, cur_len = 0, 0
        else:
            if cur_len == 0:
                cur_color, cur_len = v, 1
            else:
                if v == cur_color:
                    cur_len += 1
                else:
                    groups.append((cur_color, cur_len))
                    cur_color, cur_len = v, 1
    if cur_len > 0:
        groups.append((cur_color, cur_len))
    return groups == clue

def verify_solution(solution_json: str) -> dict:
    # Parse
    try:
        sol = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    if "grid" not in sol:
        return {"valid": False, "message": "Missing required field: grid"}
    if "valid" not in sol:
        return {"valid": False, "message": "Missing required field: valid"}

    grid = sol["grid"]

    # Check shape and values
    if not isinstance(grid, list) or len(grid) != N:
        return {"valid": False, "message": f"Grid must be a {N}x{N} array"}
    for i, row in enumerate(grid):
        if not isinstance(row, list) or len(row) != N:
            return {"valid": False, "message": f"Row {i} must have exactly {N} elements"}
        for j, cell in enumerate(row):
            if cell not in [0,1,2,3]:
                return {"valid": False, "message": f"Cell [{i}][{j}] must be in {{0,1,2,3}}, got {cell}"}

    # Rows
    for i in range(N):
        if not verify_color_clue(grid[i], ROW_CLUES[i]):
            return {"valid": False, "message": f"Row {i+1} does not satisfy clue {ROW_CLUES[i]}"}

    # Columns
    for j in range(N):
        col = [grid[i][j] for i in range(N)]
        if not verify_color_clue(col, COL_CLUES[j]):
            return {"valid": False, "message": f"Column {j+1} does not satisfy clue {COL_CLUES[j]}"}

    # Diagonals (exact patterns)
    main = [grid[i][i] for i in range(N)]
    if main != MAIN_DIAG:
        return {"valid": False, "message": f"Main diagonal does not match required pattern {MAIN_DIAG}"}
    anti = [grid[i][N-1-i] for i in range(N)]
    if anti != ANTI_DIAG:
        return {"valid": False, "message": f"Anti-diagonal does not match required pattern {ANTI_DIAG}"}

    return {"valid": True, "message": "Valid colored nonogram solution"}

def find_solution():
    """
    Return a known valid solution (constructed to match all clues and diagonal constraints).
    """
    A = [1]*10 + [2]*4 + [1]*10
    B = [1,1] + [0]*8 + [2]*4 + [0]*8 + [1,1]
    C = [1,1] + [0]*6 + [3]*8 + [0]*6 + [1,1]
    D = [1,1] + [2]*6 + [3]*8 + [2]*6 + [1,1]
    grid = [
        A,  # Row 1
        A,  # Row 2
        B,  # Row 3
        B,  # Row 4
        B,  # Row 5
        B,  # Row 6
        B,  # Row 7
        B,  # Row 8
        C,  # Row 9
        C,  # Row 10
        D,  # Row 11
        D,  # Row 12
        D,  # Row 13
        D,  # Row 14
        C,  # Row 15
        C,  # Row 16
        B,  # Row 17
        B,  # Row 18
        B,  # Row 19
        B,  # Row 20
        B,  # Row 21
        B,  # Row 22
        A,  # Row 23
        A,  # Row 24
    ]
    return {"grid": grid, "valid": True, "palette": PALETTE}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--find":
            solution = find_solution()
            print(json.dumps(solution))
        else:
            with open(sys.argv[1], 'r') as f:
                solution_json = f.read()
            result = verify_solution(solution_json)
            print(json.dumps(result))
            sys.exit(0 if result["valid"] else 1)
    else:
        solution_json = sys.stdin.read()
        result = verify_solution(solution_json)
        print(json.dumps(result))
        sys.exit(0 if result["valid"] else 1)
