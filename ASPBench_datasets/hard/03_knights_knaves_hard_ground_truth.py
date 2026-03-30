#!/usr/bin/env python3
"""
Reference model for the Knights and Knaves puzzle (Hard).

This module verifies that a given solution satisfies all logical constraints
by checking it against the ASP encoding with the assignment fixed.
"""

import json
import sys
from typing import Dict
import clingo


ASP_PROGRAM = r"""
% People
person(alice; bob; charlie; diana; ethan; fiona; george; hannah;
       ian; julia; kevin; lily; mason; nina; oliver; paula;
       quentin; rachel; sam; tina; ursula; victor; wendy; xavier).

% Groups
group_a(alice; bob; charlie; diana; ethan; fiona; george; hannah).
group_b(ian; julia; kevin; lily; mason; nina; oliver; paula).
group_c(quentin; rachel; sam; tina; ursula; victor; wendy; xavier).

% Exactly one type: choose knights; knaves are the complement
{ knight(X) : person(X) }.
knave(X) :- person(X), not knight(X).

% Alice: "Hannah knave, and (Bob knave or Charlie knight), and exactly four in Group A are knights"
s_alice_true :- knave(hannah), knave(bob), 4 { knight(X) : group_a(X) } 4.
s_alice_true :- knave(hannah), knight(charlie), 4 { knight(X) : group_a(X) } 4.
:- knight(alice), not s_alice_true.
:- knave(alice), s_alice_true.

% Bob: "Diana is the same type as me"
s_bob_true :- knight(diana), knight(bob).
s_bob_true :- knave(diana), knave(bob).
:- knight(bob), not s_bob_true.
:- knave(bob), s_bob_true.

% Charlie: "Exactly twelve of us are knights"
s_charlie_true :- 12 { knight(X) : person(X) } 12.
:- knight(charlie), not s_charlie_true.
:- knave(charlie), s_charlie_true.

% Diana: "Ethan and Fiona are different, and Hannah is a knave"
s_diana_true :- knight(ethan), knave(fiona), knave(hannah).
s_diana_true :- knave(ethan), knight(fiona), knave(hannah).
:- knight(diana), not s_diana_true.
:- knave(diana), s_diana_true.

% Ethan: "George is a knight iff Alice is a knight"
s_ethan_true :- knight(george), knight(alice).
s_ethan_true :- knave(george), knave(alice).
:- knight(ethan), not s_ethan_true.
:- knave(ethan), s_ethan_true.

% Fiona: "Bob and Charlie are of different types, and I am a knight"
s_fiona_true :- knight(fiona), knight(bob), knave(charlie).
s_fiona_true :- knight(fiona), knave(bob), knight(charlie).
:- knight(fiona), not s_fiona_true.
:- knave(fiona), s_fiona_true.

% George: "Alice and Hannah are of the same type"
s_george_true :- knight(alice), knight(hannah).
s_george_true :- knave(alice), knave(hannah).
:- knight(george), not s_george_true.
:- knave(george), s_george_true.

% Hannah: "Exactly one of Bob, Charlie, and Diana is a knight"
s_hannah_true :- 1 { knight(bob); knight(charlie); knight(diana) } 1.
:- knight(hannah), not s_hannah_true.
:- knave(hannah), s_hannah_true.

% Ian: "Alice and Paula are the same type, and Julia is a knave"
s_ian_true :- knight(alice), knight(paula), knave(julia).
s_ian_true :- knave(alice), knave(paula), knave(julia).
:- knight(ian), not s_ian_true.
:- knave(ian), s_ian_true.

% Julia: "Kevin is a knight and Nina is a knight"
s_julia_true :- knight(kevin), knight(nina).
:- knight(julia), not s_julia_true.
:- knave(julia), s_julia_true.

% Kevin: "Either Oliver is a knight or Lily is a knave"
s_kevin_true :- knight(oliver).
s_kevin_true :- knave(lily).
:- knight(kevin), not s_kevin_true.
:- knave(kevin), s_kevin_true.

% Lily: "Exactly four of us in Group B are knights, and Oliver is a knave"
s_lily_true :- 4 { knight(X) : group_b(X) } 4, knave(oliver).
:- knight(lily), not s_lily_true.
:- knave(lily), s_lily_true.

% Mason: "Bob and Ethan are the same type, and Julia is a knave"
s_mason_true :- knight(bob), knight(ethan), knave(julia).
s_mason_true :- knave(bob), knave(ethan), knave(julia).
:- knight(mason), not s_mason_true.
:- knave(mason), s_mason_true.

% Nina: "Ian and Paula are of different types"
s_nina_true :- knight(ian), knave(paula).
s_nina_true :- knave(ian), knight(paula).
:- knight(nina), not s_nina_true.
:- knave(nina), s_nina_true.

% Oliver: "Exactly two of George, Hannah, Ian, and Julia are knights"
s_oliver_true :- 2 { knight(george); knight(hannah); knight(ian); knight(julia) } 2.
:- knight(oliver), not s_oliver_true.
:- knave(oliver), s_oliver_true.

% Paula: "Rachel is a knight iff Quentin is a knave"
s_paula_true :- knight(rachel), knave(quentin).
s_paula_true :- knave(rachel), knight(quentin).
:- knight(paula), not s_paula_true.
:- knave(paula), s_paula_true.

% Quentin: "At least five of us in Group C are knights"
s_quentin_true :- 5 { knight(X) : group_c(X) }.
:- knight(quentin), not s_quentin_true.
:- knave(quentin), s_quentin_true.

% Rachel: "Charlie is a knight, Lily is a knight, and Victor is a knave"
s_rachel_true :- knight(charlie), knight(lily), knave(victor).
:- knight(rachel), not s_rachel_true.
:- knave(rachel), s_rachel_true.

% Sam: "Tina is a knave, Oliver is a knave, and Ursula is a knave"
s_sam_true :- knave(tina), knave(oliver), knave(ursula).
:- knight(sam), not s_sam_true.
:- knave(sam), s_sam_true.

% Tina: "Rachel is a knave or Mason is a knave"
s_tina_true :- knave(rachel).
s_tina_true :- knave(mason).
:- knight(tina), not s_tina_true.
:- knave(tina), s_tina_true.

% Ursula: "Ian and Julia are both knights"
s_ursula_true :- knight(ian), knight(julia).
:- knight(ursula), not s_ursula_true.
:- knave(ursula), s_ursula_true.

% Victor: "Exactly two of Alice, Bob, Charlie, and Diana are knaves"
s_victor_true :- 2 { knave(alice); knave(bob); knave(charlie); knave(diana) } 2.
:- knight(victor), not s_victor_true.
:- knave(victor), s_victor_true.

% Wendy: "Victor is a knave, Ursula is a knave, and Xavier is a knight"
s_wendy_true :- knave(victor), knave(ursula), knight(xavier).
:- knight(wendy), not s_wendy_true.
:- knave(wendy), s_wendy_true.

% Xavier: "Exactly four of us in Group C are knights, and Sam is a knight"
s_xavier_true :- 4 { knight(X) : group_c(X) } 4, knight(sam).
:- knight(xavier), not s_xavier_true.
:- knave(xavier), s_xavier_true.
"""


def verify_solution(solution: Dict[str, str]) -> bool:
    """
    Verify that a solution satisfies all constraints by fixing the assignment
    in the ASP program and checking satisfiability.
    """
    required = {
        "alice", "bob", "charlie", "diana", "ethan", "fiona", "george", "hannah",
        "ian", "julia", "kevin", "lily", "mason", "nina", "oliver", "paula",
        "quentin", "rachel", "sam", "tina", "ursula", "victor", "wendy", "xavier"
    }
    if not isinstance(solution, dict):
        print("Error: solution must be a dictionary", file=sys.stderr)
        return False
    if set(solution.keys()) != required:
        print(f"Error: solution must have exactly these keys: {sorted(required)}", file=sys.stderr)
        return False
    for k, v in solution.items():
        if v not in {"knight", "knave"}:
            print(f"Error: {k} must be 'knight' or 'knave', got '{v}'", file=sys.stderr)
            return False

    # Build an ASP program that fixes each person's assignment
    fix_facts = []
    for person, typ in solution.items():
        if typ == "knight":
            fix_facts.append(f"knight({person}).")
        else:  # knave
            # Forbid being a knight; knave will be derived via complement rule
            fix_facts.append(f":- knight({person}).")

    fixed_program = ASP_PROGRAM + "\n" + "\n".join(fix_facts) + "\n"

    ctl = clingo.Control()
    ctl.add("base", [], fixed_program)
    ctl.ground([("base", [])])

    models = []
    def on_model(m):
        models.append(m)

    result = ctl.solve(on_model=on_model)
    if not result.satisfiable:
        print("Error: assignment is inconsistent with the puzzle constraints.", file=sys.stderr)
        return False

    if len(models) != 1:
        # With all knights fixed, there should be exactly one model (deterministic s_* atoms)
        print(f"Warning: expected exactly one grounded model with fixed assignment, got {len(models)}", file=sys.stderr)

    return True


def main():
    try:
        data = sys.stdin.read().strip()
        if not data:
            print(json.dumps({"valid": False, "message": "No solution provided"}))
            sys.exit(1)
        candidate = json.loads(data)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "message": f"Error parsing JSON: {e}"}))
        sys.exit(1)

    ok = verify_solution(candidate)
    result = {
        "valid": ok,
        "message": "Solution is valid and satisfies all constraints!" if ok else "Solution is invalid - logical constraints violated"
    }
    print(json.dumps(result, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
