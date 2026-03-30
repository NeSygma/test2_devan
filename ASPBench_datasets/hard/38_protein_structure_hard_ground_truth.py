#!/usr/bin/env python3
"""
Reference Model (Validator): 2D Protein Folding
================================================
This script validates a solution for the 10-residue protein folding problem.
It reads a JSON solution from stdin and checks its validity and optimality.
"""
import json
import sys
from typing import List, Tuple, Dict

SEQUENCE = "HPHPHHPHPH"
N = len(SEQUENCE)
# The optimal energy for this sequence is known to be -4.
OPTIMAL_ENERGY = -4

def is_valid_folding(coords: List[Tuple[int, int]]) -> bool:
    """Check if folding is valid (self-avoiding, connected)."""
    # Check for 10 unique coordinates (self-avoiding)
    if len(set(coords)) != N:
        return False

    # Check connectivity (consecutive residues are adjacent)
    for i in range(N - 1):
        x1, y1 = coords[i]
        x2, y2 = coords[i + 1]
        if abs(x1 - x2) + abs(y1 - y2) != 1:
            return False

    return True

def calculate_energy(coords: List[Tuple[int, int]]) -> int:
    """Calculate energy based on non-sequential H-H contacts."""
    energy = 0
    h_positions = [i for i, residue in enumerate(SEQUENCE) if residue == 'H']

    for i_idx, i in enumerate(h_positions):
        for j in h_positions[i_idx + 1:]:
            # Ensure non-sequential check
            if abs(i - j) > 1:
                x1, y1 = coords[i]
                x2, y2 = coords[j]
                # Check for adjacency
                if abs(x1 - x2) + abs(y1 - y2) == 1:
                    energy -= 1
    return energy

def main():
    """Main verification logic."""
    try:
        solution_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"valid": False, "message": "Invalid JSON input."}))
        sys.exit()

    if "error" in solution_data:
        print(json.dumps({"valid": False, "message": f"Solution reported an error: {solution_data['error']}"}))
        return

    if "coordinates" not in solution_data or "sequence" not in solution_data:
        print(json.dumps({"valid": False, "message": "Missing 'coordinates' or 'sequence' key in JSON."}))
        return

    coords_list = solution_data["coordinates"]
    sequence = solution_data["sequence"]

    if sequence != SEQUENCE:
        print(json.dumps({"valid": False, "message": f"Incorrect sequence. Expected {SEQUENCE}, got {sequence}."}))
        return

    if not isinstance(coords_list, list) or len(coords_list) != N:
        print(json.dumps({"valid": False, "message": f"Coordinates must be a list of size {N}."}))
        return

    coords_tuples = [tuple(c) for c in coords_list]

    if not is_valid_folding(coords_tuples):
        print(json.dumps({"valid": False, "message": "Invalid folding: not self-avoiding or not connected."}))
        return

    energy = calculate_energy(coords_tuples)

    # Check optimality
    if energy != OPTIMAL_ENERGY:
        print(json.dumps({"valid": False, "message": f"Not optimal: energy={energy}, expected {OPTIMAL_ENERGY}"}))
        return

    result = {
        "valid": True,
        "message": f"Solution valid and optimal (energy={OPTIMAL_ENERGY})"
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
