#!/usr/bin/env python3
"""
Reference model for "Who Killed Agatha? — The Mansion at Midnight (Extreme Hard)"
Validates a proposed killer against the constraints (satisfiability only).
"""

import json
import sys
import clingo

NAMES = [
    "Agatha", "Butler", "Charles", "Daisy", "Edward", "Felicity",
    "George", "Harriet", "Ian", "Julia", "Kenneth", "Lucy"
]

def verify_solution(solution_json: str) -> dict:
    # Parse JSON
    try:
        solution = json.loads(solution_json)
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"Invalid JSON: {e}"}

    # Required fields
    if "killer" not in solution:
        return {"valid": False, "message": "Missing required field: killer"}
    if "killer_name" not in solution:
        return {"valid": False, "message": "Missing required field: killer_name"}

    killer = solution["killer"]
    killer_name = solution["killer_name"]

    # Validate fields
    if not isinstance(killer, int) or killer < 0 or killer >= len(NAMES):
        return {"valid": False, "message": f"Invalid killer index: {killer}. Must be 0..11"}
    if killer_name != NAMES[killer]:
        return {"valid": False, "message": f"Name mismatch: index {killer} should be {NAMES[killer]}, got {killer_name}"}

    # Build ASP program with killer fixed
    program = f"""
    % Domain
    person(0..11).
    #const agatha=0.
    #const butler=1.
    #const charles=2.
    #const daisy=3.
    #const edward=4.
    #const felicity=5.
    #const george=6.
    #const harriet=7.
    #const ian=8.
    #const julia=9.
    #const kenneth=10.
    #const lucy=11.

    room(0..11).  % 0:Study,1:Hall,2:Kitchen,3:Library,4:Garden,5:Dining,6:Cellar,7:Lounge,8:Conservatory,9:Bedroom,10:Attic,11:Garage
    #const study=0.
    #const hall=1.
    #const kitchen=2.
    #const library=3.
    #const garden=4.
    #const dining=5.
    #const cellar=6.
    #const lounge=7.
    #const conservatory=8.
    #const bedroom=9.
    #const attic=10.
    #const garage=11.

    time(0..6).
    time2(1..6).
    #const murder_time=4.
    #const victim=0.  % Agatha

    weapon(0..5).  % 0:Gun,1:Knife,2:Rope,3:Candlestick,4:Wrench,5:Poison
    #const gun=0.
    #const knife=1.
    #const rope=2.
    #const candlestick=3.
    #const wrench=4.
    #const poison=5.

    % Fix killer from provided solution
    killer({killer}).

    % Exactly one weapon used; fixed to Knife for this variant
    1 {{ used(W) : weapon(W) }} 1.
    used(knife).

    % Exactly one room per person per time
    1 {{ in(P,R,T) : room(R) }} 1 :- person(P), time(T).

    % Room adjacency (undirected)
    edge(study,hall). edge(hall,study).
    edge(study,library). edge(library,study).
    edge(hall,kitchen). edge(kitchen,hall).
    edge(hall,dining). edge(dining,hall).
    edge(hall,cellar). edge(cellar,hall).
    edge(hall,lounge). edge(lounge,hall).
    edge(hall,bedroom). edge(bedroom,hall).
    edge(library,garden). edge(garden,library).
    edge(library,lounge). edge(lounge,library).
    edge(kitchen,dining). edge(dining,kitchen).
    edge(kitchen,garage). edge(garage,kitchen).
    edge(dining,lounge). edge(lounge,dining).
    edge(cellar,garage). edge(garage,cellar).
    edge(garden,conservatory). edge(conservatory,garden).
    edge(garden,garage). edge(garage,garden).
    edge(conservatory,lounge). edge(lounge,conservatory).
    edge(bedroom,attic). edge(attic,bedroom).
    edge(bedroom,lounge). edge(lounge,bedroom).
    edge(attic,lounge). edge(lounge,attic).

    adj(R1,R2) :- edge(R1,R2).

    % Local movement constraint (stay or move to adjacent room)
    :- person(P), time2(T), in(P,R1,T-1), in(P,R2,T), R1 != R2, not adj(R1,R2).

    % High-confidence (hard) locations at time 4 (murder time)
    in(agatha, study, murder_time).
    in(lucy,   study, murder_time).
    in(butler, cellar, murder_time).
    in(charles,library,murder_time).
    in(daisy,  hall,   murder_time).
    in(edward, garden, murder_time).
    in(felicity,kitchen,murder_time).
    in(george, dining, murder_time).
    in(harriet,lounge, murder_time).
    in(ian,    conservatory, murder_time).
    in(julia,  bedroom,murder_time).
    in(kenneth,attic,  murder_time).

    % Killer must be in study at the murder time; victim in study by fact above
    :- killer(K), not in(K, study, murder_time).

    % No suicides
    :- killer(victim).

    % Hates and richer choices
    {{ hates(X,Y) }} :- person(X), person(Y).
    {{ richer(X,Y) }} :- person(X), person(Y).

    % Core constraints
    % 1) Killer hates victim
    :- killer(K), not hates(K, victim).

    % 2) Killer not richer than victim
    :- killer(K), richer(K, victim).

    % 3) Charles hates no one that Agatha hates
    :- hates(agatha, X), hates(charles, X).

    % 4) Agatha hates everybody except the butler
    :- person(X), X != butler, not hates(agatha, X).
    :- hates(agatha, butler).

    % 5) Butler hates everyone not richer than Aunt Agatha
    :- person(X), not richer(X, agatha), not hates(butler, X).

    % 6) Butler hates everyone whom Agatha hates
    :- hates(agatha, X), not hates(butler, X).

    % 7) No one hates everyone
    :- person(X), 12 {{ hates(X,Y) : person(Y) }}.

    % Wealth sanity: irreflexive and antisymmetric
    :- richer(X, X).
    :- richer(X, Y), richer(Y, X), X != Y.

    % Forensics (knife-consistent): at least 8 of 10 must hold
    f(1..10).
    fholds(1) :- used(knife).  % no GSR near body
    fholds(2) :- used(knife).  % no shell casings
    fholds(3) :- used(knife).  % not blunt-force primary
    fholds(4) :- used(knife).  % blade-consistent wounds
    fholds(5) :- used(knife).  % no ligature marks
    fholds(6) :- used(knife).  % clean-edged cut
    fholds(7) :- used(knife).  % no heavy-object spatter
    fholds(8) :- used(knife).  % no powder burns
    fholds(9) :- used(knife).  % no toxin trace in glass
    fholds(10) :- used(knife). % kitchen knife missing
    :- not 8 {{ fholds(I) : f(I) }}.

    % Medium-reliability statements: at least 14 of 18 must hold
    m(1..18).
    mholds(1)  :- in(charles, library, 3).
    mholds(2)  :- in(butler,  hall,    3).
    mholds(3)  :- in(daisy,   dining,  3).
    mholds(4)  :- in(edward,  garden,  5).
    mholds(5)  :- in(felicity,kitchen, 5).
    mholds(6)  :- in(george,  lounge,  5).
    mholds(7)  :- in(harriet, lounge,  3).
    mholds(8)  :- in(ian,     conservatory, 5).
    mholds(9)  :- in(julia,   bedroom, 5).
    mholds(10) :- in(kenneth, attic,   5).
    mholds(11) :- in(lucy,    hall,    3).
    mholds(12) :- in(agatha,  study,   3).
    mholds(13) :- in(charles, library, 5).
    mholds(14) :- in(butler,  cellar,  5).
    mholds(15) :- in(daisy,   hall,    5).
    mholds(16) :- in(edward,  garden,  3).
    mholds(17) :- in(felicity,kitchen, 3).
    mholds(18) :- in(george,  dining,  3).
    :- not 14 {{ mholds(S) : m(S) }}.
    """

    ctl = clingo.Control()
    ctl.add("base", [], program)
    ctl.ground([("base", [])])

    sat = False
    def on_model(m):
        nonlocal sat
        sat = True

    ctl.solve(on_model=on_model)
    if not sat:
        return {"valid": False, "message": f"Solution violates constraints for killer={killer_name}"}
    return {"valid": True, "message": f"Solution is valid: {killer_name} is the killer"}

def main():
    if len(sys.argv) > 1 and sys.argv[1] != "--":
        with open(sys.argv[1], "r") as f:
            data = f.read()
    else:
        data = sys.stdin.read()
    result = verify_solution(data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)

if __name__ == "__main__":
    main()
