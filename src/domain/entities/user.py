from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class User(BaseModel):
    id: str = Field(description="User ID (MongoDB ObjectId)")
    email: str = Field(..., description="User's Email")
    password: str = Field(..., description="User's Password")
    username: Optional[str] = Field(
        default=None, min_length=1, max_length=50, description="Username"
    )
    birth: Optional[date] = Field(default=None, description="Date of birth")
    gender: Optional[Gender] = Field(default=None, description="User gender")
