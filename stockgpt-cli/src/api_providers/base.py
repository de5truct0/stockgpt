from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIProvider(ABC):
    """Base class for AI providers"""
    
    @abstractmethod
    def __init__(self, api_key: str):
        pass
    
    @abstractmethod
    def generate_insights(self, prompt: str) -> str:
        """Generate insights from the given prompt"""
        pass 