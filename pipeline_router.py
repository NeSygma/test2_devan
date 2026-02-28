from solver_pipeline.llm_client import LLMClient
from solver_pipeline.prompts import SOLVER_SELECTION_PROMPT, TRANSLATION_PROMPTS
from solver_pipeline.solvers.prover9_solver import run_prover9_solver
from solver_pipeline.solvers.z3_solver import run_z3_solver
from solver_pipeline.solvers.prolog_solver import run_prolog_solver
from solver_pipeline.solvers.constraint_solver import run_constraint_solver

class LogicPipelineRouter:
    def __init__(self, api_key=None, model="llama-3.3-70b"):
        self.llm = LLMClient(api_key=api_key, model=model)
        
    def _select_solver(self, premises: str, conclusion: str) -> str:
        """
        Uses the LLM to classify the problem and pick the best solver.
        """
        prompt = SOLVER_SELECTION_PROMPT.format(premises=premises, conclusion=conclusion)
        response = self.llm.generate(prompt=prompt, temperature=0.0, max_tokens=10).strip()
        
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
        return self.llm.generate(
            prompt=prompt, 
            system_prompt=f"You are an expert coder specializing in {solver}. Only return code, no markdown or explanations.",
            temperature=0.1, 
            max_tokens=2048
        )
        
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
