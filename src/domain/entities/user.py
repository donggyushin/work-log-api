from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class User(BaseModel):
    id: Optional[str] = Field(default=None, description="User ID (MongoDB ObjectId)")
    username: Optional[str] = Field(
        ..., min_length=1, max_length=50, description="Username"
    )
    birth: Optional[date] = Field(..., description="Date of birth")
    gender: Optional[Gender] = Field(..., description="User gender")
