from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.payments_log import PaymentsLog


class PaymentsRepository(ABC):
    @abstractmethod
    async def create(self, payments: PaymentsLog):
        pass

    @abstractmethod
    async def find_by_id(self, payments_id: str) -> PaymentsLog:
        pass

    @abstractmethod
    async def find_by_user_id(
        self, user_id: str, cursor_id: Optional[str], size: int
    ) -> List[PaymentsLog]:
        pass
