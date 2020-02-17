from abc import ABC, abstractmethod

class ResourceEventFactory(ABC):
    @abstractmethod
    def generate(self):
        pass