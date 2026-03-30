#!/usr/bin/env python3
"""
Reference model for Hamiltonian Path problem.
Validates solution from stdin.
"""

import json
import sys

def find_hamiltonian_paths():
    """Compute all Hamiltonian paths from vertex 0 to vertex 5 in the given graph."""
    # Define the graph as an adjacency list
    graph = {
        0: [1, 2],
        1: [2, 3, 4],
        2: [1, 3, 4],
        3: [4, 5],
        4: [3, 5],
        5: []
    }

    # All vertices in the graph
    vertices = set(range(6))
    start_vertex = 0
    end_vertex = 5

    all_paths = []

    def dfs(current_vertex, path, visited):
        # If we've visited all vertices and reached the end vertex
        if len(visited) == len(vertices) and current_vertex == end_vertex:
            all_paths.append(path.copy())
            return

        # If we've visited all vertices but not at end vertex, no valid path
        if len(visited) == len(vertices):
            return

        # Try all neighbors of current vertex
        for neighbor in graph[current_vertex]:
            if neighbor not in visited:
                path.append(neighbor)
                visited.add(neighbor)
                dfs(neighbor, path, visited)
                path.pop()
                visited.remove(neighbor)

    # Start DFS from vertex 0
    initial_path = [start_vertex]
    initial_visited = {start_vertex}
    dfs(start_vertex, initial_path, initial_visited)

    # Sort paths for consistent output
    all_paths.sort()

    return all_paths

def load_solution():
    """Load solution from stdin."""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def validate_solution(solution):
    """Validate the solution against the reference model."""
    if not solution:
        return {"valid": False, "message": "No solution provided"}

    # Check required fields
    if "paths" not in solution:
        return {"valid": False, "message": "Missing 'paths' field"}
    if "count" not in solution:
        return {"valid": False, "message": "Missing 'count' field"}
    if "exists" not in solution:
        return {"valid": False, "message": "Missing 'exists' field"}

    # Compute expected paths
    expected_paths = find_hamiltonian_paths()
    expected_count = len(expected_paths)
    expected_exists = expected_count > 0

    # Validate paths
    solution_paths = solution["paths"]
    if not isinstance(solution_paths, list):
        return {"valid": False, "message": "'paths' must be a list"}

    # Sort solution paths for comparison
    solution_paths_sorted = sorted([list(path) for path in solution_paths])

    # Compare paths
    if solution_paths_sorted != expected_paths:
        return {
            "valid": False,
            "message": f"Incorrect paths. Expected {expected_count} paths, got {len(solution_paths)}"
        }

    # Validate count
    if solution["count"] != expected_count:
        return {
            "valid": False,
            "message": f"Incorrect count. Expected {expected_count}, got {solution['count']}"
        }

    # Validate exists
    if solution["exists"] != expected_exists:
        return {
            "valid": False,
            "message": f"Incorrect exists flag. Expected {expected_exists}, got {solution['exists']}"
        }

    return {"valid": True, "message": "Solution correct"}

if __name__ == "__main__":
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))
