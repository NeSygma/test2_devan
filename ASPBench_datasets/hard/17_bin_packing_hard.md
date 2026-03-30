# Problem Statement

A logistics company needs to pack 27 items with diverse properties into smart bins. Each item has a size, category (electronics, liquid, or standard), fragility (fragile or sturdy), and priority level (high or low). The goal is to pack all items efficiently while respecting capacity limits, compatibility rules, fragility constraints, and priority placement requirements.

## Instance Data

**Items (27 total):**

| Item ID | Size | Category | Fragility | Priority |
|---------|------|----------|-----------|----------|
| 1 | 9 | electronics | fragile | high |
| 2 | 8 | electronics | sturdy | high |
| 3 | 3 | electronics | sturdy | high |
| 4 | 9 | liquid | fragile | high |
| 5 | 7 | liquid | sturdy | high |
| 6 | 4 | liquid | sturdy | high |
| 7 | 10 | electronics | fragile | high |
| 8 | 10 | standard | sturdy | high |
| 9 | 10 | liquid | fragile | high |
| 10 | 10 | standard | sturdy | high |
| 11 | 8 | standard | sturdy | high |
| 12 | 7 | standard | sturdy | high |
| 13 | 5 | standard | sturdy | low |
| 14 | 8 | standard | fragile | low |
| 15 | 6 | standard | fragile | low |
| 16 | 6 | standard | sturdy | low |
| 17 | 8 | standard | fragile | low |
| 18 | 6 | standard | fragile | low |
| 19 | 6 | standard | sturdy | low |
| 20 | 7 | standard | sturdy | low |
| 21 | 7 | standard | sturdy | low |
| 22 | 6 | standard | sturdy | low |
| 23 | 7 | standard | sturdy | low |
| 24 | 5 | standard | fragile | low |
| 25 | 5 | standard | fragile | low |
| 26 | 3 | standard | sturdy | low |
| 27 | 5 | standard | sturdy | low |

**Constants:**
- Bin capacity: 20 units
- Fragile item limit per bin: 2 items
- Priority bin range: bins 1-6 (only these bins can hold high-priority items)

## Constraints

1. **Capacity**: The total size of items in any bin must **not exceed** 20 units.
2. **Assignment**: Each item must be assigned to **exactly one** bin.
3. **Incompatibility**: Electronics and liquids **cannot** be placed in the same bin.
4. **Fragility Limit**: **No more than** 2 fragile items per bin.
5. **Priority Placement**: High-priority items must **only** be placed in bins 1-6.

## Objective

Find a **feasible** packing that satisfies all constraints.

## Output Format

The solution must be a JSON object with the following structure:

```json
{
  "feasible": true,
  "optimal": false,
  "num_bins": 14,
  "total_priority_utilization": 100,
  "bins": [
    {
      "bin_id": 1,
      "items": [
        {"item_id": 1, "size": 9, "category": "electronics", "fragility": "fragile", "priority": "high"},
        {"item_id": 2, "size": 8, "category": "electronics", "fragility": "sturdy", "priority": "high"},
        {"item_id": 3, "size": 3, "category": "electronics", "fragility": "sturdy", "priority": "high"}
      ],
      "total_size": 20,
      "fragile_count": 1,
      "is_priority_bin": true
    },
    ...
  ]
}
```

### Field Descriptions

- `feasible`: Boolean indicating if the solution is valid
- `optimal`: Boolean indicating if the solution is optimal (false for this problem - we validate feasibility only)
- `num_bins`: Integer count of bins used
- `total_priority_utilization`: Sum of sizes in bins containing at least one high-priority item
- `bins`: Array of bin objects, each containing:
  - `bin_id`: Bin identifier (integer)
  - `items`: Array of item objects with all properties
  - `total_size`: Sum of item sizes in this bin
  - `fragile_count`: Count of fragile items in this bin
  - `is_priority_bin`: Boolean indicating if bin contains any high-priority items
