from abc import ABC
from abc import abstractmethod


class ResourceEventFactory(ABC):
    @abstractmethod
    def generate(self):
        pass
