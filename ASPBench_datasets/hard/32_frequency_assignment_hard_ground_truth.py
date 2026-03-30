#!/usr/bin/env python3

import json
import sys

# Expected optimal value
EXPECTED_OPTIMAL_COST = 200

def get_problem_spec():
    """Returns the hardcoded problem specification."""
    spec = {
        "transmitters": {f"t{i}" for i in range(1, 11)},
        "frequencies": {
            101: {"band": "low", "cost": 10}, 102: {"band": "low", "cost": 12}, 103: {"band": "low", "cost": 15},
            201: {"band": "mid", "cost": 20}, 202: {"band": "mid", "cost": 22}, 203: {"band": "mid", "cost": 25}, 204: {"band": "mid", "cost": 28},
            301: {"band": "high", "cost": 40}, 302: {"band": "high", "cost": 45},
        },
        "transmitter_types": {
            "t1": {"low"}, "t2": {"low"},
            "t3": {"mid"}, "t4": {"mid"}, "t5": {"mid"},
            "t6": {"high"},
            "t7": {"low", "mid"}, "t8": {"low", "mid"},
            "t9": {"mid", "high"}, "t10": {"mid", "high"},
        },
        "interference": {
            "t1": {"t2", "t7"}, "t2": {"t1", "t8"},
            "t3": {"t4", "t9"}, "t4": {"t3", "t5", "t7"},
            "t5": {"t4", "t8", "t10"}, "t6": {"t9", "t10"},
            "t7": {"t1", "t4"}, "t8": {"t2", "t5"},
            "t9": {"t3", "t6"}, "t10": {"t5", "t6"},
        }
    }
    return spec

def validate_solution(solution_json):
    """Validate a frequency assignment solution."""
    spec = get_problem_spec()

    try:
        if isinstance(solution_json, str):
            data = json.loads(solution_json)
        else:
            data = solution_json
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON format: {e}"}

    # Basic structure validation
    if not all(k in data for k in ["assignments", "total_cost"]):
        return {"valid": False, "message": "Missing 'assignments' or 'total_cost' key."}

    assignments = data["assignments"]
    total_cost = data["total_cost"]

    if not isinstance(assignments, list):
        return {"valid": False, "message": "'assignments' must be a list."}
    if not isinstance(total_cost, int):
        return {"valid": False, "message": "'total_cost' must be an integer."}
    if len(assignments) != len(spec["transmitters"]):
        return {"valid": False, "message": f"Expected {len(spec['transmitters'])} assignments, but got {len(assignments)}."}

    # Process assignments into a map
    freq_map = {}
    assigned_transmitters = set()
    for asn in assignments:
        if not all(k in asn for k in ["transmitter", "frequency"]):
            return {"valid": False, "message": "Each assignment must have 'transmitter' and 'frequency' keys."}

        tx = asn["transmitter"]
        freq = asn["frequency"]

        if tx not in spec["transmitters"]:
            return {"valid": False, "message": f"Invalid transmitter '{tx}'."}
        if freq not in spec["frequencies"]:
            return {"valid": False, "message": f"Invalid frequency '{freq}'."}
        if tx in assigned_transmitters:
            return {"valid": False, "message": f"Transmitter '{tx}' is assigned more than once."}

        assigned_transmitters.add(tx)
        freq_map[tx] = freq

    # Check if all transmitters are assigned
    if assigned_transmitters != spec["transmitters"]:
        missing = spec["transmitters"] - assigned_transmitters
        return {"valid": False, "message": f"Missing assignments for transmitters: {sorted(list(missing))}"}

    # Validate band constraints
    for tx, freq in freq_map.items():
        allowed_bands = spec["transmitter_types"][tx]
        assigned_band = spec["frequencies"][freq]["band"]
        if assigned_band not in allowed_bands:
            return {"valid": False, "message": f"Transmitter {tx} (type allows {allowed_bands}) cannot use frequency {freq} from '{assigned_band}' band."}

    # Validate interference constraints
    for tx1, neighbors in spec["interference"].items():
        for tx2 in neighbors:
            if tx1 < tx2:  # Avoid double-checking symmetric pairs
                freq1 = freq_map[tx1]
                freq2 = freq_map[tx2]
                band1 = spec["frequencies"][freq1]["band"]
                band2 = spec["frequencies"][freq2]["band"]

                if band1 == band2:  # Same-band interference
                    if abs(freq1 - freq2) <= 1:
                        return {"valid": False, "message": f"Same-band interference violation: {tx1}({freq1}) and {tx2}({freq2}) are on adjacent or same frequencies."}
                else:  # Cross-band interference
                    if freq1 == freq2:
                        return {"valid": False, "message": f"Cross-band interference violation: {tx1} and {tx2} cannot use the same frequency {freq1}."}

    # Validate total cost
    calculated_cost = sum(spec["frequencies"][f]["cost"] for f in freq_map.values())
    if calculated_cost != total_cost:
        return {"valid": False, "message": f"Reported total_cost {total_cost} does not match calculated cost {calculated_cost}."}

    # Check optimality
    if total_cost != EXPECTED_OPTIMAL_COST:
        return {"valid": False, "message": f"Not optimal: total_cost={total_cost}, expected {EXPECTED_OPTIMAL_COST}"}

    return {"valid": True, "message": f"Solution valid and optimal (total_cost={EXPECTED_OPTIMAL_COST})"}

if __name__ == "__main__":
    solution_input = sys.stdin.read().strip()
    if not solution_input:
        print(json.dumps({"valid": False, "message": "No solution provided"}))
        sys.exit(1)

    result = validate_solution(solution_input)
    print(json.dumps(result, indent=2))
