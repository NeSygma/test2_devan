PAPER_DECOMPOSITION_PROMPT = """SYSTEM:
You are a logician and reasoning systems expert specializing in symbolic reasoning frameworks. Given a text that may contain one or multiple logical reasoning problems, identify each problem, determine its type, and decompose the text accordingly. Return the result strictly as a JSON object with "result" containing an array of problem objects.
Specifically, your task is to:
1. First, analyze the input text to identify how many distinct reasoning problems it contains.
2. For each identified problem, determine its type from the following categories:
- Logic Programming (LP): Problems where conclusions are typically deduced step by step from a set of known facts and rules. These problems often involve applying simple logical rules repeatedly to infer new facts until the goal is reached.
- First-order Logic (FOL): Problems that require more expressive reasoning, such as statements like "for all" or "there exists", and complex relationships among multiple entities.
- Constraint Satisfaction Problem (CSP): Problems that involve finding assignments of values to variables within finite domains such that all explicit or implicit constraints are satisfied. These often include tasks like ordering, allocation, or scheduling.
- Boolean Satisfiability (SAT): These problems involve determining whether all logical constraints in a system are simultaneously satisfied. In the context of reasoning tasks, SAT typically focuses on checking if a particular configuration or entity conforms to a set of conditions expressed as logical formulas. Unlike CSP, which searches for value assignments over finite domains, SAT emphasizes verifying logical consistency in given assignments and is often applied to analytical reasoning questions.
To guide your classification:
- Consider whether the problem leans more towards reasoning from facts and rules (often LP or FOL) or checking constraints and conditions (often CSP or SAT).
- If the focus is on assigning values or arranging elements under constraints, it is more typical of CSP.
- If the focus is on verifying whether one given description satisfies the logical requirements of another, it is more typical of SAT. Analytical reasoning problems are often classified as SAT.
- Between LP and FOL, use LP if the reasoning relies on simple rules and chaining; use FOL if it involves richer logical expressions with quantifiers or complex entity relationships.
3. For each problem, create a JSON object with the following structure:
- "problem_id" (str): A unique identifier following the pattern "ques_1", "ques_2", etc., based on the order of appearance.
- "problem_type" (str): The type classification. The value must be one of LP, FOL, CSP, SAT.
- Based on the problem type, include the appropriate fields:
- If problem_type == "LP" or "FOL":
- "premise" (str): the given premise.
- "hypothesis" (str): the hypothesis to be evaluated for truth.
- "options" (list): the provided answer options.
- If problem_type == "CSP":
- "context" (str): background description.
- "question" (str): the specific question being asked.
- "options" (list): the provided answer options.
- If problem_type == "SAT":
- "trial_description" (str): description of the trial.
- "sample_description" (str): description of the sample.
- "options" (list): the provided answer options.
Preserve any existing option labels (e.g., "A)", "B)"). If options have no labels, assign labels 'A)', 'B)', 'C)', ... automatically.
4. Extract or analyze the overall goal of the input text:
- FIRST, try to extract any explicitly stated overall goal or instruction from the text (e.g., "Answer the above questions one by one", "Solve all problems to find the final answer", etc.)
- If no explicit goal is found, analyze the relationship between problems and write a brief description:
- Multiple independent problems: "Solve multiple independent reasoning problems"
- Subproblems contributing to main problem: "Solve subproblems to address the main complex problem"
- Sequential dependent problems: "Solve problems in sequence with dependencies"
- Single problem: "Solve the reasoning problem"
Return a JSON object with two keys:
- "result": an array containing all identified problems
- "overall_goal": the extracted goal text or a brief analysis-based description
Example output format:
"result": [
"problem_id": "ques_1",
"problem_type": "CSP",
"context": "...",
"question": "...",
"options": ["A) ...", "B) ..."]
],
"overall_goal": "Answer the above questions one by one"
USER:
Problem Statement:
{problem}
"""

ONE_SHOT_CLASSIFICATION_PROMPT = """SYSTEM:
You are an expert logician. Your task is to classify the provided logical reasoning problem into one of four solver types:
- LP (Logic Programming)
- FOL (First-order Logic)
- CSP (Constraint Satisfaction Problem)
- SAT (Boolean Satisfiability)

Respond ONLY with the exact name of the category (LP, FOL, CSP, or SAT).

Example 1:
Problem Statement:
Three people sit in a row. Alice does not sit next to Bob. Charlie sits on the left. Who sits in the middle?
Category: CSP

USER:
Problem Statement:
{problem}
Category:
"""

SOLVER_SELECTION_PROMPT = """Task: You are an expert logician. For a given logic puzzle (consisting of premises and a conclusion), classify which logical formalism or constraint solver is the most direct and natural fit for solving it.

You are equipped with four target solvers:
1. PROLOG: Best for logic programming, rules involving relationships, genealogies, distinct definite clauses (e.g. "If A and B then C"), and reachability.
2. Z3: Best for Satisfiability Modulo Theories (SMT), specifically problems involving explicit mathematics, inequalities, logic mixed with arithmetic, or complex combinations of propositional logic.
3. CONSTRAINT: Best for Constraint Satisfaction Problems (CSP), such as scheduling, coloring, "Einstein's Riddle" (zebra puzzle), or assigning unique values to variables from a finite domain.
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
"""

TRANSLATION_PROMPTS = {
    "PROVER9": """Task: Translate natural language logic puzzles into strict Prover9 syntax.
1. Logical Operators: -, &, |, ->, <->
2. Quantifiers: "all x", "exists x"
3. Every formula MUST end with a period "."

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
""",
    
    "Z3": """Task: Translate natural language logic puzzles into a Python script using the z3-solver library.
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
""",

    "PROLOG": """Task: Translate natural language logic puzzles into Prolog.
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
""",

    "CONSTRAINT": """Task: Translate natural language logic puzzles into a Python script using the python-constraint library (`from constraint import *`).
1. Create a `Problem()`.
2. Add variables with their domains: `problem.addVariable(name, domain)`.
3. Add constraint functions: `problem.addConstraint(...)`.
4. At the end, find solutions using `solutions = problem.getSolutions()`.
5. Check if the conclusion holds for all valid solutions (if any exist) and print a result (e.g. `print("True")` if the conclusion is absolutely guaranteed by the constraints, else print `False/Uncertain`).

Premises:
{premises}

Conclusion:
{conclusion}

Python-Constraint Code:
"""
}
