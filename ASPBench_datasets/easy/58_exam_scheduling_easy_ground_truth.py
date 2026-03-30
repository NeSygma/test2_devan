#!/usr/bin/env python3
"""
Reference model for Exam Scheduling problem.
Validates exam schedule and conflict resolution.
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


def get_student_enrollments():
    """Get student exam enrollments"""
    return {
        "S1": ["E1", "E3", "E5"],
        "S2": ["E1", "E4", "E6"],
        "S3": ["E2", "E3", "E6"],
        "S4": ["E2", "E4", "E5"]
    }


def validate_solution(solution):
    """Validate the exam scheduling solution"""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    required_fields = ["schedule", "conflicts_resolved", "room_utilization"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing field: {field}"}

    schedule = solution["schedule"]
    enrollments = get_student_enrollments()

    # Check all exams scheduled
    scheduled_exams = {entry["exam"] for entry in schedule}
    expected_exams = {"E1", "E2", "E3", "E4", "E5", "E6"}
    if scheduled_exams != expected_exams:
        missing = expected_exams - scheduled_exams
        extra = scheduled_exams - expected_exams
        msg = "Schedule incomplete"
        if missing:
            msg += f" (missing: {missing})"
        if extra:
            msg += f" (extra: {extra})"
        return {"valid": False, "message": msg}

    # Build time slot mapping
    exam_times = {}
    for entry in schedule:
        exam = entry["exam"]
        time_slot = entry.get("time_slot", 1)
        day = entry.get("day", 1)
        time_key = (day, time_slot)
        exam_times[exam] = time_key

    # Check student conflicts
    for student, exams in enrollments.items():
        student_times = set()
        for exam in exams:
            if exam in exam_times:
                time_key = exam_times[exam]
                if time_key in student_times:
                    return {"valid": False, "message": f"Student {student} has time conflict at {time_key}"}
                student_times.add(time_key)

    # Check room capacities (count students per exam, verify <= room capacity)
    room_capacities = {"R1": 3, "R2": 3}
    for entry in schedule:
        exam = entry["exam"]
        room = entry["room"]
        # Count students enrolled in this exam
        students_in_exam = sum(1 for student, exams in enrollments.items() if exam in exams)
        capacity = room_capacities.get(room, 0)
        if students_in_exam > capacity:
            return {"valid": False, "message": f"Exam {exam} has {students_in_exam} students but room {room} capacity is {capacity}"}

    return {"valid": True, "message": "Valid exam schedule with no conflicts"}


def main():
    """Main validation function"""
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
