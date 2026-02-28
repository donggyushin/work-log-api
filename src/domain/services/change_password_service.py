from datetime import datetime, timedelta
import os
from src.domain.entities.email_verification_code import EmailVerificationCode
from src.domain.exceptions import NotCorrectError, NotFoundError
from src.domain.interfaces.email_sender import EmailSender
from src.domain.interfaces.email_verification_code_repository import (
    EmailVerificationCodeRepository,
)
from src.domain.interfaces.hasher import Hasher
from src.domain.interfaces.jwt_provider import JWTProvider
from src.domain.interfaces.user_repository import UserRepository
from src.domain.interfaces.verification_code_generator import VerificationCodeGenerator


class ChangePasswordService:
    def __init__(
        self,
        email_verification_code_repository: EmailVerificationCodeRepository,
        user_repository: UserRepository,
        verification_code_generator: VerificationCodeGenerator,
        email_sender: EmailSender,
        jwt_provider: JWTProvider,
        hasher: Hasher,
    ):
        self.email_verification_code_repository = email_verification_code_repository
        self.user_repository = user_repository
        self.verification_code_generator = verification_code_generator
        self.email_sender = email_sender
        self.jwt_provider = jwt_provider
        self.hasher = hasher

    async def change_password(self, token: str, new_password: str):
        dict = self.jwt_provider.verify_token(token)
        user_id = dict.get("user_id")

        if user_id is None:
            raise NotFoundError()

        user = await self.user_repository.find_by_id(user_id)

        if user is None:
            raise NotFoundError()

        hashed_new_password = self.hasher.hash(new_password)

        user.password = hashed_new_password

        await self.user_repository.update(user)

    async def verify(self, email: str, code: str) -> str:
        user = await self.user_repository.find_by_email(email)
        if user is None:
            raise NotFoundError()

        verification_code = (
            await self.email_verification_code_repository.find_by_user_id(user.id)
        )

        if verification_code is None:
            raise NotFoundError()

        if verification_code.code != code:
            raise NotCorrectError()

        token = self.jwt_provider.generate_access_token(user.id)
        return token

    async def request_email_verification_code(self, email: str):
        user = await self.user_repository.find_by_email(email)
        code = self.verification_code_generator.generate()

        if user is None:
            raise NotFoundError()

        email_verification_code = EmailVerificationCode(
            user_id=user.id,
            email=email,
            code=code,
            expired_at=datetime.now() + timedelta(minutes=10),
        )

        await self.email_verification_code_repository.delete_by_user_id(user.id)
        await self.email_verification_code_repository.create(email_verification_code)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                            <!-- Header -->
                            <tr>
                                <td style="background-color: #4F46E5; padding: 40px 20px; text-align: center;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">이메일 인증</h1>
                                </td>
                            </tr>

                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <p style="color: #333333; font-size: 16px; line-height: 24px; margin: 0 0 20px 0;">
                                        안녕하세요,
                                    </p>
                                    <p style="color: #333333; font-size: 16px; line-height: 24px; margin: 0 0 30px 0;">
                                        아래 인증 코드를 입력하여 이메일 인증을 완료해주세요.
                                    </p>

                                    <!-- Verification Code Box -->
                                    <div style="background-color: #f8f9fa; border-radius: 8px; padding: 30px; text-align: center; margin: 30px 0;">
                                        <p style="color: #666666; font-size: 14px; margin: 0 0 10px 0;">인증 코드</p>
                                        <p style="color: #4F46E5; font-size: 36px; font-weight: bold; letter-spacing: 8px; margin: 0;">
                                            {email_verification_code.code}
                                        </p>
                                    </div>

                                    <p style="color: #666666; font-size: 14px; line-height: 20px; margin: 30px 0 0 0;">
                                        이 코드는 <strong>10분 동안</strong> 유효합니다.<br>
                                        본인이 요청하지 않았다면 이 메일을 무시해주세요.
                                    </p>
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                                    <p style="color: #999999; font-size: 12px; margin: 0;">
                                        이 메일은 발신 전용입니다. 문의사항은 고객센터를 이용해주세요.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        await self.email_sender.send_email(
            sender=os.getenv("EMAIL_FROM", "onboarding@resend.dev"),
            to=email,
            title="데일리로그 - 이메일 인증 코드",
            contents=html_content,
        )
