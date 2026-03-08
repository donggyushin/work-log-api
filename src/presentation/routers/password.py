from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.domain.services.change_password_service import ChangePasswordService
from src.presentation.dependencies import get_change_password_service

router = APIRouter(prefix="/api/v1", tags=["Password Change"])


# ========================================
# Request/Response Models
# ========================================


class EmailVerificationCodeForChangingPasswordRequest(BaseModel):
    email: str


class EmailVerifyForChangingPasswordRequest(BaseModel):
    email: str
    code: str


class EmailVerifyForChangingPasswordResponse(BaseModel):
    token: str


class ChangePasswordRequest(BaseModel):
    token: str
    new_password: str


# ========================================
# Endpoints
# ========================================


@router.post("/change_password/email_verification_code")
async def request_email_verification_code_for_changing_password(
    change_password_service: Annotated[
        ChangePasswordService, Depends(get_change_password_service)
    ],
    request: EmailVerificationCodeForChangingPasswordRequest,
):
    try:
        await change_password_service.request_email_verification_code(request.email)
    except Exception as e:
        raise e


@router.post("/change_password/verify")
async def verify_email_verification_code_for_changing_password(
    request: EmailVerifyForChangingPasswordRequest,
    change_password_service: Annotated[
        ChangePasswordService, Depends(get_change_password_service)
    ],
) -> EmailVerifyForChangingPasswordResponse:
    try:
        token = await change_password_service.verify(request.email, request.code)
        response = EmailVerifyForChangingPasswordResponse(token=token)
        return response

    except Exception as e:
        raise e


@router.patch("/change_password")
async def change_password(
    change_password_service: Annotated[
        ChangePasswordService, Depends(get_change_password_service)
    ],
    request: ChangePasswordRequest,
):
    try:
        await change_password_service.change_password(
            request.token, request.new_password
        )
    except Exception as e:
        raise e
