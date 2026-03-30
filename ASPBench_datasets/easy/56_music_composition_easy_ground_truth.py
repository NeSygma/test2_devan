#!/usr/bin/env python3
"""
Reference model for Music Composition problem.
Validates melody and musical constraints.
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
    except json.JSONDecodeError:
        return None


def validate_solution(solution):
    """Validate the music composition solution"""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    required_fields = ["melody", "intervals", "analysis"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing field: {field}"}

    melody = solution["melody"]
    intervals = solution["intervals"]
    analysis = solution.get("analysis", {})

    # Check melody length
    if len(melody) != 8:
        return {"valid": False, "message": f"Melody should have 8 notes, got {len(melody)}"}

    # Check valid notes in C major
    c_major = ["C", "D", "E", "F", "G", "A", "B"]
    for note in melody:
        if note not in c_major:
            return {"valid": False, "message": f"Note {note} not in C major scale"}

    # Check intervals array length
    if len(intervals) != len(melody) - 1:
        return {"valid": False, "message": f"Intervals array should have {len(melody)-1} elements, got {len(intervals)}"}

    # Check start and end on C
    if melody[0] != "C":
        return {"valid": False, "message": "Melody should start on C"}
    if melody[-1] != "C":
        return {"valid": False, "message": "Melody should end on C"}

    # Verify intervals are correct
    note_to_semitone = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    for i in range(len(melody) - 1):
        expected_interval = note_to_semitone[melody[i+1]] - note_to_semitone[melody[i]]
        if intervals[i] != expected_interval:
            return {"valid": False, "message": f"Interval {i} should be {expected_interval}, got {intervals[i]}"}

    # Check no large leaps (>4 semitones)
    for i, interval in enumerate(intervals):
        if abs(interval) > 4:
            return {"valid": False, "message": f"Leap at position {i} exceeds 4 semitones: {interval}"}

    return {"valid": True, "message": "Valid melody composition"}


def main():
    """Main validation function"""
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
