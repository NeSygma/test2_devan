#!/usr/bin/env python3
"""
Reference model for Drug Interaction Analysis (Easy)
Validates solution from stdin and checks optimality.
"""

import json
import sys

# Expected optimal values
EXPECTED_OPTIMAL_CONDITIONS_TREATED = 2
EXPECTED_OPTIMAL_INTERACTION_COST = 0

def validate_solution(solution_data):
    """Validate the drug interaction analysis solution."""

    # Instance data (must match the problem specification)
    instance_data = {
        "drugs": [
            {
                "id": "drug1",
                "name": "Aspirin",
                "treats": ["pain", "inflammation"],
                "contraindications": ["bleeding_disorder"],
                "max_dose": 4000,
                "interactions": [
                    {"with": "drug2", "effect": "increased_bleeding", "severity": "moderate"}
                ]
            },
            {
                "id": "drug2",
                "name": "Warfarin",
                "treats": ["blood_clot_prevention"],
                "contraindications": ["pregnancy"],
                "max_dose": 10,
                "interactions": [
                    {"with": "drug1", "effect": "increased_bleeding", "severity": "moderate"}
                ]
            },
            {
                "id": "drug3",
                "name": "Lisinopril",
                "treats": ["hypertension"],
                "contraindications": ["kidney_disease"],
                "max_dose": 40,
                "interactions": [
                    {"with": "drug4", "effect": "mild_nausea", "severity": "mild"}
                ]
            },
            {
                "id": "drug4",
                "name": "Metformin",
                "treats": ["diabetes"],
                "contraindications": ["kidney_disease"],
                "max_dose": 2000,
                "interactions": [
                    {"with": "drug3", "effect": "mild_nausea", "severity": "mild"}
                ]
            },
            {
                "id": "drug5",
                "name": "Ibuprofen",
                "treats": ["pain", "inflammation"],
                "contraindications": [],
                "max_dose": 2400,
                "interactions": [
                    {"with": "drug3", "effect": "reduced_bp_effect", "severity": "moderate"}
                ]
            }
        ],
        "patient": {
            "conditions": ["pain", "hypertension", "diabetes"],
            "contraindications": ["bleeding_disorder"],
            "max_drugs": 3
        }
    }

    try:
        # Extract input data
        drugs = {d["id"]: d for d in instance_data["drugs"]}
        patient = instance_data["patient"]
        patient_conditions = set(patient["conditions"])
        patient_contraindications = set(patient["contraindications"])
        max_drugs = patient["max_drugs"]

        # Extract solution
        prescribed_drugs = solution_data.get("prescribed_drugs", [])
        treated_conditions = set(solution_data.get("treated_conditions", []))
        untreated_conditions = set(solution_data.get("untreated_conditions", []))
        safety_analysis = solution_data.get("safety_analysis", {})

        # Validate prescription count
        if len(prescribed_drugs) > max_drugs:
            return {"valid": False, "message": f"Too many drugs prescribed: {len(prescribed_drugs)} > {max_drugs}"}

        prescribed_drug_ids = set()
        total_conditions_treated = set()

        # Validate each prescribed drug
        for prescription in prescribed_drugs:
            drug_id = prescription["drug_id"]
            dose = prescription["dose"]

            if drug_id not in drugs:
                return {"valid": False, "message": f"Unknown drug: {drug_id}"}

            if drug_id in prescribed_drug_ids:
                return {"valid": False, "message": f"Drug {drug_id} prescribed multiple times"}

            prescribed_drug_ids.add(drug_id)

            drug = drugs[drug_id]

            # Validate dose
            if dose <= 0 or dose > drug["max_dose"]:
                return {"valid": False, "message": f"Invalid dose for {drug_id}: {dose} (max: {drug['max_dose']})"}

            # Check contraindications
            drug_contraindications = set(drug.get("contraindications", []))
            violated_contraindications = drug_contraindications & patient_contraindications
            if violated_contraindications:
                return {"valid": False, "message": f"Drug {drug_id} violates contraindications: {violated_contraindications}"}

            # Add treated conditions
            total_conditions_treated.update(drug.get("treats", []))

        # Validate condition coverage
        if treated_conditions != (total_conditions_treated & patient_conditions):
            return {"valid": False, "message": f"Treated conditions mismatch. Expected: {total_conditions_treated & patient_conditions}, Got: {treated_conditions}"}

        expected_untreated = patient_conditions - treated_conditions
        if untreated_conditions != expected_untreated:
            return {"valid": False, "message": f"Untreated conditions mismatch. Expected: {expected_untreated}, Got: {untreated_conditions}"}

        # Validate safety analysis
        interactions_detected = safety_analysis.get("interactions_detected", [])

        # Check for all pairwise interactions
        expected_interactions = []
        prescribed_list = list(prescribed_drug_ids)

        for i in range(len(prescribed_list)):
            for j in range(i + 1, len(prescribed_list)):
                drug1_id, drug2_id = prescribed_list[i], prescribed_list[j]
                drug1, drug2 = drugs[drug1_id], drugs[drug2_id]

                # Check interactions from drug1 to drug2
                for interaction in drug1.get("interactions", []):
                    if interaction["with"] == drug2_id:
                        expected_interactions.append({
                            "drugs": sorted([drug1_id, drug2_id]),
                            "interaction": interaction["effect"],
                            "severity": interaction["severity"]
                        })

                # Check interactions from drug2 to drug1
                for interaction in drug2.get("interactions", []):
                    if interaction["with"] == drug1_id:
                        # Avoid duplicates
                        interaction_key = (sorted([drug1_id, drug2_id]), interaction["effect"])
                        found_duplicate = False
                        for existing in expected_interactions:
                            if (existing["drugs"] == sorted([drug1_id, drug2_id]) and
                                existing["interaction"] == interaction["effect"]):
                                found_duplicate = True
                                break
                        if not found_duplicate:
                            expected_interactions.append({
                                "drugs": sorted([drug1_id, drug2_id]),
                                "interaction": interaction["effect"],
                                "severity": interaction["severity"]
                            })

        # Normalize detected interactions
        normalized_detected = []
        for interaction in interactions_detected:
            normalized_detected.append({
                "drugs": sorted(interaction["drugs"]),
                "interaction": interaction["interaction"],
                "severity": interaction["severity"]
            })

        # Sort for comparison
        expected_interactions.sort(key=lambda x: (x["drugs"], x["interaction"]))
        normalized_detected.sort(key=lambda x: (x["drugs"], x["interaction"]))

        if normalized_detected != expected_interactions:
            return {"valid": False, "message": f"Interaction detection mismatch. Expected: {expected_interactions}, Got: {normalized_detected}"}

        # Validate contraindications avoided
        contraindications_avoided = set(safety_analysis.get("contraindications_avoided", []))
        if contraindications_avoided != patient_contraindications:
            return {"valid": False, "message": f"Contraindications avoided mismatch. Expected: {patient_contraindications}, Got: {contraindications_avoided}"}

        # Validate safety score (should be between 0 and 1)
        safety_score = safety_analysis.get("safety_score", 0)
        if not (0 <= safety_score <= 1):
            return {"valid": False, "message": f"Invalid safety score: {safety_score} (must be 0-1)"}

        # Check safety score calculation logic (simplified)
        # Lower score for more severe interactions, higher for more conditions treated
        severity_penalties = {"mild": 0.05, "moderate": 0.15, "severe": 0.3}
        total_penalty = sum(severity_penalties.get(interaction["severity"], 0.1)
                          for interaction in interactions_detected)

        coverage_bonus = len(treated_conditions) / len(patient_conditions) * 0.5
        expected_score = max(0, min(1, 0.5 + coverage_bonus - total_penalty))

        # Allow some tolerance in safety score calculation
        if abs(safety_score - expected_score) > 0.1:
            return {"valid": False, "message": f"Safety score seems incorrect. Expected ~{expected_score:.2f}, got {safety_score}"}

        # Calculate interaction cost for optimality check
        severity_costs = {"mild": 1, "moderate": 2, "severe": 3}
        total_cost = sum(severity_costs.get(interaction["severity"], 0)
                        for interaction in interactions_detected)

        # Check optimality
        if len(treated_conditions) != EXPECTED_OPTIMAL_CONDITIONS_TREATED:
            return {"valid": False, "message": f"Not optimal: treated_conditions={len(treated_conditions)}, expected {EXPECTED_OPTIMAL_CONDITIONS_TREATED}"}
        if total_cost != EXPECTED_OPTIMAL_INTERACTION_COST:
            return {"valid": False, "message": f"Not optimal: interaction_cost={total_cost}, expected {EXPECTED_OPTIMAL_INTERACTION_COST}"}

        return {"valid": True, "message": f"Solution is valid and optimal (treats {EXPECTED_OPTIMAL_CONDITIONS_TREATED} conditions with interaction_cost={EXPECTED_OPTIMAL_INTERACTION_COST})"}

    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}

def main():
    # Read solution from stdin
    try:
        data = sys.stdin.read().strip()
        if not data:
            print(json.dumps({"valid": False, "message": "No solution provided"}))
            sys.exit(1)

        solution_data = json.loads(data)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)

    result = validate_solution(solution_data)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
