#!/usr/bin/env python3
"""
Reference model for Problem 048: Crossword Generation (Hard)
Validates crossword puzzle solutions with strict constraints.
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
    """
    Validate crossword solution with constraints:
    - 6x6 grid with 4 corner black squares
    - 8 specific words: CAT, ACE, TEA, EAR, ATE, RAT, CAR, TAR
    - Each word placed exactly once (horizontal or vertical)
    - No overlaps except at intersections (matching letters)
    - At least 3 intersections
    - Words don't cross black squares
    - All non-black cells form connected component
    """

    if not solution or 'placements' not in solution:
        return {"valid": False, "message": "No placements found"}

    placements = solution['placements']

    # Check required words
    required_words = {'CAT', 'ACE', 'TEA', 'EAR', 'ATE', 'RAT', 'CAR', 'TAR'}
    placed_words = set(p['word'].upper() for p in placements)

    if placed_words != required_words:
        missing = required_words - placed_words
        extra = placed_words - required_words
        msg = []
        if missing:
            msg.append(f"Missing words: {missing}")
        if extra:
            msg.append(f"Extra words: {extra}")
        return {"valid": False, "message": "; ".join(msg)}

    # Check each word placed exactly once
    word_counts = {}
    for p in placements:
        word = p['word'].upper()
        word_counts[word] = word_counts.get(word, 0) + 1

    for word, count in word_counts.items():
        if count != 1:
            return {"valid": False, "message": f"Word {word} placed {count} times (must be 1)"}

    # Build grid and check constraints
    grid = {}
    black_squares = {(0,0), (0,5), (5,0), (5,5)}

    for p in placements:
        word = p['word'].upper()
        row, col = p['row'], p['col']
        direction = p['direction']

        # Check bounds (6x6 grid)
        if direction == 'horizontal':
            if col + len(word) > 6:
                return {"valid": False, "message": f"{word} at ({row},{col}) goes out of bounds"}
        else:
            if row + len(word) > 6:
                return {"valid": False, "message": f"{word} at ({row},{col}) goes out of bounds"}

        # Check doesn't start on black square
        if (row, col) in black_squares:
            return {"valid": False, "message": f"{word} starts on black square ({row},{col})"}

        # Place letters and check conflicts
        for i, letter in enumerate(word):
            if direction == 'horizontal':
                r, c = row, col + i
            else:
                r, c = row + i, col

            # Check black square
            if (r, c) in black_squares:
                return {"valid": False, "message": f"{word} crosses black square at ({r},{c})"}

            # Check conflicts
            if (r, c) in grid:
                if grid[(r, c)] != letter:
                    return {"valid": False,
                           "message": f"Letter conflict at ({r},{c}): {grid[(r,c)]} vs {letter}"}
            else:
                grid[(r, c)] = letter

    # Count intersections (cells occupied by 2+ words)
    cell_words = {}
    for p in placements:
        word = p['word'].upper()
        row, col = p['row'], p['col']
        direction = p['direction']

        for i, letter in enumerate(word):
            if direction == 'horizontal':
                r, c = row, col + i
            else:
                r, c = row + i, col

            if (r, c) not in cell_words:
                cell_words[(r, c)] = []
            cell_words[(r, c)].append(word)

    intersections = [(r, c) for (r, c), words in cell_words.items() if len(words) >= 2]

    if len(intersections) < 3:
        return {"valid": False,
               "message": f"Only {len(intersections)} intersections (need at least 3)"}

    # Check connectivity (BFS from first non-black cell)
    if not grid:
        return {"valid": False, "message": "No letters placed"}

    start = None
    for r in range(6):
        for c in range(6):
            if (r, c) in grid:
                start = (r, c)
                break
        if start:
            break

    visited = set()
    queue = [start]
    visited.add(start)

    while queue:
        r, c = queue.pop(0)
        for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 6 and 0 <= nc < 6:
                if (nr, nc) in grid and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))

    if len(visited) != len(grid):
        return {"valid": False,
               "message": f"Grid not connected: {len(visited)} reachable of {len(grid)} cells"}

    return {
        "valid": True,
        "message": f"Valid crossword with {len(intersections)} intersections",
        "intersections": len(intersections)
    }

if __name__ == "__main__":
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))
