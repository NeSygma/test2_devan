#!/usr/bin/env python3
"""
Reference model for Course Timetabling problem
Validates solutions and checks optimality.
"""

import json
import sys

# Expected optimal value
EXPECTED_OPTIMAL_COST = 0

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

    if "cost" not in solution:
        return {"valid": False, "message": "Missing required field: cost"}

    assignments = solution["assignments"]

    if not isinstance(assignments, list):
        return {"valid": False, "message": "assignments must be an array"}

    if len(assignments) != 8:
        return {"valid": False, "message": f"Must have exactly 8 assignments, got {len(assignments)}"}

    # Course data: (name, teacher, students, department)
    courses = [
        ("Physics I", 0, 30, "sci"),
        ("Physics II", 0, 25, "sci"),
        ("Chemistry", 1, 40, "sci"),
        ("History", 2, 50, "hum"),
        ("Literature", 3, 45, "hum"),
        ("Intro Programming", 4, 60, "eng"),
        ("Data Structures", 4, 55, "eng"),
        ("Algorithms", 4, 50, "eng")
    ]

    # Room data: (capacity, features)
    rooms = [
        (60, ['projector']),
        (50, ['projector']),
        (40, ['lab', 'projector']),
        (30, [])
    ]

    # Teacher availability
    teacher_availability = {
        0: [0, 1, 2],
        1: [2, 3, 4],
        2: [0, 1, 4, 5],
        3: [0, 2, 3, 5],
        4: [1, 2, 3, 4, 5]
    }

    # Room feature requirements
    room_requirements = {
        2: ['lab'],  # Chemistry needs lab
        5: ['projector'],  # Intro Programming needs projector
        6: ['projector'],  # Data Structures needs projector
        7: ['projector']   # Algorithms needs projector
    }

    # Prerequisites: (prereq_course, dependent_course)
    prerequisites = [
        (0, 1),  # Physics I before Physics II
        (5, 6),  # Intro Programming before Data Structures
        (6, 7)   # Data Structures before Algorithms
    ]

    # Student conflicts: pairs that can't be at same time
    student_conflicts = [
        (1, 4),  # Physics II and Literature
        (2, 5)   # Chemistry and Intro Programming
    ]

    # Check assignment structure and build schedule
    seen_courses = set()
    room_time_pairs = set()
    teacher_time_pairs = set()
    course_times = {}  # course_id -> time_slot
    slot_5_count = 0

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
        if course not in range(8):
            return {"valid": False, "message": f"Assignment {i}: Invalid course {course}, must be 0-7"}
        if room not in range(4):
            return {"valid": False, "message": f"Assignment {i}: Invalid room {room}, must be 0-3"}
        if time_slot not in range(6):
            return {"valid": False, "message": f"Assignment {i}: Invalid time_slot {time_slot}, must be 0-5"}

        # Constraint 1: Check uniqueness of courses
        if course in seen_courses:
            return {"valid": False, "message": f"Course {course} appears multiple times"}
        seen_courses.add(course)
        course_times[course] = time_slot

        # Constraint 2: Check room-time conflicts
        room_time = (room, time_slot)
        if room_time in room_time_pairs:
            return {"valid": False, "message": f"Room {room} double-booked at time {time_slot}"}
        room_time_pairs.add(room_time)

        # Constraint 4: Check capacity constraints
        course_name, teacher, students, dept = courses[course]
        room_capacity, room_features = rooms[room]
        if students > room_capacity:
            return {"valid": False, "message": f"Course {course} ({course_name}) has {students} students but room {room} capacity is {room_capacity}"}

        # Constraint 5: Check teacher availability
        if time_slot not in teacher_availability[teacher]:
            return {"valid": False, "message": f"Teacher {teacher} (course {course}: {course_name}) not available at time {time_slot}"}

        # Constraint 3: Check teacher conflicts
        teacher_time = (teacher, time_slot)
        if teacher_time in teacher_time_pairs:
            return {"valid": False, "message": f"Teacher {teacher} double-booked at time {time_slot}"}
        teacher_time_pairs.add(teacher_time)

        # Constraint 6: Check room features
        if course in room_requirements:
            required_features = room_requirements[course]
            for feature in required_features:
                if feature not in room_features:
                    return {"valid": False, "message": f"Course {course} ({course_name}) requires '{feature}' but room {room} doesn't have it (features: {room_features})"}

        # Count slot 5 assignments
        if time_slot == 5:
            slot_5_count += 1

    # Verify all courses are assigned
    if seen_courses != {0, 1, 2, 3, 4, 5, 6, 7}:
        missing = {0, 1, 2, 3, 4, 5, 6, 7} - seen_courses
        return {"valid": False, "message": f"Missing course assignments: {missing}"}

    # Constraint 7: Check prerequisites
    for prereq, dependent in prerequisites:
        if course_times[prereq] >= course_times[dependent]:
            prereq_name = courses[prereq][0]
            dependent_name = courses[dependent][0]
            return {"valid": False, "message": f"Prerequisite violation: {prereq_name} (course {prereq}) at time {course_times[prereq]} must come before {dependent_name} (course {dependent}) at time {course_times[dependent]}"}

    # Constraint 8: Check student conflicts
    for c1, c2 in student_conflicts:
        if course_times[c1] == course_times[c2]:
            return {"valid": False, "message": f"Student conflict: courses {c1} and {c2} cannot be at the same time (both at {course_times[c1]})"}

    # Constraint 9: Check evening limit
    if slot_5_count > 2:
        return {"valid": False, "message": f"Evening limit violation: {slot_5_count} courses in slot 5, maximum is 2"}

    # Verify cost calculation (optimization objective)
    # Cost = number of adjacent same-department course pairs
    calculated_cost = 0
    for c1 in range(8):
        for c2 in range(8):
            if c1 != c2:
                dept1 = courses[c1][3]
                dept2 = courses[c2][3]
                time1 = course_times[c1]
                time2 = course_times[c2]
                # Check if same department and adjacent times
                if dept1 == dept2 and abs(time1 - time2) == 1:
                    # Count each pair once (when c1 < c2 and time1 < time2)
                    if c1 < c2 and time1 < time2:
                        calculated_cost += 1

    reported_cost = solution["cost"]
    if reported_cost != calculated_cost:
        return {"valid": False, "message": f"Cost mismatch: reported {reported_cost}, calculated {calculated_cost}"}

    # Check optimality
    if calculated_cost != EXPECTED_OPTIMAL_COST:
        return {"valid": False, "message": f"Not optimal: cost={calculated_cost}, expected {EXPECTED_OPTIMAL_COST}"}

    return {"valid": True, "message": f"Solution is valid and optimal (cost={EXPECTED_OPTIMAL_COST})"}

def main():
    """Main entry point for verification."""
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], 'r') as f:
            content = f.read()
    else:
        # Read from stdin
        content = sys.stdin.read()

    # Try to parse as JSON first
    try:
        solution_json = content
        json.loads(solution_json)  # Test if it's valid JSON
    except json.JSONDecodeError:
        # If not JSON, try to execute as Python code
        import subprocess
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            result = subprocess.run(['python3', temp_file], capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(json.dumps({"valid": False, "message": f"Error executing Python code: {result.stderr}"}))
                return
            solution_json = result.stdout
        finally:
            os.unlink(temp_file)

    result = verify_solution(solution_json)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
