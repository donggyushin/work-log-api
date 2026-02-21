from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src.domain.entities.chat import ChatMessage, ChatSession
from src.domain.interfaces.chat_repository import ChatRepository


class MongoChatRepository(ChatRepository):
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str = "dailylog"):
        self.collection: AsyncIOMotorCollection = db_client[db_name]["chats"]

    async def create_session(self, session: ChatSession) -> ChatSession:
        dict = session.model_dump(exclude={"id"})
        result = await self.collection.insert_one(dict)
        session.id = str(result.inserted_id)
        return session

    async def find_active_session(self) -> Optional[ChatSession]:
        result = await self.collection.find_one({"active": True})

        if result is None:
            return None

        # MongoDB _id를 id로 변환
        _id = result.pop("_id")
        result["id"] = str(_id)

        return ChatSession(**result)

    async def add_message(self, session: ChatSession, message: ChatMessage):
        # MongoDB의 $push 연산자를 사용해 messages 배열에 추가
        message_dict = message.model_dump()
        await self.collection.update_one(
            {"_id": ObjectId(session.id)}, {"$push": {"messages": message_dict}}
        )

    async def end_session(self, session: ChatSession):
        # active 상태를 False로 변경
        await self.collection.update_one(
            {"_id": ObjectId(session.id)}, {"$set": {"active": False}}
        )
