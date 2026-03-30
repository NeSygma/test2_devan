#!/usr/bin/env python3
"""
Reference model for 006_hospital_matching_hard.md

Validates hospital/resident matching solutions from stdin.
Checks feasibility (capacities, mutual acceptability) and stability (no blocking pairs).
"""

import json
import sys
from typing import Dict, List

def validate_solution(solution: Dict) -> Dict:
    """Validate a hospital/resident matching solution."""

    # Define instance data
    residents = [f"r{i}" for i in range(1, 41)]
    hospitals = [f"h{i}" for i in range(1, 21)]

    caps = {
        "h1":2,"h2":2,"h3":2,"h4":2,"h5":2,"h6":2,
        "h7":4,"h8":3,"h9":1,
        "h10":3,"h11":3,"h12":2,
        "h13":3,"h14":3,"h15":2,
        "h16":2,"h17":2,
        "h18":1,"h19":1,"h20":1
    }

    res_prefs = {
        # A1
        "r1":["h1","h2"], "r2":["h1","h2"], "r3":["h2","h1"], "r4":["h2","h1"],
        # A2
        "r5":["h3","h4"], "r6":["h3","h4"], "r7":["h4","h3"], "r8":["h4","h3"],
        # A3
        "r9":["h5","h6"], "r10":["h5","h6"], "r11":["h6","h5"], "r12":["h6","h5"],
        # B1
        "r13":["h7","h8","h9"], "r14":["h7","h8","h9"],
        "r15":["h8","h7","h9"], "r16":["h8","h7","h9"],
        "r17":["h7","h8","h9"], "r18":["h7","h9","h8"],
        "r19":["h8","h9","h7"], "r20":["h9","h8","h7"],
        # B2
        "r21":["h10","h11","h12"], "r22":["h10","h12","h11"],
        "r23":["h11","h10","h12"], "r24":["h11","h12","h10"],
        "r25":["h10","h11","h12"], "r26":["h11","h10","h12"],
        "r27":["h12","h11","h10"], "r28":["h12","h10","h11"],
        # B3
        "r29":["h13","h14","h15"], "r30":["h13","h15","h14"],
        "r31":["h14","h13","h15"], "r32":["h14","h15","h13"],
        "r33":["h13","h14","h15"], "r34":["h14","h13","h15"],
        "r35":["h15","h14","h13"], "r36":["h15","h13","h14"],
        # A4
        "r37":["h16","h17"], "r38":["h16","h17"],
        "r39":["h17","h16"], "r40":["h17","h16"],
    }

    hosp_prefs = {
        # A1
        "h1":["r3","r4","r1","r2"], "h2":["r1","r2","r3","r4"],
        # A2
        "h3":["r7","r8","r5","r6"], "h4":["r5","r6","r7","r8"],
        # A3
        "h5":["r11","r12","r9","r10"], "h6":["r9","r10","r11","r12"],
        # B1
        "h7":["r13","r14","r17","r18","r15","r16","r19","r20"],
        "h8":["r15","r16","r19","r13","r14","r17","r18","r20"],
        "h9":["r20","r19","r18","r17","r16","r15","r14","r13"],
        # B2
        "h10":["r21","r22","r25","r23","r24","r26","r27","r28"],
        "h11":["r23","r24","r26","r21","r22","r25","r27","r28"],
        "h12":["r27","r28","r23","r24","r21","r22","r25","r26"],
        # B3
        "h13":["r29","r30","r33","r31","r32","r34","r35","r36"],
        "h14":["r31","r32","r34","r29","r30","r33","r35","r36"],
        "h15":["r35","r36","r31","r32","r29","r30","r33","r34"],
        # A4
        "h16":["r39","r40","r37","r38"],
        "h17":["r37","r38","r39","r40"],
        # Unused
        "h18":[], "h19":[], "h20":[]
    }

    # Create rank mappings
    res_rank = {r: {h: i for i, h in enumerate(res_prefs[r])} for r in res_prefs}
    hosp_rank = {h: {r: i for i, r in enumerate(hosp_prefs[h])} for h in hosp_prefs}

    def acceptable(r: str, h: str) -> bool:
        return (r in residents) and (h in hospitals) and (h in res_rank.get(r, {})) and (r in hosp_rank.get(h, {}))

    # Validate solution structure
    if "stable_matchings" not in solution:
        return {"valid": False, "message": "Missing 'stable_matchings' field"}

    matchings = solution["stable_matchings"]
    if not isinstance(matchings, list):
        return {"valid": False, "message": "'stable_matchings' must be a list"}

    if len(matchings) == 0:
        return {"valid": False, "message": "No matchings provided"}

    # Validate each matching
    for idx, matching in enumerate(matchings):
        # Build mappings
        r_to_h: Dict[str, str] = {r: None for r in residents}
        h_to_rs: Dict[str, List[str]] = {h: [] for h in hospitals}

        for pair in matching:
            if not isinstance(pair, list) or len(pair) != 2:
                return {"valid": False, "message": f"Matching {idx}: Invalid pair format"}

            r, h = pair[0], pair[1]

            if r not in residents:
                return {"valid": False, "message": f"Matching {idx}: Unknown resident {r}"}
            if h not in hospitals:
                return {"valid": False, "message": f"Matching {idx}: Unknown hospital {h}"}
            if not acceptable(r, h):
                return {"valid": False, "message": f"Matching {idx}: Inadmissible pair ({r}, {h})"}
            if r_to_h[r] is not None:
                return {"valid": False, "message": f"Matching {idx}: Resident {r} matched twice"}

            r_to_h[r] = h
            h_to_rs[h].append(r)

        # Capacity checks
        for h in hospitals:
            if len(h_to_rs[h]) > caps[h]:
                return {"valid": False, "message": f"Matching {idx}: Hospital {h} over capacity"}

        # Stability check
        for r in residents:
            for h in hospitals:
                if not acceptable(r, h):
                    continue
                if r_to_h[r] == h:
                    continue

                # Does resident prefer h?
                r_prefers = (r_to_h[r] is None) or (res_rank[r][h] < res_rank[r][r_to_h[r]])
                if not r_prefers:
                    continue

                # Would hospital accept r?
                assigned = h_to_rs[h]
                free = len(assigned) < caps[h]
                prefers_over_some = any(hosp_rank[h][r] < hosp_rank[h][r2] for r2 in assigned) if assigned else False

                if free or prefers_over_some:
                    return {"valid": False, "message": f"Matching {idx}: Blocking pair ({r}, {h})"}

    return {"valid": True, "message": f"All {len(matchings)} stable matchings are valid"}

def main():
    """Validate a hospital/resident matching solution from stdin."""
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            print(json.dumps({"valid": False, "message": "No solution provided"}))
            return

        solution = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {e}"}))
        return

    result = validate_solution(solution)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
