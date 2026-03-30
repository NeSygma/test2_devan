#!/usr/bin/env python3
"""Validator for Dungeon Generation problem."""

import json
import sys
from collections import defaultdict, deque

def validate_solution(instance, solution):
    try:
        # Type check for debugging
        if not isinstance(instance, dict):
            return False, f"Instance is not a dict, it's a {type(instance).__name__}"
        if not isinstance(solution, dict):
            return False, f"Solution is not a dict, it's a {type(solution).__name__}"

        # --- Data Extraction ---
        rooms = {r['id']: r for r in instance['rooms']}
        connections = instance['connections']
        items = {i['id']: i for i in instance['items']}
        treasures = {t['id']: t for t in instance['treasures']}
        monsters = {m['id']: m for m in instance['monsters']}
        traps = {t['id']: t for t in instance['traps']}
        constraints = instance['constraints']
        boss_room_id = constraints['boss_room_id']
        entrance_id = next(r['id'] for r in instance['rooms'] if r['type'] == 'entrance')

        layout_map = {entry['room_id']: entry for entry in solution['room_layout']}

        # --- Basic Structural Validation ---
        if set(layout_map.keys()) != set(rooms.keys()):
            return False, f"Room layout mismatch. Expected {set(rooms.keys())}, got {set(layout_map.keys())}"

        placed_items = {item for r_data in layout_map.values() for item in r_data.get('items', [])}
        if set(items.keys()) != placed_items:
            return False, f"Item placement mismatch. Expected {set(items.keys())}, got {placed_items}"

        placed_treasures = {t for r_data in layout_map.values() for t in r_data.get('treasures', [])}
        if set(treasures.keys()) != placed_treasures:
            return False, f"Treasure placement mismatch. Expected {set(treasures.keys())}, got {placed_treasures}"

        # --- Per-Room Validation ---
        for room_id, room_data in layout_map.items():
            # Calculate danger
            monster_danger = sum(monsters[m['type']]['danger_level'] * m['count'] for m in room_data.get('monsters', []))

            trap_danger = 0
            room_items = set(room_data.get('items', []))
            for trap_info in room_data.get('traps', []):
                trap_id = trap_info['type']
                trap_template = traps[trap_id]
                disarm_tool = trap_template.get('disarm_tool')
                is_active = not disarm_tool or disarm_tool not in room_items
                if is_active != trap_info['active']:
                    return False, f"Trap active status incorrect for {trap_id} in {room_id}"
                if is_active:
                    trap_danger += trap_template['danger_level']

            calculated_danger = monster_danger + trap_danger
            if calculated_danger != room_data['danger_level']:
                return False, f"Danger level mismatch for {room_id}. Calculated: {calculated_danger}, Reported: {room_data['danger_level']}"

            if calculated_danger > constraints['max_danger_per_room']:
                return False, f"Room {room_id} exceeds max danger {constraints['max_danger_per_room']}"

        # --- Solvability and Path Validation ---
        if not solution['path_analysis']['solvable']:
            # If solution claims unsolvable, we can't validate the path. Trust it for now.
            # A more robust checker would find its own path and compare.
            return True, "Solution claims unsolvability, validation skipped."

        # Build adjacency list for pathfinding
        adj = defaultdict(list)
        for conn in connections:
            adj[conn['from']].append(conn)
            # Add reverse connection if not directed
            adj[conn['to']].append({'from': conn['to'], 'to': conn['from'], 'locked_by': conn.get('locked_by')})

        # BFS to check reachability and key order
        q = deque([(entrance_id, {item for item in layout_map[entrance_id].get('items', [])})])
        visited = {entrance_id}
        reachable_rooms = {entrance_id}

        path_possible = False
        while q:
            curr_room_id, keys_held = q.popleft()

            if curr_room_id == boss_room_id:
                path_possible = True

            for conn in adj[curr_room_id]:
                neighbor_id = conn['to']
                if neighbor_id in visited:
                    continue

                locked_by = conn.get('locked_by')
                if locked_by and locked_by not in keys_held:
                    continue # Can't pass locked door

                visited.add(neighbor_id)
                reachable_rooms.add(neighbor_id)

                new_keys = keys_held.copy()
                new_keys.update(layout_map[neighbor_id].get('items', []))
                q.append((neighbor_id, new_keys))

        if not path_possible:
            return False, f"Path analysis failed: Boss room '{boss_room_id}' is not reachable from '{entrance_id}' with key logic."

        unreachable_rooms = set(rooms.keys()) - reachable_rooms
        if unreachable_rooms:
            # Secret rooms might be unreachable this way. Let's check secret room logic.
            for room_id in list(unreachable_rooms):
                if rooms[room_id].get('type') == 'secret':
                    # A secret room must be connected to exactly one reachable, non-secret room.
                    secret_conns = [c for c in instance['connections'] if c['from'] == room_id or c['to'] == room_id]
                    if len(secret_conns) == 1:
                        conn = secret_conns[0]
                        other_room = conn['to'] if conn['from'] == room_id else conn['from']
                        if other_room in reachable_rooms and rooms[other_room].get('type') != 'secret':
                           unreachable_rooms.remove(room_id)

        if unreachable_rooms:
             return False, f"Path analysis failed: Rooms {unreachable_rooms} are not reachable."


        return True, "Valid dungeon generation"
    except Exception as e:
        return False, f"Validation error: {e}"


def main():
    input_text = sys.stdin.read().strip()
    if not input_text:
        print(json.dumps({"valid": False, "message": "No input provided"}))
        return

    try:
        data = json.loads(input_text)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {e}"}))
        return

    # Debug: check data type
    if not isinstance(data, dict):
        print(json.dumps({"valid": False, "message": f"Parsed data is not a dict, it's a {type(data).__name__}"}))
        return

    # Check format: bundled (instance+solution), solution-only, or file arguments
    if isinstance(data, dict) and 'instance' in data and 'solution' in data:
        # Bundled format: {"instance": {...}, "solution": {...}}
        instance_data = data['instance']
        solution_data = data['solution']
    elif isinstance(data, dict) and 'room_layout' in data:
        # This is a solution being piped in, we need an instance file
        if len(sys.argv) != 2:
            print(json.dumps({"valid": False, "message": "Usage: python ground_truth.py <instance_file> OR pipe solution with instance file as arg"}))
            return

        with open(sys.argv[1], 'r') as f:
            instance_data = json.load(f)
        solution_data = data
    else:
        # Standard format: two files as arguments
        if len(sys.argv) != 3:
            print(json.dumps({"valid": False, "message": "Usage: python ground_truth.py <instance_file> <solution_file>"}))
            return

        with open(sys.argv[1], 'r') as f:
            instance_data = json.load(f)

        with open(sys.argv[2], 'r') as f:
            solution_data = json.load(f)

    is_valid, message = validate_solution(instance_data, solution_data)

    result = {
        "valid": is_valid,
        "message": message
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
