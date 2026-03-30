# Problem Statement

Solve the cryptarithmetic puzzle SEND + MORE = MONEY where each letter represents a unique digit.

## Instance Data

The puzzle is: **SEND + MORE = MONEY**

Letters involved: S, E, N, D, M, O, R, Y (8 unique letters)

Each letter must be assigned a digit from 0-9, and all letters must have different digits.

## Constraints

1. **Unique Digits:** Each of the 8 unique letters (S, E, N, D, M, O, R, Y) must be assigned a different digit from 0-9.
2. **Leading Zeros:** The leading letters of the numbers (S and M) cannot be assigned the digit 0.
3. **Arithmetic Correctness:** The assignment of digits to letters must satisfy the following columnar addition:
   ```
     S E N D
   + M O R E
   ---------
   = M O N E Y
   ```

## Objective

Find the unique assignment of digits to letters that satisfies all constraints.

## Output Format

```json
{
  "assignment": {
    "S": <digit>,
    "E": <digit>,
    "N": <digit>,
    "D": <digit>,
    "M": <digit>,
    "O": <digit>,
    "R": <digit>,
    "Y": <digit>
  },
  "equation": "SEND + MORE = MONEY becomes <numeric_equation>",
  "valid": true
}
```

**Field Descriptions:**
- `assignment`: Dictionary mapping each letter to its assigned digit (0-9)
- `equation`: String showing the substituted numeric equation (e.g., "9567 + 1085 = 10652")
- `valid`: Boolean indicating if the solution satisfies all constraints
