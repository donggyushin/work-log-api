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
    async def add_message(self, session: ChatSession, message: ChatMessage):
        pass

    @abstractmethod
    async def end_session(self, session: ChatSession):
        pass
