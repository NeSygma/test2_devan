#!/usr/bin/env python3
"""
Reference model for the Nurse Rostering Problem.
Validates a given roster against all hard constraints.
"""
import json
import sys

def validate_roster(data):
    """Checks if the given roster is valid."""
    # Constants
    NUM_NURSES = 5
    NUM_DAYS = 10

    # Check for roster key and that it's not null
    if "roster" not in data or data["roster"] is None:
        return {"valid": False, "message": "Input JSON must have a non-null 'roster' field."}

    roster = data["roster"]

    # --- Structural Checks ---
    if len(roster) != NUM_DAYS:
        return {"valid": False, "message": f"Roster must have {NUM_DAYS} days, but found {len(roster)}."}

    for d in range(NUM_DAYS):
        if len(roster[d]) != 3:
            return {"valid": False, "message": f"Roster for day {d+1} must have 3 shifts, but found {len(roster[d])}."}

    # --- Constraint 1: Coverage Requirements ---
    # Morning: 2 nurses, Evening: 1 nurse, Night: 1 nurse
    coverage_req = [2, 1, 1]
    for d in range(NUM_DAYS):
        for s in range(3):
            if len(roster[d][s]) != coverage_req[s]:
                return {"valid": False, "message": f"Coverage mismatch on Day {d+1}, Shift {s+1}. Required {coverage_req[s]}, found {len(roster[d][s])}."}

    # --- Constraint 2: Single Assignment per Day ---
    for d in range(NUM_DAYS):
        nurses_on_day = []
        for s in range(3):
            nurses_on_day.extend(roster[d][s])
        if len(nurses_on_day) != len(set(nurses_on_day)):
            return {"valid": False, "message": f"Nurse assigned to multiple shifts on Day {d+1}."}

    # --- Constraint 3: Rest Period ---
    # No night shift (shift 3) followed by a morning shift (shift 1) the next day.
    for d in range(NUM_DAYS - 1):
        night_nurses = roster[d][2] # 0-indexed shift 2 is night
        next_morning_nurses = roster[d+1][0] # 0-indexed shift 0 is morning
        for nurse in night_nurses:
            if nurse in next_morning_nurses:
                return {"valid": False, "message": f"Nurse {nurse} has a rest period violation between Day {d+1} and Day {d+2}."}

    return {"valid": True, "message": "Valid roster satisfying all constraints"}

if __name__ == "__main__":
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            result = {"valid": False, "message": "No input provided"}
        else:
            data = json.loads(input_data)
            result = validate_roster(data)
    except json.JSONDecodeError:
        result = {"valid": False, "message": "Invalid JSON input"}
    except Exception as e:
        result = {"valid": False, "message": str(e)}

    print(json.dumps(result))
