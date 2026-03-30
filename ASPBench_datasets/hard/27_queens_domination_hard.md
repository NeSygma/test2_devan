# Problem Statement

Find the minimum number of queens required to dominate every square on a 9×9 chessboard. A queen dominates all squares in the same row, column, and diagonals (both directions).

## Instance Data

- Board size: 9×9 (rows 0-8, columns 0-8)
- Total squares: 81

## Constraints

1. **Each queen** occupies exactly one square on the board
2. **No restrictions** on queen placement (queens may attack each other)
3. **All 81 squares** must be dominated by at least one queen
4. A square is **dominated** if it lies in the same row, column, or diagonal as a queen
5. A queen **dominates itself** (the square it occupies)

## Objective

Find a solution that **minimizes** the number of queens placed on the board.

**Expected optimal value:** 5 queens

## Output Format

The solution must be a JSON object with the following structure:

```json
{
  "queens": [
    [1, 1],
    [3, 2],
    [7, 3],
    [2, 6],
    [6, 7]
  ]
}
```

### Field Descriptions

- `queens`: Array of queen positions, where each position is `[row, col]` with both row and col in range 0-8
