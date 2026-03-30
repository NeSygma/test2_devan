#!/usr/bin/env python3
"""
Reference model for Problem 046: Metroidvania Generation
Validates solution from stdin
"""

import json
import sys

def verify_reachability(connections, item_locations):
    """
    Verify that all rooms are reachable without soft-locks.
    """

    # Build adjacency graph
    graph = {}
    for conn in connections:
        from_room = conn["from"]
        to_room = conn["to"]
        requires = conn.get("requires")

        if from_room not in graph:
            graph[from_room] = []
        graph[from_room].append({"to": to_room, "requires": requires})

    # Progressive reachability check
    start_room = "A"
    reachable_rooms = {start_room}
    available_items = set()

    # Keep expanding until no new rooms can be reached
    changed = True
    while changed:
        changed = False
        new_reachable = set(reachable_rooms)

        # Collect items in currently reachable rooms
        for item, location in item_locations.items():
            if location in reachable_rooms:
                available_items.add(item)

        for room in reachable_rooms:
            # Try to reach new rooms
            if room in graph:
                for connection in graph[room]:
                    target = connection["to"]
                    required_item = connection["requires"]

                    # Can reach if no requirement or we have the item
                    if target not in reachable_rooms:
                        if required_item is None or required_item in available_items:
                            new_reachable.add(target)
                            changed = True

        reachable_rooms = new_reachable

    # Check if all rooms are reachable
    all_rooms = {"A", "B", "C", "D", "E", "F", "G", "H"}
    return reachable_rooms == all_rooms

def validate_solution(solution):
    """
    Validate the solution structure and constraints.
    """

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    # Check required fields
    required_fields = ["rooms", "connections", "item_locations", "reachability_verified"]
    for field in required_fields:
        if field not in solution:
            return {"valid": False, "message": f"Missing required field: {field}"}

    rooms = solution["rooms"]
    connections = solution["connections"]
    item_locations = solution["item_locations"]
    reachability_verified = solution["reachability_verified"]

    # Check rooms format
    if not isinstance(rooms, list) or len(rooms) != 8:
        return {"valid": False, "message": f"Expected 8 rooms, got {len(rooms) if isinstance(rooms, list) else 'invalid type'}"}

    expected_rooms = {"A", "B", "C", "D", "E", "F", "G", "H"}
    if set(rooms) != expected_rooms:
        return {"valid": False, "message": f"Expected rooms A-H, got {set(rooms)}"}

    # Check connections format
    if not isinstance(connections, list):
        return {"valid": False, "message": "Connections must be a list"}

    if len(connections) == 0:
        return {"valid": False, "message": "No connections defined"}

    for i, conn in enumerate(connections):
        if not isinstance(conn, dict):
            return {"valid": False, "message": f"Connection {i} is not a dictionary"}

        if "from" not in conn or "to" not in conn or "requires" not in conn:
            return {"valid": False, "message": f"Connection {i} missing required fields (from/to/requires)"}

        if conn["from"] not in expected_rooms:
            return {"valid": False, "message": f"Connection {i}: invalid 'from' room {conn['from']}"}

        if conn["to"] not in expected_rooms:
            return {"valid": False, "message": f"Connection {i}: invalid 'to' room {conn['to']}"}

        if conn["requires"] is not None and conn["requires"] not in ["key1", "key2", "key3"]:
            return {"valid": False, "message": f"Connection {i}: invalid key requirement {conn['requires']}"}

    # Check item locations format
    if not isinstance(item_locations, dict):
        return {"valid": False, "message": "item_locations must be a dictionary"}

    expected_keys = {"key1", "key2", "key3"}
    if set(item_locations.keys()) != expected_keys:
        return {"valid": False, "message": f"Expected keys {expected_keys}, got {set(item_locations.keys())}"}

    for key, location in item_locations.items():
        if location not in expected_rooms:
            return {"valid": False, "message": f"Key {key} placed in invalid room {location}"}

    # Check reachability flag type
    if not isinstance(reachability_verified, bool):
        return {"valid": False, "message": "reachability_verified must be a boolean"}

    # Verify reachability independently
    actual_reachability = verify_reachability(connections, item_locations)

    if not actual_reachability:
        return {"valid": False, "message": "Not all rooms are reachable - soft-lock detected"}

    if reachability_verified != actual_reachability:
        return {"valid": False, "message": f"reachability_verified flag ({reachability_verified}) does not match actual reachability ({actual_reachability})"}

    return {"valid": True, "message": "Solution is valid - all rooms reachable without soft-locks"}

if __name__ == "__main__":
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            result = {"valid": False, "message": "No input provided"}
        else:
            solution = json.loads(input_data)
            result = validate_solution(solution)
        print(json.dumps(result))
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {str(e)}"}))
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Validation error: {str(e)}"}))
