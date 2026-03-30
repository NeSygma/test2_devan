# Problem Statement

Assemble a complete DNA sequence from overlapping DNA fragments. Each fragment is a short DNA sequence, and adjacent fragments in the assembly must have overlapping regions that match perfectly.

## Instance Data

You are given 8 DNA fragments:
- Fragment 0: ATCGATCG
- Fragment 1: CGATCGTA
- Fragment 2: ATCGTAAC
- Fragment 3: CGTAACGG
- Fragment 4: TAACGGCT
- Fragment 5: ACGGCTGA
- Fragment 6: GGCTGAAA
- Fragment 7: CTGAAATC

## Constraints

1. **All fragments used**: Each fragment must appear exactly once in the assembly
2. **Linear ordering**: Fragments form a single linear sequence
3. **Valid overlaps**: Adjacent fragments must have overlapping regions (minimum 3 nucleotides)
4. **Perfect matching**: Overlapping regions must match exactly (no mismatches)

## Objective

Find an ordering of the fragments that **maximizes** the total overlap length between adjacent fragments.

**Expected optimal overlap length: 39**

## Output Format

```json
{
  "fragments": ["ATCGATCG", "CGATCGTA", ...],
  "consensus_sequence": "ATCGATCGTAACGGCTGAAATC",
  "assembly_path": [0, 1, ...],
  "overlap_details": [
    {
      "fragment1": 0,
      "fragment2": 1,
      "overlap_length": 6,
      "position1": 2,
      "position2": 0
    },
    ...
  ]
}
```

**Field descriptions:**
- `fragments`: List of all DNA fragment sequences (strings of A, T, C, G)
- `consensus_sequence`: The assembled complete DNA sequence
- `assembly_path`: Ordered list of fragment indices showing assembly order
- `overlap_details`: List of overlap information for each adjacent pair:
  - `fragment1`: Index of first fragment
  - `fragment2`: Index of second fragment
  - `overlap_length`: Length of overlapping region
  - `position1`: Start position of overlap in first fragment
  - `position2`: Start position of overlap in second fragment (typically 0)
