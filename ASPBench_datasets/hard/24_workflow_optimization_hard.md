# Problem Statement

Schedule 10 tasks with precedence constraints and machine assignments to minimize total completion time (makespan). Each task has a fixed duration and can only run on specific machines. Machines can execute only one task at a time, and tasks cannot start until all prerequisites complete.

## Instance Data

**Tasks:** 10 tasks (IDs 0-9) with the following properties:

| Task | Duration | Eligible Machines | Prerequisites |
|------|----------|-------------------|---------------|
| 0    | 4        | [1]               | []            |
| 1    | 3        | [2]               | []            |
| 2    | 5        | [3]               | []            |
| 3    | 2        | [1]               | [0]           |
| 4    | 6        | [2]               | [1]           |
| 5    | 3        | [1]               | [3]           |
| 6    | 4        | [3]               | [2, 4]        |
| 7    | 5        | [2]               | [4]           |
| 8    | 2        | [1]               | [5]           |
| 9    | 3        | [2, 3]            | [7, 8]        |

**Machines:** 3 machines (IDs 1, 2, 3)

**Precedence relationships:**
- Task 3 requires task 0 to complete first
- Task 4 requires task 1 to complete first
- Task 5 requires task 3 to complete first
- Task 6 requires tasks 2 and 4 to complete first
- Task 7 requires task 4 to complete first
- Task 8 requires task 5 to complete first
- Task 9 requires tasks 7 and 8 to complete first

## Constraints

1. Each task **must** be assigned to **exactly one** of its eligible machines.
2. A machine can **only** execute one task at a time - tasks on the same machine **cannot** overlap.
3. Tasks **cannot** start until **all** their prerequisite tasks have completed.
4. Each task runs for its specified duration without interruption.
5. All tasks **must** be scheduled (no task can be omitted).

## Objective

Find the optimal schedule that **minimizes** the makespan (total completion time). **Expected optimal makespan: 17**

## Output Format

The solution must be a JSON object with the following structure:

```json
{
  "schedule": [
    {
      "task": 0,
      "machine": 1,
      "start_time": 0,
      "end_time": 4
    },
    ...
  ],
  "makespan": 17,
  "critical_path": [1, 4, 7, 9]
}
```

**Fields:**
- `schedule`: Array of task assignments (one per task)
  - `task`: Task ID (0-9)
  - `machine`: Assigned machine ID
  - `start_time`: When the task starts
  - `end_time`: When the task completes (start_time + duration)
- `makespan`: Maximum end time across all tasks
- `critical_path`: Sequence of task IDs forming the longest dependency chain
