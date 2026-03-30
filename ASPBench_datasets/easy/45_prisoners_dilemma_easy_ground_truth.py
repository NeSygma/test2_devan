#!/usr/bin/env python3
"""
Reference model for Problem 045: Prisoners' Dilemma Tournament

Validates tournament results from stdin and checks optimality.
"""

import json
import random
import sys
from typing import Dict, List, Tuple

# Expected optimal values
EXPECTED_OPTIMAL_WINNER = "TFT"
EXPECTED_OPTIMAL_SCORE = 1218


def play_prisoners_dilemma_tournament() -> Dict:
    """
    Simulate a prisoners' dilemma tournament with various strategies.

    Returns:
        Dict: Tournament results with strategy rankings and winner
    """

    # Tournament parameters
    ROUNDS_PER_MATCH = 100
    STRATEGIES = ["COOP", "DEFECT", "TFT", "GTFT", "RAND"]

    # Payoff matrix: (cooperate, defect) for (self, other)
    PAYOFFS = {
        ('C', 'C'): (3, 3),  # Both cooperate
        ('C', 'D'): (0, 5),  # I cooperate, other defects
        ('D', 'C'): (5, 0),  # I defect, other cooperates
        ('D', 'D'): (1, 1)   # Both defect
    }

    def get_move(strategy: str, history_self: List[str], history_other: List[str], round_num: int) -> str:
        """Get next move for a strategy given game history."""
        if strategy == "COOP":
            return 'C'
        elif strategy == "DEFECT":
            return 'D'
        elif strategy == "TFT":
            # Tit-for-tat: cooperate first, then copy opponent's last move
            if round_num == 0 or len(history_other) == 0:
                return 'C'
            return history_other[-1]
        elif strategy == "GTFT":
            # Generous tit-for-tat: like TFT but forgives defection 10% of time
            if round_num == 0 or len(history_other) == 0:
                return 'C'
            last_opponent_move = history_other[-1]
            if last_opponent_move == 'D':
                # 10% chance to forgive and cooperate anyway
                if random.random() < 0.1:
                    return 'C'
            return last_opponent_move
        elif strategy == "RAND":
            # Random: 50% chance each for cooperate/defect
            return 'C' if random.random() < 0.5 else 'D'
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def play_match(strategy1: str, strategy2: str) -> Tuple[int, int]:
        """Play a match between two strategies and return their scores."""
        history1 = []
        history2 = []
        score1 = 0
        score2 = 0

        for round_num in range(ROUNDS_PER_MATCH):
            # Get moves for both strategies
            move1 = get_move(strategy1, history1, history2, round_num)
            move2 = get_move(strategy2, history2, history1, round_num)

            # Calculate scores for this round
            payoff1, payoff2 = PAYOFFS[(move1, move2)]
            score1 += payoff1
            score2 += payoff2

            # Update histories
            history1.append(move1)
            history2.append(move2)

        return score1, score2

    # Initialize total scores for all strategies
    total_scores = {strategy: 0 for strategy in STRATEGIES}

    # Set random seed for reproducible results
    random.seed(42)

    # Play round-robin tournament
    for i, strategy1 in enumerate(STRATEGIES):
        for j, strategy2 in enumerate(STRATEGIES):
            # Each strategy plays against every strategy (including itself)
            score1, score2 = play_match(strategy1, strategy2)
            total_scores[strategy1] += score1

    # Sort strategies by total score (descending)
    sorted_results = sorted(
        [{"strategy": strategy, "total_score": score}
         for strategy, score in total_scores.items()],
        key=lambda x: x["total_score"],
        reverse=True
    )

    # Winner is the strategy with highest total score
    winner = sorted_results[0]["strategy"]

    return {
        "tournament_results": sorted_results,
        "winner": winner
    }


def validate_solution(solution: Dict) -> Dict:
    """
    Validate the solution from stdin.

    Args:
        solution: Solution dict with tournament_results and winner

    Returns:
        Dict with validation result
    """
    if not solution:
        return {"valid": False, "message": "No solution provided"}

    try:
        # Check required fields
        if "tournament_results" not in solution or "winner" not in solution:
            return {"valid": False, "message": "Missing required fields: tournament_results and/or winner"}

        tournament_results = solution["tournament_results"]
        winner = solution["winner"]

        # Check tournament results format
        if not isinstance(tournament_results, list):
            return {"valid": False, "message": "tournament_results must be a list"}

        if len(tournament_results) != 5:
            return {"valid": False, "message": "tournament_results must contain exactly 5 strategies"}

        expected_strategies = {"COOP", "DEFECT", "TFT", "GTFT", "RAND"}
        found_strategies = set()

        for entry in tournament_results:
            if not isinstance(entry, dict):
                return {"valid": False, "message": "Each tournament result entry must be a dict"}
            if "strategy" not in entry or "total_score" not in entry:
                return {"valid": False, "message": "Each entry must have 'strategy' and 'total_score' fields"}
            if not isinstance(entry["strategy"], str) or not isinstance(entry["total_score"], int):
                return {"valid": False, "message": "Invalid types: strategy must be string, total_score must be int"}
            found_strategies.add(entry["strategy"])

        # Check all strategies are present
        if found_strategies != expected_strategies:
            return {"valid": False, "message": f"Missing strategies: {expected_strategies - found_strategies}"}

        # Check winner is valid
        if winner not in expected_strategies:
            return {"valid": False, "message": f"Winner '{winner}' is not a valid strategy"}

        # Check winner matches highest score
        if tournament_results[0]["strategy"] != winner:
            return {"valid": False, "message": "Winner does not match the strategy with highest score"}

        # Check scores are in descending order
        scores = [entry["total_score"] for entry in tournament_results]
        if scores != sorted(scores, reverse=True):
            return {"valid": False, "message": "Tournament results must be sorted in descending order by score"}

        # Run reference model to get expected results
        expected = play_prisoners_dilemma_tournament()
        expected_winner = expected["winner"]
        expected_scores = {entry["strategy"]: entry["total_score"] for entry in expected["tournament_results"]}

        # Check optimality (with tolerance for randomness in RAND/GTFT strategies)
        winning_score = tournament_results[0]["total_score"]
        if winner != EXPECTED_OPTIMAL_WINNER:
            return {"valid": False, "message": f"Not optimal: winner={winner}, expected {EXPECTED_OPTIMAL_WINNER}"}
        # Allow ±10 tolerance due to randomness in RAND and GTFT strategies
        if abs(winning_score - EXPECTED_OPTIMAL_SCORE) > 10:
            return {"valid": False, "message": f"Not optimal: winning_score={winning_score}, expected ~{EXPECTED_OPTIMAL_SCORE}"}

        return {"valid": True, "message": f"Solution is valid and optimal (winner={EXPECTED_OPTIMAL_WINNER}, score={winning_score})"}

    except Exception as e:
        return {"valid": False, "message": f"Validation error: {str(e)}"}


if __name__ == "__main__":
    # Read solution from stdin
    try:
        data = sys.stdin.read().strip()
        if not data:
            result = {"valid": False, "message": "No input provided"}
        else:
            solution = json.loads(data)
            result = validate_solution(solution)
        print(json.dumps(result))
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Invalid JSON: {str(e)}"}))
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"Error: {str(e)}"}))
