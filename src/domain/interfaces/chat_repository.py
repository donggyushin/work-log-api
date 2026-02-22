from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.chat import ChatMessage, ChatSession


class ChatRepository(ABC):
    @abstractmethod
    async def create_session(self, session: ChatSession) -> ChatSession:
        pass

    @abstractmethod
    async def find_active_session(self, user_id: str) -> Optional[ChatSession]:
        pass

    @abstractmethod
    async def add_message(
        self, session: ChatSession, message: ChatMessage
    ) -> ChatMessage:
        pass

    @abstractmethod
    async def end_session(self, session: ChatSession):
        pass

    @abstractmethod
    async def find_session(self, session_id: str) -> ChatSession:
        pass

    @abstractmethod
    async def find_message(self, session_id: str, message_id: str) -> ChatMessage:
        pass
