from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Post(BaseModel):
    """Community post entity for public board"""

    id: str
    user_id: str = Field(description="Author user ID")
    title: Optional[str] = Field(default=None, description="Post title")
    content: str = Field(description="Post content")
    view_count: int = Field(default=0, description="View count")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
