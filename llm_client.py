import os
import time
import logging
from typing import Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
try:
    from cerebras.cloud.sdk import Cerebras
except ImportError:
    print("Warning: cerebras-cloud-sdk not installed.")
    Cerebras = None

logger = logging.getLogger(__name__)

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
        
    def _handle_rate_limit(self, headers):
        """Monitors Cerebras API token bucket rate limit headers and sleeps if necessary."""
        rem_req = headers.get("x-ratelimit-remaining-requests-day")
        rem_tok = headers.get("x-ratelimit-remaining-tokens-minute")
        res_req = headers.get("x-ratelimit-reset-requests-day")
        res_tok = headers.get("x-ratelimit-reset-tokens-minute")
        
        if rem_req and rem_tok:
            logger.debug(f"Rate Limit: {rem_req} requests/day, {rem_tok} tokens/min remaining")

        if rem_req and res_req and int(rem_req) < 10:
            wait_time = float(res_req)
            print(f"[RateLimit Warning] Approaching daily request limit ({rem_req} left). Sleeping for {wait_time}s")
            time.sleep(wait_time)
            
        if rem_tok and res_tok and int(rem_tok) < 10000:
            wait_time = float(res_tok)
            print(f"[RateLimit Warning] Approaching minute token limit ({rem_tok} left). Sleeping for {wait_time}s")
            time.sleep(wait_time)

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", 
                 temperature: float = 0.3, max_tokens: int = 2048) -> str:
        """
        Generates a text completion given a prompt and system instruction.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Use with_raw_response to access headers
        response = self.client.chat.completions.with_raw_response.create(
            messages=messages,
            model=self.default_model,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=1,
            stream=False
        )
        
        # Check and handle rate limits
        self._handle_rate_limit(response.headers)
        
        parsed_response = response.parse()
        return parsed_response.choices[0].message.content
