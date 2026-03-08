from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from src.domain.entities.post import Post
from src.domain.entities.user import User
from src.domain.interfaces.post_repository import PostRepository


class PostService:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository

    async def create_post(
        self, title: Optional[str], content: str, current_user: User
    ) -> Post:
        post = Post(
            id=str(ObjectId()), user_id=current_user.id, title=title, content=content
        )
        post = await self.post_repository.create(post)
        return post

    async def get_post_list(self, cursor_id: Optional[str], size: int) -> List[Post]:
        post_list = await self.post_repository.get_list(cursor_id, size)
        return post_list

    async def get_post(self, post_id: str) -> Post:
        post = await self.post_repository.get(post_id)
        return post

    async def view_post(self, post_id: str):
        post = await self.post_repository.get(post_id)
        post.view_count += 1
        post.updated_at = datetime.now()
        await self.post_repository.update(post)

    async def update_post(
        self, post_id: str, title: Optional[str], content: str
    ) -> Post:
        post = await self.post_repository.get(post_id)
        post.title = title
        post.content = content
        post.updated_at = datetime.now()
        await self.post_repository.update(post)
        return post
