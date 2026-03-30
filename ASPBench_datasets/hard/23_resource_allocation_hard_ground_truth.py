#!/usr/bin/env python3
"""
Reference model for the Extreme Hard Resource Allocation problem.
UPDATED: Now enforces optimality - checks that solution has maximal total value.
"""

import json
import sys

# Expected optimal value (extracted from reference solution)
# Maximum total value for this resource allocation instance is 470
EXPECTED_OPTIMAL_VALUE = 470

def verify_solution(solution_json: str) -> dict:
    """
    Verify if the given solution satisfies all problem constraints.
    """
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    # --- Data Definition ---
    tasks = {
        # ID: [Category, Value, Compute, Bandwidth, Storage, Specialists]
        0: ['research', 40, 20, 10, 30, 5], 1: ['research', 60, 30, 25, 20, 10],
        2: ['research', 70, 25, 20, 15, 5], 3: ['research', 55, 20, 15, 25, 10],
        4: ['development', 80, 40, 30, 20, 20], 5: ['development', 90, 35, 25, 30, 15],
        6: ['development', 75, 30, 40, 25, 18], 7: ['development', 85, 45, 35, 15, 22],
        8: ['deployment', 65, 15, 20, 40, 8], 9: ['deployment', 80, 20, 30, 35, 12],
        10: ['deployment', 70, 25, 25, 30, 10], 11: ['deployment', 95, 30, 35, 45, 15],
    }
    capacities = {"compute": 150, "bandwidth": 120, "storage": 140, "specialists": 60}
    prereq = {4: 0}
    exclusive_pair = {1, 7}
    diversity_bonus_value = 100
    conditional_specialist_cost = 5

    # --- Validation ---

    # Check structure and types
    required_fields = ["selected_tasks", "total_value", "bonus_achieved", "resource_usage"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    selected_tasks = solution.get("selected_tasks", [])
    if not isinstance(selected_tasks, list) or not all(isinstance(t, int) for t in selected_tasks):
        return {"valid": False, "message": "selected_tasks must be an array of integers."}
    if len(selected_tasks) != len(set(selected_tasks)):
        return {"valid": False, "message": "Duplicate tasks in selected_tasks."}
    for task_id in selected_tasks:
        if task_id not in tasks:
            return {"valid": False, "message": f"Invalid task ID {task_id}."}

    # --- Recalculate everything from scratch ---

    # Calculate resource usage
    actual_usage = {"compute": 0, "bandwidth": 0, "storage": 0, "specialists": 0}
    for task_id in selected_tasks:
        task_data = tasks[task_id]
        actual_usage["compute"] += task_data[2]
        actual_usage["bandwidth"] += task_data[3]
        actual_usage["storage"] += task_data[4]
        actual_usage["specialists"] += task_data[5]

    # Calculate conditional specialist cost
    dev_selected = any(tasks[t][0] == 'development' for t in selected_tasks)
    if dev_selected:
        deploy_tasks_count = sum(1 for t in selected_tasks if tasks[t][0] == 'deployment')
        actual_usage["specialists"] += deploy_tasks_count * conditional_specialist_cost

    # Calculate value and bonus
    base_value = sum(tasks[t][1] for t in selected_tasks)
    selected_categories = {tasks[t][0] for t in selected_tasks}
    actual_bonus_achieved = len(selected_categories) == 3
    actual_total_value = base_value + (diversity_bonus_value if actual_bonus_achieved else 0)

    # --- Compare calculated values with solution ---
    if actual_total_value != solution["total_value"]:
        return {"valid": False, "message": f"total_value mismatch: provided {solution['total_value']}, calculated {actual_total_value}."}
    if actual_bonus_achieved != solution["bonus_achieved"]:
        return {"valid": False, "message": f"bonus_achieved mismatch: provided {solution['bonus_achieved']}, calculated {actual_bonus_achieved}."}
    if actual_usage != solution["resource_usage"]:
        return {"valid": False, "message": f"resource_usage mismatch: provided {solution['resource_usage']}, calculated {actual_usage}."}

    # --- Check hard constraints ---
    for res, used in actual_usage.items():
        if used > capacities[res]:
            return {"valid": False, "message": f"Resource capacity exceeded for {res}: used {used}, capacity {capacities[res]}."}

    for task_id, req_id in prereq.items():
        if task_id in selected_tasks and req_id not in selected_tasks:
            return {"valid": False, "message": f"Prerequisite violated: Task {task_id} requires Task {req_id}."}

    if all(t in selected_tasks for t in exclusive_pair):
        return {"valid": False, "message": f"Mutual exclusion violated: Tasks {exclusive_pair} cannot be selected together."}

    # Check optimality
    if actual_total_value != EXPECTED_OPTIMAL_VALUE:
        return {"valid": False, "message": f"Not optimal: total_value={actual_total_value}, expected {EXPECTED_OPTIMAL_VALUE}"}

    return {"valid": True, "message": f"Solution is valid and optimal (total_value={EXPECTED_OPTIMAL_VALUE})"}

def main():
    """Main entry point for verification."""
    try:
        solution_json = sys.stdin.read()
        result = verify_solution(solution_json)
    except Exception as e:
        result = {"valid": False, "message": f"An unexpected error occurred: {e}"}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
