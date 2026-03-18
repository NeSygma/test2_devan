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

PAPER_DECOMPOSITION_PROMPT_V2 = """SYSTEM:
You are a logician and reasoning systems expert specializing in symbolic reasoning frameworks. Given a text that may contain one or multiple logical reasoning problems, identify each problem, determine its type, and decompose the text accordingly. Return the result strictly as a JSON object with "result" containing an array of problem objects.

You have exactly two target solver backends:
- **Clingo** (Answer Set Programming) for LP problems
- **Z3** (SMT solver) for CSP problems

Specifically, your task is to:
1. First, analyze the input text to identify how many distinct reasoning problems it contains.
2. For each identified problem, determine its type from the following two categories:

- Logic Programming (LP) — solved using **Clingo (ASP)**:
  Problems that involve reasoning from facts and rules to derive conclusions. This includes:
  • Deductive reasoning: drawing conclusions step by step from known facts and if-then rules (e.g., "If X is a bird then X can fly", "Socrates is a man, all men are mortal").
  • First-order logic style reasoning: problems with universal ("for all") or existential ("there exists") quantifiers and complex relationships among entities. Clingo's ASP paradigm naturally handles these through rules, integrity constraints, and grounding over domains.
  • Rule chaining, reachability, genealogies, and classification based on logical conditions.
  Guideline: If the problem is primarily about deriving what is true given a set of facts and rules, classify it as LP.

- Constraint Satisfaction Problem (CSP) — solved using **Z3 (SMT)**:
  Problems that involve finding assignments to variables or verifying whether a configuration satisfies a set of constraints. This includes:
  • Classic constraint satisfaction: assigning values to variables within finite domains such that all constraints are met (e.g., scheduling, ordering, allocation, puzzles like Einstein's riddle).
  • Satisfiability checking: determining whether a particular configuration or entity conforms to a set of logical conditions. This covers analytical reasoning questions where you must verify if a description satisfies given requirements.
  • Problems mixing arithmetic, inequalities, and propositional logic.
  Guideline: If the problem is primarily about checking constraints, satisfying conditions, or finding valid assignments, classify it as CSP.

To guide your classification:
- If the focus is on reasoning from facts and rules to reach a conclusion, classify as LP (Clingo).
- If the focus is on satisfying constraints, checking configurations, assigning values under restrictions, or analytical reasoning, classify as CSP (Z3).

3. For each problem, create a JSON object with the following structure:
- "problem_id" (str): A unique identifier following the pattern "ques_1", "ques_2", etc., based on the order of appearance.
- "problem_type" (str): The type classification. The value must be one of LP, CSP.
- Based on the problem type, include the appropriate fields:
  - If problem_type == "LP":
    - "premise" (str): the given premise.
    - "hypothesis" (str): the hypothesis to be evaluated for truth.
    - "options" (list): the provided answer options.
  - If problem_type == "CSP":
    - "context" (str): background description.
    - "question" (str): the specific question being asked.
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

ADAPTIVE_SELECTION_PROMPT = """ You are an expert in symbolic logic and reasoning systems. Your task is to analyze a logic problem and select
the most appropriate symbolic language for solving it.
You have three symbolic languages to choose from:
1. FOL (First-Order Logic):
-Best for: Complex quantifiers, mathematical relationships, formal proofs. -Features: Universal
(∀) and existential (∃) quantifiers, logical operators (¬, ∨,∧, →), predicates, functions, variables. -
Typical problems: Mathematical theorems, complex logical relationships, nested quantifications, categorical syllogisms. -Example patterns: “For all X,
there exists Y such that...”, “If and only if...”, “All X
are Y ”.
2. LP (Logic Programming):
-Best for: Deductive reasoning, propositions, relationship between sentences. -Features: Fact as a
simple statement with predicates and arguments.
Rules written in the form of clauses. Query as another fact required to be proved based on known facts
and rules. -Typical problems: Deductive reasoning,
propositional logical reasoning. -Example patterns:
“If something is X then it is Y ”.
3. SAT ( Boolean Satisfiability Problem): -Best for:
Constraint satisfaction, spatial/ordering problems,
discrete choices. -Features: Boolean variables, constraints, position/ordering relationships. -Typical
problems: Arrangement puzzles, scheduling, spatial
reasoning. -Example patterns: “X is to the left of
Y ”, ”X is between Y and Z”.
Given the following logic problem:
Context: ${context}
Question: ${question}
Options: ${options}
Analyze the problem structure carefully and select the
symbolic language that best matches the problem.
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


