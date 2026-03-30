#!/usr/bin/env python3
"""
Reference model for Resource Allocation with Dependencies (Hard)
Validates feasibility and optimality of solutions from stdin.
"""

import json
import sys

# Expected optimal value
EXPECTED_OPTIMAL_MAKESPAN = 9

def validate_resource_allocation(solution):
    """Validate a resource allocation solution."""

    # Task data
    tasks = {
        'T1':  {'duration': 2, 'skill': 'Welding',     'machine_type': 'A', 'deadline': 6,  'worker_cost': 15, 'machine_cost': 3},
        'T2':  {'duration': 3, 'skill': 'Assembly',    'machine_type': 'B', 'deadline': 8,  'worker_cost': 12, 'machine_cost': 2},
        'T3':  {'duration': 1, 'skill': 'Inspection',  'machine_type': 'A', 'deadline': 7,  'worker_cost': 18, 'machine_cost': 3},
        'T4':  {'duration': 2, 'skill': 'Welding',     'machine_type': 'A', 'deadline': 9,  'worker_cost': 15, 'machine_cost': 3},
        'T5':  {'duration': 3, 'skill': 'Assembly',    'machine_type': 'C', 'deadline': 10, 'worker_cost': 12, 'machine_cost': 4},
        'T6':  {'duration': 2, 'skill': 'Programming', 'machine_type': 'B', 'deadline': 9,  'worker_cost': 20, 'machine_cost': 2},
        'T7':  {'duration': 1, 'skill': 'Inspection',  'machine_type': 'A', 'deadline': 8,  'worker_cost': 18, 'machine_cost': 3},
        'T8':  {'duration': 2, 'skill': 'Assembly',    'machine_type': 'C', 'deadline': 11, 'worker_cost': 12, 'machine_cost': 4},
        'T9':  {'duration': 3, 'skill': 'Welding',     'machine_type': 'A', 'deadline': 12, 'worker_cost': 15, 'machine_cost': 3},
        'T10': {'duration': 2, 'skill': 'Programming', 'machine_type': 'B', 'deadline': 11, 'worker_cost': 20, 'machine_cost': 2},
        'T11': {'duration': 1, 'skill': 'Assembly',    'machine_type': 'C', 'deadline': 10, 'worker_cost': 12, 'machine_cost': 4},
        'T12': {'duration': 2, 'skill': 'Inspection',  'machine_type': 'A', 'deadline': 13, 'worker_cost': 18, 'machine_cost': 3},
    }

    # Worker data
    workers = {
        'W1': {'skills': ['Welding', 'Inspection'],               'hourly_cost': 15},
        'W2': {'skills': ['Assembly', 'Inspection'],              'hourly_cost': 12},
        'W3': {'skills': ['Programming', 'Assembly'],             'hourly_cost': 20},
        'W4': {'skills': ['Welding', 'Programming'],              'hourly_cost': 18},
        'W5': {'skills': ['Assembly', 'Inspection', 'Welding'],   'hourly_cost': 16},
    }

    # Machine data
    machines = {
        'M1': {'type': 'A', 'hourly_cost': 3},
        'M2': {'type': 'B', 'hourly_cost': 2},
        'M3': {'type': 'C', 'hourly_cost': 4},
    }

    # Precedence constraints
    precedence = [
        ('T1', 'T3'), ('T1', 'T4'),
        ('T2', 'T5'), ('T2', 'T6'),
        ('T3', 'T7'),
        ('T4', 'T9'),
        ('T5', 'T8'),
        ('T6', 'T10'),
        ('T7', 'T12'),
        ('T8', 'T11'),
    ]

    budget_limit = 470
    worker_capacity = 3
    machine_capacity = 2

    # Validate solution structure
    if not solution.get('feasible', False):
        return {"valid": False, "message": "Solution marked as infeasible"}

    if 'schedule' not in solution:
        return {"valid": False, "message": "Missing 'schedule' field"}

    schedule = solution['schedule']

    # Build task assignments
    task_assignments = {}
    for entry in schedule:
        task = entry.get('task')
        worker = entry.get('worker')
        machine = entry.get('machine')
        start = entry.get('start')

        if not all([task, worker, machine, start is not None]):
            return {"valid": False, "message": f"Incomplete schedule entry: {entry}"}

        if task not in tasks:
            return {"valid": False, "message": f"Unknown task: {task}"}

        if worker not in workers:
            return {"valid": False, "message": f"Unknown worker: {worker}"}

        if machine not in machines:
            return {"valid": False, "message": f"Unknown machine: {machine}"}

        if task in task_assignments:
            return {"valid": False, "message": f"Task {task} assigned multiple times"}

        task_assignments[task] = {
            'worker': worker,
            'machine': machine,
            'start': start,
            'end': start + tasks[task]['duration']
        }

    # C1: All tasks assigned
    if len(task_assignments) != len(tasks):
        return {"valid": False, "message": f"Not all tasks assigned: {len(task_assignments)}/{len(tasks)}"}

    # C2: Skill compatibility
    for task, assignment in task_assignments.items():
        required_skill = tasks[task]['skill']
        worker = assignment['worker']
        worker_skills = workers[worker]['skills']

        if required_skill not in worker_skills:
            return {"valid": False, "message": f"Task {task} requires {required_skill}, but worker {worker} has {worker_skills}"}

    # C3: Machine type compatibility
    for task, assignment in task_assignments.items():
        required_type = tasks[task]['machine_type']
        machine = assignment['machine']
        machine_type = machines[machine]['type']

        if machine_type != required_type:
            return {"valid": False, "message": f"Task {task} requires machine type {required_type}, but {machine} is type {machine_type}"}

    # C4: Capacity constraints
    # Build timeline of active tasks for each worker and machine
    max_time = max(a['end'] for a in task_assignments.values())

    for t in range(max_time + 1):
        # Check worker capacity
        for worker in workers:
            active_tasks = [task for task, a in task_assignments.items()
                           if a['worker'] == worker and a['start'] <= t < a['end']]
            if len(active_tasks) > worker_capacity:
                return {"valid": False, "message": f"Worker {worker} overloaded at time {t}: {len(active_tasks)} > {worker_capacity}"}

        # Check machine capacity
        for machine in machines:
            active_tasks = [task for task, a in task_assignments.items()
                           if a['machine'] == machine and a['start'] <= t < a['end']]
            if len(active_tasks) > machine_capacity:
                return {"valid": False, "message": f"Machine {machine} overloaded at time {t}: {len(active_tasks)} > {machine_capacity}"}

    # C5: Precedence constraints
    for pred, succ in precedence:
        if pred not in task_assignments or succ not in task_assignments:
            return {"valid": False, "message": f"Precedence tasks missing: {pred} -> {succ}"}

        pred_end = task_assignments[pred]['end']
        succ_start = task_assignments[succ]['start']

        if pred_end > succ_start:
            return {"valid": False, "message": f"Precedence violated: {pred} ends at {pred_end}, but {succ} starts at {succ_start}"}

    # C6: Deadlines
    for task, assignment in task_assignments.items():
        deadline = tasks[task]['deadline']
        finish_time = assignment['end']

        if finish_time > deadline:
            return {"valid": False, "message": f"Task {task} finishes at {finish_time}, exceeds deadline {deadline}"}

    # C7: Budget constraint
    total_cost = 0
    for task, assignment in task_assignments.items():
        duration = tasks[task]['duration']
        worker_cost = workers[assignment['worker']]['hourly_cost']
        machine_cost = machines[assignment['machine']]['hourly_cost']
        total_cost += (worker_cost + machine_cost) * duration

    if total_cost > budget_limit:
        return {"valid": False, "message": f"Budget exceeded: {total_cost} > {budget_limit}"}

    # Calculate makespan
    makespan = max(a['end'] for a in task_assignments.values())

    # Verify reported values
    if 'makespan' in solution and solution['makespan'] != makespan:
        return {"valid": False, "message": f"Makespan mismatch: reported {solution['makespan']}, calculated {makespan}"}

    if 'total_cost' in solution and solution['total_cost'] != total_cost:
        return {"valid": False, "message": f"Total cost mismatch: reported {solution['total_cost']}, calculated {total_cost}"}

    # Check optimality
    if makespan != EXPECTED_OPTIMAL_MAKESPAN:
        return {"valid": False, "message": f"Not optimal: makespan={makespan}, expected {EXPECTED_OPTIMAL_MAKESPAN}"}

    # Solution is valid and optimal
    return {
        "valid": True,
        "message": f"Solution is valid and optimal (makespan={EXPECTED_OPTIMAL_MAKESPAN}, total_cost={total_cost})"
    }

if __name__ == "__main__":
    try:
        solution_json = sys.stdin.read().strip()
        if not solution_json:
            print(json.dumps({"valid": False, "message": "No solution provided"}))
            sys.exit(1)

        solution = json.loads(solution_json)
        result = validate_resource_allocation(solution)
        print(json.dumps(result))
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Validation error: {e}"}))
        sys.exit(1)
