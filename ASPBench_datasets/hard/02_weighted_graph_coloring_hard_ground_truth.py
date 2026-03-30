#!/usr/bin/env python3

import json
import sys

# Lenient upper bound for weighted cost
# (exact optimal unknown - computationally expensive to verify)
MAX_ACCEPTABLE_COST = 850

# Graph structure
VERTICES = list(range(1, 37))
NUM_COLORS = 5

# Weights
WEIGHTS = {}
for v in range(1, 6):
    WEIGHTS[v] = 10
for v in range(6, 16):
    WEIGHTS[v] = 3
for v in range(16, 26):
    WEIGHTS[v] = 5
for v in range(26, 37):
    WEIGHTS[v] = 7

# Edge list
EDGES = set()

# Core K5 clique (1-5)
for i in range(1, 6):
    for j in range(i+1, 6):
        EDGES.add((i, j))
        EDGES.add((j, i))

# Cluster A (6-15) - ring with chords
ring_a = [(6,7), (7,8), (8,9), (9,10), (10,11), (11,12), (12,13), (13,14), (14,15), (15,6)]
chords_a = [(6,9), (7,10), (8,11), (9,12), (10,13), (11,14), (12,15), (13,6), (14,7), (15,8)]
for edge in ring_a + chords_a:
    EDGES.add(edge)
    EDGES.add((edge[1], edge[0]))

# Cluster A to core connections
cluster_a_core = [(6,1), (6,2), (9,2), (9,3), (12,3), (12,4), (15,4), (15,5)]
for edge in cluster_a_core:
    EDGES.add(edge)
    EDGES.add((edge[1], edge[0]))

# Cluster B (16-25) - 2x5 grid
# Row edges
for i in range(16, 20):
    EDGES.add((i, i+1))
    EDGES.add((i+1, i))
for i in range(21, 25):
    EDGES.add((i, i+1))
    EDGES.add((i+1, i))
# Column edges
for i in range(16, 21):
    EDGES.add((i, i+5))
    EDGES.add((i+5, i))
# Diagonal edges
for i in range(16, 20):
    EDGES.add((i, i+6))
    EDGES.add((i+6, i))

# Cluster B to core
EDGES.add((16, 1))
EDGES.add((1, 16))
EDGES.add((20, 5))
EDGES.add((5, 20))

# Cluster B to Cluster A
EDGES.add((18, 8))
EDGES.add((8, 18))
EDGES.add((23, 13))
EDGES.add((13, 23))

# Cluster C (26-36) - 11-cycle with chords
cycle_c = [(26,27), (27,28), (28,29), (29,30), (30,31), (31,32), (32,33), (33,34), (34,35), (35,36), (36,26)]
chords_c = [(26,29), (27,30), (28,31), (29,32), (30,33), (31,34), (32,35), (33,36), (34,26), (35,27), (36,28)]
for edge in cycle_c + chords_c:
    EDGES.add(edge)
    EDGES.add((edge[1], edge[0]))

# Cluster C to core
cluster_c_core = [(26,1), (26,5), (31,3)]
for edge in cluster_c_core:
    EDGES.add(edge)
    EDGES.add((edge[1], edge[0]))

# Cluster C to Cluster B
EDGES.add((28, 19))
EDGES.add((19, 28))
EDGES.add((33, 24))
EDGES.add((24, 33))

def validate_solution(solution_data):
    """Validate the graph coloring solution."""

    try:
        # Extract solution
        num_colors = solution_data.get("num_colors", 0)
        weighted_cost = solution_data.get("weighted_cost", 0)
        coloring = solution_data.get("coloring", [])

        # Check number of entries
        if len(coloring) != 36:
            return False, f"Coloring must have 36 entries, got {len(coloring)}"

        # Build color assignment
        color_map = {}
        colors_used = set()

        for entry in coloring:
            vertex = entry.get("vertex")
            color = entry.get("color")

            if vertex not in VERTICES:
                return False, f"Invalid vertex: {vertex}"

            if color < 1 or color > 5:
                return False, f"Color {color} for vertex {vertex} out of range [1,5]"

            if vertex in color_map:
                return False, f"Vertex {vertex} assigned multiple times"

            color_map[vertex] = color
            colors_used.add(color)

        # Check all vertices assigned
        if len(color_map) != 36:
            return False, f"Not all vertices assigned colors"

        # Check num_colors
        if num_colors != len(colors_used):
            return False, f"num_colors={num_colors} but {len(colors_used)} colors actually used"

        if num_colors != 5:
            return False, f"Must use exactly 5 colors, got {num_colors}"

        # Validate edge constraints
        for (u, v) in EDGES:
            if color_map[u] == color_map[v]:
                return False, f"Adjacent vertices {u} and {v} have same color {color_map[u]}"

        # Calculate weighted cost
        calculated_cost = sum(color_map[v] * WEIGHTS[v] for v in VERTICES)

        if weighted_cost != calculated_cost:
            return False, f"Weighted cost mismatch: stated {weighted_cost}, calculated {calculated_cost}"

        # Check against lenient upper bound
        if calculated_cost > MAX_ACCEPTABLE_COST:
            return False, f"Weighted cost too high: {calculated_cost} > {MAX_ACCEPTABLE_COST}"

        return True, f"Solution valid (weighted_cost={calculated_cost})"

    except Exception as e:
        return False, f"Validation error: {str(e)}"

def main():
    """Main entry point - reads solution from stdin and validates."""
    try:
        solution_json = sys.stdin.read().strip()
        if not solution_json:
            print(json.dumps({"valid": False, "message": "No solution provided"}))
            sys.exit(1)

        solution_data = json.loads(solution_json)
        is_valid, message = validate_solution(solution_data)

        result = {
            "valid": is_valid,
            "message": message
        }

        print(json.dumps(result))

    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Unexpected error: {e}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
