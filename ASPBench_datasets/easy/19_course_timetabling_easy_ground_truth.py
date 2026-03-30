#!/usr/bin/env python3
"""
Reference model for Course Timetabling problem
Used for solution verification only.
"""

import json
import sys

def verify_solution(solution_json: str) -> dict:
    """
    Verify if the given solution satisfies all problem constraints.

    Args:
        solution_json: JSON string containing the solution

    Returns:
        dict with keys:
        - valid: bool (True if solution is valid)
        - message: str (explanation)
    """

    # Parse solution
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    # Check required fields
    if "assignments" not in solution:
        return {"valid": False, "message": "Missing required field: assignments"}

    assignments = solution["assignments"]

    if not isinstance(assignments, list):
        return {"valid": False, "message": "assignments must be an array"}

    if len(assignments) != 5:
        return {"valid": False, "message": f"Must have exactly 5 assignments, got {len(assignments)}"}

    # Course data
    courses = [
        {"name": "Math", "teacher": 0, "students": 25},
        {"name": "Physics", "teacher": 1, "students": 20},
        {"name": "Chemistry", "teacher": 2, "students": 30},
        {"name": "Biology", "teacher": 1, "students": 15},
        {"name": "Computer Science", "teacher": 0, "students": 35}
    ]

    # Room capacities
    room_capacities = [40, 25, 20]

    # Teacher availability
    teacher_availability = {
        0: [0, 1, 2],  # Teacher 0 available in slots 0, 1, 2
        1: [1, 2, 3],  # Teacher 1 available in slots 1, 2, 3
        2: [0, 2, 3]   # Teacher 2 available in slots 0, 2, 3
    }

    # Check assignment structure
    seen_courses = set()
    room_time_pairs = set()
    teacher_time_pairs = set()

    for i, assignment in enumerate(assignments):
        if not isinstance(assignment, dict):
            return {"valid": False, "message": f"Assignment {i} must be an object"}

        # Check required fields
        for field in ["course", "room", "time_slot"]:
            if field not in assignment:
                return {"valid": False, "message": f"Assignment {i} missing field: {field}"}

        course = assignment["course"]
        room = assignment["room"]
        time_slot = assignment["time_slot"]

        # Validate ranges
        if course not in range(5):
            return {"valid": False, "message": f"Assignment {i}: Invalid course {course}, must be 0-4"}
        if room not in range(3):
            return {"valid": False, "message": f"Assignment {i}: Invalid room {room}, must be 0-2"}
        if time_slot not in range(4):
            return {"valid": False, "message": f"Assignment {i}: Invalid time_slot {time_slot}, must be 0-3"}

        # Check uniqueness of courses
        if course in seen_courses:
            return {"valid": False, "message": f"Course {course} appears multiple times"}
        seen_courses.add(course)

        # Check room-time conflicts
        room_time = (room, time_slot)
        if room_time in room_time_pairs:
            return {"valid": False, "message": f"Room {room} double-booked at time {time_slot}"}
        room_time_pairs.add(room_time)

        # Check capacity constraints
        course_students = courses[course]["students"]
        room_capacity = room_capacities[room]
        if course_students > room_capacity:
            return {"valid": False, "message": f"Course {course} has {course_students} students but room {room} capacity is {room_capacity}"}

        # Check teacher availability
        teacher = courses[course]["teacher"]
        if time_slot not in teacher_availability[teacher]:
            return {"valid": False, "message": f"Teacher {teacher} (course {course}) not available at time {time_slot}"}

        # Check teacher conflicts
        teacher_time = (teacher, time_slot)
        if teacher_time in teacher_time_pairs:
            return {"valid": False, "message": f"Teacher {teacher} double-booked at time {time_slot}"}
        teacher_time_pairs.add(teacher_time)

    # Verify all courses are assigned
    if seen_courses != {0, 1, 2, 3, 4}:
        missing = {0, 1, 2, 3, 4} - seen_courses
        return {"valid": False, "message": f"Missing course assignments: {missing}"}

    return {"valid": True, "message": "Valid course timetabling solution"}

def main():
    """Main entry point for verification."""
    content = sys.stdin.read()

    if not content.strip():
        print(json.dumps({"valid": False, "message": "No input provided"}))
        return

    result = verify_solution(content)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
