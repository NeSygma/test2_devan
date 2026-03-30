#!/usr/bin/env python3
"""
Reference Model: Simplified 2D Protein Folding
==============================================
Validates protein folding solutions from stdin.
"""

import sys
import json
from typing import List, Tuple

def is_valid_folding(coords: List[Tuple[int, int]]) -> bool:
    """Check if folding is valid (self-avoiding, connected)."""
    # Check uniqueness (self-avoiding)
    if len(set(coords)) != len(coords):
        return False

    # Check connectivity (consecutive residues are adjacent)
    for i in range(len(coords) - 1):
        x1, y1 = coords[i]
        x2, y2 = coords[i + 1]
        if abs(x1 - x2) + abs(y1 - y2) != 1:
            return False

    return True

def calculate_energy(sequence: str, coords: List[Tuple[int, int]]) -> int:
    """Calculate energy based on H-H contacts."""
    energy = 0

    for i in range(len(sequence)):
        if sequence[i] == 'H':
            for j in range(i + 2, len(sequence)):  # Non-sequential neighbors only
                if sequence[j] == 'H':
                    x1, y1 = coords[i]
                    x2, y2 = coords[j]
                    # Adjacent in lattice = H-H contact
                    if abs(x1 - x2) + abs(y1 - y2) == 1:
                        energy -= 1

    return energy

def validate_solution():
    """Validate protein folding solution from stdin."""
    try:
        # Read solution from stdin
        data = sys.stdin.read().strip()
        if not data:
            return {"valid": False, "message": "No input provided"}

        solution = json.loads(data)

        # Check for error field
        if "error" in solution:
            return {"valid": False, "message": "Solution contains error"}

        # Check required fields
        if "coordinates" not in solution:
            return {"valid": False, "message": "Missing 'coordinates' field"}

        if "sequence" not in solution:
            return {"valid": False, "message": "Missing 'sequence' field"}

        coordinates = solution["coordinates"]
        sequence = solution["sequence"]

        # Verify sequence
        if sequence != "HPPHPPHH":
            return {"valid": False, "message": f"Incorrect sequence: {sequence}"}

        # Check number of coordinates
        if len(coordinates) != 8:
            return {"valid": False, "message": f"Expected 8 coordinates, got {len(coordinates)}"}

        # Convert to tuples for validation
        coords = [tuple(coord) for coord in coordinates]

        # Check validity (self-avoiding, connected)
        if not is_valid_folding(coords):
            return {"valid": False, "message": "Invalid folding: not self-avoiding or not connected"}

        # Calculate energy
        energy = calculate_energy(sequence, coords)

        # Check for optimal energy (-3)
        if energy != -3:
            return {"valid": False, "message": f"Non-optimal energy: {energy} (expected: -3)"}

        return {"valid": True, "message": f"Valid protein folding with optimal energy: {energy}"}

    except json.JSONDecodeError:
        return {"valid": False, "message": "Invalid JSON input"}
    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}

if __name__ == "__main__":
    result = validate_solution()
    print(json.dumps(result))
