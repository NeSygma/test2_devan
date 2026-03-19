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
    from openai import OpenAI, RateLimitError
except ImportError:
    print("Warning: openai not installed. Please pip install openai")
    OpenAI = None
    RateLimitError = Exception

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-oss-120b"):
        """
        A wrapper for the Nvidia NIM LLM API using OpenAI SDK.
        Default model: openai/gpt-oss-120b
        """
        # Prioritize passed-in key, then env NVIDiA_API_KEY, then the provided testing key
        key = api_key or os.environ.get("NVIDIA_API_KEY") or "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"
        
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=key
        )
        self.default_model = model
        self._total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
    def _handle_rate_limit(self, headers):
        """Monitors API rate limit headers and sleeps if necessary."""
        # Standard OpenAI rate limit headers from Nvidia NIM
        rem_req = headers.get("x-ratelimit-remaining-requests")
        rem_tok = headers.get("x-ratelimit-remaining-tokens")
        
        if rem_req and rem_tok:
            logger.debug(f"Rate Limit: {rem_req} requests, {rem_tok} tokens remaining")

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.",
                 max_retries: int = 5, temperature: Optional[float] = None,
                 max_completion_tokens: Optional[int] = None,
                 top_p: Optional[float] = None,
                 **kwargs) -> tuple:
        """
        Generates a text completion given a prompt and system instruction.
        Retries automatically on RateLimitErrors.
        
        Args:
            temperature: Sampling temperature.
            max_completion_tokens: Maximum tokens in the completion.
            top_p: Top P sampling.
            **kwargs: Extra arguments passed to OpenAI completions.create (e.g. interchangeable)
        
        Returns:
            tuple: (content_str, usage_dict, reasoning_str)
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Build API create parameters
        create_kwargs = dict(messages=messages, model=self.default_model, stream=False)
        
        if temperature is not None:
            create_kwargs["temperature"] = temperature
        if top_p is not None:
            create_kwargs["top_p"] = top_p
        if max_completion_tokens is not None:
            # Note: For OpenAI client, max_tokens is typically used
            create_kwargs["max_tokens"] = max_completion_tokens
            
        # Optional backward compatibility kwargs
        kwargs.pop("reasoning_format", None) # Remove it if passed by old scripts, handled natively
        create_kwargs.update(kwargs)
        
        for attempt in range(max_retries):
            try:
                # Use raw response object to inspect headers and parsed choice correctly
                response = self.client.chat.completions.with_raw_response.create(**create_kwargs)
                
                if response.headers:
                    self._handle_rate_limit(response.headers)
                
                parsed_response = response.parse()
                message = parsed_response.choices[0].message
                content = message.content or ""
                
                # Support DeepSeek-R1 structured reasoning via reasoning_content property 
                reasoning = getattr(message, "reasoning_content", "")
                if not reasoning and hasattr(message, "reasoning"):
                    reasoning = getattr(message, "reasoning", "")
                
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
                
                return content, usage, reasoning
                
            except RateLimitError as e:
                wait_time = min((2 ** attempt) * 2, 60)
                print(f"[API Queue Error] High traffic (429). Retrying in {wait_time}s (Attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            except Exception as e:
                # To prevent blocking completely on other weird network errors, we also retry here 
                # but log the exception type
                wait_time = min((2 ** attempt) * 2, 60)
                print(f"[API Error] Unexpected exact error {e}. Retrying in {wait_time}s (Attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
                
        # If it failed all retries
        print("[API Action] Max retries reached. Failing.")
        raise RuntimeError(f"Failed after {max_retries} retries.")

    def get_total_usage(self) -> dict:
        return dict(self._total_usage)

    def reset_usage(self):
        self._total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
