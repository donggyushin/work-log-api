from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.domain.entities.chat import ChatMessage, ChatSession
from src.domain.entities.diary import Diary
from src.domain.entities.user import User
from src.domain.exceptions import (
    EmailAlreadyExistsError,
    ExpiredError,
    NotCorrectError,
    NotFoundError,
    PasswordLengthNotEnoughError,
    PasswordNotCorrectError,
    UserNotFoundError,
)
from src.domain.services.auth_service import AuthService
from src.domain.services.diary_service import DiaryService
from src.domain.services.email_verification_service import EmailVerificationService
from src.infrastructure.database import connect_to_mongo, close_mongo_connection
from src.presentation.dependencies import (
    get_auth_service,
    get_current_user,
    get_diary_service,
    get_email_verification_service,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(lifespan=lifespan)

# CORS 설정: 개발 환경에서 모든 origin 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용하도록 변경 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1")
async def hello():
    return {"message": "hello world"}


@app.get("/api/v1/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@app.get(
    "/api/v1/chat-current-session",
    response_model=ChatSession,
    status_code=status.HTTP_200_OK,
)
async def get_current_chat_session(
    diary_service: Annotated[DiaryService, Depends(get_diary_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    current_session = await diary_service.get_chat_session(current_user)
    return current_session


@app.delete("/api/v1/chat-current-session")
async def end_current_chat_session(
    diary_service: Annotated[DiaryService, Depends(get_diary_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await diary_service.end_current_session(current_user)


class ChatSendMessageRequest(BaseModel):
    session_id: str
    message: ChatMessage


@app.post(
    "/api/v1/chat/message", status_code=status.HTTP_200_OK, response_model=ChatMessage
)
async def send_message(
    request: ChatSendMessageRequest,
    diary_service: Annotated[DiaryService, Depends(get_diary_service)],
):
    reply = await diary_service.send_chat_message(request.message, request.session_id)
    return reply


@app.get("/api/v1/diaries", response_model=List[Diary], status_code=status.HTTP_200_OK)
async def get_diary_list(
    current_user: Annotated[User, Depends(get_current_user)],
    diary_service: Annotated[DiaryService, Depends(get_diary_service)],
    cursor_id: Annotated[
        Optional[str], Query(description="Cursor ID for pagination")
    ] = None,
    size: Annotated[
        int, Query(ge=1, le=100, description="Number of diaries to fetch")
    ] = 30,
):
    diaries = await diary_service.get_diary_list(current_user, cursor_id, size)
    return diaries


@app.delete("/api/v1/diary/{diary_id}")
async def delete_diary(
    diary_service: Annotated[DiaryService, Depends(get_diary_service)], diary_id: str
):
    await diary_service.delete(diary_id)


@app.get(
    "/api/v1/diary/{diary_id}", response_model=Diary, status_code=status.HTTP_200_OK
)
async def find_diary(
    diary_service: Annotated[DiaryService, Depends(get_diary_service)], diary_id: str
):
    try:
        return await diary_service.get_diary_by_id(diary_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/api/v1/diary", response_model=Diary)
async def find_diary_by_date(
    diary_service: Annotated[DiaryService, Depends(get_diary_service)],
    writed_at: Annotated[date, Query()],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        diary = await diary_service.get_diary_by_date(writed_at, current_user)
        return diary
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


class WriteDiaryRequest(BaseModel):
    session_id: str
    message_id: str


@app.post("/api/v1/diary", response_model=Diary, status_code=status.HTTP_200_OK)
async def write_diary(
    request: WriteDiaryRequest,
    diary_service: Annotated[DiaryService, Depends(get_diary_service)],
):
    return await diary_service.write_diary(request.session_id, request.message_id)


class DiaryThumbnailExampleResponse(BaseModel):
    img_url: str


@app.get(
    "/api/v1/diary/thumbnail/{diary_id}",
    response_model=DiaryThumbnailExampleResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_diary_thumbnail_example_image(
    diary_service: Annotated[DiaryService, Depends(get_diary_service)], diary_id: str
):
    img_url = await diary_service.generate_example_thumbnail(diary_id)
    return DiaryThumbnailExampleResponse(img_url=img_url)


class ChangeDiaryThumbnailRequest(BaseModel):
    img_url: str


@app.patch("/api/v1/diary/{diary_id}/thumbnail", response_model=Diary)
async def change_diary_thumbnail(
    diary_service: Annotated[DiaryService, Depends(get_diary_service)],
    request: ChangeDiaryThumbnailRequest,
    diary_id: str,
):
    try:
        diary = await diary_service.update_thumbnail(diary_id, request.img_url)
        return diary
    except Exception as e:
        print(f"Error updating thumbnail: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class RegisterRequest(BaseModel):
    email: str = Field(min_length=10, description="User email")
    password: str = Field(min_length=10, description="User password")


class AuthTokenResponse(BaseModel):
    accessToken: str
    refreshToken: str


@app.post(
    "/api/v1/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """Register a new user and return JWT tokens"""
    try:
        tokens = await auth_service.register(
            email=request.email, password=request.password
        )
        return AuthTokenResponse(**tokens)
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PasswordLengthNotEnoughError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/v1/login", response_model=AuthTokenResponse)
async def login(
    request: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        token = await auth_service.login(request.email, request.password)
        return AuthTokenResponse(**token)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 정보입니다."
        )
    except PasswordNotCorrectError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 정보입니다."
        )


@app.post("/api/v1/email_verification_code", status_code=status.HTTP_200_OK)
async def send_email_verification_code(
    current_user: Annotated[User, Depends(get_current_user)],
    email_verification_service: Annotated[
        EmailVerificationService, Depends(get_email_verification_service)
    ],
):
    """Send email verification code to current user's email"""
    await email_verification_service.send_verification_code(current_user)


class VerifyEmailRequest(BaseModel):
    code: str


@app.post("/api/v1/verify_email")
async def verify_email(
    request: VerifyEmailRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    email_verification_service: Annotated[
        EmailVerificationService, Depends(get_email_verification_service)
    ],
):
    try:
        await email_verification_service.verifiy(current_user, request.code)
    except NotCorrectError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 인증번호 입니다.",
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 인증번호 입니다.",
        )
    except ExpiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효 기간이 만료 되었습니다.",
        )


class RefreshTokenRequest(BaseModel):
    refreshToken: str


@app.post(
    "/api/v1/refresh_token",
    status_code=status.HTTP_200_OK,
    response_model=AuthTokenResponse,
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    result = await auth_service.refresh_token(request.refreshToken)

    return AuthTokenResponse(**result)
