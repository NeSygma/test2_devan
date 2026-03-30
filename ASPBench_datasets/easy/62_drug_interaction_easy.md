# Problem Statement

Analyze pharmaceutical safety by determining safe drug combinations for patients with multiple conditions. Given a patient's medical conditions and contraindications, along with available drugs and their properties, find an optimal prescription that treats the patient's conditions while avoiding dangerous drug interactions and respecting contraindications.

## Instance Data

**Patient:**
- Conditions: pain, hypertension, diabetes
- Contraindications: bleeding_disorder
- Maximum drugs allowed: 3

**Available Drugs:**

1. **drug1** (Aspirin - display name only)
   - Drug ID: `drug1`
   - Treats: pain, inflammation
   - Contraindications: bleeding_disorder
   - Max dose: 4000 mg
   - Interactions: with drug2 (increased_bleeding, moderate severity)

2. **drug2** (Warfarin - display name only)
   - Drug ID: `drug2`
   - Treats: blood_clot_prevention
   - Contraindications: pregnancy
   - Max dose: 10 mg
   - Interactions: with drug1 (increased_bleeding, moderate severity)

3. **drug3** (Lisinopril - display name only)
   - Drug ID: `drug3`
   - Treats: hypertension
   - Contraindications: kidney_disease
   - Max dose: 40 mg
   - Interactions: with drug4 (mild_nausea, mild severity)

4. **drug4** (Metformin - display name only)
   - Drug ID: `drug4`
   - Treats: diabetes
   - Contraindications: kidney_disease
   - Max dose: 2000 mg
   - Interactions: with drug3 (mild_nausea, mild severity)

5. **drug5** (Ibuprofen - display name only)
   - Drug ID: `drug5`
   - Treats: pain, inflammation
   - Contraindications: none
   - Max dose: 2400 mg
   - Interactions: with drug3 (reduced_bp_effect, moderate severity)

**Important:** Use drug IDs (`drug1`, `drug2`, etc.) in all outputs, not display names (Aspirin, Warfarin, etc.).

## Constraints

1. **Maximum drugs**: Select **no more than** the patient's maximum allowed drugs (3 in this instance).
2. **Contraindications**: **Cannot** prescribe drugs that match any of the patient's contraindications.
3. **Dosage**: Each prescribed drug **must** have a dose between 1 and the drug's max_dose.
4. **Treatment coverage**: A condition is treated if **at least one** prescribed drug treats that condition.

## Objective

Find a prescription that **maximizes** the number of treated patient conditions while **minimizing** the severity of drug interactions (severe > moderate > mild).

Expected optimal solution: Prescribes 2 drugs (Metformin and Ibuprofen) treating 2 conditions (diabetes and pain) with total interaction cost = 0.

## Output Format

```json
{
  "prescribed_drugs": [
    {"drug_id": "...", "dose": 1000, "frequency": "twice_daily"},
    ...
  ],
  "treated_conditions": ["...", ...],
  "untreated_conditions": ["...", ...],
  "safety_analysis": {
    "interactions_detected": [
      {"drugs": ["...", "..."], "interaction": "...", "severity": "..."},
      ...
    ],
    "contraindications_avoided": ["...", ...],
    "safety_score": 0.85
  }
}
```

**Field Descriptions:**
- `prescribed_drugs`: List of prescribed drugs with `drug_id` (use drug IDs like "drug1", "drug4", not display names), dose (mg), and frequency
- `treated_conditions`: List of patient conditions that are treated by at least one prescribed drug
- `untreated_conditions`: List of patient conditions not covered by any prescribed drug
- `safety_analysis.interactions_detected`: List of all pairwise interactions between prescribed drugs (use drug IDs in the `drugs` array)
- `safety_analysis.contraindications_avoided`: List of patient contraindications (informational)
- `safety_analysis.safety_score`: Float in [0, 1] indicating overall safety (higher is safer)

**Safety Score Calculation:**
The `safety_score` is calculated using the following formula:

```
safety_score = 0.5 + coverage_bonus - total_penalty
```

Where:
- Base safety score: `0.5`
- Coverage bonus: `(treated_conditions / total_conditions) * 0.5`
  - Example: If 3 out of 3 conditions are treated: `(3/3) * 0.5 = 0.5`
  - Example: If 2 out of 3 conditions are treated: `(2/3) * 0.5 ≈ 0.33`
- Total penalty: Sum of interaction penalties for all detected interactions:
  - `severe` interaction: `-0.3` per interaction
  - `moderate` interaction: `-0.15` per interaction
  - `mild` interaction: `-0.05` per interaction

The final `safety_score` is clamped to the range [0, 1].

**Example:** If a prescription treats all 3 conditions and has 1 moderate interaction:
- `safety_score = 0.5 + 0.5 - 0.15 = 0.85`

**Important:** The `drug_id` field must contain the drug identifier (e.g., "drug1", "drug4"), NOT the display name (e.g., "Aspirin", "Metformin").
