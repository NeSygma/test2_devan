from solver_select_pipeline.llm_client import LLMClient
from solver_select_pipeline.prompts import SOLVER_SELECTION_PROMPT, TRANSLATION_PROMPTS, PAPER_DECOMPOSITION_PROMPT
from solver_select_pipeline.solvers.prover9_solver import run_prover9_solver
from solver_select_pipeline.solvers.z3_solver import run_z3_solver
from solver_select_pipeline.solvers.prolog_solver import run_prolog_solver
from solver_select_pipeline.solvers.constraint_solver import run_constraint_solver
import json

class LogicPipelineRouter:
    def __init__(self, api_key=None, model="gpt-oss-120b"): # Using model as requested
        self.llm = LLMClient(api_key=api_key, model=model)
        
    def classify_solver_type(self, text: str) -> str:
        """
        Decomposes the natural language problem and identifies the solver type
        using configurations from arXiv:2510.06774v1 (Temp=0.01, MaxTokens=4096)
        """
        prompt = PAPER_DECOMPOSITION_PROMPT.format(problem=text)
        
        # We don't provide a system prompt since the PAPER_DECOMPOSITION_PROMPT already includes the SYSTEM tags natively
        response = self.llm.generate(
            prompt=prompt, 
            system_prompt="", # Instructed by the paper's prompt structure
            temperature=0.01, 
            max_tokens=4096
        )
        
        # Parse JSON
        try:
            # Handle potential markdown formatting from LLM
            if "```json" in response:
                clean_json = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                clean_json = response.split("```")[1].split("```")[0]
            else:
                clean_json = response
                
            data = json.loads(clean_json.strip())
            
            if "result" in data and len(data["result"]) > 0:
                return data["result"][0].get("problem_type", "UNKNOWN")
        except json.JSONDecodeError as e:
            print(f"Error parsing classification output: {e}\nRaw response:\n{response}")
            
        return "ERROR"

    def classify_solver_oneshot(self, text: str) -> str:
        """
        Classifies the problem using a simple one-shot prompt (baseline).
        """
        sys_prompt = (
            "You are an expert logician. Your task is to classify the provided logical reasoning problem into one of four solver types:\n"
            "- LP (Logic Programming)\n"
            "- FOL (First-order Logic)\n"
            "- CSP (Constraint Satisfaction Problem)\n"
            "- SAT (Boolean Satisfiability)\n\n"
            "Respond ONLY with the exact name of the category (LP, FOL, CSP, or SAT).\n\n"
            "Example 1:\n"
            "Problem Statement:\n"
            "Three people sit in a row. Alice does not sit next to Bob. Charlie sits on the left. Who sits in the middle?\n"
            "Category: CSP\n"
        )
        
        user_prompt = f"Problem Statement:\n{text}\nCategory:\n"
        
        response = self.llm.generate(
            prompt=user_prompt, 
            system_prompt=sys_prompt, 
            temperature=0.01, 
            max_tokens=1024
        )
        
        if not response:
            return "UNKNOWN"
            
        response_clean = response.strip().upper()
        for s in ["LP", "FOL", "CSP", "SAT"]:
            if s in response_clean:
                return s
        return "UNKNOWN"

    def _select_solver(self, premises: str, conclusion: str) -> str:
        """
        Uses the LLM to classify the problem and pick the best solver.
        """
        prompt = SOLVER_SELECTION_PROMPT.format(premises=premises, conclusion=conclusion)
        response = self.llm.generate(prompt=prompt, temperature=0.0, max_tokens=50)
        response = response.strip() if response else ""
        
        # Clean response to ensure it matches exactly one of our 4 expected outputs
        for s in ["PROVER9", "Z3", "PROLOG", "CONSTRAINT"]:
            if s in response.upper():
                return s
        # Fallback
        return "PROLOG" 
    def _translate(self, premises: str, conclusion: str, solver: str) -> str:
        """
        Uses the LLM to translate natural language into the specific DSL/Code.
        """
        prompt = TRANSLATION_PROMPTS[solver].format(premises=premises, conclusion=conclusion)
        response = self.llm.generate(
            prompt=prompt, 
            system_prompt=f"You are an expert coder specializing in {solver}. Only return code, no markdown or explanations.",
            temperature=0.1, 
            max_tokens=2048
        )
        return response if response else ""
        
    def execute_problem(self, premises: str, conclusion: str, forced_solver: str = None) -> dict:
        """
        The core pipeline: Selection -> Translation -> Execution.
        """
        # 1. Selection
        solver = forced_solver if forced_solver else self._select_solver(premises, conclusion)
        
        # 2. Translation
        generated_code = self._translate(premises, conclusion, solver)
        
        # 3. Execution
        status = "Unknown"
        output = ""
        if solver == "PROVER9":
            status, output = run_prover9_solver(generated_code)
        elif solver == "Z3":
            status, output = run_z3_solver(generated_code)
        elif solver == "PROLOG":
            status, output = run_prolog_solver(generated_code)
        elif solver == "CONSTRAINT":
            status, output = run_constraint_solver(generated_code)
        else:
            status = "Error"
            output = f"Unknown solver: {solver}"
            
        return {
            "solver": solver,
            "code": generated_code,
            "status": status,
            "output": output
        }
