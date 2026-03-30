# Problem Statement

A distribution center needs to pack 9 items of various sizes into bins with a capacity of 10 units each. Find an assignment of items to bins that minimizes the total number of bins used while ensuring no bin exceeds its capacity.

## Instance Data

**Items and Sizes:**
- Item 1: 4 units
- Item 2: 6 units
- Item 3: 2 units
- Item 4: 3 units
- Item 5: 7 units
- Item 6: 1 unit
- Item 7: 5 units
- Item 8: 2 units
- Item 9: 4 units

**Bin Capacity:** 10 units per bin

Total item size: 34 units (theoretical minimum: 4 bins)

## Constraints

1. **Each item** must be assigned to exactly one bin
2. **No bin** can have a total size exceeding 10 units
3. **All items** must be packed

## Objective

Find a solution that **minimizes** the number of bins used.

**Expected optimal solution:** 4 bins

## Output Format

Output a JSON object with the following structure:

```json
{
  "bins": [
    {"bin_id": 1, "items": [5, 3, ...], "total_size": 10},
    {"bin_id": 2, "items": [2, 9, ...], "total_size": 10},
    ...
  ],
  "num_bins": 4,
  "feasible": true
}
```

**Field descriptions:**
- `bins`: Array of bin objects, each containing:
  - `bin_id`: Unique identifier (consecutive integers starting from 1)
  - `items`: Array of item IDs assigned to this bin
  - `total_size`: Sum of sizes of items in this bin
- `num_bins`: Total number of bins used in the solution
- `feasible`: Boolean indicating whether a valid solution was found
