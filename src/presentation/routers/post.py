from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.domain.entities.post import Post
from src.domain.services.post_service import PostService
from src.presentation.dependencies import get_post_service


router = APIRouter(prefix="/api/v1", tags=["Posts"])

# ========================================
# Request/Response Models
# ========================================


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
) -> Post:
    try:
        post = await post_service.get_post(post_id)
        return post
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emotion timeline: {str(e)}",
        )
