# Problem Statement

You are a player ("Ego") entering a 2-round Prisoners' Dilemma tournament. You must choose a single, fixed strategy to play for the entire tournament. Your opponents are drawn from a known pool with a fixed distribution of strategies. Determine which of your available strategies will yield the highest total expected score when played against the entire pool of opponents.

## Instance Data

**Rounds per game:** 2

**Ego's available strategies:** `COOP`, `DEFECT`, `TFT`

**Opponent Pool Composition (10 opponents total):**
- 5 opponents use strategy `type_A`
- 3 opponents use strategy `type_B`
- 2 opponents use strategy `type_C`

**Payoff Matrix (for Ego):**
- You Cooperate, Opponent Cooperates: 3 points
- You Defect, Opponent Cooperates: 5 points
- You Cooperate, Opponent Defects: 0 points
- You Defect, Opponent Defects: 1 point

**Strategy Definitions:**
- `COOP` (Ego): Always Cooperate ('C')
- `DEFECT` (Ego): Always Defect ('D')
- `TFT` (Ego): Play 'C' in round 1, then copy the opponent's move from the previous round
- `type_A` (Opponent): Always Defect ('D')
- `type_B` (Opponent): Tit-for-Tat. Plays 'C' in round 1, then copies Ego's move from the previous round
- `type_C` (Opponent): Forgiving Tit-for-Tat. Plays 'C' in round 1 and also plays 'C' in round 2, regardless of Ego's round 1 move

## Constraints

1. **Single Strategy Selection**: Ego must choose exactly one strategy for the entire tournament
2. **Fixed Opponent Pool**: The distribution of opponent strategies is fixed (5 type_A, 3 type_B, 2 type_C)
3. **Deterministic Strategies**: All strategies are deterministic and follow their defined behavior
4. **Round Structure**: Each game consists of exactly 2 rounds
5. **Score Calculation**: Expected total score is the sum of scores from all matchups weighted by opponent count

## Objective

Find a solution that **maximizes** the expected total score across all matchups with the opponent pool.

**Expected optimal:** strategy=DEFECT, score=48

## Output Format

The solution must be a JSON object with the following structure:

```json
{
  "best_strategy_choice": "DEFECT",
  "expected_scores": [
    {"strategy": "DEFECT", "expected_total_score": 48},
    {"strategy": "TFT", "expected_total_score": 35},
    {"strategy": "COOP", "expected_total_score": 30}
  ]
}
```

### Field Descriptions

- `best_strategy_choice`: String value representing the optimal strategy choice (one of "COOP", "DEFECT", "TFT")
- `expected_scores`: Array of objects, each containing:
  - `strategy`: String name of the strategy
  - `expected_total_score`: Integer total expected score for that strategy
  - Array must be sorted in descending order by score
