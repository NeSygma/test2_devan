#!/usr/bin/env python3

import json
import sys

# Expected optimal value (extracted from reference solution)
EXPECTED_OPTIMAL_COST = 1000

def validate_solution(instance, solution):
    """
    Validates the solution for the Social Network Influence problem.
    This function re-implements the cascade logic in Python to verify the solution's claims.
    """
    try:
        # --- Extract Instance Data ---
        # Add tier and community derived from category
        users = {}
        for u in instance['users']:
            user_copy = u.copy()
            category = u['category']
            user_copy['community'] = category
            user_copy['tier'] = "top_tier" if category in ["influencer", "expert"] else "regular_tier"
            users[u['id']] = user_copy
        connections = instance['connections']
        # Parameters are at the top level of the instance
        budget = instance['budget']['total'] if isinstance(instance['budget'], dict) else instance['budget']
        max_seeds = instance['max_seeds']
        # Determine key_user from required_seed_category (pick first user of that category)
        required_cat = instance.get('required_seed_category', 'expert')
        key_user = next((u['id'] for u in instance['users'] if u['category'] == required_cat), 'u1')
        synergy_bonus_val = 0  # Not in instance
        redundancy_penalty_val = 0  # Not in instance

        # --- Extract Solution Data ---
        selected_seeds = set(solution.get('selected_seeds', []))
        reported_activated = set(solution.get('activated_users', []))
        reported_cost = solution.get('total_cost', -1)
        reported_activated_count = solution.get('total_activated_count', -1)
        reported_key_user_activated = solution.get('key_user_activated', None)
        reported_score = solution.get('final_score', -1)

        # --- Validation Step 1: Seed Selection Constraints ---
        if len(selected_seeds) > max_seeds:
            return False, f"Exceeded max seeds: {len(selected_seeds)} > {max_seeds}"

        calculated_cost = 0
        for seed_id in selected_seeds:
            if seed_id not in users:
                return False, f"Selected seed '{seed_id}' is not a valid user."
            calculated_cost += users[seed_id]['cost']

        if calculated_cost > budget:
            return False, f"Exceeded budget: {calculated_cost} > {budget}"

        if calculated_cost != reported_cost:
            return False, f"Mismatch in total cost: calculated {calculated_cost}, reported {reported_cost}"

        # --- Validation Step 2: Cascade Simulation ---
        # This is the core of the validation. We simulate the cascade from scratch.
        activated = set(selected_seeds)

        # Use a fixed-point iteration to find all activated users
        while True:
            newly_activated_this_round = set()
            for user_id, user_data in users.items():
                if user_id in activated:
                    continue

                # Sum influence from already activated neighbors
                incoming_influence = 0.0
                for conn in connections:
                    if conn['to'] == user_id and conn['from'] in activated:
                        incoming_influence += conn['strength']

                # Check if threshold is met
                if incoming_influence >= user_data['activation_threshold'] and user_data['activation_threshold'] > 0:
                    newly_activated_this_round.add(user_id)

            if not newly_activated_this_round:
                break # No change, fixed point reached

            activated.update(newly_activated_this_round)

        # Compare calculated cascade with reported cascade
        if activated != reported_activated:
            msg = (f"Cascade mismatch. "
                   f"Calculated: {sorted(list(activated))}, "
                   f"Reported: {sorted(list(reported_activated))}. "
                   f"Missing from report: {sorted(list(activated - reported_activated))}. "
                   f"Extra in report: {sorted(list(reported_activated - activated))}.")
            return False, msg

        if len(activated) != reported_activated_count:
            return False, f"Mismatch in activated count: calculated {len(activated)}, reported {reported_activated_count}"

        # --- Validation Step 3: Score Calculation ---
        calculated_key_user_activated = key_user in activated
        if calculated_key_user_activated != reported_key_user_activated:
            return False, f"Mismatch in key user status: calculated {calculated_key_user_activated}, reported {reported_key_user_activated}"

        # Check for synergy/redundancy
        synergy_bonus = 0
        redundancy_penalty = 0
        seed_list = list(selected_seeds)
        if len(seed_list) == 2:
            u1_id, u2_id = seed_list[0], seed_list[1]
            u1, u2 = users[u1_id], users[u2_id]
            if u1['tier'] == 'top_tier' and u2['tier'] == 'top_tier':
                if u1['community'] != u2['community']:
                    synergy_bonus = synergy_bonus_val
                else:
                    redundancy_penalty = redundancy_penalty_val

        # Final score calculation based on problem description
        calculated_score = (len(activated) * 10)
        if calculated_key_user_activated:
            calculated_score += 50
        calculated_score += synergy_bonus
        calculated_score -= redundancy_penalty

        if calculated_score != reported_score:
            return False, f"Mismatch in final score: calculated {calculated_score}, reported {reported_score}"

        # Check optimality
        if calculated_cost != EXPECTED_OPTIMAL_COST:
            return False, f"Not optimal: total_cost={calculated_cost}, expected {EXPECTED_OPTIMAL_COST}"

        return True, f"Solution valid and optimal (total_cost={EXPECTED_OPTIMAL_COST})"

    except Exception as e:
        return False, f"Validation failed with an exception: {e}"


def get_hardcoded_instance():
    """Hardcoded instance data for validation"""
    return {
      "users": [
        {"id": "u1", "cost": 250, "category": "influencer", "activation_threshold": 10},
        {"id": "u2", "cost": 80, "category": "regular", "activation_threshold": 60},
        {"id": "u3", "cost": 70, "category": "regular", "activation_threshold": 90},
        {"id": "u4", "cost": 150, "category": "expert", "activation_threshold": 100},
        {"id": "u5", "cost": 90, "category": "regular", "activation_threshold": 70},
        {"id": "u6", "cost": 200, "category": "influencer", "activation_threshold": 120},
        {"id": "u7", "cost": 300, "category": "influencer", "activation_threshold": 10},
        {"id": "u8", "cost": 110, "category": "regular", "activation_threshold": 40},
        {"id": "u9", "cost": 60, "category": "regular", "activation_threshold": 80},
        {"id": "u10", "cost": 220, "category": "expert", "activation_threshold": 150},
        {"id": "u11", "cost": 50, "category": "regular", "activation_threshold": 50},
        {"id": "u12", "cost": 130, "category": "regular", "activation_threshold": 90},
        {"id": "u13", "cost": 280, "category": "influencer", "activation_threshold": 10},
        {"id": "u14", "cost": 85, "category": "regular", "activation_threshold": 60},
        {"id": "u15", "cost": 180, "category": "expert", "activation_threshold": 10},
        {"id": "u16", "cost": 95, "category": "regular", "activation_threshold": 50},
        {"id": "u17", "cost": 40, "category": "regular", "activation_threshold": 100},
        {"id": "u18", "cost": 190, "category": "expert", "activation_threshold": 110},
        {"id": "u19", "cost": 210, "category": "influencer", "activation_threshold": 130},
        {"id": "u20", "cost": 75, "category": "regular", "activation_threshold": 70},
        {"id": "u21", "cost": 100, "category": "expert", "activation_threshold": 80},
        {"id": "u22", "cost": 120, "category": "regular", "activation_threshold": 10},
        {"id": "u23", "cost": 140, "category": "regular", "activation_threshold": 120},
        {"id": "u24", "cost": 160, "category": "expert", "activation_threshold": 90},
        {"id": "u25", "cost": 240, "category": "influencer", "activation_threshold": 10}
      ],
      "connections": [
        {"from": "u1", "to": "u2", "strength": 70},
        {"from": "u1", "to": "u5", "strength": 50},
        {"from": "u7", "to": "u8", "strength": 50},
        {"from": "u7", "to": "u9", "strength": 30},
        {"from": "u15", "to": "u16", "strength": 60},
        {"from": "u22", "to": "u5", "strength": 30},
        {"from": "u2", "to": "u3", "strength": 40},
        {"from": "u8", "to": "u3", "strength": 50},
        {"from": "u8", "to": "u9", "strength": 60}
      ],
      "budget": {"total": 1000, "influencer": 600},
      "max_seeds": 5,
      "required_seed_category": "expert",
      "optimization_weights": {"reach": 10, "diversity": 20, "cost": -1}
    }

def main():
    if len(sys.argv) > 1:
        # For local testing: `ground_truth.py instance.json solution.json`
        instance_file = sys.argv[1]
        solution_file = sys.argv[2]
        with open(instance_file, 'r') as f:
            instance = json.load(f)
        with open(solution_file, 'r') as f:
            solution = json.load(f)
    else:
        # For agent use: reads from stdin
        try:
            data = json.loads(sys.stdin.read())
            # Check if bundled format or solution-only
            if isinstance(data, dict) and 'instance' in data and 'solution' in data:
                instance = data['instance']
                solution = data['solution']
            else:
                # Solution-only format - use hardcoded instance
                instance = get_hardcoded_instance()
                solution = data
        except json.JSONDecodeError as e:
            print(json.dumps({"valid": False, "message": f"Invalid JSON provided: {e}"}))
            return

    is_valid, message = validate_solution(instance, solution)
    print(json.dumps({"valid": is_valid, "message": message}))


if __name__ == "__main__":
    main()
