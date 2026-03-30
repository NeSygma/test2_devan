#!/usr/bin/env python3
"""
Reference model for the Workflow Optimization problem.
Validates solution and enforces optimality - checks that solution has minimal makespan.
"""

import json
import sys
from collections import defaultdict

# Expected optimal value
# Minimum makespan for this workflow instance is 17
EXPECTED_OPTIMAL_MAKESPAN = 17

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

    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    required_fields = ["schedule", "makespan", "critical_path"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    schedule = solution["schedule"]
    makespan = solution["makespan"]

    # Task data: [duration, [eligible_machines], [prerequisites]]
    tasks_data = {
        0: [4, [1], []],
        1: [3, [2], []],
        2: [5, [3], []],
        3: [2, [1], [0]],
        4: [6, [2], [1]],
        5: [3, [1], [3]],
        6: [4, [3], [2, 4]],
        7: [5, [2], [4]],
        8: [2, [1], [5]],
        9: [3, [2, 3], [7, 8]],
    }

    if len(schedule) != len(tasks_data):
        return {"valid": False, "message": f"Schedule must have {len(tasks_data)} entries, got {len(schedule)}"}

    task_schedule = {}
    machine_schedules = defaultdict(list)

    for i, entry in enumerate(schedule):
        req_entry_fields = ["task", "machine", "start_time", "end_time"]
        for field in req_entry_fields:
            if field not in entry:
                return {"valid": False, "message": f"Schedule entry {i} missing field: {field}"}

        task, machine, start_time, end_time = entry["task"], entry["machine"], entry["start_time"], entry["end_time"]

        if task not in tasks_data:
            return {"valid": False, "message": f"Invalid task ID {task}"}

        duration, eligible_machines, _ = tasks_data[task]

        if end_time != start_time + duration:
            return {"valid": False, "message": f"Task {task} end_time {end_time} doesn't match start_time({start_time}) + duration({duration})"}

        if machine not in eligible_machines:
            return {"valid": False, "message": f"Task {task} assigned to ineligible machine {machine}"}

        if task in task_schedule:
            return {"valid": False, "message": f"Duplicate task {task} in schedule"}

        task_schedule[task] = {"start": start_time, "end": end_time}
        machine_schedules[machine].append({"task": task, "start": start_time, "end": end_time})

    if set(task_schedule.keys()) != set(tasks_data.keys()):
        return {"valid": False, "message": "Not all tasks are scheduled"}

    # Check precedence constraints
    for task_id, task_info in task_schedule.items():
        prerequisites = tasks_data[task_id][2]
        for prereq_id in prerequisites:
            prereq_end_time = task_schedule[prereq_id]["end"]
            if task_info["start"] < prereq_end_time:
                return {"valid": False, "message": f"Task {task_id} starts at {task_info['start']} before prerequisite {prereq_id} ends at {prereq_end_time}"}

    # Check machine usage (no overlap)
    for machine_id, tasks_on_machine in machine_schedules.items():
        tasks_on_machine.sort(key=lambda x: x["start"])
        for j in range(len(tasks_on_machine) - 1):
            task1 = tasks_on_machine[j]
            task2 = tasks_on_machine[j+1]
            if task1["end"] > task2["start"]:
                return {"valid": False, "message": f"Machine {machine_id} has overlapping tasks: {task1['task']} (ends {task1['end']}) and {task2['task']} (starts {task2['start']})"}

    # Check makespan
    actual_makespan = max(t["end"] for t in task_schedule.values()) if task_schedule else 0
    if makespan != actual_makespan:
        return {"valid": False, "message": f"Makespan mismatch: expected {actual_makespan}, got {makespan}"}

    # Check optimality
    if makespan != EXPECTED_OPTIMAL_MAKESPAN:
        return {"valid": False, "message": f"Not optimal: makespan={makespan}, expected {EXPECTED_OPTIMAL_MAKESPAN}"}

    return {"valid": True, "message": f"Solution is valid and optimal (makespan={EXPECTED_OPTIMAL_MAKESPAN})"}

def main():
    """Main entry point for verification."""
    solution_json = sys.stdin.read()
    result = verify_solution(solution_json)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
