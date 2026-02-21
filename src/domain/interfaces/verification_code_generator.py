from abc import ABC, abstractmethod


class VerificationCodeGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        pass
