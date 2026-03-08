from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from src.domain.entities.user import Gender, User
from src.domain.services.user_profile_service import UserProfileService
from src.presentation.dependencies import get_current_user, get_user_profile_service

router = APIRouter(prefix="/api/v1", tags=["User Profile"])


# ========================================
# Request/Response Models
# ========================================


class UpdateUserRequest(BaseModel):
    username: str
    birth: Optional[date]
    gender: Optional[Gender]


# ========================================
# Endpoints
# ========================================


@router.get("/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.put("/me")
async def update_me(
    current_user: Annotated[User, Depends(get_current_user)],
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    request: UpdateUserRequest,
) -> User:
    try:
        updated_user = current_user
        updated_user.username = request.username
        updated_user.birth = request.birth
        updated_user.gender = request.gender

        response = await user_profile_service.update_user_profile(
            current_user, updated_user
        )
        return response
    except Exception as e:
        raise e


@router.put("/me/profile-image")
async def update_profile_image(
    current_user: Annotated[User, Depends(get_current_user)],
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
    file: UploadFile = File(...),
) -> User:
    """
    Update user profile image.

    Uploads new profile image to R2 storage and deletes old image if exists.
    """
    try:
        # Read image data from uploaded file
        image_data = await file.read()

        # Update profile image using service
        updated_user = await user_profile_service.update_profile_img(
            current_user, image_data
        )
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile image: {str(e)}",
        )


@router.delete("/me/profile-image")
async def delete_profile_image(
    current_user: Annotated[User, Depends(get_current_user)],
    user_profile_service: Annotated[
        UserProfileService, Depends(get_user_profile_service)
    ],
) -> User:
    """
    Delete user profile image.

    Removes profile image from R2 storage and sets profile_image_url to None.
    """
    try:
        # Pass None to delete image without uploading new one
        updated_user = await user_profile_service.update_profile_img(current_user, None)
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile image: {str(e)}",
        )
