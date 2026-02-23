from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from typing import Any, Dict, List, Optional
from src.domain.entities.payments_log import PaymentsLog
from src.domain.exceptions import NotFoundError
from src.domain.interfaces.payments_repository import PaymentsRepository


class MongoPaymentsRepository(PaymentsRepository):
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str = "dailylog"):
        self.collection: AsyncIOMotorCollection = db_client[db_name]["payments_logs"]

    async def create(self, payments: PaymentsLog):
        id = payments.id
        dict = payments.model_dump(exclude={"id"})
        dict["_id"] = ObjectId(id)

        await self.collection.insert_one(dict)

    async def find_by_id(self, payments_id: str) -> PaymentsLog:
        result = await self.collection.find_one({"_id": ObjectId(payments_id)})

        if result is None:
            raise NotFoundError()

        result["id"] = str(result.pop("_id"))

        log = PaymentsLog(**result)
        return log

    async def find_by_user_id(
        self, user_id: str, cursor_id: Optional[str], size: int
    ) -> List[PaymentsLog]:
        # 기본 필터: user_id로 검색
        filter_query: Dict[str, Any] = {"user_id": user_id}

        # 커서 기반 페이지네이션: cursor_id 이후의 결과만 가져오기
        if cursor_id:
            filter_query["_id"] = {"$lt": ObjectId(cursor_id)}

        # _id 기준 내림차순 정렬 (최신순)
        cursor = self.collection.find(filter_query).sort("_id", -1).limit(size)

        results = await cursor.to_list(length=size)

        # _id를 id로 변환
        payments_logs = []
        for result in results:
            result["id"] = str(result.pop("_id"))
            payments_logs.append(PaymentsLog(**result))

        return payments_logs
