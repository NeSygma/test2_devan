#!/usr/bin/env python3
"""
Reference model for Recipe Planning problem.
Validates cooking schedule and resource constraints.
"""

import json
import sys
from typing import List, Dict, Tuple


def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def get_problem_setup():
    """Get the problem setup"""
    return {
        "recipes": {
            "pasta": [
                {"step": "prep", "duration": 10, "resource": "prep_area"},
                {"step": "boil", "duration": 15, "resource": "stove"},
                {"step": "serve", "duration": 5, "resource": "prep_area"}
            ],
            "salad": [
                {"step": "chop", "duration": 15, "resource": "prep_area"},
                {"step": "mix", "duration": 5, "resource": "prep_area"}
            ],
            "bread": [
                {"step": "bake", "duration": 30, "resource": "oven"}
            ]
        },
        "precedences": {
            "pasta": [("prep", "boil"), ("boil", "serve")],
            "salad": [("chop", "mix")],
            "bread": []
        },
        "resources": ["prep_area", "stove", "oven"]
    }


def validate_schedule_step(step: Dict, setup: Dict) -> Tuple[bool, str]:
    """Validate a single schedule step"""

    required_fields = ["recipe", "step", "start_time", "end_time", "resources"]
    for field in required_fields:
        if field not in step:
            return False, f"Missing field: {field}"

    recipe = step["recipe"]
    step_name = step["step"]
    start_time = step["start_time"]
    end_time = step["end_time"]
    resources = step["resources"]

    # Check recipe exists
    if recipe not in setup["recipes"]:
        return False, f"Unknown recipe: {recipe}"

    # Find step info
    recipe_steps = setup["recipes"][recipe]
    step_info = None
    for s in recipe_steps:
        if s["step"] == step_name:
            step_info = s
            break

    if step_info is None:
        return False, f"Unknown step {step_name} for recipe {recipe}"

    # Check duration
    expected_duration = step_info["duration"]
    actual_duration = end_time - start_time
    if actual_duration != expected_duration:
        return False, f"Incorrect duration for {recipe}.{step_name}: expected {expected_duration}, got {actual_duration}"

    # Check resource
    expected_resource = step_info["resource"]
    if len(resources) != 1 or resources[0] != expected_resource:
        return False, f"Incorrect resource for {recipe}.{step_name}: expected [{expected_resource}], got {resources}"

    # Check times are non-negative
    if start_time < 0 or end_time < 0:
        return False, f"Negative time for {recipe}.{step_name}: start={start_time}, end={end_time}"

    return True, "Valid step"


def check_precedence_constraints(schedule: List[Dict], setup: Dict) -> Tuple[bool, str]:
    """Check precedence constraints within recipes"""

    # Build step timing map
    step_times = {}
    for step in schedule:
        recipe = step["recipe"]
        step_name = step["step"]
        if recipe not in step_times:
            step_times[recipe] = {}
        step_times[recipe][step_name] = (step["start_time"], step["end_time"])

    # Check precedences
    for recipe, precedences in setup["precedences"].items():
        for step1, step2 in precedences:
            if recipe in step_times and step1 in step_times[recipe] and step2 in step_times[recipe]:
                end1 = step_times[recipe][step1][1]
                start2 = step_times[recipe][step2][0]

                if start2 < end1:
                    return False, f"Precedence violation: {recipe}.{step2} starts before {recipe}.{step1} ends"

    return True, "Precedence constraints satisfied"


def check_resource_conflicts(schedule: List[Dict]) -> Tuple[bool, str]:
    """Check for resource conflicts"""

    # Group steps by resource
    resource_usage = {}
    for step in schedule:
        for resource in step["resources"]:
            if resource not in resource_usage:
                resource_usage[resource] = []
            resource_usage[resource].append({
                "recipe": step["recipe"],
                "step": step["step"],
                "start": step["start_time"],
                "end": step["end_time"]
            })

    # Check for overlaps within each resource
    for resource, usages in resource_usage.items():
        usages.sort(key=lambda x: x["start"])

        for i in range(len(usages)):
            for j in range(i+1, len(usages)):
                usage1 = usages[i]
                usage2 = usages[j]

                # Check if they overlap
                if usage1["start"] < usage2["end"] and usage2["start"] < usage1["end"]:
                    return False, f"Resource conflict on {resource}: {usage1['recipe']}.{usage1['step']} and {usage2['recipe']}.{usage2['step']} overlap"

    return True, "No resource conflicts"


def validate_resource_usage(resource_usage: Dict, schedule: List[Dict]) -> Tuple[bool, str]:
    """Validate resource usage matches schedule"""

    # Build expected resource usage from schedule
    expected_usage = {"oven": [], "stove": [], "prep_area": []}

    for step in schedule:
        for resource in step["resources"]:
            if resource in expected_usage:
                expected_usage[resource].append({
                    "start": step["start_time"],
                    "end": step["end_time"],
                    "recipe": step["recipe"]
                })

    # Sort for comparison
    for resource in expected_usage:
        expected_usage[resource].sort(key=lambda x: (x["start"], x["end"], x["recipe"]))
        if resource in resource_usage:
            actual_usage = sorted(resource_usage[resource], key=lambda x: (x["start"], x["end"], x["recipe"]))
            if actual_usage != expected_usage[resource]:
                return False, f"Resource usage mismatch for {resource}"

    return True, "Resource usage matches schedule"


def validate_solution(solution: Dict) -> Tuple[bool, str]:
    """Validate the recipe planning solution"""

    if not solution:
        return False, "No solution provided"

    required_fields = ["total_time", "schedule", "resource_usage"]
    for field in required_fields:
        if field not in solution:
            return False, f"Missing field: {field}"

    setup = get_problem_setup()

    # Validate schedule steps
    for i, step in enumerate(solution["schedule"]):
        is_valid, message = validate_schedule_step(step, setup)
        if not is_valid:
            return False, f"Step {i+1} invalid: {message}"

    # Check completeness - all recipe steps must be present
    expected_steps = set()
    for recipe, steps in setup["recipes"].items():
        for step_info in steps:
            expected_steps.add((recipe, step_info["step"]))

    actual_steps = set()
    for step in solution["schedule"]:
        actual_steps.add((step["recipe"], step["step"]))

    if actual_steps != expected_steps:
        missing = expected_steps - actual_steps
        extra = actual_steps - expected_steps
        return False, f"Step completeness error. Missing: {sorted(missing)}, Extra: {sorted(extra)}"

    # Check precedence constraints
    is_valid, message = check_precedence_constraints(solution["schedule"], setup)
    if not is_valid:
        return False, message

    # Check resource conflicts
    is_valid, message = check_resource_conflicts(solution["schedule"])
    if not is_valid:
        return False, message

    # Validate total time
    max_end_time = max(step["end_time"] for step in solution["schedule"]) if solution["schedule"] else 0
    if solution["total_time"] != max_end_time:
        return False, f"Incorrect total time: expected {max_end_time}, got {solution['total_time']}"

    # Validate resource usage
    is_valid, message = validate_resource_usage(solution["resource_usage"], solution["schedule"])
    if not is_valid:
        return False, message

    # Check optimality (expected optimal: 35 minutes)
    if solution["total_time"] != 35:
        return False, f"Suboptimal solution: total time {solution['total_time']} exceeds optimal of 35 minutes"

    return True, f"Valid optimal recipe schedule completing in {solution['total_time']} minutes"


def main():
    """Main validation function"""
    solution = load_solution()

    if solution is None:
        result = {"valid": False, "message": "Invalid or missing JSON input"}
    else:
        is_valid, message = validate_solution(solution)
        result = {"valid": is_valid, "message": message}

    print(json.dumps(result))


if __name__ == "__main__":
    main()
