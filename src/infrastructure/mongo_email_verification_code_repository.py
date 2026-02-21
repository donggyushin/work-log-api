from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src.domain.entities.email_verification_code import EmailVerificationCode
from src.domain.interfaces.email_verification_code_repository import (
    EmailVerificationCodeRepository,
)


class MongoEmailVerificationCodeRepository(EmailVerificationCodeRepository):
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str = "dailylog"):
        self.collection: AsyncIOMotorCollection = db_client[db_name][
            "email_verification_codes"
        ]

    async def find_by_user_id(self, user_id: str) -> Optional[EmailVerificationCode]:
        result = await self.collection.find_one({"user_id": user_id})
        if result is None:
            return None

        return EmailVerificationCode(**result)

    async def create(
        self, verification_code: EmailVerificationCode
    ) -> EmailVerificationCode:
        dict = verification_code.model_dump(exclude={"id"})
        result = await self.collection.insert_one(dict)
        return EmailVerificationCode(**dict, id=str(result.inserted_id))

    async def delete(self, verification_code: EmailVerificationCode):
        await self.collection.delete_one({"_id": ObjectId(verification_code.id)})
