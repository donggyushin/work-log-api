from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from src.domain.entities.user import User


class MongoUserRepository:
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str = "dailylog"):
        self.collection: AsyncIOMotorCollection = db_client[db_name]["users"]

    async def create(self, user: User) -> User:
        user_dict = user.model_dump(exclude={"id"})
        result = await self.collection.insert_one(user_dict)
        return User(**user_dict, id=str(result.inserted_id))
