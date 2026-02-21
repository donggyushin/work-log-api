from datetime import datetime
from pydantic import BaseModel, Field


class EmailVerificationCode(BaseModel):
    id: str = Field()
    user_id: str = Field()
    email: str = Field()
    code: str = Field()
    expired_at: datetime
