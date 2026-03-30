#!/usr/bin/env python3
"""
Reference Model for Zebra Puzzle (Einstein's Riddle)
Validates a solution by checking all constraints.
"""

import json
import sys
from typing import Dict, List, Optional

def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def validate_solution(solution: Dict) -> Dict:
    """Validate the Zebra Puzzle solution."""
    if not solution:
        return {"valid": False, "message": "No solution provided"}

    # Extract solution array
    if "solution" not in solution:
        return {"valid": False, "message": "Missing 'solution' field"}

    houses = solution["solution"]
    if not isinstance(houses, list) or len(houses) != 5:
        return {"valid": False, "message": "Solution must contain exactly 5 houses"}

    # Check zebra_owner field
    if "zebra_owner" not in solution:
        return {"valid": False, "message": "Missing 'zebra_owner' field"}

    # Build lookup tables
    house_by_num = {}
    for house_data in houses:
        if "house" not in house_data:
            return {"valid": False, "message": "Missing 'house' field in solution"}
        house_num = house_data["house"]
        if house_num < 1 or house_num > 5:
            return {"valid": False, "message": f"Invalid house number: {house_num}"}
        house_by_num[house_num] = house_data

    # Verify all houses 1-5 are present
    for i in range(1, 6):
        if i not in house_by_num:
            return {"valid": False, "message": f"Missing house {i}"}

    # Check uniqueness of attributes
    attributes = ["color", "nationality", "drink", "cigarette", "pet"]
    for attr in attributes:
        values = []
        for house_data in houses:
            if attr not in house_data:
                return {"valid": False, "message": f"Missing '{attr}' field in house {house_data.get('house', '?')}"}
            values.append(house_data[attr])
        if len(values) != len(set(values)):
            return {"valid": False, "message": f"Duplicate values found for attribute '{attr}'"}

    # Check constraints
    def find_house_with(attr: str, value: str) -> Optional[int]:
        """Find house number with given attribute value."""
        for house_data in houses:
            if house_data.get(attr) == value:
                return house_data["house"]
        return None

    # Constraint 1: The Brit lives in the red house
    brit_house = find_house_with("nationality", "Brit")
    red_house = find_house_with("color", "Red")
    if brit_house != red_house:
        return {"valid": False, "message": "Constraint 1 violated: Brit must live in red house"}

    # Constraint 2: The Swede keeps dogs as pets
    swede_house = find_house_with("nationality", "Swede")
    dog_house = find_house_with("pet", "Dog")
    if swede_house != dog_house:
        return {"valid": False, "message": "Constraint 2 violated: Swede must keep dogs"}

    # Constraint 3: The Dane drinks tea
    dane_house = find_house_with("nationality", "Dane")
    tea_house = find_house_with("drink", "Tea")
    if dane_house != tea_house:
        return {"valid": False, "message": "Constraint 3 violated: Dane must drink tea"}

    # Constraint 4: The green house is on the left of the white house
    green_house = find_house_with("color", "Green")
    white_house = find_house_with("color", "White")
    if green_house is None or white_house is None:
        return {"valid": False, "message": "Missing green or white house"}
    if white_house != green_house + 1:
        return {"valid": False, "message": "Constraint 4 violated: Green house must be directly left of white house"}

    # Constraint 5: The green house's owner drinks coffee
    coffee_house = find_house_with("drink", "Coffee")
    if green_house != coffee_house:
        return {"valid": False, "message": "Constraint 5 violated: Green house owner must drink coffee"}

    # Constraint 6: The person who smokes Pall Mall rears birds
    pall_mall_house = find_house_with("cigarette", "Pall Mall")
    birds_house = find_house_with("pet", "Birds")
    if pall_mall_house != birds_house:
        return {"valid": False, "message": "Constraint 6 violated: Pall Mall smoker must rear birds"}

    # Constraint 7: The owner of the yellow house smokes Dunhill
    yellow_house = find_house_with("color", "Yellow")
    dunhill_house = find_house_with("cigarette", "Dunhill")
    if yellow_house != dunhill_house:
        return {"valid": False, "message": "Constraint 7 violated: Yellow house owner must smoke Dunhill"}

    # Constraint 8: The man living in the center house drinks milk
    center_house = house_by_num[3]
    if center_house["drink"] != "Milk":
        return {"valid": False, "message": "Constraint 8 violated: Center house must drink milk"}

    # Constraint 9: The Norwegian lives in the first house
    first_house = house_by_num[1]
    if first_house["nationality"] != "Norwegian":
        return {"valid": False, "message": "Constraint 9 violated: Norwegian must live in first house"}

    # Constraint 10: The man who smokes Blends lives next to the one who keeps cats
    blends_house = find_house_with("cigarette", "Blends")
    cats_house = find_house_with("pet", "Cats")
    if blends_house is None or cats_house is None:
        return {"valid": False, "message": "Missing Blends or Cats"}
    if abs(blends_house - cats_house) != 1:
        return {"valid": False, "message": "Constraint 10 violated: Blends smoker must be next to cat owner"}

    # Constraint 11: The man who keeps a horse lives next to the man who smokes Dunhill
    horse_house = find_house_with("pet", "Horse")
    if horse_house is None or dunhill_house is None:
        return {"valid": False, "message": "Missing Horse or Dunhill"}
    if abs(horse_house - dunhill_house) != 1:
        return {"valid": False, "message": "Constraint 11 violated: Horse owner must be next to Dunhill smoker"}

    # Constraint 12: The owner who smokes Blue Master drinks beer
    blue_master_house = find_house_with("cigarette", "Blue Master")
    beer_house = find_house_with("drink", "Beer")
    if blue_master_house != beer_house:
        return {"valid": False, "message": "Constraint 12 violated: Blue Master smoker must drink beer"}

    # Constraint 13: The German smokes Prince
    german_house = find_house_with("nationality", "German")
    prince_house = find_house_with("cigarette", "Prince")
    if german_house != prince_house:
        return {"valid": False, "message": "Constraint 13 violated: German must smoke Prince"}

    # Constraint 14: The Norwegian lives next to the blue house
    norwegian_house = find_house_with("nationality", "Norwegian")
    blue_house = find_house_with("color", "Blue")
    if norwegian_house is None or blue_house is None:
        return {"valid": False, "message": "Missing Norwegian or Blue house"}
    if abs(norwegian_house - blue_house) != 1:
        return {"valid": False, "message": "Constraint 14 violated: Norwegian must be next to blue house"}

    # Constraint 15: The man who smokes Blends has a neighbor who drinks water
    water_house = find_house_with("drink", "Water")
    if blends_house is None or water_house is None:
        return {"valid": False, "message": "Missing Blends or Water"}
    if abs(blends_house - water_house) != 1:
        return {"valid": False, "message": "Constraint 15 violated: Blends smoker must be next to water drinker"}

    # Check zebra owner
    zebra_house = find_house_with("pet", "Zebra")
    if zebra_house is None:
        return {"valid": False, "message": "No one owns the zebra"}

    zebra_owner_actual = house_by_num[zebra_house]["nationality"]
    if solution["zebra_owner"] != zebra_owner_actual:
        return {"valid": False, "message": f"Zebra owner mismatch: got {solution['zebra_owner']}, expected {zebra_owner_actual}"}

    return {"valid": True, "message": f"Solution correct! The {zebra_owner_actual} owns the zebra."}

def main():
    """Main function to validate solution from stdin."""
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
