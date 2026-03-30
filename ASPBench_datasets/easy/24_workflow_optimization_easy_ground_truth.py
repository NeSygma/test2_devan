#!/usr/bin/env python3
"""
Reference model for Workflow Optimization problem
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
    required_fields = ["schedule", "makespan", "critical_path"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    schedule = solution["schedule"]
    makespan = solution["makespan"]
    critical_path = solution["critical_path"]

    # Validate types
    if not isinstance(schedule, list):
        return {"valid": False, "message": "schedule must be an array"}
    if not isinstance(makespan, int):
        return {"valid": False, "message": "makespan must be an integer"}
    if not isinstance(critical_path, list):
        return {"valid": False, "message": "critical_path must be an array"}

    # Task data: [duration, prerequisites]
    tasks_data = [
        [3, []],        # Task 0
        [2, []],        # Task 1
        [4, [0]],       # Task 2
        [1, [1]],       # Task 3
        [5, [2, 3]],    # Task 4
        [2, [0]],       # Task 5
        [3, [4]],       # Task 6
        [2, [5, 6]]     # Task 7
    ]

    # Validate schedule structure
    if len(schedule) != 8:
        return {"valid": False, "message": f"Schedule must have 8 entries, got {len(schedule)}"}

    task_schedule = {}
    for i, entry in enumerate(schedule):
        if not isinstance(entry, dict):
            return {"valid": False, "message": f"Schedule entry {i} must be an object"}

        required_entry_fields = ["task", "start_time", "end_time"]
        for field in required_entry_fields:
            if field not in entry:
                return {"valid": False, "message": f"Schedule entry {i} missing field: {field}"}

        task = entry["task"]
        start_time = entry["start_time"]
        end_time = entry["end_time"]

        # Validate types and ranges
        if not isinstance(task, int) or task not in range(8):
            return {"valid": False, "message": f"Invalid task {task} in schedule entry {i}"}
        if not isinstance(start_time, int) or start_time < 0:
            return {"valid": False, "message": f"Invalid start_time {start_time} for task {task}"}
        if not isinstance(end_time, int) or end_time <= start_time:
            return {"valid": False, "message": f"Invalid end_time {end_time} for task {task}"}

        # Check duration
        expected_end = start_time + tasks_data[task][0]
        if end_time != expected_end:
            return {"valid": False, "message": f"Task {task} end_time {end_time} doesn't match start_time + duration = {expected_end}"}

        if task in task_schedule:
            return {"valid": False, "message": f"Duplicate task {task} in schedule"}

        task_schedule[task] = (start_time, end_time)

    # Check all tasks are scheduled
    if set(task_schedule.keys()) != set(range(8)):
        return {"valid": False, "message": "Not all tasks are scheduled"}

    # Check precedence constraints
    for task, (start_time, end_time) in task_schedule.items():
        prerequisites = tasks_data[task][1]
        for prereq in prerequisites:
            if prereq not in task_schedule:
                return {"valid": False, "message": f"Prerequisite {prereq} not scheduled for task {task}"}
            prereq_end = task_schedule[prereq][1]
            if start_time < prereq_end:
                return {"valid": False, "message": f"Task {task} starts at {start_time} before prerequisite {prereq} ends at {prereq_end}"}

    # Check makespan
    actual_makespan = max(end_time for start_time, end_time in task_schedule.values())
    if makespan != actual_makespan:
        return {"valid": False, "message": f"Makespan mismatch: expected {actual_makespan}, got {makespan}"}

    # Validate critical path
    for task in critical_path:
        if not isinstance(task, int) or task not in range(8):
            return {"valid": False, "message": f"Invalid task {task} in critical_path"}

    # Check optimality - minimum makespan is 17
    optimal_makespan = 17
    if makespan == optimal_makespan:
        return {"valid": True, "message": f"Solution correct. Optimal makespan: {makespan}"}
    else:
        return {"valid": False, "message": f"Solution suboptimal. Makespan {makespan}, optimal is {optimal_makespan}"}

def main():
    """Main entry point for verification."""
    solution_json = sys.stdin.read()
    result = verify_solution(solution_json)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
