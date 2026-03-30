#!/usr/bin/env python3
"""
Reference model for Problem 046 (Hard): Metroidvania Generation

Validates a Metroidvania level layout against all problem constraints.
Reads solution from stdin and outputs JSON validation result.
"""

import json
import sys
from collections import defaultdict

def verify_solution(solution: dict) -> tuple:
    """
    Verifies the provided Metroidvania level solution against all constraints.
    Returns (is_valid, message) tuple.
    """
    # Define problem constants
    all_room_names = {f"R{i}" for i in range(1, 11)} | {"Start", "Goal"}
    all_item_names = {"RedKey", "BlueKey", "GreenKey", "YellowKey", "Grapple", "Boots"}

    # C1: Check basic structure and placement rules
    try:
        special_types = solution["special_room_types"]
        item_locs = solution["item_locations"]
        connections = solution["connections"]

        if set(special_types.keys()) != {"Flooded", "Chasm"}:
            return False, "Must have exactly 'Flooded' and 'Chasm' special rooms."
        flooded_room = special_types["Flooded"]
        chasm_room = special_types["Chasm"]
        if flooded_room == chasm_room:
            return False, "Flooded and Chasm rooms must be different."
        if not ({flooded_room, chasm_room} <= (all_room_names - {"Start", "Goal"})):
            return False, "Special rooms must be within R1-R10."

        if set(item_locs.keys()) != all_item_names:
            return False, "Incorrect set of items."
        if not (set(item_locs.values()) <= (all_room_names - {"Start", "Goal"})):
            return False, "Items must be placed in rooms R1-R10."

    except (KeyError, TypeError):
        return False, "Missing or malformed top-level fields."

    # C4.4: Equipment cannot be in the room type it is for
    if item_locs["Boots"] == flooded_room:
        return False, "Boots cannot be in the Flooded room."
    if item_locs["Grapple"] == chasm_room:
        return False, "Grapple cannot be in the Chasm room."

    # C5.2: YellowKey must be in the Chasm room
    if item_locs["YellowKey"] != chasm_room:
        return False, "YellowKey must be in the Chasm room."

    # C3: Connection Rules
    graph = defaultdict(list)
    reverse_graph = defaultdict(list)
    all_edges = set()
    for conn in connections:
        c_from, c_to, c_req = conn["from"], conn["to"], conn["requires"]
        if (c_from, c_to) in all_edges:
            return False, f"Duplicate connection: {c_from} -> {c_to}."
        all_edges.add((c_from, c_to))
        graph[c_from].append(conn)
        reverse_graph[c_to].append(c_from)

    # Count bidirectional and one-way connections, and validate keyless return constraint
    bidirectional_pairs_counted = set()
    one_way_count = 0

    for u in graph:
        for u_to_v_conn in graph[u]:
            v = u_to_v_conn["to"]
            u_to_v_req = u_to_v_conn["requires"]

            # Check if reverse exists (v -> u)
            reverse_conns = [c for c in graph.get(v, []) if c["to"] == u]

            pair = tuple(sorted((u, v)))
            if reverse_conns and pair not in bidirectional_pairs_counted:
                # Bidirectional pair
                bidirectional_pairs_counted.add(pair)

                # Check constraint: if u->v uses key, v->u must have keyless option
                if u_to_v_req is not None:
                    if not any(rc["requires"] is None for rc in reverse_conns):
                        return False, f"Keyed connection {u}->{v} requires keyless return path"

                # Check reverse: if any v->u uses key, u->v must have keyless option
                if any(rc["requires"] is not None for rc in reverse_conns):
                    forward_conns = [c for c in graph[u] if c["to"] == v]
                    if not any(fc["requires"] is None for fc in forward_conns):
                        return False, f"Keyed connection {v}->{u} requires keyless return path"

            elif not reverse_conns:
                # One-way connection
                one_way_count += 1

    bidirectional_count = len(bidirectional_pairs_counted)

    if not (10 <= bidirectional_count <= 15):
        return False, f"Expected 10-15 bidirectional connections, found {bidirectional_count}."

    # One one-way path is the goal path, the other is the required one-way path.
    if one_way_count != 2:
        return False, f"Expected 2 one-way connections (one regular, one to Goal), found {one_way_count}."

    if len(graph["Goal"]) != 0:
        return False, "Goal room cannot have outgoing connections."
    if len(reverse_graph["Goal"]) != 1:
        return False, "Goal room must have exactly one incoming connection."

    # C6: Reachability and Progression
    reachable_rooms = {"Start"}
    inventory = set()

    # Simulate progression until no new rooms can be reached
    while True:
        newly_reached_this_iteration = set()

        # Collect items from newly reached rooms
        for room in reachable_rooms:
            for item, loc in item_locs.items():
                if loc == room:
                    inventory.add(item)

        # Try to traverse to new rooms
        for room in list(reachable_rooms):
            for conn in graph.get(room, []):
                next_room = conn["to"]
                if next_room in reachable_rooms:
                    continue

                # Check connection requirement
                req_key = conn["requires"]
                if req_key and req_key not in inventory:
                    continue

                # Check room entry requirement
                if next_room == flooded_room and "Boots" not in inventory:
                    continue
                if next_room == chasm_room and "Grapple" not in inventory:
                    continue

                newly_reached_this_iteration.add(next_room)

        if not newly_reached_this_iteration:
            break

        reachable_rooms.update(newly_reached_this_iteration)

        # C6.2: Check if Goal was reached prematurely
        if "Goal" in newly_reached_this_iteration and len(reachable_rooms) < len(all_room_names):
            return False, "Goal was reached before all other rooms were accessible."

    # C6.1: Check if all rooms are reachable
    if reachable_rooms != all_room_names:
        unreachable = all_room_names - reachable_rooms
        return False, f"Solution is not fully reachable. Unreachable rooms: {unreachable}"

    return True, "Solution satisfies all constraints."


if __name__ == "__main__":
    try:
        solution_json = sys.stdin.read()
        solution = json.loads(solution_json)
        is_valid, message = verify_solution(solution)
        print(json.dumps({"valid": is_valid, "message": message}))
    except json.JSONDecodeError:
        print(json.dumps({"valid": False, "message": "Invalid JSON format."}))
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"An unexpected error occurred during verification: {e}"}))
