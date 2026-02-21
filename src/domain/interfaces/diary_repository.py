from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from src.domain.entities.diary import Diary


class DiaryRepository(ABC):
    @abstractmethod
    async def create(self, diary: Diary) -> Diary:
        pass

    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[Diary]:
        pass

    @abstractmethod
    async def find_by_date(self, date: date) -> Optional[Diary]:
        pass
