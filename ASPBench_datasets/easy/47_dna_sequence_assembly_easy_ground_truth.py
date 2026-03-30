#!/usr/bin/env python3
"""
Reference model for Problem 047: DNA Sequence Assembly

Validates DNA sequence assembly solutions and checks optimality.
"""

import json
import sys

# Expected optimal value
EXPECTED_OPTIMAL_OVERLAP = 39

def validate_solution(solution):
    """
    Validate DNA sequence assembly solution.

    Args:
        solution: Dict with fragments, consensus_sequence, assembly_path, overlap_details

    Returns:
        Dict: {"valid": bool, "message": str}
    """

    # Check required fields
    required_fields = ["fragments", "consensus_sequence", "assembly_path", "overlap_details"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    fragments = solution["fragments"]
    consensus = solution["consensus_sequence"]
    path = solution["assembly_path"]
    overlaps = solution["overlap_details"]

    # Expected fragments
    expected_fragments = [
        "ATCGATCG",
        "CGATCGTA",
        "ATCGTAAC",
        "CGTAACGG",
        "TAACGGCT",
        "ACGGCTGA",
        "GGCTGAAA",
        "CTGAAATC"
    ]

    # Check fragments match expected
    if fragments != expected_fragments:
        return {"valid": False, "message": "Fragments do not match expected set"}

    # Check consensus sequence
    if not isinstance(consensus, str) or not all(c in "ATCG" for c in consensus):
        return {"valid": False, "message": "Invalid consensus sequence format"}

    # Check assembly path
    if not isinstance(path, list) or len(path) != 8:
        return {"valid": False, "message": f"Assembly path must have 8 fragments, got {len(path)}"}

    if set(path) != set(range(8)):
        return {"valid": False, "message": "Assembly path must use all fragments exactly once"}

    # Check overlap details
    if not isinstance(overlaps, list):
        return {"valid": False, "message": "Overlap details must be a list"}

    # Should have 7 overlaps for 8 fragments
    if len(overlaps) != 7:
        return {"valid": False, "message": f"Expected 7 overlap entries, got {len(overlaps)}"}

    # Verify each overlap
    for i, overlap in enumerate(overlaps):
        required_overlap_fields = ["fragment1", "fragment2", "overlap_length", "position1", "position2"]
        for field in required_overlap_fields:
            if field not in overlap:
                return {"valid": False, "message": f"Overlap entry {i} missing field: {field}"}

        frag1 = overlap["fragment1"]
        frag2 = overlap["fragment2"]
        overlap_len = overlap["overlap_length"]
        pos1 = overlap["position1"]
        pos2 = overlap["position2"]

        # Check indices
        if frag1 not in range(8) or frag2 not in range(8):
            return {"valid": False, "message": f"Invalid fragment indices in overlap {i}"}

        # Check that consecutive fragments in path match overlap
        if path[i] != frag1 or path[i+1] != frag2:
            return {"valid": False, "message": f"Overlap {i} does not match assembly path"}

        # Verify overlap is valid
        if overlap_len > 0:
            seq1 = fragments[frag1]
            seq2 = fragments[frag2]

            if pos1 + overlap_len > len(seq1):
                return {"valid": False, "message": f"Overlap {i}: position1 + overlap_length exceeds fragment1 length"}

            if pos2 + overlap_len > len(seq2):
                return {"valid": False, "message": f"Overlap {i}: position2 + overlap_length exceeds fragment2 length"}

            overlap_seq1 = seq1[pos1:pos1+overlap_len]
            overlap_seq2 = seq2[pos2:pos2+overlap_len]

            if overlap_seq1 != overlap_seq2:
                return {"valid": False, "message": f"Overlap {i}: sequences do not match"}

            # Check minimum overlap requirement
            if overlap_len < 3:
                return {"valid": False, "message": f"Overlap {i}: overlap length {overlap_len} is less than minimum 3"}

    # Verify consensus sequence is constructed correctly
    reconstructed = fragments[path[0]]
    for i in range(1, len(path)):
        current_frag = fragments[path[i]]
        overlap_len = overlaps[i-1]["overlap_length"]

        if overlap_len > 0:
            reconstructed += current_frag[overlap_len:]
        else:
            reconstructed += current_frag

    if reconstructed != consensus:
        return {"valid": False, "message": "Consensus sequence does not match reconstruction from overlaps"}

    # Calculate total overlap
    total_overlap = sum(o["overlap_length"] for o in overlaps)

    # Check optimality
    if total_overlap != EXPECTED_OPTIMAL_OVERLAP:
        return {"valid": False, "message": f"Not optimal: total_overlap={total_overlap}, expected {EXPECTED_OPTIMAL_OVERLAP}"}

    return {
        "valid": True,
        "message": f"Solution is valid and optimal (total_overlap={EXPECTED_OPTIMAL_OVERLAP})"
    }

if __name__ == "__main__":
    try:
        data = sys.stdin.read().strip()
        if not data:
            print(json.dumps({"valid": False, "message": "No input provided"}))
            sys.exit(1)

        solution = json.loads(data)
        result = validate_solution(solution)
        print(json.dumps(result))

    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Validation error: {str(e)}"}))
        sys.exit(1)
