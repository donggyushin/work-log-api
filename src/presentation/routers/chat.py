from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from src.domain.entities.chat import ChatMessage, ChatSession
from src.domain.entities.user import User
from src.domain.services.diary_service import DiaryService
from src.presentation.dependencies import get_current_user, get_diary_service

router = APIRouter(prefix="/api/v1", tags=["Chat Sessions"])


# ========================================
# Request/Response Models
# ========================================


class ChatSendMessageRequest(BaseModel):
    session_id: str
    message: ChatMessage


# ========================================
# Endpoints
# ========================================


@router.get(
    "/chat-current-session",
    response_model=ChatSession,
    status_code=status.HTTP_200_OK,
)
async def get_current_chat_session(
    diary_service: Annotated[DiaryService, Depends(get_diary_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    current_session = await diary_service.get_chat_session(current_user)
    return current_session


@router.delete("/chat-current-session")
async def end_current_chat_session(
    diary_service: Annotated[DiaryService, Depends(get_diary_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await diary_service.end_current_session(current_user)


@router.post(
    "/chat/message",
    status_code=status.HTTP_200_OK,
    response_model=ChatMessage,
)
async def send_message(
    request: ChatSendMessageRequest,
    diary_service: Annotated[DiaryService, Depends(get_diary_service)],
):
    reply = await diary_service.send_chat_message(request.message, request.session_id)
    return reply
