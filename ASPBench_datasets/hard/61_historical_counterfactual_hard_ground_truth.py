#!/usr/bin/env python3

import json
import sys
from collections import defaultdict

def validate_solution(data):
    """
    Validates the entire solution by re-implementing the causal logic in Python.
    This ground_truth is complex because the problem logic is complex.
    """
    try:
        instance = data["instance"]
        solution = data["solution"]

        events = {e["id"]: e for e in instance["events"]}
        prereqs = defaultdict(list)
        for p in instance["prerequisites"]:
            prereqs[p["event"]].append(p["requires"])

        cond_prereqs = defaultdict(list)
        for cp in instance["conditional_prerequisites"]:
            cond_prereqs[cp["event"]].append({"requires": cp["requires"], "unless": cp["unless"]})

        pivots = defaultdict(list)
        for p in instance["pivots"]:
            pivots[p["group"]].append(p["event"])

        interventions = {i["event_id"]: i["action"] for i in instance["interventions"]}

        # --- 1. Validate Original Timeline ---
        original_timeline = set(solution["original_timeline"])
        occurred_original = set()

        # Sort events by year to process in order
        sorted_events_original = sorted(solution["original_timeline"], key=lambda e_id: events[e_id]["year"])

        for event_id in sorted_events_original:
            if not all(p in occurred_original for p in prereqs[event_id]):
                return False, f"Original timeline: Prereq for {event_id} not met."

            # Conditional prereqs (original timeline has no "unless" conditions met if they are not chosen)
            for cp in cond_prereqs[event_id]:
                if cp["requires"] not in occurred_original:
                     return False, f"Original timeline: Conditional prereq {cp['requires']} for {event_id} not met."
                if cp["unless"] in original_timeline:
                     return False, f"Original timeline: Conditional prereq for {event_id} violated by presence of {cp['unless']}."

            occurred_original.add(event_id)

        # Validate pivot choices in original timeline (earliest year wins)
        for group, pivot_events in pivots.items():
            possible_pivots = []
            for p_event in pivot_events:
                if all(p in original_timeline for p in prereqs[p_event]):
                    possible_pivots.append(p_event)

            if not possible_pivots:
                continue

            chosen_pivot = next((p for p in possible_pivots if p in original_timeline), None)
            if not chosen_pivot:
                 return False, f"Original timeline: Pivot group '{group}' has possible events but none were chosen."

            winner = min(possible_pivots, key=lambda e_id: events[e_id]["year"])
            if chosen_pivot != winner:
                return False, f"Original timeline: Pivot choice for '{group}' should have been '{winner}' but was '{chosen_pivot}'."

            if len([p for p in possible_pivots if p in original_timeline]) > 1:
                return False, f"Original timeline: Multiple events from pivot group '{group}' occurred."

        # --- 2. Validate Alternate Timeline ---
        alternate_timeline = set(solution["alternate_timeline"])

        for event_id in interventions:
            if event_id in alternate_timeline:
                return False, f"Alternate timeline contains intervened event '{event_id}'."

        for event_id in alternate_timeline:
            # Check normal prerequisites
            if not all(p in alternate_timeline for p in prereqs[event_id]):
                return False, f"Alternate timeline: Prereq for {event_id} not met."

            # Check conditional prerequisites
            for cp in cond_prereqs[event_id]:
                # If "unless" condition is met, the requirement is waived
                if cp["unless"] in alternate_timeline:
                    continue  # Skip this conditional prereq - the "unless" clause applies
                # Otherwise, check the requirement
                if cp["requires"] not in alternate_timeline:
                    return False, f"Alternate timeline: Conditional prereq '{cp['requires']}' for {event_id} not met."

        # Validate pivot choices in alternate timeline
        for group, pivot_events in pivots.items():
            occurred_pivots = [p for p in pivot_events if p in alternate_timeline]
            if len(occurred_pivots) > 1:
                return False, f"Alternate timeline: Multiple events from pivot group '{group}' occurred: {occurred_pivots}."

            possible_pivots = []
            for p_event in pivot_events:
                if p_event in interventions: continue
                if all(p in alternate_timeline for p in prereqs[p_event]):
                    possible_pivots.append(p_event)

            if possible_pivots and not occurred_pivots:
                return False, f"Alternate timeline: Pivot group '{group}' had possible events but none were chosen."

        # --- 3. Validate Analysis Fields ---
        all_event_ids = set(events.keys())
        calculated_prevented = sorted(list(all_event_ids - alternate_timeline))
        if calculated_prevented != sorted(solution["prevented_events"]):
            return False, f"Prevented events list is incorrect. Expected {calculated_prevented}, got {solution['prevented_events']}"

        calculated_activated = sorted(list(alternate_timeline - original_timeline))
        if calculated_activated != sorted(solution["activated_events"]):
            return False, f"Activated events list is incorrect. Expected {calculated_activated}, got {solution['activated_events']}"

        if solution["paradoxes"]:
             return False, f"Solution claims to be valid but found paradoxes: {solution['paradoxes']}"

        return True, "Solution is valid and adheres to all complex causal rules."

    except Exception as e:
        return False, f"Validation failed with exception: {e}"


def main():
    try:
        data = json.loads(sys.stdin.read())
        is_valid, message = validate_solution(data)
    except json.JSONDecodeError as e:
        is_valid = False
        message = f"Failed to decode JSON from stdin: {e}"
    except Exception as e:
        is_valid = False
        message = f"An unexpected error occurred during validation: {e}"

    print(json.dumps({"valid": is_valid, "message": message}))


if __name__ == "__main__":
    main()