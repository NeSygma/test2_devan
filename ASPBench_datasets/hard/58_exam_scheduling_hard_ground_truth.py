#!/usr/bin/env python3
"""
Reference model for the Exam Scheduling problem.

This script validates a given schedule against a fixed set of constraints:
- Student conflicts (no two exams at the same time for one student).
- Room conflicts (no two exams in the same room at the same time).
- Room type requirements (e.g., lab exams must be in labs).
- Room capacity.
- Completeness (all exams must be scheduled).
"""

import json
import sys
from collections import defaultdict

# --- Problem Instance Definition ---

def get_problem_definition():
    """Returns the fixed parameters for this problem instance."""
    return {
        "exams": {f"E{i}" for i in range(1, 9)},
        "students": {
            "S1": ["E1", "E3", "E7"],
            "S2": ["E2", "E4", "E8"],
            "S3": ["E1", "E5"],
            "S4": ["E2", "E6"],
            "S5": ["E3", "E5", "E8"],
            "S6": ["E4", "E6", "E7"],
        },
        "rooms": {
            "R1": {"type": "classroom", "capacity": 2},
            "R2": {"type": "classroom", "capacity": 2},
            "R3": {"type": "lab", "capacity": 2},
        },
        "exam_requirements": {
            "E1": "classroom", "E2": "classroom", "E3": "classroom",
            "E4": "classroom", "E5": "classroom", "E6": "classroom",
            "E7": "lab", "E8": "lab",
        }
    }

def load_solution():
    """Loads a JSON solution from stdin."""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None, "Empty input."
        return json.loads(data), None
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {e}"

def validate_solution(solution):
    """Validates the entire schedule."""
    if not isinstance(solution, dict) or "schedule" not in solution:
        return False, "Missing 'schedule' key in JSON object."

    schedule = solution["schedule"]
    if not isinstance(schedule, list):
        return False, "'schedule' must be a list."

    p = get_problem_definition()
    student_enrollments = p["students"]

    # 1. Check for completeness: all exams are scheduled exactly once.
    scheduled_exams = {item.get("exam") for item in schedule}
    if scheduled_exams != p["exams"]:
        missing = p["exams"] - scheduled_exams
        extra = scheduled_exams - p["exams"]
        msg = []
        if missing: msg.append(f"Missing exams: {sorted(list(missing))}")
        if extra: msg.append(f"Unknown exams: {sorted(list(extra))}")
        return False, ". ".join(msg)

    if len(schedule) != len(p["exams"]):
        return False, "Each exam must be scheduled exactly once."

    # Build data structures for efficient checking
    room_time_map = defaultdict(list)
    student_time_map = defaultdict(list)
    exam_map = {}

    for entry in schedule:
        exam = entry.get("exam")
        time = entry.get("time_slot")
        room = entry.get("room")

        if not all([exam, time, room]):
            return False, f"Schedule entry missing fields: {entry}"

        exam_map[exam] = (time, room)
        room_time_map[(room, time)].append(exam)

    # 2. Check room conflicts (type, capacity, multiple exams)
    for (room, time), exams_in_room in room_time_map.items():
        if len(exams_in_room) > 1:
            return False, f"Room conflict: Room {room} has multiple exams at time {time}."

        exam = exams_in_room[0]

        # Check room type
        required_type = p["exam_requirements"].get(exam)
        room_type = p["rooms"].get(room, {}).get("type")
        if required_type != room_type:
            return False, f"Room type conflict: {exam} needs '{required_type}' but is in {room} ('{room_type}')."

        # Check room capacity
        room_capacity = p["rooms"].get(room, {}).get("capacity")
        students_in_exam = [s for s, exams in student_enrollments.items() if exam in exams]
        if len(students_in_exam) > room_capacity:
            return False, f"Capacity conflict: Exam {exam} ({len(students_in_exam)} students) exceeds capacity of {room} ({room_capacity})."

    # 3. Check student conflicts
    for student, exams in student_enrollments.items():
        student_schedule = defaultdict(list)
        for exam in exams:
            if exam in exam_map:
                time, _ = exam_map[exam]
                student_schedule[time].append(exam)

        for time, scheduled_exams in student_schedule.items():
            if len(scheduled_exams) > 1:
                return False, f"Student conflict: {student} has multiple exams at time {time}: {scheduled_exams}."

    return True, "All constraints satisfied."

def main():
    """Main validation function."""
    solution, error_msg = load_solution()

    if error_msg:
        result = {"valid": False, "message": error_msg}
    else:
        is_valid, message = validate_solution(solution)
        result = {"valid": is_valid, "message": message}

    print(json.dumps(result))

if __name__ == "__main__":
    main()
