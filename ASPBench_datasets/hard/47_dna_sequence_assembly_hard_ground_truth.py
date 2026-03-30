#!/usr/bin/env python3
"""
Reference model and validator for Problem 047: DNA Sequence Assembly (Hard).

This script reads a JSON solution from stdin and validates that it adheres to all
problem constraints including fragment overlaps, GC-content rules, start/stop codons,
and optimal number of contigs.
"""

import sys
import json

# Expected optimal value
EXPECTED_OPTIMAL_NUM_CONTIGS = 2

class AssemblyValidator:
    """Validates a DNA assembly solution against problem constraints."""

    def __init__(self, fragments):
        self.fragments = {f"F{i}": seq for i, seq in enumerate(fragments)}

    def _get_reverse_complement(self, dna):
        complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        return "".join(complement.get(base, base) for base in reversed(dna))

    def _get_gc_content(self, dna):
        if not dna:
            return 0
        gc_count = dna.count('G') + dna.count('C')
        return (gc_count / len(dna)) * 100

    def _find_overlap(self, s1, s2):
        """Finds the longest suffix-prefix overlap between two strings."""
        max_len = 0
        for i in range(1, min(len(s1), len(s2)) + 1):
            if s1[-i:] == s2[:i]:
                max_len = i
        return max_len

    def validate(self, solution_json):
        """Validates the given solution."""
        try:
            solution = json.loads(solution_json)
        except json.JSONDecodeError as e:
            return {"valid": False, "message": f"Invalid JSON: {e}"}

        # Extract data
        contigs = solution.get("contigs", [])
        excluded = solution.get("excluded", {}).get("chimeric", [])

        # Check all fragments are accounted for
        all_solution_frags = set(excluded)
        for contig in contigs:
            frags = contig.get("fragments", [])
            all_solution_frags.update(frags)

        if all_solution_frags != set(self.fragments.keys()):
            return {"valid": False, "message": "Solution does not account for all original fragments."}

        # Validate each contig
        for contig in contigs:
            cid = contig.get("contig_id")
            frags = contig.get("fragments", [])
            orients = contig.get("orientations", [])
            seq = contig.get("sequence", "")

            if len(frags) != len(orients):
                return {"valid": False, "message": f"Contig {cid}: fragments and orientations length mismatch."}

            # Check start codon
            if not seq.startswith("ATG"):
                return {"valid": False, "message": f"Contig {cid}: sequence does not start with ATG."}

            # Check stop codon
            stop_codons = {"TAA", "TAG", "TGA"}
            if not any(seq.endswith(stop) for stop in stop_codons):
                return {"valid": False, "message": f"Contig {cid}: sequence does not end with a stop codon."}

            # Verify sequence reconstruction and overlaps
            reconstructed = ""
            for i, fid in enumerate(frags):
                orig_seq = self.fragments.get(fid)
                if not orig_seq:
                    return {"valid": False, "message": f"Contig {cid}: unknown fragment {fid}."}

                orient = orients[i]
                if orient == "forward":
                    frag_seq = orig_seq
                elif orient == "reverse":
                    frag_seq = self._get_reverse_complement(orig_seq)
                else:
                    return {"valid": False, "message": f"Contig {cid}: invalid orientation '{orient}' for {fid}."}

                if i == 0:
                    reconstructed = frag_seq
                else:
                    # Check overlap with previous fragment
                    prev_fid = frags[i-1]
                    prev_orient = orients[i-1]
                    prev_seq = self.fragments[prev_fid]
                    if prev_orient == "reverse":
                        prev_seq = self._get_reverse_complement(prev_seq)

                    overlap_len = self._find_overlap(prev_seq, frag_seq)

                    # Check GC-content conditional rule
                    gc1 = self._get_gc_content(self.fragments[prev_fid])
                    gc2 = self._get_gc_content(self.fragments[fid])
                    min_overlap = 4 if (gc1 > 50 and gc2 > 50) else 3

                    if overlap_len < min_overlap:
                        return {"valid": False, "message": f"Contig {cid}: overlap between {prev_fid} and {fid} is {overlap_len}, minimum required is {min_overlap}."}

                    reconstructed += frag_seq[overlap_len:]

            if reconstructed != seq:
                return {"valid": False, "message": f"Contig {cid}: reconstructed sequence '{reconstructed}' does not match provided sequence '{seq}'."}

        # Check excluded fragments are not used
        for fid in excluded:
            for contig in contigs:
                if fid in contig.get("fragments", []):
                    return {"valid": False, "message": f"Excluded fragment {fid} is used in a contig."}

        # Check optimality - minimum number of contigs
        num_contigs = len(contigs)
        if num_contigs != EXPECTED_OPTIMAL_NUM_CONTIGS:
            return {"valid": False, "message": f"Not optimal: number of contigs={num_contigs}, expected {EXPECTED_OPTIMAL_NUM_CONTIGS}"}

        return {"valid": True, "message": f"Solution valid and optimal (num_contigs={EXPECTED_OPTIMAL_NUM_CONTIGS})"}

def main():
    """Main entry point."""
    fragments = [
        "ATGGGCGC", "GGCGCCAT", "GCCATT", "ATTTAA",
        "ATGCCTCG", "GCTCGAGG", "TCGAGCTG", "AGCTGA", "ATTCG"
    ]
    validator = AssemblyValidator(fragments)

    try:
        solution_json = sys.stdin.read()
        if not solution_json:
            print(json.dumps({"valid": False, "message": "No solution provided on stdin."}))
            sys.exit(1)

        result = validator.validate(solution_json)
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"valid": False, "message": f"An unexpected error occurred during validation: {e}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
