import os
from typing import Optional
try:
    from cerebras.cloud.sdk import Cerebras
except ImportError:
    print("Warning: cerebras-cloud-sdk not installed.")
    Cerebras = None

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-oss-120b"):
        """
        A standard wrapper for the Cerebras cloud LLM API.
        Default model: llama3.1-70b
        """
        key = api_key or os.environ.get("CEREBRAS_API_KEY")
        if not key:
            raise ValueError("CEREBRAS_API_KEY is not set.")
            
        self.client = Cerebras(api_key=key)
        self.default_model = model
        
    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", 
                 temperature: float = 0.2, max_tokens: int = 1024) -> str:
        """
        Generates a text completion given a prompt and system instruction.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.default_model,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=1,
            stream=False
        )
        
        return response.choices[0].message.content
