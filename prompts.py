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
Specifically, your task is to:
1. First, analyze the input text to identify how many distinct reasoning problems it contains.
2. For each identified problem, determine its type from the following categories:
- Logic Programming (LP): Problems where conclusions are deduced step by step from known facts and rules, often operating under a closed-world assumption and capable of non-monotonic default reasoning or computing transitive closures. It is highly effective for explicit deductive reasoning, expert systems, and combinatorial search using generate-define-test methodologies.
- First-order Logic (FOL): Problems requiring expressive monotonic reasoning under an open-world assumption, involving complex entity relationships, universal ("for all"), and existential ("there exists") quantifiers. Pure FOL problems can be semi-decidable, making them distinct from bounded logic programming tasks.
- CSP/SAT/SMT: A unified category for problems that involve combinatorial optimization, strict boolean satisfiability, or continuous-variable algebra. These problems require determining if a configuration satisfies a set of constraints (SAT), finding optimal value assignments over finite discrete domains (CSP), or solving constraints across infinite and continuous domains like real numbers modulo background theories (SMT).
To guide your classification:
- Consider whether the problem leans towards reasoning from facts, defaults, and relationships (LP or FOL) or towards optimizing assignments and checking the satisfiability of arithmetic/boolean constraints (CSP/SAT/SMT).
- in CSP/SAT/SMT, the problems can be either multiple-choice questions or free-form, open-ended constraint puzzles.
- use CSP/SAT/SMT if the problem involves ordering, sequencing, or allocating items based on available constraints.
- Between LP and FOL, use LP if the reasoning relies on explicit chaining, rule-based deduction, or non-monotonic exceptions; 
- use FOL if it requires complex quantified statements or open-world assumptions.
- FOL problems may involve implicit quantifiers disguised as natural language generalizations (e.g., categorical statements like "A is a B").
3. For each problem, create a JSON object with the following structure:
- "problem_id" (str): A unique identifier following the pattern "ques_1", "ques_2", etc., based on the order of appearance.
- "problem_type" (str): The type classification. The value must be one of LP, FOL, or CSP/SAT/SMT.
- Based on the problem type, include the appropriate fields:
- If problem_type == "LP" or "FOL":
- "premise" (str): the given premise.
- "hypothesis" (str): the hypothesis to be evaluated for truth.
- "options" (list): the provided answer options if present.
- If problem_type == "CSP/SAT/SMT":
- "context" (str): background description, constraints, or trial parameters.
- "question" (str): the specific question being asked or sample description to verify.
- "options" (list): the provided answer options if present.
If options are present, preserve any existing option labels (e.g., "A)", "B)"). If the present options have no labels, assign labels 'A)', 'B)', 'C)',... automatically.
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
{{
"result": [
"problem_id": "ques_1",
"problem_type": "CSP/SAT/SMT",
"context": "...",
"question": "...",
"options": ["A) ...", "B) ..."]
],
"overall_goal": "Answer the above questions one by one"
}}
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

ADAPTIVE_SELECTION_PROMPT_V2 = """ You are an expert in symbolic logic and reasoning systems. Your task is to analyze a logic problem and select
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
Provide your final answer STRICTLY as a JSON object with the following format. Do not include any other text, reasoning or markdown format outside of this JSON block:
{
    "problem_type": "YOUR_SELECTION"
}
Example output format:
{
    "problem_type": "LP"
}
"""

ADAPTIVE_SELECTION_PROMPT_V2_1 = """ You are an expert in symbolic logic and reasoning systems. Your task is to analyze a logic problem and select
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
Provide your final answer after the analysis as a JSON object with the following format.
{
    "problem_type": "YOUR_SELECTION"
}
Example output format:
{
    "problem_type": "LP"
}
"""

ADAPTIVE_SELECTION_PROMPT_V3 = """ You are an expert in symbolic logic and reasoning systems. Your task is to analyze a logic problem and select
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
symbolic language that best matches the problem and write it the final answer as "Chosen symbolic languange : YOUR_SELECTION".
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

FEW_SHOT_CLASSIFICATION_PROMPT = """SYSTEM:
You are an expert logician. Your task is to classify the provided logical reasoning problem into one of three solver types:
- LP (Logic Programming)
- FOL (First-order Logic)
- CSP (Constraint Satisfaction Problem)

Respond ONLY with the exact name of the category (LP, FOL, or CSP).

Example 1:
Problem Statement:
If someone is a bird and does not have a known exception to flying, then they can fly. Tweety is a bird. Penguins are birds but cannot fly. Is Tweety able to fly?
Category: LP

Example 2:
Problem Statement:
All mammals are warm-blooded. No reptiles are warm-blooded. Some pets are mammals. Some pets are reptiles. Is it true that there exists a pet that is warm-blooded?
Category: FOL

Example 3:
Problem Statement:
Three people sit in a row. Alice does not sit next to Bob. Charlie sits on the left. Who sits in the middle?
Category: CSP

USER:
Problem Statement:
{problem}
Category:
"""
