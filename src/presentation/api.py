from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.domain.entities.user import User
from src.domain.exceptions import EmailAlreadyExistsError, PasswordLengthNotEnoughError
from src.domain.services.auth_service import AuthService
from src.domain.services.email_verification_service import EmailVerificationService
from src.infrastructure.database import connect_to_mongo, close_mongo_connection
from src.presentation.dependencies import (
    get_auth_service,
    get_current_user,
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


@app.get("/api/v1")
async def hello():
    return {"message": "hello world"}


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
    token = await auth_service.login(request.email, request.password)
    return AuthTokenResponse(**token)


@app.post("/api/v1/email_verification_code", status_code=status.HTTP_200_OK)
async def send_email_verification_code(
    current_user: Annotated[User, Depends(get_current_user)],
    email_verification_service: Annotated[
        EmailVerificationService, Depends(get_email_verification_service)
    ],
):
    """Send email verification code to current user's email"""
    await email_verification_service.send_verification_code(current_user)


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
