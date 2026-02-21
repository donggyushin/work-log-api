from datetime import datetime, timedelta
from src.domain.entities.email_verification_code import EmailVerificationCode
from src.domain.entities.user import User
from src.domain.exceptions import ExpiredError, NotCorrectError, NotFoundError
from src.domain.interfaces.email_sender import EmailSender
from src.domain.interfaces.email_verification_code_repository import (
    EmailVerificationCodeRepository,
)
from src.domain.interfaces.user_repository import UserRepository
from src.domain.interfaces.verification_code_generator import VerificationCodeGenerator


class EmailVerificationService:
    def __init__(
        self,
        email_sender: EmailSender,
        verification_code_generator: VerificationCodeGenerator,
        email_verification_code_repository: EmailVerificationCodeRepository,
        user_repository: UserRepository,
    ):
        self.email_sender = email_sender
        self.verification_code_generator = verification_code_generator
        self.email_verification_code_repository = email_verification_code_repository
        self.user_repository = user_repository

    async def verifiy(self, user: User, code: str):
        verification_code = (
            await self.email_verification_code_repository.find_by_user_id(user.id)
        )
        if verification_code is None:
            raise NotFoundError()

        # src/domain/services/email_verification_service.py:33 근처에 추가
        print(f"Expected code: {verification_code.code}")
        print(f"Received code: {code}")
        print(f"Match: {verification_code.code == code}")

        if verification_code.code != code:
            raise NotCorrectError()

        if verification_code.expired_at < datetime.now():
            raise ExpiredError()

        user.email_verified = True
        await self.user_repository.update(user)
        await self.email_verification_code_repository.delete(verification_code)

    async def send_verification_code(self, user: User):
        """
        Send verification code to user's email

        Args:
            user: User entity containing email address

        Returns:
            Generated verification code (for saving to repository)
        """
        code = EmailVerificationCode(
            id="",  # mongodb 에서 자동 생성
            user_id=user.id,
            email=user.email,
            code=self.verification_code_generator.generate(),
            expired_at=datetime.now() + timedelta(minutes=10),
        )

        await self.email_verification_code_repository.create(code)

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
                                            {code.code}
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
            sender="onboarding@resend.dev",  # Resend test email (free to use)
            to=user.email,
            title="Daily Log - 이메일 인증 코드",
            contents=html_content,
        )
