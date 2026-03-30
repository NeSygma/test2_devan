#!/usr/bin/env python3
"""
Reference Model Validator for Meeting Scheduling Problem

Validates solution from stdin and outputs {"valid": true/false, "message": "..."}.
"""

import json
import sys
from typing import Dict, List, Tuple

def load_solution():
    """Load solution from stdin."""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def validate_solution(solution):
    """Validate the meeting scheduling solution."""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    # Check required fields
    required_fields = ["schedule", "conflicts", "preference_violations", "feasible"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    if not solution["feasible"]:
        return {"valid": False, "message": "Solution is marked as infeasible"}

    schedule = solution["schedule"]

    # Problem data
    meetings = {'m1', 'm2', 'm3', 'm4', 'm5'}
    people = {'p1', 'p2', 'p3', 'p4', 'p5'}
    days = {1, 2, 3}
    slots = {1, 2, 3}
    rooms = {'r1', 'r2'}

    # Meeting attendees
    attendees = {
        'm1': {'p1', 'p2', 'p3'},
        'm2': {'p1', 'p5'},
        'm3': {'p2', 'p3'},
        'm4': {'p1', 'p4'},
        'm5': {'p1', 'p2', 'p3'}
    }

    # Time preferences
    preferences = {
        'm1': (1, 1),
        'm2': (1, 2),
        'm4': (3, 3)
    }

    # Check all meetings are scheduled
    scheduled_meetings = {entry["meeting"] for entry in schedule}
    if scheduled_meetings != meetings:
        return {"valid": False, "message": f"Not all meetings scheduled. Expected {meetings}, got {scheduled_meetings}"}

    # Check each meeting entry
    for entry in schedule:
        if "meeting" not in entry or "day" not in entry or "slot" not in entry or "room" not in entry:
            return {"valid": False, "message": f"Invalid schedule entry: {entry}"}

        meeting = entry["meeting"]
        day = entry["day"]
        slot = entry["slot"]
        room = entry["room"]

        if meeting not in meetings:
            return {"valid": False, "message": f"Unknown meeting: {meeting}"}
        if day not in days:
            return {"valid": False, "message": f"Invalid day {day} for meeting {meeting}"}
        if slot not in slots:
            return {"valid": False, "message": f"Invalid slot {slot} for meeting {meeting}"}
        if room not in rooms:
            return {"valid": False, "message": f"Invalid room {room} for meeting {meeting}"}

    # Check constraint 1: Each meeting assigned exactly once (already verified above)

    # Check constraint 2: No person attends two meetings at same time
    time_person_map = {}
    for entry in schedule:
        meeting = entry["meeting"]
        day = entry["day"]
        slot = entry["slot"]
        time_key = (day, slot)

        if time_key not in time_person_map:
            time_person_map[time_key] = set()

        for person in attendees[meeting]:
            if person in time_person_map[time_key]:
                return {"valid": False, "message": f"Person {person} has conflicting meetings at day {day}, slot {slot}"}
            time_person_map[time_key].add(person)

    # Check constraint 3: Only one meeting per room per time slot
    time_room_map = {}
    for entry in schedule:
        meeting = entry["meeting"]
        day = entry["day"]
        slot = entry["slot"]
        room = entry["room"]
        time_room_key = (day, slot, room)

        if time_room_key in time_room_map:
            return {"valid": False, "message": f"Room {room} double-booked at day {day}, slot {slot}"}
        time_room_map[time_room_key] = meeting

    # Count actual preference violations
    actual_violations = 0
    for entry in schedule:
        meeting = entry["meeting"]
        if meeting in preferences:
            preferred_day, preferred_slot = preferences[meeting]
            if entry["day"] != preferred_day or entry["slot"] != preferred_slot:
                actual_violations += 1

    # Check reported violations match actual
    reported_violations = solution["preference_violations"]
    if reported_violations != actual_violations:
        return {"valid": False, "message": f"Incorrect preference violations count. Expected {actual_violations}, got {reported_violations}"}

    # Check for optimality (minimum violations is 0)
    if actual_violations != 0:
        return {"valid": False, "message": f"Solution not optimal. Expected 0 violations, got {actual_violations}"}

    return {"valid": True, "message": f"Solution correct with {actual_violations} preference violations (optimal)"}

def main():
    """Main validation function."""
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
