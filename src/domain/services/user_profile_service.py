from src.domain.entities.user import User
from src.domain.interfaces.user_repository import UserRepository


class UserProfileService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def update_user_profile(self, current_user: User, updated_user: User) -> User:
        current_user.update_basic_profile(updated_user)
        await self.user_repository.update(current_user)
        return current_user
