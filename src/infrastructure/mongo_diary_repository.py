from datetime import date
from typing import List, Optional

from bson import ObjectId
from src.domain.entities.diary import Diary
from src.domain.exceptions import NotFoundError
from src.domain.interfaces.diary_repository import DiaryRepository
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


class MongoDiaryRepository(DiaryRepository):
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str = "dailylog"):
        self.collection: AsyncIOMotorCollection = db_client[db_name]["diaries"]

    async def create(self, diary: Diary) -> Diary:
        dict = diary.model_dump(mode="json", exclude={"id"})
        result = await self.collection.insert_one(dict)
        dict["id"] = str(result.inserted_id)
        return Diary(**dict)

    async def find_by_date(self, date: date, user_id: str) -> Optional[Diary]:
        result = await self.collection.find_one(
            {"writed_at": date.isoformat(), "user_id": user_id}
        )

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

    async def get_diary_list(
        self, user_id: str, cursor_id: Optional[str], size: int
    ) -> List[Diary]:
        # 해당 사용자의 일기만 조회
        query: dict = {"user_id": user_id}

        # cursor_id가 있으면 해당 일기의 날짜보다 오래된 일기들만 조회
        if cursor_id:
            cursor_diary = await self.collection.find_one({"_id": ObjectId(cursor_id)})
            if cursor_diary:
                query["date"] = {"$lt": cursor_diary["date"]}

        # 날짜 기준 내림차순 정렬 (최신 일기가 먼저)
        cursor = self.collection.find(query).sort("date", -1).limit(size)
        results = await cursor.to_list(length=size)

        # MongoDB 문서를 Diary 엔티티로 변환
        diaries = []
        for result in results:
            result["id"] = str(result.pop("_id"))
            diaries.append(Diary(**result))

        return diaries
