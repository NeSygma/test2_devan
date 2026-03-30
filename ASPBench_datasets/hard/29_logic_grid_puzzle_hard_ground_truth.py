#!/usr/bin/env python3

import json
import sys

def validate_solution(solution_str):
    """Validate the logic grid puzzle solution."""
    try:
        data = json.loads(solution_str)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    if "assignments" not in data:
        return {"valid": False, "message": "Missing 'assignments' key."}

    assignments = data["assignments"]
    if not isinstance(assignments, list) or len(assignments) != 5:
        return {"valid": False, "message": f"Expected 'assignments' to be a list of 5 objects, got {len(assignments)}."}

    # Define domains
    PEOPLE = {"Evelyn", "Frank", "Grace", "Henry", "Iris"}
    LOCATIONS = {"Library", "Park", "Cafe", "Museum", "Studio"}
    HOBBIES = {"Painting", "Coding", "Gardening", "Baking", "Sculpting"}
    SNACKS = {"Apple", "Muffin", "Nuts", "Yogurt", "Tea"}
    PROJECTS = {"A", "B", "C", "D", "E"}

    # Check for uniqueness and valid values
    used_people, used_locs, used_hobbies, used_snacks, used_projs = set(), set(), set(), set(), set()
    for asn in assignments:
        for field in ["person", "location", "hobby", "snack", "project"]:
            if field not in asn:
                return {"valid": False, "message": f"Assignment missing field: {field}"}
        used_people.add(asn["person"])
        used_locs.add(asn["location"])
        used_hobbies.add(asn["hobby"])
        used_snacks.add(asn["snack"])
        used_projs.add(asn["project"])

    if used_people != PEOPLE:
        return {"valid": False, "message": f"People not uniquely assigned. Expected {PEOPLE}, got {used_people}"}
    if used_locs != LOCATIONS:
        return {"valid": False, "message": f"Locations not uniquely assigned. Expected {LOCATIONS}, got {used_locs}"}
    if used_hobbies != HOBBIES:
        return {"valid": False, "message": f"Hobbies not uniquely assigned. Expected {HOBBIES}, got {used_hobbies}"}
    if used_snacks != SNACKS:
        return {"valid": False, "message": f"Snacks not uniquely assigned. Expected {SNACKS}, got {used_snacks}"}
    if used_projs != PROJECTS:
        return {"valid": False, "message": f"Projects not uniquely assigned. Expected {PROJECTS}, got {used_projs}"}

    # Create maps for easy constraint checking
    person_map = {a['person']: a for a in assignments}
    hobby_map = {a['hobby']: a for a in assignments}
    location_map = {a['location']: a for a in assignments}
    snack_map = {a['snack']: a for a in assignments}
    project_map = {a['project']: a for a in assignments}

    # --- Check all 11 clues ---

    # 1. Coder's location is alphabetically before Gardener's location.
    if hobby_map["Coding"]["location"] >= hobby_map["Gardening"]["location"]:
        return {"valid": False, "message": "Clue 1 violated: Coder's location must be before Gardener's."}

    # 2. If hobby is not Painting, snack is not Apple.
    for p in PEOPLE:
        if person_map[p]["hobby"] != "Painting" and person_map[p]["snack"] == "Apple":
            return {"valid": False, "message": f"Clue 2 violated: {p} has a non-Painting hobby but snack is Apple."}

    # 3. Exactly 2 hobbies start with 'S' or 'C'.
    sc_hobbies_count = sum(1 for h in HOBBIES if h.startswith('S') or h.startswith('C'))
    if sc_hobbies_count != 2:
         # This is a check on the problem spec itself, but we can validate the solution has these hobbies assigned.
        count = sum(1 for a in assignments if a['hobby'].startswith('S') or a['hobby'].startswith('C'))
        if count != 2:
             return {"valid": False, "message": f"Clue 3 violated: Found {count} hobbies starting with S/C, expected 2."}

    # 4. Henry works on Project D.
    if person_map["Henry"]["project"] != "D":
        return {"valid": False, "message": "Clue 4 violated: Henry must work on Project D."}

    # 5. Person in Museum does not eat Nuts.
    if location_map["Museum"]["snack"] == "Nuts":
        return {"valid": False, "message": "Clue 5 violated: Person in Museum cannot eat Nuts."}

    # 6. Project E's location is after Project A's location.
    if project_map["E"]["location"] <= project_map["A"]["location"]:
        return {"valid": False, "message": "Clue 6 violated: Project E's location must be alphabetically after Project A's."}

    # 7. Baker's project is after Park person's project.
    if hobby_map["Baking"]["project"] <= location_map["Park"]["project"]:
        return {"valid": False, "message": "Clue 7 violated: Baker's project must be after Park person's project."}

    # 8. Frank is at the Cafe.
    if person_map["Frank"]["location"] != "Cafe":
        return {"valid": False, "message": "Clue 8 violated: Frank must be at the Cafe."}

    # 9. Evelyn does not enjoy Gardening.
    if person_map["Evelyn"]["hobby"] == "Gardening":
        return {"valid": False, "message": "Clue 9 violated: Evelyn cannot enjoy Gardening."}

    # 10. Alphabetical distance of projects for Muffin-eater and Sculptor is 2.
    proj_muffin = snack_map["Muffin"]["project"]
    proj_sculpting = hobby_map["Sculpting"]["project"]
    if abs(ord(proj_muffin) - ord(proj_sculpting)) != 2:
        return {"valid": False, "message": "Clue 10 violated: Project distance between Muffin-eater and Sculptor must be 2."}

    # 11. Sum of compatibility scores is 15.
    compat_scores = {
        ("Painting", "Apple"): 3, ("Coding", "Muffin"): 5, ("Gardening", "Nuts"): 2,
        ("Baking", "Yogurt"): 4, ("Sculpting", "Tea"): 1
    }
    total_score = sum(compat_scores.get((a["hobby"], a["snack"]), 0) for a in assignments)
    if total_score != 15:
        return {"valid": False, "message": f"Clue 11 violated: Total compatibility score is {total_score}, should be 15."}

    return {"valid": True, "message": "Solution is valid."}

if __name__ == "__main__":
    solution_str = sys.stdin.read()
    result = validate_solution(solution_str)
    print(json.dumps(result))
