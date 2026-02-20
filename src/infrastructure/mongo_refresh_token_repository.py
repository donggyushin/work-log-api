from src.domain.interfaces.refresh_token_repository import RefreshTokenRepository
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from typing import List


class MongoRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str = "dailylog"):
        self.collection: AsyncIOMotorCollection = db_client[db_name]["refresh_tokens"]

    async def create(self, token: str, user_id: str):
        await self.collection.insert_one({"user_id": user_id, "refresh_token": token})

    async def delete(self, token: str):
        await self.collection.delete_one({"refresh_token": token})

    async def find_tokens_by_user_id(self, user_id: str) -> List[str]:
        cursor = self.collection.find({"user_id": user_id})
        documents = await cursor.to_list(length=None)
        return [doc["refresh_token"] for doc in documents]

    async def exists(self, token: str) -> bool:
        result = await self.collection.find_one({"refresh_token": token})
        return result is not None
