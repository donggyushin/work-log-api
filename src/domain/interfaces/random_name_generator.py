from abc import ABC, abstractmethod


class RandomNameGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        pass
