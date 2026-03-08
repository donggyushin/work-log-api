from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.post import Post


class PostRepository(ABC):
    @abstractmethod
    async def create(self, post: Post) -> Post:
        pass

    @abstractmethod
    async def get(self, post_id: str) -> Post:
        pass

    @abstractmethod
    async def get_list(self, cursor_id: Optional[str], size: int) -> List[Post]:
        pass

    @abstractmethod
    async def update(self, post: Post) -> Post:
        pass
