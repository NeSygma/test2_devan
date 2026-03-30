#!/usr/bin/env python3
"""
Reference model validator for Nurse Rostering Problem
Validates solution from stdin and checks optimality.
"""

import json
import sys
from typing import Dict, List, Set

# Expected optimal value (16 is minimum: 4 nurses must work all 7 days to meet coverage)
EXPECTED_OPTIMAL_VIOLATIONS = 16

def validate_solution(solution: Dict) -> Dict:
    """Validate nurse rostering solution"""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    # Check required fields
    if "roster" not in solution or "violations" not in solution or "coverage_met" not in solution:
        return {"valid": False, "message": "Missing required fields: roster, violations, coverage_met"}

    roster = solution["roster"]
    violations_reported = solution["violations"]
    coverage_met = solution["coverage_met"]

    # Validate roster structure
    if len(roster) != 7:
        return {"valid": False, "message": f"Roster must have 7 days, got {len(roster)}"}

    for day_idx, day_roster in enumerate(roster):
        if len(day_roster) != 3:
            return {"valid": False, "message": f"Day {day_idx+1} must have 3 shifts, got {len(day_roster)}"}

    # Constants
    nurses = {1, 2, 3, 4}
    coverage_req = [2, 1, 1]  # morning, evening, night

    # Validate coverage requirements (hard constraint 1)
    actual_coverage_met = True
    for day in range(7):
        for shift in range(3):
            if len(roster[day][shift]) != coverage_req[shift]:
                actual_coverage_met = False
                return {"valid": False, "message": f"Day {day+1} shift {shift+1} requires {coverage_req[shift]} nurses, got {len(roster[day][shift])}"}

    # Validate single assignment per day (hard constraint 2)
    for day in range(7):
        nurses_today = set()
        for shift in range(3):
            for nurse in roster[day][shift]:
                if nurse in nurses_today:
                    return {"valid": False, "message": f"Nurse {nurse} assigned to multiple shifts on day {day+1}"}
                nurses_today.add(nurse)

    # Validate rest period (hard constraint 3)
    for day in range(6):  # Check days 1-6 (0-5 in 0-indexed)
        night_nurses = set(roster[day][2])  # Night shift
        morning_next = set(roster[day+1][0])  # Morning shift next day
        overlap = night_nurses & morning_next
        if overlap:
            return {"valid": False, "message": f"Nurse(s) {overlap} work night shift day {day+1} then morning shift day {day+2} (rest period violation)"}

    # Calculate actual violations (soft constraints)
    actual_violations = 0

    # Count consecutive days violations (constraint 4)
    for nurse in nurses:
        consecutive = 0
        for day in range(7):
            worked = any(nurse in roster[day][shift] for shift in range(3))
            if worked:
                consecutive += 1
            else:
                if consecutive > 3:
                    actual_violations += consecutive - 3
                consecutive = 0
        # Check final consecutive period
        if consecutive > 3:
            actual_violations += consecutive - 3

    # Count fair distribution violations (constraint 5)
    for nurse in nurses:
        total_shifts = sum(1 for day in range(7) for shift in range(3) if nurse in roster[day][shift])
        if total_shifts < 6:
            actual_violations += 6 - total_shifts
        elif total_shifts > 8:
            actual_violations += total_shifts - 8

    # Count weekend coverage violations (constraint 6)
    weekend_nurses = set()
    for day in [5, 6]:  # Weekend days (6,7 in 1-indexed, 5,6 in 0-indexed)
        for shift in range(3):
            weekend_nurses.update(roster[day][shift])
    if len(weekend_nurses) < 2:
        actual_violations += 1

    # Validate coverage_met field
    if coverage_met != actual_coverage_met:
        return {"valid": False, "message": f"coverage_met should be {actual_coverage_met}, got {coverage_met}"}

    # Validate violations count
    if violations_reported != actual_violations:
        return {"valid": False, "message": f"Violation count should be {actual_violations}, got {violations_reported}"}

    # Check optimality
    if actual_violations != EXPECTED_OPTIMAL_VIOLATIONS:
        return {"valid": False, "message": f"Not optimal: violations={actual_violations}, expected {EXPECTED_OPTIMAL_VIOLATIONS}"}

    # All checks passed - solution is valid and optimal
    return {
        "valid": True,
        "message": f"Solution is valid and optimal (violations={EXPECTED_OPTIMAL_VIOLATIONS})"
    }

def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError as e:
        return None

if __name__ == "__main__":
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))
