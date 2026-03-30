# Problem Statement

The Byzantine Generals Problem models achieving consensus among distributed nodes when some nodes may exhibit arbitrary (Byzantine) failures. The goal is to have all honest nodes agree on a common decision value despite the presence of faulty or malicious nodes.

## Instance Data

**Generals:** 4 generals (G1, G2, G3, G4)

**Initial Proposals:**
- G1: 1
- G2: 1
- G3: 0
- G4: 1

**Traitor:** G4 (can send different messages to different generals)

**Fault Tolerance:** System can handle at most 1 traitor among 4 generals

## Constraints

1. **Agreement:** All honest generals **must** decide on the same value
2. **Validity:** If all honest generals have the same initial value, that **must** be the consensus
3. **Majority Rule:** The consensus should reflect the majority vote among honest generals
4. **Tie-Breaking:** In case of a tie among honest votes, use value 0 as the default

## Objective

Determine the consensus value that honest generals should adopt.

## Output Format

```json
{
  "consensus": 1,
  "honest_generals": ["G1", "G2", ...],
  "traitor": "G4"
}
```

**Field Descriptions:**
- `consensus`: The agreed-upon decision value (0 or 1)
- `honest_generals`: List of non-traitor generals
- `traitor`: The Byzantine (faulty) general
