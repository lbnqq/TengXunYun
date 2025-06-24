from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generates a response from the LLM based on the given prompt.
        """
        pass 