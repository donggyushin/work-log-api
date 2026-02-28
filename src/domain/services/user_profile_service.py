from typing import Optional
from uuid import uuid4
from src.domain.entities.user import User
from src.domain.interfaces.image_storage import ImageStorage
from src.domain.interfaces.user_repository import UserRepository


class UserProfileService:
    def __init__(self, user_repository: UserRepository, image_storage: ImageStorage):
        self.user_repository = user_repository
        self.image_storage = image_storage

    async def update_user_profile(self, current_user: User, updated_user: User) -> User:
        current_user.update_basic_profile(updated_user)
        await self.user_repository.update(current_user)
        return current_user

    async def update_profile_img(
        self, current_user: User, image_data: Optional[bytes]
    ) -> User:
        if current_user.profile_image_url:
            await self.image_storage.delete(current_user.profile_image_url)
            current_user.profile_image_url = None

        if image_data:
            img_url = await self.image_storage.upload(image_data, str(uuid4()))
            current_user.profile_image_url = img_url

        await self.user_repository.update(current_user)

        return current_user
