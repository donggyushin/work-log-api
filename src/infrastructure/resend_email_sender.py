import os
import resend

from src.domain.interfaces.email_sender import EmailSender


class ResendEmailSender(EmailSender):
    def __init__(self):
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            raise ValueError("RESEND_API_KEY environment variable is not set")
        resend.api_key = api_key

    async def send_email(self, sender: str, to: str, title: str, contents: str):
        """
        Send email using Resend API

        Args:
            sender: Email address of the sender (must be verified domain or use onboarding@resend.dev for testing)
            to: Email address of the recipient
            title: Email subject
            contents: Email body (HTML supported)
        """
        params: resend.Emails.SendParams = {
            "from": sender,
            "to": [to],
            "subject": title,
            "html": contents,
        }

        try:
            # Resend SDK is synchronous, but it's I/O bound so acceptable in async context
            response = resend.Emails.send(params)
            print(response)
        except Exception as e:
            # Re-raise with more context
            raise Exception(f"Failed to send email via Resend: {str(e)}") from e
