# Adaptive Neuro-Symbolic Reasoning: Dynamic Logical Solver Selection and Prompt Engineering
**Final University Project Report**

---

## 1. Literature Review

The integration of Large Language Models (LLMs) with formal symbolic solvers represents a major frontier in artificial intelligence, aiming to combine the flexible natural language understanding of neural networks with the rigorous, deterministic deduction of symbolic systems. This project draws primary inspiration from two recent papers that address the dynamic integration of these paradigms.

### 1.1 Adaptive LLM-Symbolic Reasoning via Dynamic Logical Solver Composition (arXiv:2510.06774)
This paper introduces an adaptive, multi-paradigm neuro-symbolic framework. It critiques current neuro-symbolic methods for being overwhelmingly "static"—meaning the target symbolic solver (e.g., a specific theorem prover or satisfiability solver) is hard-coded at design time. This static binding prevents systems from generalizing across heterogeneous reasoning tasks. The authors propose a dynamic framework capable of automatically identifying the required formal reasoning strategy from natural language and routing it to the appropriate specialized solver via autoformalization interfaces. Their experiments demonstrate that LLMs can predict necessary reasoning strategies with >90% accuracy, outperforming both static neuro-symbolic baselines and pure LLM reasoning approaches. In our pipeline, this paper inspired the initial **Decomposition Prompts**, which tasked the LLM with breaking down problem texts and identifying the broad reasoning category (Logic Programming, First-Order Logic, Constraint Satisfaction).

### 1.2 Adaptive Selection of Symbolic Languages for Improving LLM Logical Reasoning (arXiv:2510.10703)
Building on the need for dynamic routing, this paper argues that the performance of neuro-symbolic systems is heavily bottlenecked by the choice of the target Symbolic Language (SL) prior to translation. It posits that different logical reasoning problems inherently map better to specific formalisms. For instance, First-Order Logic (FOL) excels at categorical syllogisms and complex quantifiers, while Boolean Satisfiability (SAT) or Satisfiability Modulo Theories (SMT) excel at constraint satisfaction and spatial reasoning. The authors introduce a method to prompt LLMs to adaptively select the most suitable SL (FOL, Logic Programming, or SAT) before attempting autoformalization. Their adaptive selection method achieved a 96% accuracy on mixed datasets, significantly improving overall pipeline performance compared to static or random selection. In our workspace, this directly inspired the **Adaptive Selection Prompts**, which we evolved to specifically target exact solvers (VAMPIRE, CLINGO, Z3) rather than generic languages.

---

## 2. Research Methods and Prompt Engineering Pipeline

The objective of this research was to operationalize the adaptive theories from the literature and progressively engineer LLM prompts to maximize solver selection accuracy. We utilized multiple logical reasoning benchmarks (FOLIO, AR-LSAT, ASPBench, ProofWriter, LogDeduc) and evaluated prompts using state-of-the-art LLMs, primarily GPT-OSS-120B and Gemini 3.1 Flash Lite. 

### 2.1 Evolution of the Decomposition Prompts
Initially, based on arXiv:2510.06774, we created the `PAPER_DECOMPOSITION_PROMPT`. This prompt instructed the LLM to classify problems into Logic Programming (LP), First-order Logic (FOL), Constraint Satisfaction (CSP), or Boolean Satisfiability (SAT). 
- **Trials and Improvements**: We observed that CSP and SAT boundaries were blurry for the LLM. In `PAPER_DECOMPOSITION_PROMPT_V2`, we merged CSP, SAT, and SMT into a unified constraint-solving category. By `V3`, we refined the definitions further, mapping LP specifically to non-monotonic deductive reasoning, FOL to expressive open-world reasoning, and SAT to strict boolean/continuous variable assignments. 

### 2.2 Evolution of the Adaptive Selection Prompts
Inspired by arXiv:2510.10703, we transitioned from identifying generic problem types to explicitly selecting downstream solvers, shifting from theoretical categories (FOL, LP, SAT) to practical targets: **VAMPIRE** (FOL), **CLINGO** (LP), and **Z3** (SMT/SAT).

- **`ADAPTIVE_SELECTION_PROMPT_V3`**: Introduced specific descriptions for VAMPIRE, CLINGO, and Z3, asking the LLM for a single `"solver_type"` prediction.
- **`ADAPTIVE_SELECTION_PROMPT_RANK`**: A major paradigm shift. Instead of a single classification, the LLM was asked to rank all three solvers (`["MOST_SUITABLE", "SECOND_CHOICE", "LEAST_SUITABLE"]`). This allowed us to measure the LLM's nuanced understanding of solver applicability.
- **`ADAPTIVE_SELECTION_PROMPT_RANK_2`**: We realized the LLM was making naïve choices. We injected explicit negative constraints ("Warnings") into the prompt. For example, explicitly warning that VAMPIRE struggles with explicit integer arithmetic, and CLINGO grounds out exponentially on large numerical ranges, pushing those problems correctly to Z3.
- **`ADAPTIVE_SELECTION_PROMPT_RANK_3`**: We added "Target Answer Types" to the prompt, teaching the LLM to consider the expected output. For instance, True/False entails VAMPIRE, whereas constructed configurations entail CLINGO, and multiple-choice bounding entails Z3.
- **`ADAPTIVE_SELECTION_PROMPT_RANK_4`**: The final iteration merged the strengths of `RANK_2` and `RANK_3`, providing the LLM with both "Target Answer Types" and explicit "Warnings" regarding domain boundaries and mathematical capabilities.

### 2.3 Evaluation Methodology
To assess the effectiveness of our prompt evolution, we implemented an **Order-Based Scoring System** via `run_rank_comparison.py`. Rather than binary correct/incorrect accuracy, we compared the LLM's full predicted ranking against an ideal benchmark ranking (e.g., AR-LSAT ideal: `[Z3, CLINGO, VAMPIRE]`). 
- **1.0 (Perfect)**: Exact match with the ideal order.
- **0.75 (Top-2 Swap)**: 1st and 2nd choices swapped, but the worst solver correctly placed last.
- **0.50 (Bot-2 Swap)**: 1st choice correct, but 2nd and 3rd swapped.
- **0.00 (Bad)**: The least suitable solver leaked into the 1st or 2nd position.

---

## 3. Results and Discussion

The rigorous iteration of prompts yielded significant, observable improvements in how the LLMs routed problems to formal solvers. 

1. **Impact of Explicit Constraints (`RANK_2`)**: Providing the LLM with explicit warnings about solver limitations (e.g., CLINGO's grounding blowout) drastically reduced the number of "Bad" (0.0) scores, particularly on mathematically heavy datasets like AR-LSAT. The LLM learned to avoid assigning arithmetic problems to Logic Programming.
2. **Impact of Answer-Type Targeting (`RANK_3`)**: Teaching the LLM to look at the expected answer structure (True/False vs. State Generation) improved the accuracy on FOLIO and ASPBench. The model could effectively bypass deep semantic confusion by looking at the syntactic structure of the goal.
3. **Synergy in `RANK_4`**: By combining warnings and answer-type heuristics, `RANK_4` provided the most stable and reliable rankings across all benchmarks. It successfully demonstrated that the theories from arXiv:2510.10703 could be practically implemented to achieve near-perfect target solver routing.
4. **Cross-Model Generalization**: The experiments confirmed that while massive models like GPT-OSS-120B could effectively utilize the complex `RANK_4` context out of the box, highly optimized smaller models like Gemini 3.1 Flash Lite also showed high responsiveness to the structured prompt guidelines, mirroring the findings of arXiv:2510.06774 regarding the viability of smaller models in neuro-symbolic adaptive environments.

### Conclusion
The project successfully instantiated a dynamic, adaptive neuro-symbolic routing pipeline. By moving from theoretical language selection to constrained, solver-specific ranking prompts, we significantly improved the reliability of autoformalization workflows. The progression from basic decomposition to sophisticated ranking prompts highlights that successful LLM reasoning integration requires explicit boundary definition, failure-mode awareness, and output-oriented heuristics.
