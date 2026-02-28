SOLVER_SELECTION_PROMPT = \"\"\"Task: You are an expert logician. For a given logic puzzle (consisting of premises and a conclusion), classify which logical formalism or constraint solver is the most direct and natural fit for solving it.

You are equipped with four target solvers:
1. PROLOG: Best for logic programming, rules involving relationships, genealogies, distinct definite clauses (e.g. \"If A and B then C\"), and reachability.
2. Z3: Best for Satisfiability Modulo Theories (SMT), specifically problems involving explicit mathematics, inequalities, logic mixed with arithmetic, or complex combinations of propositional logic.
3. CONSTRAINT: Best for Constraint Satisfaction Problems (CSP), such as scheduling, coloring, \"Einstein's Riddle\" (zebra puzzle), or assigning unique values to variables from a finite domain.
4. PROVER9: Best for First Order Logic (FOL) with universal (forall) and existential (exists) quantifiers, abstract predicates, and formal mathematical proofs.

Rules:
Return ONLY the name of the solver: PROLOG, Z3, CONSTRAINT, or PROVER9. No other text.

Example 1:
Premises: All men are mortal. Socrates is a man.
Conclusion: Socrates is mortal.
Chosen solver: PROVER9

Example 2:
Premises: Three people sit in a row. Alice does not sit next to Bob. Charlie sits on the left.
Conclusion: Bob sits in the middle.
Chosen solver: CONSTRAINT

Example 3:
Premises: Jane is the mother of Mary. Mary is the mother of Paul. A grandmother is a mother of a mother.
Conclusion: Jane is the grandmother of Paul.
Chosen solver: PROLOG

Example 4:
Premises: X + Y > 10. Y is less than 5. X is an integer.
Conclusion: X is at least 6.
Chosen solver: Z3

Your problem follows.
Premises: {premises}
Conclusion: {conclusion}
Chosen solver:
\"\"\"

TRANSLATION_PROMPTS = {
    \"PROVER9\": \"\"\"Task: Translate natural language logic puzzles into strict Prover9 syntax.
1. Logical Operators: -, &, |, ->, <->
2. Quantifiers: \"all x\", \"exists x\"
3. Every formula MUST end with a period \".\"

Follow this exact structure:
formulas(assumptions).
  <formula_1>.
  <formula_2>.
end_of_list.

formulas(goals).
  <conclusion_formula>.
end_of_list.

Premises:
{premises}

Conclusion:
{conclusion}

Prover9 Code:
\"\"\",
    
    \"Z3\": \"\"\"Task: Translate natural language logic puzzles into a Python script using the z3-solver library.
1. Import z3: `from z3 import *`
2. Define variables and a solver `s = Solver()`.
3. Add premises to the solver: `s.add(...)`.
4. The goal is to prove the conclusion. To prove a statement P, we assert its negation `Not(P)` and check if it is unsatisfiable (`unsat`).
5. After adding constraints, print `s.check()`. DO NOT print anything else.

Premises:
{premises}

Conclusion:
{conclusion}

Python Z3 Code:
\"\"\",

    \"PROLOG\": \"\"\"Task: Translate natural language logic puzzles into Prolog.
1. Define facts and rules. For example: `mortal(X) :- man(X).` and `man(socrates).`
2. All assertions must end with a period `.`.
3. Lowercase all atoms. Variables must be capitalized.
4. Your script must END with a query testing the conclusion, prefixed by `?-`.
Example end: `?- mortal(socrates).`

Premises:
{premises}

Conclusion:
{conclusion}

Prolog Code:
\"\"\",

    \"CONSTRAINT\": \"\"\"Task: Translate natural language logic puzzles into a Python script using the python-constraint library (`from constraint import *`).
1. Create a `Problem()`.
2. Add variables with their domains: `problem.addVariable(name, domain)`.
3. Add constraint functions: `problem.addConstraint(...)`.
4. At the end, find solutions using `solutions = problem.getSolutions()`.
5. Check if the conclusion holds for all valid solutions (if any exist) and print a result (e.g. `print(\"True\")` if the conclusion is absolutely guaranteed by the constraints, else print `False/Uncertain`).

Premises:
{premises}

Conclusion:
{conclusion}

Python-Constraint Code:
\"\"\"
}
