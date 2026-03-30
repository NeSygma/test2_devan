#!/usr/bin/env python3

import json
import sys

def validate_solution():
    """Validate the historical counterfactual reasoning solution from stdin."""

    try:
        # Read solution from stdin
        data = sys.stdin.read().strip()
        if not data:
            return {"valid": False, "message": "No solution provided"}

        solution = json.loads(data)

        # Define the instance data
        events = {
            "discovery_of_america": {
                "year": 1492,
                "prerequisites": [],
                "enables": ["columbian_exchange", "spanish_empire"]
            },
            "columbian_exchange": {
                "year": 1500,
                "prerequisites": ["discovery_of_america"],
                "enables": []
            },
            "spanish_empire": {
                "year": 1520,
                "prerequisites": ["discovery_of_america"],
                "enables": ["industrial_revolution"]
            },
            "industrial_revolution": {
                "year": 1750,
                "prerequisites": ["spanish_empire"],
                "enables": ["world_wars"]
            },
            "world_wars": {
                "year": 1914,
                "prerequisites": ["industrial_revolution"],
                "enables": []
            }
        }

        intervention = "discovery_of_america"

        # Extract solution components
        original_timeline = solution.get("original_timeline", [])
        alternate_timeline = solution.get("alternate_timeline", [])
        prevented_events = solution.get("prevented_events", [])
        causal_analysis = solution.get("causal_analysis", {})

        # Validate original timeline
        if len(original_timeline) != len(events):
            return {"valid": False, "message": f"Original timeline has {len(original_timeline)} events, expected {len(events)}"}

        occurred_events = set()
        for event_id in original_timeline:
            if event_id not in events:
                return {"valid": False, "message": f"Unknown event {event_id} in original timeline"}

            event = events[event_id]
            for prereq in event["prerequisites"]:
                if prereq not in occurred_events:
                    return {"valid": False, "message": f"Event {event_id} occurs before prerequisite {prereq}"}

            occurred_events.add(event_id)

        # Validate prevention cascade
        prevented_set = set(prevented_events)

        # Intervention event must be prevented
        if intervention not in prevented_set:
            return {"valid": False, "message": f"Intervention event {intervention} not in prevented_events"}

        # Check cascade: events with prevented prerequisites must be prevented
        for event_id, event in events.items():
            has_prevented_prereq = any(prereq in prevented_set for prereq in event["prerequisites"])
            if has_prevented_prereq and event_id not in prevented_set:
                return {"valid": False, "message": f"Event {event_id} has prevented prerequisite but is not prevented"}

        # Check alternate timeline doesn't contain prevented events
        for event_id in alternate_timeline:
            if event_id in prevented_set:
                return {"valid": False, "message": f"Prevented event {event_id} appears in alternate timeline"}

        # Check alternate timeline order
        alt_occurred = set()
        for event_id in alternate_timeline:
            if event_id not in events:
                return {"valid": False, "message": f"Unknown event {event_id} in alternate timeline"}

            event = events[event_id]
            for prereq in event["prerequisites"]:
                if prereq not in prevented_set and prereq not in alt_occurred:
                    return {"valid": False, "message": f"Alternate timeline: {event_id} occurs before prerequisite {prereq}"}

            alt_occurred.add(event_id)

        # Validate causal analysis components
        direct_effects = set(causal_analysis.get("direct_effects", []))
        cascade_effects = set(causal_analysis.get("cascade_effects", []))
        preserved_events_list = set(causal_analysis.get("preserved_events", []))
        intervention_events = set(causal_analysis.get("intervention_events", []))

        # Intervention events should be exactly the intervention
        if intervention_events != {intervention}:
            return {"valid": False, "message": f"Expected intervention_events to be {{{intervention}}}, got {intervention_events}"}

        # Preserved events should be exactly the alternate timeline
        if preserved_events_list != set(alternate_timeline):
            return {"valid": False, "message": "Preserved events don't match alternate timeline"}

        # All events should be accounted for
        all_categorized = direct_effects | cascade_effects | preserved_events_list | intervention_events
        if all_categorized != set(events.keys()):
            missing = set(events.keys()) - all_categorized
            extra = all_categorized - set(events.keys())
            msg = []
            if missing:
                msg.append(f"missing events: {missing}")
            if extra:
                msg.append(f"extra events: {extra}")
            return {"valid": False, "message": f"Causal analysis incomplete: {', '.join(msg)}"}

        # Check no overlap between categories
        categories = [
            ("direct_effects", direct_effects),
            ("cascade_effects", cascade_effects),
            ("preserved_events", preserved_events_list),
            ("intervention_events", intervention_events)
        ]

        for i, (name1, set1) in enumerate(categories):
            for name2, set2 in categories[i+1:]:
                if set1 & set2:
                    return {"valid": False, "message": f"{name1} and {name2} overlap: {set1 & set2}"}

        return {"valid": True, "message": "Valid historical counterfactual analysis"}

    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {str(e)}"}
    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}

if __name__ == "__main__":
    result = validate_solution()
    print(json.dumps(result))
