from datetime import date
from src.domain.entities.chat import ChatMessage, ChatSession
from src.domain.entities.diary import Diary
from src.domain.entities.user import User
from src.domain.exceptions import NotFoundError
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

    async def get_chat_session(self, user: User) -> ChatSession:
        active_session = await self.chat_repository.find_active_session()

        if active_session:
            return active_session

        new_session = ChatSession(id="", user_id=user.id, messages=[])
        new_session = await self.chat_repository.create_session(new_session)
        return new_session

    async def end_chat_session(self, session: ChatSession):
        await self.chat_repository.end_session(session)

    async def send_chat_message(
        self, session: ChatSession, new_message: ChatMessage
    ) -> ChatMessage:
        session.messages.append(new_message)
        await self.chat_repository.add_message(session, new_message)
        reply = await self.ai_chat_bot.send(session)
        await self.chat_repository.add_message(session, reply)
        return reply

    async def write_diary(
        self, chat_session: ChatSession, target_message: ChatMessage
    ) -> Diary:
        diary = Diary(
            user_id=chat_session.user_id,
            chat_session_id=chat_session.id,
            title=None,
            content=target_message.content,
            thumbnail_url=None,
        )

        diary = await self.diary_repository.create(diary)
        return diary

    async def get_diary_by_date(self, writed_at: date) -> Diary:
        diary = await self.diary_repository.find_by_date(writed_at)
        if diary is None:
            raise NotFoundError()

        return diary
