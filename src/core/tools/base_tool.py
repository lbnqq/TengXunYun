from abc import ABC, abstractmethod

class BaseTool(ABC):
    """
    Base class for all tools.
    Defines the common interface for executing tool actions.
    """
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def __str__(self):
        return self.__class__.__name__ 