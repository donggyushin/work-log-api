from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


class MongoUserRepository:
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str = "dailylog"):
        self.collection: AsyncIOMotorCollection = db_client[db_name]["refresh_tokens"]
