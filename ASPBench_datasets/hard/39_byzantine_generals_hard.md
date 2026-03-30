# Problem Statement

In the Byzantine Generals problem with hierarchy and deception, a group of generals must reach consensus on a binary decision despite some being traitors. The system features a command hierarchy where generals have different ranks, a trust network providing bonus weights to trusted relationships, and specific deception rules where traitors lie strategically based on rank comparisons. Your task is to determine which generals are traitors and find the final consensus value that all honest generals agree upon after two rounds of message exchange.

## Instance Data

**Generals and Ranks:**
- G1: commander (weight: 3, order: 3)
- G2: lieutenant (weight: 2, order: 2)
- G3: lieutenant (weight: 2, order: 2)
- G4: sergeant (weight: 1, order: 1)
- G5: sergeant (weight: 1, order: 1)
- G6: sergeant (weight: 1, order: 1)

**Initial Proposals (Round 0):**
- G1: 1
- G2: 1
- G3: 0
- G4: 0
- G5: 1
- G6: 1

**Trust Network:**
- High trust pairs: (G1, G2), (G2, G1)
- Trust bonus: +1 weight

**Protocol Parameters:**
- Number of traitors: exactly 2
- Number of rounds: 2
- Tie-breaking rule: defaults to 0

## Constraints

1. **Traitor identification**: Exactly **2 generals** must be identified as traitors
2. **Message passing**: In each round, every general sends their current belief to every other general
3. **Honest behavior**: Honest generals always send their true belief from the previous round
4. **Traitor deception**: Traitors send lies (opposite of their belief) to generals of equal or lower rank, but send truth to higher-ranked generals
5. **Belief update**: Honest generals update their belief based on **weighted majority** of received messages
6. **Trust weighting**: Messages from trusted generals receive the rank weight plus trust bonus
7. **Consensus requirement**: All honest generals must agree on the **same final value** after the final round

## Objective

Identify the two traitors and determine the consensus value that all honest generals agree upon after two rounds of message exchange.

## Output Format

```json
{
  "consensus_value": 1,
  "final_beliefs": [
    {"general": "G1", "belief": 1},
    {"general": "G2", "belief": 1},
    {"general": "G5", "belief": 1},
    {"general": "G6", "belief": 1}
  ]
}
```

**Field Descriptions:**
- `consensus_value`: The binary value (0 or 1) that all honest generals agree upon
- `final_beliefs`: Array of belief objects for each honest general after the final round
  - `general`: Name of the general (e.g., "G1", "G2", etc.)
  - `belief`: The general's final belief value (0 or 1)

**Note:** Only honest generals appear in `final_beliefs`. The list should contain exactly 4 generals (6 total - 2 traitors = 4 honest).
