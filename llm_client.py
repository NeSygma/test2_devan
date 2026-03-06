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
        self._total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
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
                 max_retries: int = 5, temperature: Optional[float] = None) -> tuple:
        """
        Generates a text completion given a prompt and system instruction.
        Retries automatically on 429 RateLimitErrors.
        
        Args:
            temperature: Sampling temperature. None uses the API default.
        
        Returns:
            tuple: (content_str, usage_dict) where usage_dict has
                   prompt_tokens, completion_tokens, total_tokens.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        from cerebras.cloud.sdk import RateLimitError
        
        # Build API kwargs
        create_kwargs = dict(messages=messages, model=self.default_model, stream=False)
        if temperature is not None:
            create_kwargs["temperature"] = temperature
        
        for attempt in range(max_retries):
            try:
                # Use with_raw_response to access headers
                response = self.client.chat.completions.with_raw_response.create(**create_kwargs)
                
                # Check and handle rate limits
                self._handle_rate_limit(response.headers)
                
                parsed_response = response.parse()
                content = parsed_response.choices[0].message.content
                
                # Extract token usage
                usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                if hasattr(parsed_response, 'usage') and parsed_response.usage:
                    usage["prompt_tokens"] = getattr(parsed_response.usage, 'prompt_tokens', 0) or 0
                    usage["completion_tokens"] = getattr(parsed_response.usage, 'completion_tokens', 0) or 0
                    usage["total_tokens"] = getattr(parsed_response.usage, 'total_tokens', 0) or 0
                
                # Accumulate totals
                self._total_usage["prompt_tokens"] += usage["prompt_tokens"]
                self._total_usage["completion_tokens"] += usage["completion_tokens"]
                self._total_usage["total_tokens"] += usage["total_tokens"]
                
                return content, usage
                
            except RateLimitError as e:
                wait_time = (2 ** attempt) * 2  # Exponential backoff: 2, 4, 8, 16...
                print(f"[API Queue Error] High traffic (429). Retrying in {wait_time}s (Attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
                
        # If it failed all retries, raise the last exception
        print("[API Queue Error] Max retries reached. Failing.")
        raise RuntimeError(f"Failed after {max_retries} retries due to rate limiting.")

    def get_total_usage(self) -> dict:
        """Returns accumulated token usage across all generate() calls."""
        return dict(self._total_usage)

    def reset_usage(self):
        """Resets the accumulated token usage counters."""
        self._total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
