#!/usr/bin/env python3

import json
import sys

def validate_solution(solution):
    """Validate a logic grid puzzle solution."""

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    if "assignments" not in solution:
        return {"valid": False, "message": "Missing 'assignments' key"}

    assignments = solution["assignments"]

    if len(assignments) != 4:
        return {"valid": False, "message": f"Expected 4 assignments, got {len(assignments)}"}

    # Check required fields
    required_fields = ["person", "color", "pet", "house"]
    for i, assignment in enumerate(assignments):
        for field in required_fields:
            if field not in assignment:
                return {"valid": False, "message": f"Assignment {i+1} missing '{field}' field"}

    # Check valid values
    people = {"Alice", "Bob", "Carol", "Dave"}
    colors = {"Red", "Blue", "Green", "Yellow"}
    pets = {"Cat", "Dog", "Bird", "Fish"}
    houses = {1, 2, 3, 4}

    assigned_people = set()
    assigned_colors = set()
    assigned_pets = set()
    assigned_houses = set()

    for i, assignment in enumerate(assignments):
        person = assignment["person"]
        color = assignment["color"]
        pet = assignment["pet"]
        house = assignment["house"]

        # Check valid values
        if person not in people:
            return {"valid": False, "message": f"Invalid person: {person}"}
        if color not in colors:
            return {"valid": False, "message": f"Invalid color: {color}"}
        if pet not in pets:
            return {"valid": False, "message": f"Invalid pet: {pet}"}
        if house not in houses:
            return {"valid": False, "message": f"Invalid house: {house}"}

        # Check uniqueness
        if person in assigned_people:
            return {"valid": False, "message": f"Person {person} assigned multiple times"}
        if color in assigned_colors:
            return {"valid": False, "message": f"Color {color} assigned multiple times"}
        if pet in assigned_pets:
            return {"valid": False, "message": f"Pet {pet} assigned multiple times"}
        if house in assigned_houses:
            return {"valid": False, "message": f"House {house} assigned multiple times"}

        assigned_people.add(person)
        assigned_colors.add(color)
        assigned_pets.add(pet)
        assigned_houses.add(house)

    # Create person->assignment mapping for constraint checking
    person_map = {}
    house_map = {}
    for assignment in assignments:
        person_map[assignment["person"]] = assignment
        house_map[assignment["house"]] = assignment

    # Check constraints from the problem
    # 1. Alice lives in house 1
    if person_map["Alice"]["house"] != 1:
        return {"valid": False, "message": "Constraint violated: Alice must live in house 1"}

    # 2. The person with the red color lives in house 2
    if house_map[2]["color"] != "Red":
        return {"valid": False, "message": "Constraint violated: Person in house 2 must have red color"}

    # 3. Bob has a cat
    if person_map["Bob"]["pet"] != "Cat":
        return {"valid": False, "message": "Constraint violated: Bob must have a cat"}

    # 4. Carol's favorite color is blue
    if person_map["Carol"]["color"] != "Blue":
        return {"valid": False, "message": "Constraint violated: Carol's color must be blue"}

    # 5. The person with the yellow color has a fish
    yellow_person = None
    for assignment in assignments:
        if assignment["color"] == "Yellow":
            yellow_person = assignment
            break
    if not yellow_person or yellow_person["pet"] != "Fish":
        return {"valid": False, "message": "Constraint violated: Person with yellow color must have a fish"}

    # 6. The person with the green color lives in house 4
    if house_map[4]["color"] != "Green":
        return {"valid": False, "message": "Constraint violated: Person in house 4 must have green color"}

    # 7. Dave has the dog
    if person_map["Dave"]["pet"] != "Dog":
        return {"valid": False, "message": "Constraint violated: Dave must have the dog"}

    # 8. Alice does not have the bird
    if person_map["Alice"]["pet"] == "Bird":
        return {"valid": False, "message": "Constraint violated: Alice must not have the bird"}

    return {"valid": True, "message": "Solution is valid"}

if __name__ == "__main__":
    try:
        data = sys.stdin.read().strip()
        if not data:
            result = {"valid": False, "message": "No input provided"}
        else:
            solution = json.loads(data)
            result = validate_solution(solution)
    except json.JSONDecodeError as e:
        result = {"valid": False, "message": f"Invalid JSON: {e}"}
    except Exception as e:
        result = {"valid": False, "message": f"Error validating solution: {e}"}

    print(json.dumps(result))
