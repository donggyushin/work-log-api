from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src.domain.entities.chat import ChatMessage, ChatSession
from src.domain.exceptions import NotFoundError
from src.domain.interfaces.chat_repository import ChatRepository


class MongoChatRepository(ChatRepository):
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str = "dailylog"):
        self.collection: AsyncIOMotorCollection = db_client[db_name]["chats"]

    async def create_session(self, session: ChatSession) -> ChatSession:
        dict = session.model_dump(mode="json", exclude={"id"})
        result = await self.collection.insert_one(dict)
        session.id = str(result.inserted_id)
        return session

    async def find_active_session(self, user_id: str) -> Optional[ChatSession]:
        result = await self.collection.find_one({"active": True, "user_id": user_id})

        if result is None:
            return None

        # MongoDB _id를 id로 변환
        _id = result.pop("_id")
        result["id"] = str(_id)

        # messages 배열의 각 메시지도 _id를 id로 변환
        if "messages" in result:
            for message in result["messages"]:
                message_id = message.pop("_id")
                message["id"] = str(message_id)

        return ChatSession(**result)

    async def add_message(self, session: ChatSession, message: ChatMessage):
        # MongoDB의 $push 연산자를 사용해 messages 배열에 추가
        # message.id는 제외하고 새로운 MongoDB _id 생성
        message_dict = message.model_dump(mode="json", exclude={"id"})
        message_dict["_id"] = ObjectId()

        await self.collection.update_one(
            {"_id": ObjectId(session.id)}, {"$push": {"messages": message_dict}}
        )

    async def end_session(self, session: ChatSession):
        # active 상태를 False로 변경
        await self.collection.update_one(
            {"_id": ObjectId(session.id)}, {"$set": {"active": False}}
        )

    async def find_session(self, session_id: str) -> ChatSession:
        result = await self.collection.find_one({"_id": ObjectId(session_id)})

        if result is None:
            raise NotFoundError()

        result["id"] = str(result.pop("_id"))

        # messages 배열의 각 메시지도 _id를 id로 변환
        if "messages" in result:
            for message in result["messages"]:
                message_id = message.pop("_id")
                message["id"] = str(message_id)

        return ChatSession(**result)

    async def find_message(self, session_id: str, message_id: str) -> ChatMessage:
        found_session = await self.find_session(session_id)

        found_message = next(
            (msg for msg in found_session.messages if msg.id == message_id), None
        )

        if found_message:
            return found_message
        else:
            raise NotFoundError()
