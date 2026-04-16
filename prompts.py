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

PAPER_DECOMPOSITION_PROMPT_V3 = """SYSTEM:
You are a logician and reasoning systems expert specializing in symbolic reasoning frameworks. Given a text that may contain one or multiple logical reasoning problems, identify each problem, determine its type, and decompose the text accordingly. Return the result strictly as a JSON object with "result" containing an array of problem objects.
Specifically, your task is to:
1. First, analyze the input text to identify how many distinct reasoning problems it contains.
2. For each identified problem, determine its type from the following categories:
- Logic Programming (LP): Problems where conclusions are deduced step by step from known facts and rules, often operating under a closed-world assumption and capable of non-monotonic default reasoning or computing transitive closures. It is highly effective for explicit deductive reasoning, expert systems, and combinatorial search using generate-define-test methodologies.
- First-order Logic (FOL): Problems requiring expressive monotonic reasoning under an open-world assumption, involving complex entity relationships, universal ("for all"), and existential ("there exists") quantifiers. Pure FOL problems can be semi-decidable, making them distinct from bounded logic programming tasks.
- SAT: A unified category for problems that involve combinatorial optimization, strict boolean satisfiability, or continuous-variable algebra. These problems require determining if a configuration satisfies a set of constraints, finding optimal value assignments over finite discrete domains, or solving constraints across infinite and continuous domains like real numbers modulo background theories.
To guide your classification:
- Consider whether the problem leans towards reasoning from facts, defaults, and relationships (LP or FOL) or towards optimizing assignments and checking the satisfiability of arithmetic/boolean constraints (SAT).
- in SAT, the problems can be either multiple-choice questions or free-form, open-ended constraint puzzles.
- use SAT if the problem involves ordering, sequencing, or allocating items based on available constraints.
- Between LP and FOL, use LP if the reasoning relies on explicit chaining, rule-based deduction, or non-monotonic exceptions; 
- use FOL if it requires complex quantified statements or open-world assumptions.
- FOL problems may involve implicit quantifiers disguised as natural language generalizations (e.g., categorical statements like "A is a B").
3. For each problem, create a JSON object with the following structure:
- "problem_id" (str): A unique identifier following the pattern "ques_1", "ques_2", etc., based on the order of appearance.
- "problem_type" (str): The type classification. The value must be one of LP, FOL, or SAT
- Based on the problem type, include the appropriate fields:
- If problem_type == "LP" or "FOL":
- "premise" (str): the given premise.
- "hypothesis" (str): the hypothesis to be evaluated for truth.
- "options" (list): the provided answer options if present.
- If problem_type == "SAT":
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
5. As a limit to the output :
- ONLY provide the problem type output as LP, FOL, or SAT. DO NOT produce any other output such as UNKNOWN.
Return a JSON object with two keys:
- "result": an array containing all identified problems
- "overall_goal": the extracted goal text or a brief analysis-based description
Example output format:
{{
"result": [
"problem_id": "ques_1",
"problem_type": "SAT",
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

ADAPTIVE_SELECTION_PROMPT_V3 = """ You are an expert in symbolic logic and reasoning systems. Your task is to analyze a logic problem and select the most appropriate solver for solving it.
You have three solvers to choose from:

1. VAMPIRE (Automated Theorem Prover — First-Order Logic):
- Best for: Problems requiring expressive monotonic reasoning under an open-world assumption, involving complex entity relationships, universal ("for all") and existential ("there exists") quantifiers, and formal theorem proving over rich relational structures.
- Features: Universal (∀) and existential (∃) quantifiers, logical connectives (¬, ∧, ∨, →, ↔), predicates, functions, constants, equality, and negation-based refutation proofs using TPTP format.
- Open-world assumption: anything not explicitly asserted as an axiom or derivable from axioms is unknown, not false.
- Typical problems: Mathematical theorems, categorical syllogisms, complex logical entailments, nested quantifications, claim checking via proof/refutation.
- Example patterns: "For all X, there exists Y such that...", "If and only if...", "All X are Y", "No A are B", "Is it true that...?", proving/disproving logical claims.

2. CLINGO (Answer Set Programming — Logic Programming):
- Best for: Problems where conclusions are deduced step by step from known facts and rules, operating under a closed-world assumption, capable of non-monotonic default reasoning, planning, and combinatorial search using generate-define-test methodology.
- Features: Facts as simple statements, rules written as clauses with heads and bodies, integrity constraints that eliminate invalid worlds, choice rules for generating candidate solutions, optimization via #minimize/#maximize, and aggregates (#count, #sum).
- Closed-world assumption: anything not explicitly stated as a fact or derivable from a rule is considered false.
- Typical problems: Deductive reasoning, rule-based inference, expert systems, planning with temporal logic and frame axioms, state exclusivity, graph coloring, scheduling with explicit action modeling.
- Example patterns: "If something is X then it is Y", "X is a bird and does not have an exception, so X can fly", "Given these rules, what can be concluded?", step-by-step rule chaining, default reasoning with exceptions.

3. Z3 (SMT Solver — Satisfiability Modulo Theories):
- Best for: Problems that involve constraints, satisfiability, consistency checking, arithmetic/logical conditions, assignment under constraints, scheduling/allocation constraints, ordering/sequencing, or SAT-like analytical reasoning. Handles both CSP-style and SAT-style problems.
- Features: Boolean (Bool), integer (Int), and real (Real) symbolic variables, Z3 logical operators (And, Or, Not, Implies), arithmetic constraints, arrays, optimization (minimize/maximize), model finding, and theorem proving via negation.
- Typical problems: Constraint satisfaction puzzles, arrangement/allocation problems, scheduling, spatial reasoning, arithmetic optimization, verifying whether a configuration satisfies logical requirements, checking consistency of assignments.
- Example patterns: "X is to the left of Y", "X is between Y and Z", "Find values such that all constraints are satisfied", "Which arrangement is valid?", ordering under constraints, resource allocation.

Given the following logic problem:
Context: ${context}
Question: ${question}
Options: ${options}
Analyze the problem structure carefully and select the solver that best matches the problem.
Provide your final answer after the analysis as a JSON object with the following format.
{
    "solver_type": "YOUR_SELECTION"
}
Example output format:
{
    "solver_type": "CLINGO"
}
"""

ADAPTIVE_SELECTION_PROMPT_RANK = """ You are an expert in symbolic logic and reasoning systems. Your task is to analyze a logic problem and select the most appropriate solver for solving it.
You have three solvers to choose from:

1. VAMPIRE (Automated Theorem Prover — First-Order Logic):
- Best for: Problems requiring expressive monotonic reasoning under an open-world assumption, involving complex entity relationships, universal ("for all") and existential ("there exists") quantifiers, and formal theorem proving over rich relational structures.
- Features: Universal (∀) and existential (∃) quantifiers, logical connectives (¬, ∧, ∨, →, ↔), predicates, functions, constants, equality, and negation-based refutation proofs using TPTP format.
- Open-world assumption: anything not explicitly asserted as an axiom or derivable from axioms is unknown, not false.
- Typical problems: Mathematical theorems, categorical syllogisms, complex logical entailments, nested quantifications, claim checking via proof/refutation.
- Example patterns: "For all X, there exists Y such that...", "If and only if...", "All X are Y", "No A are B", "Is it true that...?", proving/disproving logical claims.

2. CLINGO (Answer Set Programming — Logic Programming):
- Best for: Problems where conclusions are deduced step by step from known facts and rules, operating under a closed-world assumption, capable of non-monotonic default reasoning, planning, and combinatorial search using generate-define-test methodology.
- Features: Facts as simple statements, rules written as clauses with heads and bodies, integrity constraints that eliminate invalid worlds, choice rules for generating candidate solutions, optimization via #minimize/#maximize, and aggregates (#count, #sum).
- Closed-world assumption: anything not explicitly stated as a fact or derivable from a rule is considered false.
- Typical problems: Deductive reasoning, rule-based inference, expert systems, planning with temporal logic and frame axioms, state exclusivity, graph coloring, scheduling with explicit action modeling.
- Example patterns: "If something is X then it is Y", "X is a bird and does not have an exception, so X can fly", "Given these rules, what can be concluded?", step-by-step rule chaining, default reasoning with exceptions.

3. Z3 (SMT Solver — Satisfiability Modulo Theories):
- Best for: Problems that involve constraints, satisfiability, consistency checking, arithmetic/logical conditions, assignment under constraints, scheduling/allocation constraints, ordering/sequencing, or SAT-like analytical reasoning. Handles both CSP-style and SAT-style problems.
- Features: Boolean (Bool), integer (Int), and real (Real) symbolic variables, Z3 logical operators (And, Or, Not, Implies), arithmetic constraints, arrays, optimization (minimize/maximize), model finding, and theorem proving via negation.
- Typical problems: Constraint satisfaction puzzles, arrangement/allocation problems, scheduling, spatial reasoning, arithmetic optimization, verifying whether a configuration satisfies logical requirements, checking consistency of assignments.
- Example patterns: "X is to the left of Y", "X is between Y and Z", "Find values such that all constraints are satisfied", "Which arrangement is valid?", ordering under constraints, resource allocation.

Given the following logic problem:
Context: ${context}
Question: ${question}
Options: ${options}
Analyze the problem structure carefully and rank ALL three solvers from most suitable to least suitable for this problem.
Provide your final answer after the analysis as a JSON object with the following format.
{
    "solver_ranking": ["MOST_SUITABLE", "SECOND_CHOICE", "LEAST_SUITABLE"]
}
Example output format:
{
    "solver_ranking": ["CLINGO", "Z3", "VAMPIRE"]
}
"""

ADAPTIVE_SELECTION_PROMPT_RANK_2 = """ You are an expert in symbolic logic and reasoning systems. Your task is to analyze a logic problem and select the most appropriate solver for solving it.
You have three solvers to choose from:

1. VAMPIRE (Automated Theorem Prover — First-Order Logic):
- Best for: Determining whether a natural-language conclusion logically follows from a set of premises, where the answer may be True, False, or Uncertain. Excels at abstract categorical reasoning with universal ("for all") and existential ("there exists") quantifiers over rich relational structures, under an open-world assumption.
- Features: Universal (∀) and existential (∃) quantifiers, predicates, logical connectives (¬, ∧, ∨, →, ↔), and negation-based refutation proofs using TPTP format.
- Warning: Not ideal for problems requiring numeric counting bounds, entity-to-position assignment, or explicit integer arithmetic.
- Typical problems: Entailment checking from premises to a conclusion, categorical syllogisms, property inheritance chains, proving/disproving abstract claims.
- Example patterns: "All X are Y", "No A are B", "If someone is P then they are Q", premises describing categories and properties of named individuals.

2. CLINGO (Answer Set Programming — Logic Programming):
- Best for: Combinatorial search and planning problems that require finding a valid configuration or action sequence over fully-specified discrete domains. Operates under a strict closed-world assumption with generate-define-test methodology.
- Features: Facts, rules, integrity constraints, choice rules, optimization (#minimize/#maximize), aggregates (#count, #sum), and recursive reachability/path finding.
- Warning: Grounding blows up on large numeric ranges. If the problem requires complex arithmetic, real numbers, or counting bounds with conditional slot references, do not use Clingo.
- Typical problems: Logic puzzles, graph coloring, multi-step action planning, resource allocation with discrete choices, set cover, combinatorial optimization.
- Example patterns: "Find a valid sequence of state transitions connecting a start state to a goal state", "Assign properties to discrete elements such that no exclusion rules are violated", "Find all valid combinations that satisfy a closed set of conditions".

3. Z3 (SMT Solver — Satisfiability Modulo Theories):
- Best for: Problems that assign entities to ordered positions or slots under strict conditional constraints with numeric counting bounds ("at least N", "no more than M", "exactly K per slot"). Handles both constraint satisfaction and validity checking with precise arithmetic.
- Features: Integer, Real, and Boolean symbolic variables, Z3 logical operators (And, Or, Not, Implies), arithmetic constraints, Distinct, arrays, optimization (minimize/maximize), and model finding.
- Warning: Not ideal for multi-step action planning, recursive path finding, or pure qualitative logic with complex quantifier nesting where no numeric or positional structure is present.
- Typical problems: Entity-to-slot scheduling under conditional rules, selection problems with cardinality bounds, ordering/sequencing with positional constraints, verifying which arrangement is valid or must be true.
- Example patterns: "Assign items to a discrete sequence of positions governed by relational constraints", "Select subsets governed by specific numeric minimum or maximum cardinality bounds", "Evaluate which conditional assignments must or could logically be true".

Given the following logic problem:
Context: ${context}
Question: ${question}
Options: ${options}
Analyze the problem structure carefully and rank ALL three solvers from most suitable to least suitable for this problem.
Provide your final answer after the analysis as a JSON object with the following format.
{
    "solver_ranking": ["MOST_SUITABLE", "SECOND_CHOICE", "LEAST_SUITABLE"]
}
Example output format:
{
    "solver_ranking": ["CLINGO", "Z3", "VAMPIRE"]
}
"""

ADAPTIVE_SELECTION_PROMPT_RANK_3 = """ You are an expert in symbolic logic and reasoning systems. Your task is to analyze a logic problem and select the most appropriate solver for solving it.
You have three solvers to choose from:

1. VAMPIRE (Automated Theorem Prover — First-Order Logic):
- Target Answer Types: True/False/Uncertain, Yes/No entailment checks, and determining if a specific hypothesis is valid or invalid.
- Best for: Problems requiring expressive monotonic reasoning under an open-world assumption, involving complex entity relationships, universal ("for all") and existential ("there exists") quantifiers, and formal theorem proving over rich relational structures.
- Features: Universal (∀) and existential (∃) quantifiers, logical connectives (¬, ∧, ∨, →, ↔), predicates, functions, constants, equality, and negation-based refutation proofs using TPTP format.
- Open-world assumption: anything not explicitly asserted as an axiom or derivable from axioms is unknown, not false.
- Typical problems: Mathematical theorems, categorical syllogisms, complex logical entailments, nested quantifications, claim checking via proof/refutation.
- Example patterns: "For all X, there exists Y such that...", "If and only if...", "All X are Y", "No A are B", "Is it true that...?", proving/disproving logical claims.

2. CLINGO (Answer Set Programming — Logic Programming):
- Target Answer Types: Constructed configurations, enumeration of all valid states, exact plans/schedules, or structurally generated outputs.
- Best for: Problems where conclusions are deduced step by step from known facts and rules, operating under a closed-world assumption, capable of non-monotonic default reasoning, planning, and combinatorial search using generate-define-test methodology.
- Features: Facts as simple statements, rules written as clauses with heads and bodies, integrity constraints that eliminate invalid worlds, choice rules for generating candidate solutions, optimization via #minimize/#maximize, and aggregates (#count, #sum).
- Closed-world assumption: anything not explicitly stated as a fact or derivable from a rule is considered false.
- Typical problems: Deductive reasoning, rule-based inference, expert systems, planning with temporal logic and frame axioms, state exclusivity, graph coloring, scheduling with explicit action modeling.
- Example patterns: "If something is X then it is Y", "X is a bird and does not have an exception, so X can fly", "Given these rules, what can be concluded?", step-by-step rule chaining, default reasoning with exceptions.

3. Z3 (SMT Solver — Satisfiability Modulo Theories):
- Target Answer Types: Multiple-choice options (by testing each option against constraints to see which must/could be true), and specific variable assignments.
- Best for: Problems that involve constraints, satisfiability, consistency checking, arithmetic/logical conditions, assignment under constraints, scheduling/allocation constraints, ordering/sequencing, or SAT-like analytical reasoning. Handles both CSP-style and SAT-style problems.
- Features: Boolean (Bool), integer (Int), and real (Real) symbolic variables, Z3 logical operators (And, Or, Not, Implies), arithmetic constraints, arrays, optimization (minimize/maximize), model finding, and theorem proving via negation.
- Typical problems: Constraint satisfaction puzzles, arrangement/allocation problems, scheduling, spatial reasoning, arithmetic optimization, verifying whether a configuration satisfies logical requirements, checking consistency of assignments.
- Example patterns: "X is to the left of Y", "X is between Y and Z", "Find values such that all constraints are satisfied", "Which arrangement is valid?", ordering under constraints, resource allocation.

Given the following logic problem:
Context: ${context}
Question: ${question}
Options: ${options}
Analyze the problem and answer structure carefully and rank ALL three solvers from most suitable to least suitable for this problem regardless of its difficulty.
Provide your final answer after the analysis as a JSON object with the following format.
{
    "solver_ranking": ["MOST_SUITABLE", "SECOND_CHOICE", "LEAST_SUITABLE"]
}
Example output format:
{
    "solver_ranking": ["CLINGO", "Z3", "VAMPIRE"]
}
"""

ADAPTIVE_SELECTION_PROMPT_RANK_4 = """ You are an expert in symbolic logic and reasoning systems. Your task is to analyze a logic problem and select the most appropriate solver for solving it.
You have three solvers to choose from:

1. VAMPIRE (Automated Theorem Prover — First-Order Logic):
- Target Answer Types: True/False/Uncertain, Yes/No entailment checks, and determining if a specific hypothesis is valid or invalid.
- Best for: Determining whether a natural-language conclusion logically follows from a set of premises, where the answer may be True, False, or Uncertain. Excels at abstract categorical reasoning with universal ("for all") and existential ("there exists") quantifiers over rich relational structures, under an open-world assumption.
- Features: Universal (∀) and existential (∃) quantifiers, predicates, logical connectives (¬, ∧, ∨, →, ↔), functions, constants, equality, and negation-based refutation proofs using TPTP format.
- Open-world assumption: anything not explicitly asserted as an axiom or derivable from axioms is unknown, not false.
- Warning: Not ideal for problems requiring numeric counting bounds, entity-to-position assignment, or explicit integer arithmetic.
- Typical problems: Entailment checking from premises to a conclusion, categorical syllogisms, property inheritance chains, complex logical entailments, nested quantifications, proving/disproving abstract claims.
- Example patterns: "All X are Y", "No A are B", "If someone is P then they are Q", "For all X, there exists Y such that...", "If and only if...", "Is it true that...?", premises describing categories and properties of named individuals.

2. CLINGO (Answer Set Programming — Logic Programming):
- Target Answer Types: Constructed configurations, enumeration of all valid states, exact plans/schedules, or structurally generated outputs.
- Best for: Combinatorial search and planning problems that require finding a valid configuration or action sequence over fully-specified discrete domains. Operates under a strict closed-world assumption with generate-define-test methodology. Capable of non-monotonic default reasoning and step-by-step deduction from known facts and rules.
- Features: Facts as simple statements, rules written as clauses with heads and bodies, integrity constraints that eliminate invalid worlds, choice rules for generating candidate solutions, optimization via #minimize/#maximize, aggregates (#count, #sum), and recursive reachability/path finding.
- Closed-world assumption: anything not explicitly stated as a fact or derivable from a rule is considered false.
- Warning: Grounding blows up on large numeric ranges. If the problem requires complex arithmetic, real numbers, or counting bounds with conditional slot references, do not use Clingo.
- Typical problems: Logic puzzles, graph coloring, multi-step action planning, resource allocation with discrete choices, combinatorial optimization, deductive reasoning, rule-based inference, expert systems, state exclusivity.
- Example patterns: "If something is X then it is Y", "X is a bird and does not have an exception, so X can fly", "Given these rules, what can be concluded?", "Find a valid sequence of state transitions connecting a start state to a goal state", "Assign properties to discrete elements such that no exclusion rules are violated", step-by-step rule chaining, default reasoning with exceptions.

3. Z3 (SMT Solver — Satisfiability Modulo Theories):
- Target Answer Types: Multiple-choice options (by testing each option against constraints to see which must/could be true), and specific variable assignments.
- Best for: Problems that assign entities to ordered positions or slots under strict conditional constraints with numeric counting bounds ("at least N", "no more than M", "exactly K per slot"). Handles constraint satisfaction, consistency checking, arithmetic/logical conditions, scheduling/allocation constraints, ordering/sequencing, and SAT-like analytical reasoning. Handles both CSP-style and SAT-style problems.
- Features: Boolean (Bool), integer (Int), and real (Real) symbolic variables, Z3 logical operators (And, Or, Not, Implies), arithmetic constraints, Distinct, arrays, optimization (minimize/maximize), model finding, and theorem proving via negation.
- Warning: Not ideal for multi-step action planning, recursive path finding, or pure qualitative logic with complex quantifier nesting where no numeric or positional structure is present.
- Typical problems: Entity-to-slot scheduling under conditional rules, selection problems with cardinality bounds, ordering/sequencing with positional constraints, arrangement/allocation problems, spatial reasoning, arithmetic optimization, verifying whether a configuration satisfies logical requirements, checking consistency of assignments.
- Example patterns: "X is to the left of Y", "X is between Y and Z", "Assign items to a discrete sequence of positions governed by relational constraints", "Select subsets governed by specific numeric minimum or maximum cardinality bounds", "Evaluate which conditional assignments must or could logically be true", "Which arrangement is valid?", ordering under constraints, resource allocation.

Given the following logic problem:
Context: ${context}
Question: ${question}
Options: ${options}
Analyze the problem and answer structure carefully and rank ALL three solvers from most suitable to least suitable for this problem regardless of its difficulty.
Provide your final answer after the analysis as a JSON object with the following format.
{
    "solver_ranking": ["MOST_SUITABLE", "SECOND_CHOICE", "LEAST_SUITABLE"]
}
Example output format:
{
    "solver_ranking": ["CLINGO", "Z3", "VAMPIRE"]
}
"""

DECOMPOSITION_CUSTOM_PROMPT = """ You are a logician and reasoning systems expert specializing in symbolic reasoning frameworks. Given a text that may contain one or multiple logical reasoning problems, identify each problem, determine its type, and decompose the text accordingly. Return the result strictly as a JSON object with "result" containing an array of problem objects.
Specifically, your task is to:
1. First, analyze the input text to identify how many distinct reasoning problems it contains.
2. For each identified problem, determine its type from the following categories:
- Logic Programming (LP): Problems to be solved with Answer Set Programming (ASP) using clingo. This includes rule-based inference, default/non-monotonic reasoning, planning, and related ASP-style tasks.
- First-order Logic (FOL): Problems to be solved with the Vampire automated theorem prover. These typically involve quantified statements (e.g., "for all", "there exists"), predicates, and theorem proving over rich relational structures.
- Satisfiability Modulo Theories (SMT): Problems that involve constraints, satisfiability, consistency checking, arithmetic/logical conditions, assignment under constraints, scheduling/allocation constraints, or SAT-like analytical reasoning. Treat both CSP-style and SAT-style problems as SMT problems to be solved using the Z3 solver.
Output mapping requirement:
- LP -> CLINGO
- FOL -> VAMPIRE
- SMT -> Z3
To guide your classification:
- Consider whether the problem leans more toward ASP-style rule reasoning/planning (LP), first-order theorem proving (FOL), or constraint/satisfiability solving (SMT).
- Use LP when the task is naturally represented as logic rules, answer sets, or planning transitions/actions.
- Use FOL when the task is best expressed with quantified first-order formulas and theorem-proving style entailment/refutation.
- Use SMT when the task centers on checking satisfiability/validity under constraints, including tasks that previously look like CSP or SAT.
3. For each problem, create a JSON object with the following structure:
- "problem_id" (str): A unique identifier following the pattern "ques_1", "ques_2", etc., based on the order of appearance.
- "problem_type" (str): The solver label. The value must be exactly one of CLINGO, VAMPIRE, Z3.
- Based on the problem type, include the appropriate fields:
- If problem_type == "CLINGO" or "VAMPIRE":
- "premise" (str): the given premise.
- "hypothesis" (str): the hypothesis to be evaluated for truth.
- "options" (list): the provided answer options.
- If problem_type == "Z3":
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

Strict value/output constraints:
- In every problem object, "problem_type" must be exactly CLINGO, VAMPIRE, or Z3 (uppercase).
- Do not use LP, FOL, SMT, CSP, or SAT in the output JSON values.
- Return valid JSON only, with no extra commentary outside the JSON.

Example output format:
{{
  "result": [
    {{
      "problem_id": "ques_1",
      "problem_type": "Z3",
      "context": "...",
      "question": "...",
      "options": ["A) ...", "B) ..."]
    }}
  ],
  "overall_goal": "Answer the above questions one by one"
}}
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
