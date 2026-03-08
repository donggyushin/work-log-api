from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.domain.entities.post import Post
from src.domain.entities.user import User
from src.domain.services.post_service import PostService
from src.presentation.dependencies import get_current_user, get_post_service


router = APIRouter(prefix="/api/v1", tags=["Posts"])

# ========================================
# Request/Response Models
# ========================================


class CreatePostRequest(BaseModel):
    title: Optional[str] = Field(default=None)
    content: str


class PostAndUserResponse(BaseModel):
    post: Post
    writer: User


# ========================================
# Endpoints
# ========================================


@router.get("/post")
async def get_post_list(
    post_service: Annotated[PostService, Depends(get_post_service)],
    cursor_id: Annotated[
        Optional[str], Query(description="Cursor ID for pagination")
    ] = None,
    size: Annotated[
        int, Query(ge=1, le=100, description="Number of posts to fetch")
    ] = 30,
) -> List[Post]:
    try:
        post_list = await post_service.get_post_list(cursor_id, size)
        return post_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emotion timeline: {str(e)}",
        )


@router.get("/post/{post_id}")
async def get_post(
    post_service: Annotated[PostService, Depends(get_post_service)], post_id: str
) -> PostAndUserResponse:
    try:
        dict = await post_service.get_post_and_user(post_id)
        response = PostAndUserResponse(**dict)
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emotion timeline: {str(e)}",
        )


@router.post("/post")
async def create_post(
    post_service: Annotated[PostService, Depends(get_post_service)],
    request: CreatePostRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Post:
    try:
        post = await post_service.create_post(
            request.title, request.content, current_user
        )
        return post
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emotion timeline: {str(e)}",
        )


@router.put("/post/{post_id}")
async def update_post(
    post_id: str,
    post_service: Annotated[PostService, Depends(get_post_service)],
    request: CreatePostRequest,
) -> Post:
    try:
        post = await post_service.update_post(post_id, request.title, request.content)
        return post
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emotion timeline: {str(e)}",
        )


@router.patch("/post/{post_id}/view")
async def view_post(
    post_id: str,
    post_service: Annotated[PostService, Depends(get_post_service)],
):
    await post_service.view_post(post_id)


@router.delete("/post/{post_id}")
async def delete_post(
    post_id: str,
    post_service: Annotated[PostService, Depends(get_post_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        await post_service.delete_post(current_user, post_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emotion timeline: {str(e)}",
        )
