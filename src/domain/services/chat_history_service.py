from src.domain.entities.chat import ChatSession
from src.domain.exceptions import NotFoundError
from src.domain.interfaces.chat_repository import ChatRepository
from src.domain.interfaces.diary_repository import DiaryRepository


class ChatHistoryService:
    def __init__(
        self, chat_repository: ChatRepository, diary_repository: DiaryRepository
    ):
        self.chat_repository = chat_repository
        self.diary_repository = diary_repository

    async def find_session(self, diary_id: str) -> ChatSession:
        diary = await self.diary_repository.find_by_id(diary_id)

        if diary is None:
            raise NotFoundError()

        chat_session = await self.chat_repository.find_session(diary.chat_session_id)
        return chat_session
