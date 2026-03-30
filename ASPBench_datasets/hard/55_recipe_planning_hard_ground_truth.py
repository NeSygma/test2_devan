#!/usr/bin/env python3
"""
Reference model for Recipe Planning (Hard) problem.
Validates a cooking schedule with resource constraints and dependencies.
"""

import json
import sys
from typing import Dict, Any, Tuple

# Expected optimal value
EXPECTED_OPTIMAL_TIME = 75

def get_problem_setup() -> Dict[str, Any]:
    """Get the problem setup."""
    return {
        "recipes": {
            "roast_chicken": [
                {"step": "prep_chicken", "duration": 15, "resource": "prep_area"},
                {"step": "bake_chicken", "duration": 50, "resource": "oven"},
                {"step": "rest_chicken", "duration": 10, "resource": "prep_area"}
            ],
            "vegetable_soup": [
                {"step": "chop_veg_soup", "duration": 20, "resource": "prep_area"},
                {"step": "simmer_stock", "duration": 30, "resource": "stove"}
            ],
            "risotto": [
                {"step": "chop_onion", "duration": 5, "resource": "prep_area"},
                {"step": "cook_risotto", "duration": 25, "resource": "stove"}
            ],
            "side_salad": [
                {"step": "wash_greens", "duration": 5, "resource": "prep_area"},
                {"step": "mix_dressing", "duration": 10, "resource": "prep_area"}
            ]
        },
        "precedences": {
            "roast_chicken": [("prep_chicken", "bake_chicken"), ("bake_chicken", "rest_chicken")],
            "vegetable_soup": [("chop_veg_soup", "simmer_stock")],
            "risotto": [("chop_onion", "cook_risotto")],
            "side_salad": [("wash_greens", "mix_dressing")]
        },
        "dependencies": [
            {"producer_recipe": "vegetable_soup", "producer_step": "simmer_stock",
             "consumer_recipe": "risotto", "consumer_step": "cook_risotto"}
        ],
        "resources": {
            "prep_area": {"capacity": 2},
            "oven": {"capacity": 1, "preheat_required": True},
            "stove": {"capacity": 1}
        },
        "special_tasks": {
            "preheat_oven": {"duration": 10, "resource": "oven"}
        }
    }

def validate_solution(solution: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate the recipe planning solution."""
    if not solution:
        return False, "No solution provided"

    setup = get_problem_setup()

    # Check required fields
    if "total_time" not in solution or "schedule" not in solution:
        return False, "Missing required fields (total_time or schedule)"

    schedule = solution["schedule"]

    # Build task map
    task_map = {}
    scheduled_steps = set()

    for task in schedule:
        # Validate task structure
        if not all(k in task for k in ["start_time", "end_time", "resource"]):
            return False, f"Task missing required fields: {task}"

        start, end = task["start_time"], task["end_time"]
        if start < 0 or end <= start:
            return False, f"Invalid times: start={start}, end={end}"

        # Categorize task
        if "recipe" in task:
            key = (task["recipe"], task["step"])
            task_map[key] = task
            scheduled_steps.add(key)
        elif "task" in task:
            key = ("special", task["task"])
            task_map[key] = task
        else:
            return False, f"Task must have either 'recipe' or 'task' field: {task}"

    # Check completeness: all required steps present
    required_steps = set()
    for recipe, steps in setup["recipes"].items():
        for step in steps:
            required_steps.add((recipe, step["step"]))

    if not required_steps.issubset(scheduled_steps):
        missing = sorted(list(required_steps - scheduled_steps))
        return False, f"Missing required steps: {missing}"

    # Validate each task's duration and resource
    for task in schedule:
        is_valid, msg = validate_task(task, setup)
        if not is_valid:
            return False, msg

    # Check precedences
    is_valid, msg = check_precedences(task_map, setup)
    if not is_valid:
        return False, msg

    # Check dependencies
    is_valid, msg = check_dependencies(task_map, setup)
    if not is_valid:
        return False, msg

    # Check oven preheating
    is_valid, msg = check_oven_preheat(task_map, schedule)
    if not is_valid:
        return False, msg

    # Check resource capacity constraints
    is_valid, msg = check_resource_constraints(schedule, setup)
    if not is_valid:
        return False, msg

    # Verify total_time
    max_end_time = max(t["end_time"] for t in schedule) if schedule else 0
    if solution["total_time"] != max_end_time:
        return False, f"Incorrect total_time: expected {max_end_time}, got {solution['total_time']}"

    # Check optimality
    if solution["total_time"] > EXPECTED_OPTIMAL_TIME:
        return False, f"Not optimal: total_time={solution['total_time']}, expected {EXPECTED_OPTIMAL_TIME}"

    return True, f"Solution valid and optimal (total_time={solution['total_time']})"

def validate_task(task: Dict[str, Any], setup: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a single task."""
    duration = task["end_time"] - task["start_time"]

    if "recipe" in task:
        recipe, step = task["recipe"], task["step"]
        info = next((s for s in setup["recipes"].get(recipe, []) if s["step"] == step), None)
        if not info:
            return False, f"Unknown step: {recipe}.{step}"
        if duration != info["duration"]:
            return False, f"Wrong duration for {recipe}.{step}: expected {info['duration']}, got {duration}"
        if task["resource"] != info["resource"]:
            return False, f"Wrong resource for {recipe}.{step}: expected {info['resource']}, got {task['resource']}"
    else:
        task_name = task["task"]
        info = setup["special_tasks"].get(task_name)
        if not info:
            return False, f"Unknown special task: {task_name}"
        if duration != info["duration"]:
            return False, f"Wrong duration for {task_name}: expected {info['duration']}, got {duration}"
        if task["resource"] != info["resource"]:
            return False, f"Wrong resource for {task_name}: expected {info['resource']}, got {task['resource']}"

    return True, ""

def check_precedences(task_map: Dict, setup: Dict) -> Tuple[bool, str]:
    """Check intra-recipe precedences."""
    for recipe, precs in setup["precedences"].items():
        for step1, step2 in precs:
            key1, key2 = (recipe, step1), (recipe, step2)
            if key1 not in task_map or key2 not in task_map:
                continue
            if task_map[key1]["end_time"] > task_map[key2]["start_time"]:
                return False, f"Precedence violated: {recipe}.{step1} must finish before {recipe}.{step2} starts"
    return True, ""

def check_dependencies(task_map: Dict, setup: Dict) -> Tuple[bool, str]:
    """Check inter-recipe dependencies."""
    for dep in setup["dependencies"]:
        key_prod = (dep["producer_recipe"], dep["producer_step"])
        key_cons = (dep["consumer_recipe"], dep["consumer_step"])
        if key_prod not in task_map or key_cons not in task_map:
            continue
        if task_map[key_prod]["end_time"] > task_map[key_cons]["start_time"]:
            return False, f"Dependency violated: {key_prod[1]} must finish before {key_cons[1]} starts"
    return True, ""

def check_oven_preheat(task_map: Dict, schedule: list) -> Tuple[bool, str]:
    """Check oven preheating requirement."""
    bake_tasks = [t for t in schedule if "recipe" in t and t["step"] == "bake_chicken"]
    preheat_tasks = [t for t in schedule if "task" in t and t["task"] == "preheat_oven"]

    if not bake_tasks:
        return True, ""  # No baking, no preheat needed

    if not preheat_tasks:
        return False, "Oven requires preheating before baking"

    first_bake_start = min(t["start_time"] for t in bake_tasks)
    preheat_end = max(t["end_time"] for t in preheat_tasks)

    if preheat_end > first_bake_start:
        return False, "Oven preheat must complete before baking starts"

    return True, ""

def check_resource_constraints(schedule: list, setup: Dict) -> Tuple[bool, str]:
    """Check resource capacity constraints."""
    # Group tasks by resource
    by_resource = {}
    for task in schedule:
        res = task["resource"]
        if res not in by_resource:
            by_resource[res] = []
        by_resource[res].append(task)

    # Check capacity for each resource
    for res, tasks in by_resource.items():
        capacity = setup["resources"][res]["capacity"]

        # Check at each time point
        all_times = set()
        for task in tasks:
            all_times.add(task["start_time"])
            all_times.add(task["end_time"])

        for t in sorted(all_times):
            active = sum(1 for task in tasks if task["start_time"] <= t < task["end_time"])
            if active > capacity:
                return False, f"Resource {res} capacity {capacity} exceeded at time {t}: {active} tasks active"

    return True, ""

def main():
    """Main validation function."""
    try:
        solution = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        solution = None

    is_valid, message = validate_solution(solution)
    result = {"valid": is_valid, "message": message}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
