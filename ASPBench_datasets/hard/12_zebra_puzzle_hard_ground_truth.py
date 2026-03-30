#!/usr/bin/env python3
"""
Reference Model for Zebra Puzzle (Hard).

This script reads a JSON solution from stdin and validates it against all
problem constraints. It does not solve the puzzle.
"""

import json
import sys
from typing import Dict, List, Any, Optional

class ZebraValidator:
    def __init__(self, solution_data: Dict[str, Any]):
        self.data = solution_data
        self.solution = {item['suite']: item for item in solution_data.get('solution', [])}
        self.lizard_owner = solution_data.get('lizard_owner')
        self.errors = []

    def validate(self) -> Dict[str, Any]:
        """Runs all validation checks."""
        try:
            self.check_structure()
            self.check_uniqueness()
            self.check_all_constraints()
            self.check_question()
        except Exception as e:
            self.errors.append(f"An unexpected error occurred during validation: {e}")

        if not self.errors:
            return {"valid": True, "message": "Solution is valid."}
        else:
            return {"valid": False, "message": "\n".join(self.errors)}

    def find_suite_with(self, attr_type: str, value: Any) -> Optional[int]:
        """Finds the suite number for a given attribute value."""
        for suite_num, details in self.solution.items():
            if details.get(attr_type) == value:
                return suite_num
        return None

    def check_structure(self):
        """Validates the basic structure of the JSON input."""
        if 'solution' not in self.data or 'lizard_owner' not in self.data:
            self.errors.append("Missing 'solution' or 'lizard_owner' key in JSON.")
            raise ValueError("Fatal structure error")
        if not isinstance(self.data['solution'], list) or len(self.data['solution']) != 8:
            self.errors.append("'solution' must be a list of 8 items.")
            raise ValueError("Fatal structure error")
        if not all('suite' in item for item in self.data['solution']):
            self.errors.append("Not all items in 'solution' have a 'suite' key.")
            raise ValueError("Fatal structure error")

    def check_uniqueness(self):
        """Checks that each attribute value is used exactly once."""
        attributes = ["nationality", "profession", "car", "drink", "music", "pet", "destination"]
        for attr in attributes:
            values = [self.solution[i].get(attr) for i in range(1, 9)]
            if len(values) != len(set(values)):
                self.errors.append(f"Duplicate values found for attribute '{attr}'.")
            if None in values:
                self.errors.append(f"Missing value for attribute '{attr}'.")

    def check_all_constraints(self):
        """Iterates through and checks all 18 puzzle constraints."""
        constraints = [
            self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8,
            self.c9, self.c10, self.c11, self.c12, self.c13, self.c14, self.c15,
            self.c16, self.c17, self.c18
        ]
        for i, constraint_func in enumerate(constraints, 1):
            if not constraint_func():
                self.errors.append(f"Constraint {i} failed.")

    def check_question(self):
        """Checks the main question: Who owns the Lizard?"""
        lizard_suite = self.find_suite_with('pet', 'Lizard')
        if not lizard_suite:
            self.errors.append("Question check failed: No one owns a Lizard.")
            return
        owner_nationality = self.solution[lizard_suite].get('nationality')
        if owner_nationality != self.lizard_owner:
            self.errors.append(f"Question check failed: Expected Lizard owner '{self.lizard_owner}', but found '{owner_nationality}'.")

    # Constraint implementations
    def c1(self): return self.solution.get(4, {}).get('drink') == 'Milk'
    def c2(self): return self.solution.get(4, {}).get('nationality') == 'Hungarian'
    def c3(self): s = self.find_suite_with('nationality', 'American'); return s and self.solution[s]['profession'] == 'Lawyer'
    def c4(self): s = self.find_suite_with('car', 'BMW'); return s and self.solution[s]['profession'] == 'Biologist'
    def c5(self): s = self.find_suite_with('nationality', 'Canadian'); return s and self.solution[s]['pet'] == 'Snake'
    def c6(self): s = self.find_suite_with('music', 'Classical'); return s and self.solution[s]['car'] == 'Audi'
    def c7(self): s = self.find_suite_with('nationality', 'German'); return s and self.solution[s]['drink'] == 'Coffee'
    def c8(self): s = self.find_suite_with('destination', 'Tokyo'); return s and self.solution[s]['profession'] == 'Chemist'
    def c9(self): s_eng = self.find_suite_with('profession', 'Engineer'); s_law = self.find_suite_with('profession', 'Lawyer'); return s_eng and s_law and s_eng == s_law - 1
    def c10(self): s_dog = self.find_suite_with('pet', 'Dog'); s_volvo = self.find_suite_with('car', 'Volvo'); return s_dog and s_volvo and abs(s_dog - s_volvo) == 1
    def c11(self): s_rock = self.find_suite_with('music', 'Rock'); s_pop = self.find_suite_with('music', 'Pop'); return s_rock and s_pop and abs(s_rock - s_pop) == 1
    def c12(self): s_paris = self.find_suite_with('destination', 'Paris'); s_fish = self.find_suite_with('pet', 'Fish'); return s_paris and s_fish and abs(s_paris - s_fish) == 1
    def c13(self): s_pilot = self.find_suite_with('profession', 'Pilot'); return s_pilot and s_pilot % 2 == 0
    def c14(self): s_wine = self.find_suite_with('drink', 'Wine'); s_coffee = self.find_suite_with('drink', 'Coffee'); return s_wine and s_coffee and s_wine > s_coffee
    def c15(self): s_ford = self.find_suite_with('car', 'Ford'); return s_ford and ((s_ford > 1 and self.solution[s_ford - 1]['drink'] == 'Tea') or (s_ford < 8 and self.solution[s_ford + 1]['drink'] == 'Tea'))
    def c16(self): s_nissan = self.find_suite_with('car', 'Nissan'); return s_nissan and s_nissan not in [1, 8]
    def c17(self): s_jazz = self.find_suite_with('music', 'Jazz'); s_blues = self.find_suite_with('music', 'Blues'); return s_jazz and s_blues and s_jazz < s_blues
    def c18(self): return self.solution.get(1, {}).get('nationality') == 'Dutch'

def main():
    """Main function to read from stdin, validate, and print result."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"valid": False, "message": "Invalid JSON input."}, indent=2))
        return

    validator = ZebraValidator(input_data)
    result = validator.validate()
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
