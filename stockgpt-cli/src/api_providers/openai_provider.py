from .base import AIProvider
from openai import OpenAI, RateLimitError

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def generate_insights(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except RateLimitError:
            raise RuntimeError("API rate limit exceeded. Please try again later.") 