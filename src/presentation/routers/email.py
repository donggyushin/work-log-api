from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.domain.entities.user import User
from src.domain.exceptions import ExpiredError, NotCorrectError, NotFoundError
from src.domain.services.email_verification_service import EmailVerificationService
from src.presentation.dependencies import (
    get_current_user,
    get_email_verification_service,
)

router = APIRouter(prefix="/api/v1", tags=["Email Verification"])


# ========================================
# Request/Response Models
# ========================================


class VerifyEmailRequest(BaseModel):
    code: str


# ========================================
# Endpoints
# ========================================


@router.post(
    "/email_verification_code",
    status_code=status.HTTP_200_OK,
)
async def send_email_verification_code(
    current_user: Annotated[User, Depends(get_current_user)],
    email_verification_service: Annotated[
        EmailVerificationService, Depends(get_email_verification_service)
    ],
):
    """Send email verification code to current user's email"""
    await email_verification_service.send_verification_code(current_user)


@router.post("/verify_email")
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
