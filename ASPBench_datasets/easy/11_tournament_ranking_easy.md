# Problem Statement

Given the results of matches between 5 teams in a round-robin tournament, find the optimal ranking that minimizes violations. A violation occurs when a lower-ranked team beat a higher-ranked team in the final ranking.

## Instance Data

**Teams:** A, B, C, D, E

**Match Results:**
- A beat B
- B beat C
- C beat A (creates a cycle)
- A beat D
- D beat E
- E beat C
- B beat E
- D beat C
- A beat E
- B beat D

Note: This tournament contains cycles (e.g., A→B→C→A), making it impossible to find a ranking with zero violations.

## Constraints

1. **Each team** appears exactly once in the ranking
2. **All teams** must be included in the ranking (5 teams total)
3. A violation is counted when a match beat(X,Y) occurs where Y is ranked higher than X in the final ranking

## Objective

Find a solution that **minimizes** the total number of violations.

**Expected optimal violations:** 1

## Output Format

Output a JSON object with these fields:

```json
{
  "ranking": ["A", "B", ...],
  "violations": 1,
  "valid": true
}
```

Where:
- `ranking`: Ordered list of teams from 1st place to 5th place (exactly 5 teams)
- `violations`: Total number of matches that violate this ranking (minimum possible)
- `valid`: Boolean indicating if the solution is valid (should be true)
