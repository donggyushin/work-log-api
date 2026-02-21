import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.interfaces.email_sender import EmailSender
from src.domain.interfaces.email_verification_code_repository import (
    EmailVerificationCodeRepository,
)
from src.domain.interfaces.hasher import Hasher
from src.domain.interfaces.jwt_provider import JWTProvider
from src.domain.interfaces.refresh_token_repository import RefreshTokenRepository
from src.domain.interfaces.user_repository import UserRepository
from src.domain.interfaces.verification_code_generator import VerificationCodeGenerator
from src.domain.services.auth_service import AuthService
from src.domain.services.email_verification_service import EmailVerificationService
from src.infrastructure.bcrypt_hasher import BcryptHasher
from src.infrastructure.database import get_database
from src.infrastructure.mongo_email_verification_code_repository import (
    MongoEmailVerificationCodeRepository,
)
from src.infrastructure.mongo_refresh_token_repository import (
    MongoRefreshTokenRepository,
)
from src.infrastructure.mongo_user_repository import MongoUserRepository
from src.infrastructure.py_jwt_provider import PyJWTProvider
from src.infrastructure.random_number_code_generator import RandomNumberCodeGenerator
from src.infrastructure.resend_email_sender import ResendEmailSender


def get_db() -> AsyncIOMotorDatabase:
    """Get database connection"""
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available",
        )
    return db


def get_user_repository(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> UserRepository:
    """Get user repository instance"""
    return MongoUserRepository(db.client)


def get_refresh_token_repository(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> RefreshTokenRepository:
    """Get refresh token repository instance"""
    return MongoRefreshTokenRepository(db.client)


def get_email_verification_code_repository(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)],
) -> EmailVerificationCodeRepository:
    return MongoEmailVerificationCodeRepository(db.client)


def get_hasher() -> Hasher:
    """Get password hasher instance"""
    return BcryptHasher()


def get_jwt_provider() -> JWTProvider:
    """Get JWT provider instance"""
    jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    return PyJWTProvider(secret_key=jwt_secret)


def get_email_sender() -> EmailSender:
    return ResendEmailSender()


def get_verification_code_generator() -> VerificationCodeGenerator:
    return RandomNumberCodeGenerator()


def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    refresh_token_repo: Annotated[
        RefreshTokenRepository, Depends(get_refresh_token_repository)
    ],
    hasher: Annotated[Hasher, Depends(get_hasher)],
    jwt_provider: Annotated[JWTProvider, Depends(get_jwt_provider)],
) -> AuthService:
    """Get auth service instance with all dependencies injected"""
    return AuthService(
        user_repository=user_repo,
        jwt_provider=jwt_provider,
        hasher=hasher,
        refresh_token_repository=refresh_token_repo,
    )


def get_email_verification_service(
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
    verification_code_generator: Annotated[
        VerificationCodeGenerator, Depends(get_verification_code_generator)
    ],
    email_verification_code_repository: Annotated[
        EmailVerificationCodeRepository, Depends(get_email_verification_code_repository)
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> EmailVerificationService:
    return EmailVerificationService(
        email_sender,
        verification_code_generator,
        email_verification_code_repository,
        user_repository,
    )
