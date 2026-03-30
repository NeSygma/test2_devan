#!/usr/bin/env python3
"""
Reference model for Social Network Influence Maximization (Easy)
Validates solution from stdin and checks optimality.
"""

import json
import sys
from collections import defaultdict

# Expected optimal value
EXPECTED_OPTIMAL_REACH = 8

def validate_solution(solution_data):
    """Validate the social network influence maximization solution."""

    # Instance data
    users = {
        "user1": {"influence_weight": 0.8, "cost": 100, "category": "influencer"},
        "user2": {"influence_weight": 0.3, "cost": 50, "category": "regular"},
        "user3": {"influence_weight": 0.5, "cost": 80, "category": "regular"},
        "user4": {"influence_weight": 0.9, "cost": 150, "category": "influencer"},
        "user5": {"influence_weight": 0.4, "cost": 60, "category": "regular"},
        "user6": {"influence_weight": 0.6, "cost": 90, "category": "regular"},
        "user7": {"influence_weight": 0.7, "cost": 120, "category": "influencer"},
        "user8": {"influence_weight": 0.2, "cost": 40, "category": "regular"}
    }

    connections = [
        {"from": "user1", "to": "user2", "strength": 0.6},
        {"from": "user1", "to": "user3", "strength": 0.7},
        {"from": "user2", "to": "user3", "strength": 0.4},
        {"from": "user2", "to": "user5", "strength": 0.5},
        {"from": "user3", "to": "user4", "strength": 0.3},
        {"from": "user4", "to": "user5", "strength": 0.8},
        {"from": "user4", "to": "user6", "strength": 0.6},
        {"from": "user5", "to": "user7", "strength": 0.5},
        {"from": "user6", "to": "user7", "strength": 0.7},
        {"from": "user7", "to": "user8", "strength": 0.4}
    ]

    budget = 300
    max_seeds = 2

    try:
        # Build adjacency graph
        graph = defaultdict(list)
        for conn in connections:
            graph[conn["from"]].append({
                "to": conn["to"],
                "strength": conn["strength"]
            })

        # Extract solution
        selected_seeds = solution_data.get("selected_seeds", [])
        cascade_analysis = solution_data.get("cascade_analysis", {})
        network_metrics = solution_data.get("network_metrics", {})

        # Validate seed selection constraints
        if len(selected_seeds) > max_seeds:
            return {"valid": False, "message": f"Too many seeds selected: {len(selected_seeds)} > {max_seeds}"}

        total_cost = 0
        selected_user_ids = set()

        for seed in selected_seeds:
            user_id = seed["user_id"]
            cost = seed["cost"]
            expected_reach = seed["expected_reach"]

            if user_id not in users:
                return {"valid": False, "message": f"Unknown user: {user_id}"}

            if user_id in selected_user_ids:
                return {"valid": False, "message": f"User {user_id} selected multiple times"}

            selected_user_ids.add(user_id)

            # Validate cost
            if cost != users[user_id]["cost"]:
                return {"valid": False, "message": f"Incorrect cost for {user_id}: {cost} != {users[user_id]['cost']}"}

            total_cost += cost

            # Validate expected reach is reasonable
            if expected_reach < 0 or expected_reach > len(users):
                return {"valid": False, "message": f"Invalid expected reach for {user_id}: {expected_reach}"}

        # Validate budget constraint
        if total_cost > budget:
            return {"valid": False, "message": f"Budget exceeded: {total_cost} > {budget}"}

        # Validate budget used in cascade analysis
        if cascade_analysis.get("total_budget_used", 0) != total_cost:
            return {"valid": False, "message": f"Budget used mismatch: {cascade_analysis.get('total_budget_used', 0)} != {total_cost}"}

        # Validate cascade analysis
        direct_influence = set(cascade_analysis.get("direct_influence", []))
        secondary_influence = set(cascade_analysis.get("secondary_influence", []))
        total_reach = cascade_analysis.get("total_reach", 0)
        influence_probability = cascade_analysis.get("influence_probability", 0)

        # Check influence probability bounds
        if not (0 <= influence_probability <= 1):
            return {"valid": False, "message": f"Invalid influence probability: {influence_probability}"}

        # Validate secondary influence doesn't overlap with direct
        if direct_influence & secondary_influence:
            return {"valid": False, "message": f"Direct and secondary influence overlap: {direct_influence & secondary_influence}"}

        # Check that influenced users exist
        all_influenced = direct_influence | secondary_influence
        for user_id in all_influenced:
            if user_id not in users:
                return {"valid": False, "message": f"Unknown influenced user: {user_id}"}

        # Validate total reach
        if total_reach != len(selected_user_ids) + len(all_influenced):
            return {"valid": False, "message": f"Total reach mismatch: {total_reach} != {len(selected_user_ids) + len(all_influenced)}"}

        # Validate network metrics
        coverage_ratio = network_metrics.get("coverage_ratio", 0)
        efficiency_score = network_metrics.get("efficiency_score", 0)
        cascade_depth = network_metrics.get("cascade_depth", 0)

        # Validate coverage ratio
        expected_coverage = total_reach / len(users)
        if abs(coverage_ratio - expected_coverage) > 0.01:
            return {"valid": False, "message": f"Coverage ratio mismatch: {coverage_ratio} != {expected_coverage:.3f}"}

        # Validate efficiency score (reach per unit cost)
        if total_cost > 0:
            expected_efficiency = total_reach / total_cost
            if abs(efficiency_score - expected_efficiency) > 0.1:
                return {"valid": False, "message": f"Efficiency score mismatch: {efficiency_score} != {expected_efficiency:.3f}"}

        # Validate cascade depth
        if cascade_depth < 1 or cascade_depth > len(users):
            return {"valid": False, "message": f"Invalid cascade depth: {cascade_depth}"}

        # Check optimality
        if total_reach != EXPECTED_OPTIMAL_REACH:
            return {"valid": False, "message": f"Not optimal: total_reach={total_reach}, expected {EXPECTED_OPTIMAL_REACH}"}

        return {"valid": True, "message": f"Solution is valid and optimal (total_reach={EXPECTED_OPTIMAL_REACH}, total_cost={total_cost})"}

    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}

def main():
    try:
        data = sys.stdin.read().strip()
        if not data:
            result = {"valid": False, "message": "No solution provided"}
        else:
            solution_data = json.loads(data)
            result = validate_solution(solution_data)
    except json.JSONDecodeError as e:
        result = {"valid": False, "message": f"Invalid JSON: {str(e)}"}

    print(json.dumps(result))

if __name__ == "__main__":
    main()
