#!/usr/bin/env python3
"""
Reference Model & Verifier: Byzantine Generals with Hierarchy and Deception
============================================================================
This model simulates the hierarchical consensus protocol to verify a solution.
It iterates through all possible traitor combinations to see if any of them
produce the submitted consensus.
"""

import sys
import json
from itertools import combinations

# --- Problem Instance Definition ---
GENERALS = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6']
RANKS = {'G1': 'commander', 'G2': 'lieutenant', 'G3': 'lieutenant', 'G4': 'sergeant', 'G5': 'sergeant', 'G6': 'sergeant'}
RANK_ORDER = {'commander': 3, 'lieutenant': 2, 'sergeant': 1}
RANK_WEIGHT = {'commander': 3, 'lieutenant': 2, 'sergeant': 1}
PROPOSALS = {'G1': 1, 'G2': 1, 'G3': 0, 'G4': 0, 'G5': 1, 'G6': 1}
HIGH_TRUST = {('G1', 'G2'), ('G2', 'G1')}
TRUST_BONUS = 1
NUM_TRAITORS = 2
NUM_ROUNDS = 2

def simulate_protocol(traitors):
    """
    Simulates the full 2-round protocol for a given set of traitors.
    Returns the final beliefs of all honest generals.
    """
    traitors = set(traitors)
    honest_generals = [g for g in GENERALS if g not in traitors]

    # Initialize beliefs from initial proposals
    beliefs = {r: {g: PROPOSALS[g] for g in GENERALS} for r in range(NUM_ROUNDS + 1)}

    for r in range(1, NUM_ROUNDS + 1):
        # Gather messages for this round
        messages = {g: {} for g in GENERALS}
        for sender in GENERALS:
            sender_belief = beliefs[r-1][sender]
            for receiver in GENERALS:
                if sender == receiver:
                    continue

                is_traitor = sender in traitors
                sent_value = sender_belief

                if is_traitor:
                    # Traitor's deception logic
                    if RANK_ORDER[RANKS[receiver]] <= RANK_ORDER[RANKS[sender]]:
                        sent_value = 1 - sender_belief # Lie

                messages[receiver][sender] = sent_value

        # Honest generals update their beliefs
        for g in honest_generals:
            votes = {0: 0, 1: 0}
            for sender, value in messages[g].items():
                weight = RANK_WEIGHT[RANKS[sender]]
                if (g, sender) in HIGH_TRUST:
                    weight += TRUST_BONUS
                votes[value] += weight

            if votes[1] > votes[0]:
                beliefs[r][g] = 1
            elif votes[0] > votes[1]:
                beliefs[r][g] = 0
            else:
                beliefs[r][g] = 0 # Tie-break to 0

    final_beliefs = {g: beliefs[NUM_ROUNDS][g] for g in honest_generals}
    return final_beliefs

def verify_solution(solution_data):
    """
    Verifies the submitted solution by simulating the protocol for all
    possible traitor combinations.
    """
    try:
        submitted_consensus = solution_data["consensus_value"]
        submitted_beliefs = {item['general']: item['belief'] for item in solution_data["final_beliefs"]}
    except (KeyError, TypeError) as e:
        return {"valid": False, "message": f"Invalid JSON structure: {e}"}

    # Iterate through all possible pairs of traitors
    for traitor_combo in combinations(GENERALS, NUM_TRAITORS):
        final_beliefs = simulate_protocol(traitor_combo)

        # Check for agreement among honest generals
        honest_values = list(final_beliefs.values())
        if not all(v == honest_values[0] for v in honest_values):
            continue # This traitor combo doesn't lead to consensus

        # A valid consensus was found for this traitor combo
        calculated_consensus = honest_values[0]

        # Check if the calculated consensus and beliefs match the submission
        if calculated_consensus == submitted_consensus and final_beliefs == submitted_beliefs:
            return {"valid": True, "message": f"Correct consensus found. Traitors could be {traitor_combo}."}

    return {"valid": False, "message": "Submitted consensus is not achievable under the protocol rules for any traitor combination."}


if __name__ == "__main__":
    if not sys.stdin.isatty():
        try:
            solution_json = sys.stdin.read()
            solution_data = json.loads(solution_json)
            result = verify_solution(solution_data)
        except json.JSONDecodeError:
            result = {"valid": False, "message": "Invalid JSON input."}
        except Exception as e:
            result = {"valid": False, "message": f"An unexpected error occurred during verification: {e}"}
        print(json.dumps(result))
    else:
        print("This script is a verifier. Pipe a JSON solution to its stdin.")
