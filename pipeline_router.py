from solver_select_pipeline.llm_client import LLMClient
from solver_select_pipeline.prompts import PAPER_DECOMPOSITION_PROMPT
import json

class LogicPipelineRouter:
    def __init__(self, api_key=None, model="openai/gpt-oss-120b", temperature=None):
        self.llm = LLMClient(api_key=api_key, model=model)
        self.temperature = temperature

    def get_token_usage(self) -> dict:
        """Returns accumulated token usage from the LLM client."""
        return self.llm.get_total_usage()

    def reset_token_usage(self):
        """Resets the LLM client's token usage counters."""
        self.llm.reset_usage()
        
    def classify_solver_type(self, text: str) -> str:
        """
        Decomposes the natural language problem and identifies the solver type
        using the paper's prompt structure from arXiv:2510.06774v1
        """
        prompt = PAPER_DECOMPOSITION_PROMPT.format(problem=text)
        
        # We don't provide a system prompt since the PAPER_DECOMPOSITION_PROMPT already includes the SYSTEM tags natively
        response, _usage, _reasoning = self.llm.generate(
            prompt=prompt,
            system_prompt="",  # Instructed by the paper's prompt structure
            temperature=self.temperature
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
        
        response, _usage, _reasoning = self.llm.generate(
            prompt=user_prompt,
            system_prompt=sys_prompt,
            temperature=self.temperature
        )
        
        if not response:
            return "UNKNOWN"
            
        response_clean = response.strip().upper()
        for s in ["LP", "FOL", "CSP", "SAT"]:
            if s in response_clean:
                return s
        return "UNKNOWN"
