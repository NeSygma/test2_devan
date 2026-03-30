#!/usr/bin/env python3
"""
Reference model for Ecosystem Balance problem.
Validates ecosystem population balance and sustainability.
"""

import json
import sys


def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def validate_solution(solution):
    """Validate the ecosystem balance solution"""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    required_fields = ["stable_populations", "food_web", "ecosystem_health", "balance_achieved"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing field: {field}"}

    populations = solution["stable_populations"]
    expected_species = {"Grass", "Rabbits", "Foxes", "Hawks"}

    # Check all species present
    if set(populations.keys()) != expected_species:
        return {"valid": False, "message": f"Missing species. Expected: {expected_species}, got: {set(populations.keys())}"}

    # Check population values are positive
    for species, pop in populations.items():
        if not isinstance(pop, (int, float)) or pop <= 0:
            return {"valid": False, "message": f"Invalid population for {species}: {pop} (must be positive)"}

    # Check carrying capacity constraints
    carrying_capacity = {"Grass": 100, "Rabbits": 30, "Foxes": 10, "Hawks": 5}
    for species, pop in populations.items():
        if pop > carrying_capacity[species]:
            return {"valid": False, "message": f"Population for {species} exceeds carrying capacity: {pop} > {carrying_capacity[species]}"}

    # Check ecological balance constraints
    if populations["Rabbits"] > populations["Grass"] * 0.5:
        return {"valid": False, "message": "Too many rabbits relative to grass (must be ≤ 0.5 × Grass)"}

    if populations["Foxes"] > populations["Rabbits"] * 0.3:
        return {"valid": False, "message": "Too many foxes relative to rabbits (must be ≤ 0.3 × Rabbits)"}

    # Check food_web structure
    food_web = solution["food_web"]
    if not isinstance(food_web, list):
        return {"valid": False, "message": "food_web must be a list"}

    for relationship in food_web:
        if not all(k in relationship for k in ["predator", "prey", "consumption_rate"]):
            return {"valid": False, "message": f"Invalid food_web relationship: {relationship}"}

        rate = relationship["consumption_rate"]
        if not isinstance(rate, (int, float)) or not (0.1 <= rate <= 0.5):
            return {"valid": False, "message": f"Consumption rate must be between 0.1 and 0.5: {rate}"}

    # Check ecosystem_health structure
    health = solution["ecosystem_health"]
    required_health_fields = ["biodiversity_index", "stability_score", "sustainability"]
    for field in required_health_fields:
        if field not in health:
            return {"valid": False, "message": f"Missing ecosystem_health field: {field}"}

    # Check health metrics are valid
    for metric in ["biodiversity_index", "stability_score"]:
        value = health[metric]
        if not isinstance(value, (int, float)) or not (0 <= value <= 1):
            return {"valid": False, "message": f"{metric} must be between 0 and 1: {value}"}

    if not isinstance(health["sustainability"], bool):
        return {"valid": False, "message": f"sustainability must be boolean: {health['sustainability']}"}

    # Check balance_achieved is boolean
    if not isinstance(solution["balance_achieved"], bool):
        return {"valid": False, "message": f"balance_achieved must be boolean: {solution['balance_achieved']}"}

    return {"valid": True, "message": "Valid ecosystem balance solution"}


def main():
    """Main validation function"""
    solution = load_solution()

    if solution is None:
        result = {"valid": False, "message": "Invalid or missing JSON input"}
    else:
        result = validate_solution(solution)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
