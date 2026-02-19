from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from src.domain.entities.user import User
from src.domain.interfaces.user_repository import UserRepository


class MongoUserRepository(UserRepository):
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str = "dailylog"):
        self.collection: AsyncIOMotorCollection = db_client[db_name]["users"]

    async def create(self, user: User) -> User:
        user_dict = user.model_dump(exclude={"id"})
        result = await self.collection.insert_one(user_dict)
        return User(**user_dict, id=str(result.inserted_id))

    async def find_by_email(self, email: str) -> Optional[User]:
        result = await self.collection.find_one({"email": email})
        if result is None:
            return None

        result["id"] = str(result.pop("_id"))
        return User(**result)
