from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.domain.exceptions import (
    EmailAlreadyExistsError,
    PasswordLengthNotEnoughError,
    PasswordNotCorrectError,
    UserNotFoundError,
)
from src.domain.services.auth_service import AuthService
from src.presentation.dependencies import get_auth_service

router = APIRouter(prefix="/api/v1", tags=["Authentication"])


# ========================================
# Request/Response Models
# ========================================


class RegisterRequest(BaseModel):
    email: str = Field(min_length=10, description="User email")
    password: str = Field(min_length=10, description="User password")


class AuthTokenResponse(BaseModel):
    accessToken: str
    refreshToken: str


class RefreshTokenRequest(BaseModel):
    refreshToken: str


# ========================================
# Endpoints
# ========================================


@router.post(
    "/register",
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


@router.post("/login", response_model=AuthTokenResponse)
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


@router.post(
    "/refresh_token",
    status_code=status.HTTP_200_OK,
    response_model=AuthTokenResponse,
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    result = await auth_service.refresh_token(request.refreshToken)
    return AuthTokenResponse(**result)
