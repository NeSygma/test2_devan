#!/usr/bin/env python3
"""
Reference Model for Job Shop Scheduling Problem

Validates job shop scheduling solutions from stdin.
Checks precedence constraints, machine conflicts, and optimal makespan.
"""

import json
import sys
from typing import Dict, List, Tuple

def load_solution():
    """Load solution from stdin."""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def validate_solution(solution):
    """Validate the job shop scheduling solution."""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    # Check required fields
    if "schedule" not in solution or "makespan" not in solution or "feasible" not in solution:
        return {"valid": False, "message": "Missing required fields: schedule, makespan, feasible"}

    if not solution["feasible"]:
        return {"valid": False, "message": "Solution marked as infeasible"}

    schedule = solution["schedule"]
    makespan = solution["makespan"]

    # Problem data - 3 jobs, 3 operations each, 3 machines
    jobs = [1, 2, 3]
    operations = [1, 2, 3]

    # Job operation data: (job, operation, machine, duration)
    job_data = {
        # Job 1: m1(3) -> m2(2) -> m3(4)
        (1, 1): (1, 3),
        (1, 2): (2, 2),
        (1, 3): (3, 4),
        # Job 2: m2(2) -> m1(5) -> m3(1)
        (2, 1): (2, 2),
        (2, 2): (1, 5),
        (2, 3): (3, 1),
        # Job 3: m3(4) -> m1(1) -> m2(3)
        (3, 1): (3, 4),
        (3, 2): (1, 1),
        (3, 3): (2, 3),
    }

    # Check that all operations are scheduled
    if len(schedule) != 9:
        return {"valid": False, "message": f"Expected 9 operations, got {len(schedule)}"}

    # Build schedule mapping
    schedule_map = {}
    for entry in schedule:
        if not all(k in entry for k in ["job", "operation", "machine", "start", "duration"]):
            return {"valid": False, "message": "Schedule entry missing required fields"}

        job = entry["job"]
        op = entry["operation"]
        machine = entry["machine"]
        start = entry["start"]
        duration = entry["duration"]

        # Validate job and operation numbers
        if job not in jobs or op not in operations:
            return {"valid": False, "message": f"Invalid job {job} or operation {op}"}

        # Validate machine and duration match expected data
        expected_machine, expected_duration = job_data[(job, op)]
        if machine != expected_machine:
            return {"valid": False, "message": f"Job {job}, operation {op}: expected machine {expected_machine}, got {machine}"}
        if duration != expected_duration:
            return {"valid": False, "message": f"Job {job}, operation {op}: expected duration {expected_duration}, got {duration}"}

        # Validate non-negative start time
        if start < 0:
            return {"valid": False, "message": f"Negative start time {start} for job {job}, operation {op}"}

        schedule_map[(job, op)] = (machine, start, duration)

    # Check precedence constraints
    for job in jobs:
        for op in range(1, len(operations)):
            if (job, op) in schedule_map and (job, op + 1) in schedule_map:
                _, start1, duration1 = schedule_map[(job, op)]
                _, start2, _ = schedule_map[(job, op + 1)]

                if start1 + duration1 > start2:
                    return {"valid": False, "message": f"Precedence violated: Job {job}, operation {op} finishes at {start1 + duration1}, but operation {op+1} starts at {start2}"}

    # Check machine conflicts
    machine_intervals = {}
    for (job, op), (machine, start, duration) in schedule_map.items():
        end = start + duration

        if machine not in machine_intervals:
            machine_intervals[machine] = []

        # Check for overlaps with existing intervals on this machine
        for existing_start, existing_end, existing_job, existing_op in machine_intervals[machine]:
            if not (end <= existing_start or start >= existing_end):
                return {"valid": False, "message": f"Machine conflict on machine {machine}: Job {job} op {op} [{start}, {end}) overlaps with Job {existing_job} op {existing_op} [{existing_start}, {existing_end})"}

        machine_intervals[machine].append((start, end, job, op))

    # Calculate actual makespan
    actual_makespan = 0
    for (job, op), (machine, start, duration) in schedule_map.items():
        end = start + duration
        actual_makespan = max(actual_makespan, end)

    # Check makespan matches
    if actual_makespan != makespan:
        return {"valid": False, "message": f"Makespan mismatch: calculated {actual_makespan}, reported {makespan}"}

    # Check optimality (expected optimal makespan is 11)
    expected_optimal_makespan = 11
    if makespan != expected_optimal_makespan:
        return {"valid": False, "message": f"Solution is not optimal: makespan {makespan}, expected optimal {expected_optimal_makespan}"}

    return {"valid": True, "message": f"Solution correct with optimal makespan {makespan}"}

def main():
    """Main validation function."""
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
