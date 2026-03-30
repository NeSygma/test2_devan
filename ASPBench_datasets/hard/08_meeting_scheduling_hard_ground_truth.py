#!/usr/bin/env python3
"""
Reference Model — Meeting Scheduling Problem (Hard)

Reads a solution from stdin and validates feasibility only.
- Hard constraints: assignment, attendee conflicts, room occupancy, equipment

Outputs JSON: {"valid": true/false, "message": "..."}
"""

import json
import sys
from typing import Dict, Any, Set

def get_problem_data():
    """Returns the problem data structure."""
    rooms = ["r1", "r2", "r3", "r4"]
    meetings = [f"m{i}" for i in range(1, 21)]  # m1..m20
    people = [f"p{i}" for i in range(1, 21)]  # p1..p20

    # Room equipment capabilities
    room_has = {
        "r1": {"projector", "whiteboard", "video", "confcall"},
        "r2": {"projector", "whiteboard", "confcall"},
        "r3": {"whiteboard", "confcall"},
        "r4": {"projector", "video"},
    }

    # Meeting equipment requirements (based on meeting number mod 10)
    def reqs_for(i: int) -> Set[str]:
        k = i % 10
        if k == 0: return {"projector", "whiteboard"}
        if k == 1: return {"projector"}
        if k == 2: return {"whiteboard"}
        if k == 3: return {"confcall"}
        if k == 4: return {"video", "projector"}
        if k == 5: return {"projector", "confcall"}
        if k == 6: return {"whiteboard", "confcall"}
        if k == 7: return {"projector", "whiteboard", "confcall"}
        if k == 8: return {"video", "confcall"}
        return {"projector", "video"}

    meeting_requires = {f"m{i}": reqs_for(i) for i in range(1, 21)}

    # Meeting attendees (4 per meeting)
    meeting_attendees = {}
    for i in range(1, 21):
        a = ((i - 1) % 10) + 1
        b = ((i + 2 - 1) % 10) + 1 + 10
        c = ((i + 5 - 1) % 10) + 1 + 20 if ((i + 5 - 1) % 10) + 1 + 20 <= 20 else ((i + 5 - 1) % 10) + 1
        d = ((i + 7 - 1) % 10) + 1 + 10 if ((i + 7 - 1) % 10) + 1 + 10 <= 20 else ((i + 7 - 1) % 10) + 11

        # Ensure we stay within p1..p20
        attendees = set()
        for p_num in [a, b, c, d]:
            if p_num <= 20:
                attendees.add(f"p{p_num}")

        # If we have fewer than 4, wrap around
        while len(attendees) < 4:
            p_num = ((len(attendees) + i) % 20) + 1
            attendees.add(f"p{p_num}")

        meeting_attendees[f"m{i}"] = attendees

    return {
        "rooms": rooms,
        "meetings": meetings,
        "people": people,
        "room_has": room_has,
        "meeting_requires": meeting_requires,
        "meeting_attendees": meeting_attendees,
        "days": list(range(1, 6)),  # 1..5
        "slots": list(range(1, 5)),  # 1..4
    }

def validate_solution(solution):
    """Validate a meeting scheduling solution from stdin."""
    data = get_problem_data()

    # Check solution structure
    if not isinstance(solution, dict):
        return {"valid": False, "message": "Solution must be a JSON object"}

    if not solution.get("feasible", False):
        return {"valid": False, "message": "Solution marked as infeasible"}

    if "schedule" not in solution:
        return {"valid": False, "message": "Missing 'schedule' field"}

    schedule = solution["schedule"]
    if not isinstance(schedule, list):
        return {"valid": False, "message": "'schedule' must be a list"}

    # Handle empty schedule (valid if marked feasible)
    if len(schedule) == 0:
        return {"valid": True, "message": "Empty schedule accepted (marked as feasible)"}

    # Parse schedule into assignment map
    assignments = {}  # meeting -> (day, slot, room)
    for entry in schedule:
        if not isinstance(entry, dict):
            return {"valid": False, "message": "Schedule entry must be a dict"}

        if "meeting" not in entry or "day" not in entry or "slot" not in entry or "room" not in entry:
            return {"valid": False, "message": "Schedule entry missing required fields"}

        m = entry["meeting"]
        d = entry["day"]
        s = entry["slot"]
        r = entry["room"]

        if m in assignments:
            return {"valid": False, "message": f"Meeting {m} assigned multiple times"}

        if m not in data["meetings"]:
            return {"valid": False, "message": f"Unknown meeting {m}"}

        if d not in data["days"]:
            return {"valid": False, "message": f"Invalid day {d} for meeting {m}"}

        if s not in data["slots"]:
            return {"valid": False, "message": f"Invalid slot {s} for meeting {m}"}

        if r not in data["rooms"]:
            return {"valid": False, "message": f"Invalid room {r} for meeting {m}"}

        assignments[m] = (d, s, r)

    # Check all meetings assigned
    if len(assignments) != len(data["meetings"]):
        return {"valid": False, "message": f"Not all meetings assigned: {len(assignments)} of {len(data['meetings'])}"}

    # Validate hard constraints
    # 1. No person attends two meetings at the same (day, slot)
    timeslots = {}  # (day, slot) -> set of people
    for m, (d, s, r) in assignments.items():
        key = (d, s)
        if key not in timeslots:
            timeslots[key] = set()

        attendees = data["meeting_attendees"][m]
        overlap = timeslots[key] & attendees
        if overlap:
            return {"valid": False, "message": f"Person conflict at day {d}, slot {s}: {overlap}"}

        timeslots[key].update(attendees)

    # 2. Only one meeting per room per time slot
    room_slots = {}  # (day, slot, room) -> meeting
    for m, (d, s, r) in assignments.items():
        key = (d, s, r)
        if key in room_slots:
            return {"valid": False, "message": f"Room conflict: {m} and {room_slots[key]} both at day {d}, slot {s}, room {r}"}
        room_slots[key] = m

    # 3. Room must have all required equipment
    for m, (d, s, r) in assignments.items():
        required = data["meeting_requires"][m]
        available = data["room_has"][r]
        missing = required - available
        if missing:
            return {"valid": False, "message": f"Meeting {m} requires {missing} but room {r} doesn't have it"}

    return {"valid": True, "message": "Valid meeting scheduling solution"}

def main():
    try:
        solution_json = sys.stdin.read().strip()
        if not solution_json:
            print(json.dumps({"valid": False, "message": "No solution provided"}))
            sys.exit(1)

        solution = json.loads(solution_json)
        result = validate_solution(solution)
        print(json.dumps(result))
        sys.exit(0 if result["valid"] else 1)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Validation error: {e}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
