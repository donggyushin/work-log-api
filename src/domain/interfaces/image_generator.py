from abc import ABC, abstractmethod


class ImageGenerator(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass
