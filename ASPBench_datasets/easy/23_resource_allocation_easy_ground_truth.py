#!/usr/bin/env python3
"""
Reference model for Resource Allocation problem
Validates solution from stdin and outputs JSON result.
"""

import json
import sys

def verify_solution(solution_json: str) -> dict:
    """
    Verify if the given solution satisfies all problem constraints.

    Args:
        solution_json: JSON string containing the solution

    Returns:
        dict with keys 'valid' (bool) and 'message' (str)
    """

    # Parse solution
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    # Check required fields
    required_fields = ["selected_tasks", "total_value", "resource_usage"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    selected_tasks = solution["selected_tasks"]
    total_value = solution["total_value"]
    resource_usage = solution["resource_usage"]

    # Validate types
    if not isinstance(selected_tasks, list):
        return {"valid": False, "message": "selected_tasks must be an array"}
    if not isinstance(total_value, int):
        return {"valid": False, "message": "total_value must be an integer"}
    if not isinstance(resource_usage, dict):
        return {"valid": False, "message": "resource_usage must be an object"}

    # Check resource_usage structure
    required_resources = ["resource_a", "resource_b", "resource_c"]
    for res in required_resources:
        if res not in resource_usage:
            return {"valid": False, "message": f"Missing resource in usage: {res}"}
        if not isinstance(resource_usage[res], int):
            return {"valid": False, "message": f"Resource usage {res} must be an integer"}

    # Task data: [value, resource_a, resource_b, resource_c]
    tasks = [
        [50, 30, 20, 10],  # Task 0
        [40, 25, 15, 15],  # Task 1
        [60, 20, 30, 20],  # Task 2
        [35, 15, 25, 10],  # Task 3
        [70, 40, 10, 25],  # Task 4
        [45, 20, 20, 15]   # Task 5
    ]

    # Resource capacities
    capacities = {"resource_a": 100, "resource_b": 80, "resource_c": 60}

    # Validate selected tasks
    for task in selected_tasks:
        if not isinstance(task, int):
            return {"valid": False, "message": f"Task {task} must be an integer"}
        if task not in range(6):
            return {"valid": False, "message": f"Invalid task {task}, must be 0-5"}

    # Check no duplicates
    if len(selected_tasks) != len(set(selected_tasks)):
        return {"valid": False, "message": "Duplicate tasks in selected_tasks"}

    # Calculate actual values and resource usage
    actual_value = sum(tasks[task][0] for task in selected_tasks)
    actual_usage = {
        "resource_a": sum(tasks[task][1] for task in selected_tasks),
        "resource_b": sum(tasks[task][2] for task in selected_tasks),
        "resource_c": sum(tasks[task][3] for task in selected_tasks)
    }

    # Check total value
    if total_value != actual_value:
        return {"valid": False, "message": f"total_value mismatch: expected {actual_value}, got {total_value}"}

    # Check resource usage
    for res in required_resources:
        if resource_usage[res] != actual_usage[res]:
            return {"valid": False, "message": f"{res} usage mismatch: expected {actual_usage[res]}, got {resource_usage[res]}"}

    # Check capacity constraints
    for res in required_resources:
        if resource_usage[res] > capacities[res]:
            return {"valid": False, "message": f"{res} exceeds capacity: used {resource_usage[res]}, capacity {capacities[res]}"}

    # Check optimality - the maximum value is 180 (tasks 0, 2, 4)
    optimal_value = 180
    is_optimal = total_value == optimal_value

    if is_optimal:
        return {"valid": True, "message": f"Valid and optimal resource allocation with value {total_value}"}
    else:
        return {"valid": False, "message": f"Suboptimal allocation. Value {total_value}, optimal is {optimal_value}"}

def main():
    """Main entry point for verification."""
    solution_json = sys.stdin.read().strip()
    if not solution_json:
        print(json.dumps({"valid": False, "message": "No solution provided"}))
        return

    result = verify_solution(solution_json)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
