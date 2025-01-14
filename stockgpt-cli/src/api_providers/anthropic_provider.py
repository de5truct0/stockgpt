from .base import AIProvider
from anthropic import Anthropic, RateLimitError

class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def generate_insights(self, prompt: str) -> str:
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except RateLimitError:
            raise RuntimeError("API rate limit exceeded. Please try again later.") 