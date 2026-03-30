#!/usr/bin/env python3
"""
Reference model for Problem 048: Crossword Generation

Validates crossword puzzle solutions from stdin.
"""

import json
import sys
from typing import Dict, List


def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def validate_solution(solution):
    """
    Validate crossword puzzle solution.

    Args:
        solution: Dictionary with grid, words, theme, intersections

    Returns:
        Dictionary with valid boolean and message string
    """
    if not solution:
        return {"valid": False, "message": "No solution provided"}

    # Check required fields
    required_fields = ["grid", "words", "theme", "intersections"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    grid = solution["grid"]
    words = solution["words"]
    theme = solution["theme"]
    intersections = solution["intersections"]

    # Validate grid format (5x5)
    if not isinstance(grid, list) or len(grid) != 5:
        return {"valid": False, "message": "Grid must be 5x5"}

    for i, row in enumerate(grid):
        if not isinstance(row, list) or len(row) != 5:
            return {"valid": False, "message": f"Grid row {i} must have 5 cells"}
        for j, cell in enumerate(row):
            if not isinstance(cell, str) or len(cell) != 1:
                return {"valid": False, "message": f"Grid cell ({i},{j}) must be single character"}

    # Validate words
    if not isinstance(words, list) or len(words) < 6:
        return {"valid": False, "message": "Must place at least 6 words"}

    expected_words = {"CODE", "DATA", "TECH", "CHIP", "BYTE", "NET"}
    placed_words = set()

    for i, word_info in enumerate(words):
        if not isinstance(word_info, dict):
            return {"valid": False, "message": f"Word {i} must be dictionary"}

        required_word_fields = ["word", "position", "direction", "clue"]
        for field in required_word_fields:
            if field not in word_info:
                return {"valid": False, "message": f"Word {i} missing field: {field}"}

        word = word_info["word"]
        position = word_info["position"]
        direction = word_info["direction"]

        if not isinstance(word, str) or len(word) < 3:
            return {"valid": False, "message": f"Word {i} must be string with at least 3 letters"}

        if not isinstance(position, list) or len(position) != 2:
            return {"valid": False, "message": f"Word {i} position must be [row, col]"}

        row, col = position
        if not (0 <= row < 5 and 0 <= col < 5):
            return {"valid": False, "message": f"Word {i} position out of bounds"}

        if direction not in ["horizontal", "vertical"]:
            return {"valid": False, "message": f"Word {i} direction must be horizontal or vertical"}

        # Check word fits in grid
        if direction == "horizontal":
            if col + len(word) > 5:
                return {"valid": False, "message": f"Word {i} ({word}) extends beyond grid"}
        else:  # vertical
            if row + len(word) > 5:
                return {"valid": False, "message": f"Word {i} ({word}) extends beyond grid"}

        # Verify word is placed correctly in grid
        for k, letter in enumerate(word):
            if direction == "horizontal":
                grid_letter = grid[row][col + k]
            else:
                grid_letter = grid[row + k][col]

            if grid_letter != letter:
                return {"valid": False, "message": f"Word {i} ({word}) mismatch at position {k}: expected {letter}, got {grid_letter}"}

        placed_words.add(word)

    # Check all expected words are placed
    missing = expected_words - placed_words
    if missing:
        return {"valid": False, "message": f"Missing words: {missing}"}

    # Validate theme
    if not isinstance(theme, str):
        return {"valid": False, "message": "Theme must be string"}

    # Validate intersections format
    if not isinstance(intersections, list):
        return {"valid": False, "message": "Intersections must be list"}

    for i, intersection in enumerate(intersections):
        if not isinstance(intersection, dict):
            return {"valid": False, "message": f"Intersection {i} must be dictionary"}

        required_int_fields = ["word1", "word2", "position1", "position2", "letter"]
        for field in required_int_fields:
            if field not in intersection:
                return {"valid": False, "message": f"Intersection {i} missing field: {field}"}

        word1_idx = intersection["word1"]
        word2_idx = intersection["word2"]
        pos1 = intersection["position1"]
        pos2 = intersection["position2"]
        letter = intersection["letter"]

        if not isinstance(word1_idx, int) or not (0 <= word1_idx < len(words)):
            return {"valid": False, "message": f"Intersection {i} word1 index out of range"}

        if not isinstance(word2_idx, int) or not (0 <= word2_idx < len(words)):
            return {"valid": False, "message": f"Intersection {i} word2 index out of range"}

        if not isinstance(pos1, int) or not isinstance(pos2, int):
            return {"valid": False, "message": f"Intersection {i} positions must be integers"}

        if not isinstance(letter, str) or len(letter) != 1:
            return {"valid": False, "message": f"Intersection {i} letter must be single character"}

        # Verify intersection is valid
        word1 = words[word1_idx]["word"]
        word2 = words[word2_idx]["word"]

        if pos1 >= len(word1):
            return {"valid": False, "message": f"Intersection {i} position1 out of range for word {word1}"}

        if pos2 >= len(word2):
            return {"valid": False, "message": f"Intersection {i} position2 out of range for word {word2}"}

        if word1[pos1] != letter or word2[pos2] != letter:
            return {"valid": False, "message": f"Intersection {i} letter mismatch"}

    return {"valid": True, "message": "Solution satisfies all constraints"}


if __name__ == "__main__":
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))
