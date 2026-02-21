from abc import ABC, abstractmethod

from src.domain.entities.chat import ChatMessage, ChatSession


class AIChatBot(ABC):
    @abstractmethod
    async def send(self, chat: ChatSession) -> ChatMessage:
        pass
