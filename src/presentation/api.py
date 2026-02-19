import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.domain.exceptions import EmailAlreadyExistsError, PasswordLengthNotEnoughError
from src.domain.services.auth_service import AuthService
from src.infrastructure.bcrypt_hasher import BcryptHasher
from src.infrastructure.database import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
)
from src.infrastructure.mongo_refresh_token_repository import (
    MongoRefreshTokenRepository,
)
from src.infrastructure.mongo_user_repository import MongoUserRepository
from src.infrastructure.py_jwt_provider import PyJWTProvider


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(lifespan=lifespan)


def get_auth_service() -> AuthService:
    """Create AuthService instance with dependencies"""
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available",
        )

    user_repo = MongoUserRepository(db.client)
    refresh_token_repo = MongoRefreshTokenRepository(db.client)
    hasher = BcryptHasher()

    jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    jwt_provider = PyJWTProvider(secret_key=jwt_secret)

    return AuthService(
        user_repository=user_repo,
        jwt_provider=jwt_provider,
        hasher=hasher,
        refresh_token_repository=refresh_token_repo,
    )


@app.get("/api/v1")
async def hello():
    return {"message": "hello world"}


class RegisterRequest(BaseModel):
    email: str = Field(min_length=10, description="User email")
    password: str = Field(min_length=10, description="User password")


class RegisterResponse(BaseModel):
    accessToken: str
    refreshToken: str


@app.post(
    "/api/v1/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(request: RegisterRequest):
    """Register a new user and return JWT tokens"""
    auth_service = get_auth_service()

    try:
        tokens = await auth_service.register(
            email=request.email, password=request.password
        )
        return RegisterResponse(**tokens)
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PasswordLengthNotEnoughError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
