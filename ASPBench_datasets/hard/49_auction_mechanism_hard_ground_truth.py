#!/usr/bin/env python3
"""
Reference model for Problem 049 (Hard): Auction Mechanism

This script validates a given solution from stdin to ensure it complies with all
the auction rules and checks optimality.
"""

import json
import sys
import clingo

# Expected optimal value
EXPECTED_OPTIMAL_REVENUE = 335

class AuctionValidator:
    """Validates an auction solution against all constraints."""

    def __init__(self, solution_data):
        self.solution = solution_data
        self.program = self._get_asp_rules()
        self.facts = self._get_base_facts()

    def _get_asp_rules(self):
        """Returns the ASP constraint rules for validation."""
        return """
        % --- Constraint 1: Item Conflict ---
        % No two winning bids can contain the same item.
        item_conflict :- win(ID1), win(ID2), bid_item(ID1, I), bid_item(ID2, I), ID1 < ID2.

        % --- Constraint 2: Bidder Budget ---
        % A bidder's total spend must not exceed their budget.
        budget_violation(B) :- bidder(B, _, Budget, _),
                               #sum{Price, ID : win(ID), bid(ID, B, Price)} > Budget.

        % --- Constraint 3: Licensing ---
        % A bidder needs a license for a category if they win a bid with items from that category.
        needs_license(B, Cat) :- win(ID), bid(ID, B, _), bid_item(ID, Item), item_category(Item, Cat).

        % A bidder has a license if they win the corresponding license item.
        has_license(B, Cat) :- win(ID), bid(ID, B, _), bid_item(ID, Item), license_category(Item, Cat).

        % It's a violation if a bidder needs a license they don't have.
        license_violation(B, Cat) :- needs_license(B, Cat), not has_license(B, Cat).

        % --- Constraint 4: Fairness (Max Items per Bidder) ---
        % No bidder can win more than a certain number of items.
        fairness_violation(B) :- bidder(B,_,_,_), max_items_per_bidder(Max),
                                 #count{Item : win(ID), bid(ID, B, _), bid_item(ID, Item)} > Max.
        """

    def _get_base_facts(self):
        """Generates ASP facts from the problem instance."""
        return """
        bidder(a, gold, 150, 20). bidder(b, silver, 200, 10).
        bidder(c, gold, 180, 25). bidder(d, silver, 100, 5).

        item_category(item1, electronics). item_category(item2, electronics).
        item_category(item3, furniture). item_category(item4, furniture).
        item_category(item5, electronics). item_category(item6, furniture).
        license_category(lic_E, electronics). license_category(lic_F, furniture).

        bid(1, a, 70). bid_item(1, item1). bid_item(1, item2).
        bid(2, a, 40). bid_item(2, lic_E).
        bid(3, b, 90). bid_item(3, item3). bid_item(3, item4).
        bid(4, b, 50). bid_item(4, lic_F).
        bid(5, b, 60). bid_item(5, item5).
        bid(6, c, 100). bid_item(6, item1). bid_item(6, item5).
        bid(7, c, 60). bid_item(7, lic_E).
        bid(8, c, 80). bid_item(8, item3). bid_item(8, item6).
        bid(9, d, 25). bid_item(9, lic_F).
        bid(10, d, 70). bid_item(10, item4).

        max_items_per_bidder(3).
        """

    def _get_solution_facts(self):
        """Generates ASP facts from the proposed solution."""
        facts = []
        try:
            for bid_id in self.solution.get("winning_bids", []):
                facts.append(f"win({bid_id}).")
        except (TypeError, ValueError):
            # Handle malformed winning_bids
            pass
        return "\n".join(facts)

    def validate(self):
        """Runs the validation and returns a result dictionary."""
        ctl = clingo.Control()
        ctl.add("base", [], self.program)
        ctl.add("base", [], self.facts)

        solution_facts = self._get_solution_facts()
        if not solution_facts:
             return {"valid": False, "message": "Solution is missing or has malformed 'winning_bids' field."}
        ctl.add("base", [], solution_facts)

        ctl.ground([("base", [])])

        violations = []
        with ctl.solve(yield_=True) as handle:
            model = handle.model()
            if model:
                for atom in model.symbols(atoms=True):
                    if atom.name == "item_conflict":
                        violations.append("Item conflict detected: an item was allocated twice.")
                    elif atom.name == "budget_violation":
                        violations.append(f"Budget violation for bidder '{atom.arguments[0]}'.")
                    elif atom.name == "license_violation":
                        violations.append(f"License violation for bidder '{atom.arguments[0]}' in category '{atom.arguments[1]}'.")
                    elif atom.name == "fairness_violation":
                        violations.append(f"Fairness violation for bidder '{atom.arguments[0]}': too many items won.")

        if violations:
            return {"valid": False, "message": "Solution violates constraints: " + " ".join(violations)}

        # Also check internal consistency of the JSON
        return self.verify_json_consistency()

    def verify_json_consistency(self):
        """Verify the JSON fields are consistent with each other."""
        try:
            winning_bids_from_json = self.solution["winning_bids"]
            all_bids = self.solution["bids"]
            bid_map = {b['id']: b for b in all_bids}

            # Verify total revenue
            calculated_base_revenue = sum(bid_map[bid_id]['price'] for bid_id in winning_bids_from_json)

            wins_per_bidder = {}
            for bid_id in winning_bids_from_json:
                bidder = bid_map[bid_id]['bidder']
                wins_per_bidder[bidder] = wins_per_bidder.get(bidder, 0) + 1

            bidder_map = {b['bidder']: b for b in self.solution['bidders']}
            calculated_synergy_bonus = 0
            synergy_bonuses_from_json = self.solution.get("synergy_bonuses", [])
            synergy_map = {s['bidder']: s['bonus'] for s in synergy_bonuses_from_json}

            for bidder, count in wins_per_bidder.items():
                if count >= 2:
                    bonus = bidder_map[bidder]['synergy_bonus']
                    calculated_synergy_bonus += bonus
                    if synergy_map.get(bidder) != bonus:
                        return {"valid": False, "message": f"Incorrect synergy bonus reported for bidder '{bidder}'."}

            if len(synergy_map) != len([b for b, c in wins_per_bidder.items() if c >= 2]):
                 return {"valid": False, "message": "Mismatch in number of bidders receiving synergy bonuses."}

            calculated_total_revenue = calculated_base_revenue + calculated_synergy_bonus
            if self.solution["total_revenue"] != calculated_total_revenue:
                return {"valid": False, "message": f"Total revenue mismatch. Stated: {self.solution['total_revenue']}, Calculated: {calculated_total_revenue}."}

            # Check optimality
            if self.solution["total_revenue"] != EXPECTED_OPTIMAL_REVENUE:
                return {"valid": False, "message": f"Not optimal: total_revenue={self.solution['total_revenue']}, expected {EXPECTED_OPTIMAL_REVENUE}"}

            # Verify item allocation
            calculated_alloc = {}
            for bid_id in winning_bids_from_json:
                bid = bid_map[bid_id]
                for item in bid['items']:
                    calculated_alloc[item] = bid['bidder']

            if self.solution["item_allocation"] != calculated_alloc:
                return {"valid": False, "message": "Item allocation map is inconsistent with winning bids."}

        except (KeyError, TypeError, IndexError) as e:
            return {"valid": False, "message": f"JSON structure is invalid or inconsistent: {e}"}

        return {"valid": True, "message": f"Solution valid and optimal (total_revenue={EXPECTED_OPTIMAL_REVENUE})"}


if __name__ == "__main__":
    try:
        solution_json = sys.stdin.read()
        solution_data = json.loads(solution_json)
        validator = AuctionValidator(solution_data)
        result = validator.validate()
        print(json.dumps(result))
    except json.JSONDecodeError:
        print(json.dumps({"valid": False, "message": "Invalid JSON provided."}))
    except Exception as e:
        print(json.dumps({"valid": False, "message": f"An unexpected error occurred during validation: {e}"}))
