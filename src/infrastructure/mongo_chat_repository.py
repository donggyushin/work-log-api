from typing import Optional
from src.domain.entities.chat import ChatMessage, ChatSession
from src.domain.interfaces.chat_repository import ChatRepository


class MongoChatRepository(ChatRepository):
    async def create_session(self, session: ChatSession) -> ChatSession:
        return await super().create_session(session)

    async def find_active_session(self) -> Optional[ChatSession]:
        return await super().find_active_session()

    async def add_message(self, session: ChatSession, message: ChatMessage):
        return await super().add_message(session, message)

    async def end_session(self, session: ChatSession):
        return await super().end_session(session)
