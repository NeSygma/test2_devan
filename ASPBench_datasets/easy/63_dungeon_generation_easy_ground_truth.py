#!/usr/bin/env python3

import json
import sys
from collections import defaultdict, deque

def validate_solution(solution_data):
    """Validate the dungeon generation solution."""

    # Define instance data inline
    instance_data = {
        "rooms": [
            {"id": "room1", "type": "entrance", "size": "small", "connections": ["room2", "room3"]},
            {"id": "room2", "type": "chamber", "size": "large", "connections": ["room1", "room4"]},
            {"id": "room3", "type": "corridor", "size": "small", "connections": ["room1", "room5"]},
            {"id": "room4", "type": "chamber", "size": "medium", "connections": ["room2", "room6"]},
            {"id": "room5", "type": "treasury", "size": "medium", "connections": ["room3", "room6", "room7"]},
            {"id": "room6", "type": "corridor", "size": "small", "connections": ["room4", "room5"]},
            {"id": "room7", "type": "boss_room", "size": "large", "connections": ["room5"]}
        ],
        "treasures": [
            {"id": "treasure1", "value": 100, "rarity": "common"},
            {"id": "treasure2", "value": 500, "rarity": "rare"},
            {"id": "treasure3", "value": 1000, "rarity": "legendary"}
        ],
        "monsters": [
            {"id": "goblin", "danger_level": 2, "group_size": 3},
            {"id": "orc", "danger_level": 4, "group_size": 2},
            {"id": "dragon", "danger_level": 8, "group_size": 1}
        ],
        "constraints": {
            "max_danger_per_room": 10,
            "min_treasures_per_path": 1
        }
    }

    try:
        # Extract input data
        rooms = {r["id"]: r for r in instance_data["rooms"]}
        treasures = {t["id"]: t for t in instance_data["treasures"]}
        monsters = {m["id"]: m for m in instance_data["monsters"]}
        constraints = instance_data["constraints"]

        # Extract solution
        room_layout = solution_data.get("room_layout", [])
        connectivity = solution_data.get("connectivity", {})
        balance_analysis = solution_data.get("balance_analysis", {})

        # Build layout lookup
        layout_by_room = {room["room_id"]: room for room in room_layout}

        # Validate all rooms are included
        if set(layout_by_room.keys()) != set(rooms.keys()):
            return False, f"Room mismatch. Expected: {set(rooms.keys())}, Got: {set(layout_by_room.keys())}"

        # Validate each room's layout
        total_danger = 0
        treasure_counts = defaultdict(int)
        treasure_placement = defaultdict(list)

        for room_data in room_layout:
            room_id = room_data["room_id"]
            if room_id not in rooms:
                return False, f"Unknown room: {room_id}"

            # Validate monster placement
            room_danger = 0
            for monster_placement in room_data.get("monsters", []):
                monster_type = monster_placement["type"]
                count = monster_placement["count"]

                if monster_type not in monsters:
                    return False, f"Unknown monster type: {monster_type}"

                monster = monsters[monster_type]
                room_danger += monster["danger_level"] * count

                # Check group size constraints (allow some flexibility)
                if count > monster["group_size"] * 2:
                    return False, f"Too many {monster_type} in {room_id}: {count} > {monster['group_size'] * 2}"

            # Validate danger constraints
            max_danger = constraints.get("max_danger_per_room", 10)
            if room_danger > max_danger:
                return False, f"Room {room_id} exceeds danger limit: {room_danger} > {max_danger}"

            if room_data["danger_level"] != room_danger:
                return False, f"Room {room_id} danger level mismatch: {room_data['danger_level']} != {room_danger}"

            total_danger += room_danger

            # Validate treasure placement
            room_treasures = room_data.get("treasures", [])
            for treasure_id in room_treasures:
                if treasure_id not in treasures:
                    return False, f"Unknown treasure: {treasure_id}"
                treasure_counts[treasures[treasure_id]["rarity"]] += 1
                treasure_placement[treasure_id].append(room_id)

        # Check each treasure is placed exactly once
        for treasure_id in treasures:
            if treasure_id not in treasure_placement:
                return False, f"Treasure {treasure_id} not placed"
            if len(treasure_placement[treasure_id]) != 1:
                return False, f"Treasure {treasure_id} placed in multiple rooms: {treasure_placement[treasure_id]}"

        # Validate connectivity
        paths = connectivity.get("paths", [])
        isolated_rooms = set(connectivity.get("isolated_rooms", []))

        # Check for entrance and exit
        entrance_rooms = [r["id"] for r in instance_data["rooms"] if r["type"] == "entrance"]
        exit_rooms = [r["id"] for r in instance_data["rooms"] if r["type"] == "boss_room" or r["type"] == "exit"]

        if not entrance_rooms:
            entrance_rooms = [list(rooms.keys())[0]]
        if not exit_rooms:
            exit_rooms = [list(rooms.keys())[-1]]

        # Validate graph connectivity using original room connections
        adj_graph = defaultdict(list)
        for room in instance_data["rooms"]:
            for connected_room in room.get("connections", []):
                adj_graph[room["id"]].append(connected_room)
                adj_graph[connected_room].append(room["id"])

        def is_reachable(start, end, graph):
            """Check if end is reachable from start using BFS."""
            if start == end:
                return True

            queue = deque([start])
            visited = {start}

            while queue:
                current = queue.popleft()
                for neighbor in graph[current]:
                    if neighbor == end:
                        return True
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            return False

        # Check all rooms are reachable from entrance
        entrance = entrance_rooms[0] if entrance_rooms else list(rooms.keys())[0]
        for room_id in rooms:
            if not is_reachable(entrance, room_id, adj_graph):
                if room_id not in isolated_rooms:
                    return False, f"Room {room_id} is not reachable from entrance but not marked as isolated"

        # There should be no isolated rooms
        if isolated_rooms:
            return False, f"Solution has isolated rooms: {isolated_rooms}"

        # Validate path information
        for path in paths:
            from_room = path["from"]
            to_room = path["to"]
            route = path["route"]

            if not route or route[0] != from_room or route[-1] != to_room:
                return False, f"Invalid route from {from_room} to {to_room}: {route}"

            # Validate route follows connections
            for i in range(len(route) - 1):
                current, next_room = route[i], route[i + 1]
                if next_room not in adj_graph[current]:
                    return False, f"Invalid connection in route: {current} -> {next_room}"

            # Validate path danger calculation
            path_danger = sum(layout_by_room[room]["danger_level"] for room in route)
            if path["total_danger"] != path_danger:
                return False, f"Path danger mismatch: {path['total_danger']} != {path_danger}"

            # Validate treasures found along path
            path_treasures = []
            for room in route:
                path_treasures.extend(layout_by_room[room].get("treasures", []))

            if set(path["treasures_found"]) != set(path_treasures):
                return False, f"Path treasures mismatch: {path['treasures_found']} != {path_treasures}"

        # Validate balance analysis
        if balance_analysis.get("total_danger", 0) != total_danger:
            return False, f"Total danger mismatch: {balance_analysis.get('total_danger', 0)} != {total_danger}"

        # Validate treasure distribution
        expected_distribution = dict(treasure_counts)
        actual_distribution = balance_analysis.get("treasure_distribution", {})

        if actual_distribution != expected_distribution:
            return False, f"Treasure distribution mismatch: {actual_distribution} != {expected_distribution}"

        # Validate difficulty progression
        difficulty_progression = balance_analysis.get("difficulty_progression", "")
        if difficulty_progression not in ["easy", "balanced", "hard", "extreme"]:
            return False, f"Invalid difficulty progression: {difficulty_progression}"

        # Check rare treasure constraint: rare treasures should be in higher danger rooms
        for treasure_id, treasure in treasures.items():
            if treasure["rarity"] == "rare" or treasure["rarity"] == "legendary":
                rare_room = treasure_placement[treasure_id][0]
                rare_danger = layout_by_room[rare_room]["danger_level"]

                for common_treasure_id, common_treasure in treasures.items():
                    if common_treasure["rarity"] == "common":
                        common_room = treasure_placement[common_treasure_id][0]
                        common_danger = layout_by_room[common_room]["danger_level"]

                        if rare_danger < common_danger:
                            return False, f"Rare treasure {treasure_id} (danger={rare_danger}) in room with less danger than common treasure {common_treasure_id} (danger={common_danger})"

        return True, "Valid dungeon generation"

    except Exception as e:
        return False, f"Validation error: {str(e)}"

def main():
    try:
        data = sys.stdin.read().strip()
        if not data:
            result = {"valid": False, "message": "No solution provided"}
            print(json.dumps(result))
            return

        solution_data = json.loads(data)
    except json.JSONDecodeError as e:
        result = {"valid": False, "message": f"Invalid JSON: {str(e)}"}
        print(json.dumps(result))
        return

    is_valid, message = validate_solution(solution_data)

    result = {
        "valid": is_valid,
        "message": message
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
