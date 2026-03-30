#!/usr/bin/env python3

import json
import sys

# Expected optimal value
EXPECTED_OPTIMAL_COST = 220

# Hardcoded instance data
INSTANCE_DATA = {
    "drugs": [
        {
            "id": "cardio_ease",
            "name": "CardioEase",
            "treats": ["hypertension"],
            "cost": 50,
            "toxicity": 20,
            "max_dose": 100,
            "contraindications": []
        },
        {
            "id": "metformax",
            "name": "Metformax",
            "treats": ["diabetes"],
            "cost": 40,
            "toxicity": 25,
            "max_dose": 1000,
            "contraindications": [],
            "interactions": [
                {
                    "with": "pain_plus",
                    "effect": "reduced_efficacy",
                    "severity": "moderate"
                }
            ]
        },
        {
            "id": "anxio_calm",
            "name": "AnxioCalm",
            "treats": ["anxiety"],
            "cost": 70,
            "toxicity": 30,
            "max_dose": 50,
            "contraindications": []
        },
        {
            "id": "pain_off",
            "name": "PainOff",
            "treats": ["pain"],
            "cost": 60,
            "toxicity": 15,
            "max_dose": 400,
            "contraindications": []
        },
        {
            "id": "glucopain",
            "name": "Glucopain",
            "treats": ["diabetes", "pain"],
            "cost": 110,
            "toxicity": 40,
            "max_dose": 600,
            "contraindications": [
                {
                    "type": "genetic",
                    "marker": "G6PD_deficiency"
                }
            ]
        },
        {
            "id": "hydro_stress",
            "name": "HydroStress",
            "treats": ["hypertension", "anxiety"],
            "cost": 90,
            "toxicity": 35,
            "max_dose": 200,
            "contraindications": [],
            "interactions": [
                {
                    "with": "metformax",
                    "effect": "risk_of_lactic_acidosis",
                    "severity": "severe",
                    "requires_condition": "diabetes"
                }
            ]
        },
        {
            "id": "renal_guard",
            "name": "RenalGuard",
            "treats": ["hypertension"],
            "cost": 120,
            "toxicity": 10,
            "max_dose": 150,
            "contraindications": [
                {
                    "type": "standard",
                    "condition": "renal_failure"
                }
            ]
        },
        {
            "id": "pain_plus",
            "name": "PainPlus",
            "treats": ["pain"],
            "cost": 80,
            "toxicity": 25,
            "max_dose": 300,
            "contraindications": [],
            "synergies": [
                {
                    "with": "anxio_calm",
                    "for_condition": "anxiety",
                    "efficacy_bonus": 2
                }
            ]
        }
    ],
    "patient": {
        "conditions": ["hypertension", "diabetes", "anxiety", "pain"],
        "contraindications": ["renal_failure"],
        "genetic_markers": ["G6PD_deficiency"],
        "max_drugs": 4,
        "max_budget": 250,
        "max_total_toxicity": 100
    }
}

def validate_solution(instance_data, solution_data):
    """Validate the drug interaction analysis solution."""

    try:
        # Extract input data
        drugs = {d["id"]: d for d in instance_data["drugs"]}
        patient = instance_data["patient"]
        patient_conditions = set(patient["conditions"])
        patient_contraindications = set(patient.get("contraindications", []))
        patient_genetic_markers = set(patient.get("genetic_markers", []))
        max_drugs = patient["max_drugs"]
        max_budget = patient["max_budget"]
        max_total_toxicity = patient["max_total_toxicity"]

        # Extract solution
        prescribed_drugs = solution_data.get("prescribed_drugs", [])
        treated_conditions = set(solution_data.get("treated_conditions", []))
        untreated_conditions = set(solution_data.get("untreated_conditions", []))
        total_cost = solution_data.get("total_cost", 0)
        total_toxicity = solution_data.get("total_toxicity", 0)
        safety_analysis = solution_data.get("safety_analysis", {})

        # Validate prescription count
        if len(prescribed_drugs) > max_drugs:
            return False, f"Too many drugs prescribed: {len(prescribed_drugs)} > {max_drugs}"

        prescribed_drug_ids = set()
        total_conditions_treated = set()
        actual_total_cost = 0
        actual_total_toxicity = 0

        # Validate each prescribed drug
        for prescription in prescribed_drugs:
            drug_id = prescription["drug_id"]
            if drug_id not in drugs:
                return False, f"Unknown drug: {drug_id}"
            if drug_id in prescribed_drug_ids:
                return False, f"Drug {drug_id} prescribed multiple times"
            prescribed_drug_ids.add(drug_id)

            drug = drugs[drug_id]
            actual_total_cost += drug.get("cost", 0)
            actual_total_toxicity += drug.get("toxicity", 0)

            # Check contraindications
            for contra in drug.get("contraindications", []):
                if contra.get("type") == "standard" and contra.get("condition") in patient_contraindications:
                    return False, f"Drug {drug_id} violates standard contraindication: {contra.get('condition')}"
                if contra.get("type") == "genetic" and contra.get("marker") in patient_genetic_markers:
                    return False, f"Drug {drug_id} violates genetic contraindication: {contra.get('marker')}"

            total_conditions_treated.update(drug.get("treats", []))

        # Validate aggregate values
        if total_cost != actual_total_cost:
            return False, f"Total cost mismatch. Expected: {actual_total_cost}, Got: {total_cost}"
        if total_toxicity != actual_total_toxicity:
            return False, f"Total toxicity mismatch. Expected: {actual_total_toxicity}, Got: {total_toxicity}"
        if actual_total_cost > max_budget:
            return False, f"Budget exceeded: {actual_total_cost} > {max_budget}"
        if actual_total_toxicity > max_total_toxicity:
            return False, f"Toxicity exceeded: {actual_total_toxicity} > {max_total_toxicity}"

        # Validate condition coverage
        if treated_conditions != (total_conditions_treated & patient_conditions):
            return False, f"Treated conditions mismatch. Expected: {sorted(list(total_conditions_treated & patient_conditions))}, Got: {sorted(list(treated_conditions))}"

        expected_untreated = patient_conditions - treated_conditions
        if untreated_conditions != expected_untreated:
            return False, f"Untreated conditions mismatch. Expected: {sorted(list(expected_untreated))}, Got: {sorted(list(untreated_conditions))}"

        # Validate safety analysis: Interactions
        interactions_detected = safety_analysis.get("interactions_detected", [])
        expected_interactions = []
        prescribed_list = list(prescribed_drug_ids)

        for i in range(len(prescribed_list)):
            for j in range(i + 1, len(prescribed_list)):
                d1_id, d2_id = prescribed_list[i], prescribed_list[j]
                d1, d2 = drugs[d1_id], drugs[d2_id]

                all_interactions = d1.get("interactions", []) + d2.get("interactions", [])
                for interaction in all_interactions:
                    partners = {d1_id, d2_id}
                    if interaction["with"] in partners:
                        # Check for conditional interactions
                        req_cond = interaction.get("requires_condition")
                        if req_cond and req_cond not in patient_conditions:
                            continue # Interaction is not active

                        # Avoid duplicates
                        current_interaction = {
                            "drugs": sorted([d1_id, d2_id]),
                            "interaction": interaction["effect"],
                            "severity": interaction["severity"]
                        }
                        if current_interaction not in expected_interactions:
                            expected_interactions.append(current_interaction)

        # Normalize and compare interactions
        normalized_detected = sorted([
            {k: tuple(sorted(v)) if k == 'drugs' else v for k, v in item.items()}
            for item in interactions_detected
        ], key=lambda x: (x['drugs'], x['interaction']))
        normalized_expected = sorted([
            {k: tuple(v) if k == 'drugs' else v for k, v in item.items()}
            for item in expected_interactions
        ], key=lambda x: (x['drugs'], x['interaction']))

        if normalized_detected != normalized_expected:
             return False, f"Interaction detection mismatch. Expected: {expected_interactions}, Got: {interactions_detected}"

        # Check optimality
        if total_cost != EXPECTED_OPTIMAL_COST:
            return False, f"Not optimal: total_cost={total_cost}, expected {EXPECTED_OPTIMAL_COST}"

        return True, f"Solution valid and optimal (total_cost={EXPECTED_OPTIMAL_COST})"

    except Exception as e:
        return False, f"Validation error: {str(e)}"

def main():
    """Main entry point - reads solution from stdin and validates against hardcoded instance."""
    try:
        solution_json = sys.stdin.read().strip()
        if not solution_json:
            print(json.dumps({"valid": False, "message": "No solution provided"}))
            sys.exit(1)

        solution_data = json.loads(solution_json)
        is_valid, message = validate_solution(INSTANCE_DATA, solution_data)

        result = {
            "valid": is_valid,
            "message": message
        }

        print(json.dumps(result))

    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Unexpected error: {e}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
