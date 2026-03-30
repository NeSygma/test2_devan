#!/usr/bin/env python3
"""
Reference model for Ecosystem Balance problem.
Validates a 16-state ecosystem model against 5 ecological constraints.
"""
import json
import sys
from collections import defaultdict

def load_solution():
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return None

def validate_solution(sol):
    if not sol or "population_levels" not in sol:
        return False, "Invalid or missing 'population_levels' field."

    levels = sol["population_levels"]
    if not isinstance(levels, list) or len(levels) != 16:
        return False, f"Expected 'population_levels' to be a list of 16 items, but got {len(levels)}."

    # Convert list to a dictionary for easy lookup: (species, zone, season) -> level
    pop_map = {}
    all_species = {"Grass", "Rabbits", "Foxes", "Hawks"}
    for item in levels:
        try:
            key = (item["species"], item["zone"], item["season"])
            if key in pop_map:
                return False, f"Duplicate state found: {key}"
            pop_map[key] = item["level"]
        except KeyError as e:
            return False, f"Missing key {e} in population entry."

    # Rule C1: Carrying Capacity
    if pop_map.get(("Grass", "Forest", "Summer"), -1) > 1 or pop_map.get(("Grass", "Forest", "Winter"), -1) > 1:
        return False, "C1 Violation: Grass level in Forest cannot exceed 1."
    if pop_map.get(("Foxes", "Meadow", "Summer"), -1) > 0 or pop_map.get(("Foxes", "Meadow", "Winter"), -1) > 0:
        return False, "C1 Violation: Foxes level in Meadow must be 0."
    for s in ["Summer", "Winter"]:
        for z in ["Forest", "Meadow"]:
            if pop_map.get(("Hawks", z, s), -1) > 1:
                return False, f"C1 Violation: Hawks level cannot exceed 1, but was {pop_map[('Hawks',z,s)]} in {z},{s}."

    # Rule C2: Winter Scarcity
    for z in ["Forest", "Meadow"]:
        if pop_map.get(("Grass", z, "Winter"), -1) > 1:
            return False, f"C2 Violation: Grass level in Winter cannot exceed 1."
        if pop_map.get(("Rabbits", z, "Winter"), -1) > 1:
            return False, f"C2 Violation: Rabbits level in Winter cannot be 2."

    # Rule C3: Predator-Prey Balance
    eats = {"Rabbits": "Grass", "Foxes": "Rabbits", "Hawks": "Foxes"}
    for pred, prey in eats.items():
        for z in ["Forest", "Meadow"]:
            for s in ["Summer", "Winter"]:
                pred_level = pop_map.get((pred, z, s), -1)
                prey_level = pop_map.get((prey, z, s), -1)
                if pred_level > prey_level:
                    return False, f"C3 Violation: {pred} level ({pred_level}) > {prey} level ({prey_level}) in {z}, {s}."

    # Rule C4 & C5: Sums
    species_sums = defaultdict(int)
    for (species, _, _), level in pop_map.items():
        species_sums[species] += level

    # Rule C4: Biodiversity
    for species in all_species:
        if species_sums.get(species, 0) < 1:
            return False, f"C4 Violation: Total population for {species} is less than 1."

    # Rule C5: Hawk Population
    if species_sums.get("Hawks", 0) != 2:
        return False, f"C5 Violation: Total Hawks population must be 2, but was {species_sums.get('Hawks', 0)}."

    return True, "Solution is valid."

def main():
    solution = load_solution()
    if solution is None:
        print(json.dumps({"valid": False, "message": "Invalid JSON input."}))
        return

    is_valid, message = validate_solution(solution)
    print(json.dumps({"valid": is_valid, "message": message}))

if __name__ == "__main__":
    main()
