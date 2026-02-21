from src.domain.entities.chat import ChatSession
from src.domain.interfaces.ai_chat_bot import AIChatBot
from src.domain.interfaces.chat_repository import ChatRepository
from src.domain.interfaces.diary_repository import DiaryRepository


class DiaryService:
    def __init__(
        self,
        diary_repository: DiaryRepository,
        chat_repository: ChatRepository,
        ai_chat_bot: AIChatBot,
    ):
        self.diary_repository = diary_repository
        self.chat_repository = chat_repository
        self.ai_chat_bot = ai_chat_bot

    async def start_chat(self) -> ChatSession:
        active_session = await self.chat_repository.find_active_session()

        if active_session:
            return active_session

        new_session = ChatSession(id="", messages=[])
        new_session = await self.chat_repository.create_session(new_session)
        return new_session
