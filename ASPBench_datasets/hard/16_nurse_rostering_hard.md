# Problem Statement

Create a valid work schedule for 5 nurses over a 10-day period that satisfies all hard constraints. This is a constraint satisfaction problem with no optimization objective.

## Instance Data

- **Nurses**: 5 nurses (IDs: 1, 2, 3, 4, 5)
- **Days**: 10 days (IDs: 1 through 10)
- **Shifts**: 3 shifts per day:
  - `1`: Morning Shift
  - `2`: Evening Shift
  - `3`: Night Shift

## Constraints

1. **Coverage Requirements**: Each shift on each day must have exactly the required number of nurses:
   - **Morning Shift (1)**: Exactly 2 nurses
   - **Evening Shift (2)**: Exactly 1 nurse
   - **Night Shift (3)**: Exactly 1 nurse

2. **Single Assignment per Day**: A nurse can be assigned to **at most one** shift on any given day.

3. **Rest Period**: A nurse who works a **night shift** (3) on any day **cannot** work the **morning shift** (1) on the following day.

## Objective

Find any valid roster that satisfies **all** hard constraints.

## Output Format

The solution must be a JSON object with the following structure:

```json
{
  "roster": [
    [ [1, 2], [3], [4] ],
    [ [1, 5], [2], [3] ],
    [ [2, 4], [5], [1] ],
    [ [3, 5], [4], [2] ],
    [ [1, 4], [3], [5] ],
    [ [1, 2], [3], [4] ],
    [ [1, 5], [2], [3] ],
    [ [2, 4], [5], [1] ],
    [ [3, 5], [4], [2] ],
    [ [1, 4], [3], [5] ]
  ]
}
```

### Field Descriptions

- `roster`: A 10-element array where each element represents a day
  - Each day is a 3-element array: `[morning_nurses, evening_nurses, night_nurses]`
  - Each shift is an array of nurse IDs assigned to that shift
  - If no valid schedule exists, the value should be `null`
