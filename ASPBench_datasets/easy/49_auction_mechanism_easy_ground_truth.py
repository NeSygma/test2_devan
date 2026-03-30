#!/usr/bin/env python3
"""
Reference model for Problem 049: Auction Mechanism

Validates combinatorial auction solutions.
"""

import json
import sys

def load_solution():
    """Load solution from stdin"""
    try:
        data = sys.stdin.read().strip()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def validate_solution(solution):
    """
    Validate that the solution satisfies all constraints and optimality.

    Args:
        solution: Dictionary with winning_bids, total_revenue, item_allocation

    Returns:
        Dictionary with 'valid' (bool) and 'message' (str)
    """

    if not solution:
        return {"valid": False, "message": "No solution provided"}

    # Instance data
    items = ["item1", "item2", "item3", "item4", "item5"]
    bidders = ["A", "B", "C", "D"]

    # All submitted bids
    all_bids = [
        {"bidder": "A", "items": ["item1", "item2"], "price": 100},
        {"bidder": "A", "items": ["item3"], "price": 50},
        {"bidder": "B", "items": ["item2", "item3"], "price": 120},
        {"bidder": "B", "items": ["item4", "item5"], "price": 80},
        {"bidder": "C", "items": ["item1", "item3", "item5"], "price": 150},
        {"bidder": "D", "items": ["item4"], "price": 40}
    ]

    # Check required fields
    if "winning_bids" not in solution:
        return {"valid": False, "message": "Missing 'winning_bids' field"}
    if "total_revenue" not in solution:
        return {"valid": False, "message": "Missing 'total_revenue' field"}
    if "item_allocation" not in solution:
        return {"valid": False, "message": "Missing 'item_allocation' field"}

    winning_bids = solution["winning_bids"]
    total_revenue = solution["total_revenue"]
    item_allocation = solution["item_allocation"]

    # Validate winning_bids is a list
    if not isinstance(winning_bids, list):
        return {"valid": False, "message": "'winning_bids' must be a list"}

    # Track allocated items for conflict checking
    allocated_items = {}
    calculated_revenue = 0

    for bid in winning_bids:
        # Check bid format
        if not isinstance(bid, dict):
            return {"valid": False, "message": "Each winning bid must be a dictionary"}
        if "bidder" not in bid or "items" not in bid or "price" not in bid:
            return {"valid": False, "message": "Each bid must have 'bidder', 'items', and 'price'"}

        bidder = bid["bidder"]
        bid_items = bid["items"]
        price = bid["price"]

        # Validate bidder
        if bidder not in bidders:
            return {"valid": False, "message": f"Invalid bidder: {bidder}"}

        # Validate items
        if not isinstance(bid_items, list) or not bid_items:
            return {"valid": False, "message": "Bid items must be a non-empty list"}

        for item in bid_items:
            if item not in items:
                return {"valid": False, "message": f"Invalid item: {item}"}

        # Check for conflicts (item allocated to multiple bidders)
        for item in bid_items:
            if item in allocated_items:
                return {"valid": False, "message": f"Item {item} allocated to multiple bidders"}
            allocated_items[item] = bidder

        # Verify bid exists in original bids
        bid_found = False
        for original_bid in all_bids:
            if (original_bid["bidder"] == bidder and
                set(original_bid["items"]) == set(bid_items) and
                original_bid["price"] == price):
                bid_found = True
                break

        if not bid_found:
            return {"valid": False, "message": f"Bid not found in original bids: {bid}"}

        calculated_revenue += price

    # Validate total_revenue
    if not isinstance(total_revenue, (int, float)):
        return {"valid": False, "message": "'total_revenue' must be a number"}

    if abs(total_revenue - calculated_revenue) > 0.01:
        return {"valid": False, "message": f"Revenue mismatch: expected {calculated_revenue}, got {total_revenue}"}

    # Validate item_allocation consistency
    if not isinstance(item_allocation, dict):
        return {"valid": False, "message": "'item_allocation' must be a dictionary"}

    for item, bidder in item_allocation.items():
        if item not in items:
            return {"valid": False, "message": f"Invalid item in allocation: {item}"}
        if bidder not in bidders:
            return {"valid": False, "message": f"Invalid bidder in allocation: {bidder}"}

        # Verify allocation matches winning bids
        if item not in allocated_items or allocated_items[item] != bidder:
            return {"valid": False, "message": f"Allocation mismatch for item {item}"}

    # Check for optimal revenue (expected: 230)
    expected_optimal = 230

    if total_revenue < expected_optimal:
        return {"valid": False, "message": f"Suboptimal revenue: {total_revenue} < {expected_optimal}"}

    if total_revenue != expected_optimal:
        return {"valid": False, "message": f"Revenue mismatch: expected {expected_optimal}, got {total_revenue}"}

    return {"valid": True, "message": f"Solution correct with optimal revenue {total_revenue}"}

if __name__ == "__main__":
    solution = load_solution()
    result = validate_solution(solution)
    print(json.dumps(result))
