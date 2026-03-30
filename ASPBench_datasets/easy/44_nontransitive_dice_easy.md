# Problem Statement

Design three six-sided dice (A, B, C) with nontransitive winning properties: A beats B, B beats C, and C beats A, demonstrating a probability paradox where circular dominance exists.

## Instance Data

**Dice configuration:**
- Three dice: A, B, C
- Each die has exactly 6 faces
- Face values must be integers from the set {0, 1, 2, 3, 4, 5, 6}

**Winning criterion:**
- Die X "beats" Die Y if P(X > Y) > 0.5
- Where P(X > Y) is the probability that a random roll of X beats a random roll of Y
- For 6-sided dice, this means winning in more than 18 of the 36 possible face-pair matchups

## Constraints

1. **Each die has exactly 6 faces** with integer values from {0, 1, 2, 3, 4, 5, 6}
2. **A beats B:** P(A > B) > 0.5 (A wins in >18 of 36 matchups)
3. **B beats C:** P(B > C) > 0.5 (B wins in >18 of 36 matchups)
4. **C beats A:** P(C > A) > 0.5 (C wins in >18 of 36 matchups)
5. **All three dominance relationships must hold simultaneously**

## Objective

Find **any valid** assignment of face values to the three dice that satisfies the nontransitive property.

## Output Format

```json
{
  "dice": {
    "A": [1, 2, ...],
    "B": [3, 4, ...],
    "C": [5, 6, ...]
  },
  "win_probabilities": {
    "A_beats_B": 0.556,
    "B_beats_C": 0.583,
    "C_beats_A": 0.611
  }
}
```

**Field descriptions:**
- `dice`: Dictionary mapping die names ("A", "B", "C") to arrays of 6 integers (face values)
- `win_probabilities`: Dictionary containing three keys:
  - `A_beats_B`: Probability that die A beats die B (float between 0 and 1)
  - `B_beats_C`: Probability that die B beats die C (float between 0 and 1)
  - `C_beats_A`: Probability that die C beats die A (float between 0 and 1)
- All three win probabilities must be > 0.5
