from datetime import date
from typing import Optional

from bson import ObjectId
from src.domain.entities.diary import Diary
from src.domain.exceptions import NotFoundError
from src.domain.interfaces.diary_repository import DiaryRepository
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


class MongoDiaryRepository(DiaryRepository):
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str = "dailylog"):
        self.collection: AsyncIOMotorCollection = db_client[db_name]["diaries"]

    async def create(self, diary: Diary) -> Diary:
        dict = diary.model_dump(exclude={"id"})
        result = await self.collection.insert_one(dict)
        dict["id"] = str(result.inserted_id)
        return Diary(**dict)

    async def find_by_date(self, date: date) -> Optional[Diary]:
        result = await self.collection.find_one({"date": date})

        if result is None:
            raise NotFoundError()

        result["id"] = str(result.pop("_id"))
        return Diary(**result)

    async def find_by_id(self, id: str) -> Optional[Diary]:
        result = await self.collection.find_one({"_id": ObjectId(id)})

        if result is None:
            raise NotFoundError()

        result["id"] = str(result.pop("_id"))
        return Diary(**result)
