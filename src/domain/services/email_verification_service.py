from src.domain.entities.user import User
from src.domain.interfaces.email_sender import EmailSender
from src.domain.interfaces.verification_code_generator import VerificationCodeGenerator


class EmailVerificationService:
    def __init__(
        self,
        email_sender: EmailSender,
        verification_code_generator: VerificationCodeGenerator,
    ):
        self.email_sender = email_sender
        self.verification_code_generator = verification_code_generator

    async def send_verification_code(self, user: User):
        random_code = self.verification_code_generator.generate()
        await self.email_sender.send_email(
            sender="i need sender email",
            to=user.email,
            title="Verify Email",
            contents=f"I need HTML code using {random_code}",
        )
