from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from src.domain.entities.post import Post
from src.domain.exceptions import NotFoundError
from src.domain.interfaces.post_repository import PostRepository


class MongoPostRepository(PostRepository):
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str = "dailylog"):
        self.collection: AsyncIOMotorCollection = db_client[db_name]["posts"]

    async def delete(self, post_id: str):
        await self.collection.delete_one({"_id": ObjectId(post_id)})

    async def create(self, post: Post) -> Post:
        """Create a new post"""
        post_dict = post.model_dump(mode="json", exclude={"id"})
        result = await self.collection.insert_one(post_dict)
        post_dict["id"] = str(result.inserted_id)
        return Post(**post_dict)

    async def get(self, post_id: str) -> Post:
        """Get post by ID"""
        result = await self.collection.find_one({"_id": ObjectId(post_id)})

        if result is None:
            raise NotFoundError()

        result["id"] = str(result.pop("_id"))
        return Post(**result)

    async def get_list(self, cursor_id: Optional[str], size: int) -> List[Post]:
        """Get all posts with cursor-based pagination (latest first)"""
        query: dict = {}

        # cursor_id가 있으면 해당 포스트보다 오래된 포스트들만 조회
        if cursor_id:
            cursor_post = await self.collection.find_one({"_id": ObjectId(cursor_id)})
            if cursor_post:
                query["created_at"] = {"$lt": cursor_post["created_at"]}

        # 생성일 기준 내림차순 정렬 (최신 포스트가 먼저)
        cursor = self.collection.find(query).sort("created_at", -1).limit(size)
        results = await cursor.to_list(length=size)

        # MongoDB 문서를 Post 엔티티로 변환
        posts = []
        for result in results:
            result["id"] = str(result.pop("_id"))
            posts.append(Post(**result))

        return posts

    async def update(self, post: Post) -> Post:
        """Update existing post"""
        post_dict = post.model_dump(mode="json", exclude={"id"})

        await self.collection.update_one(
            {"_id": ObjectId(post.id)}, {"$set": post_dict}
        )

        return post
