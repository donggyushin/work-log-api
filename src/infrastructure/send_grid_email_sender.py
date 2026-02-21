import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.domain.interfaces.email_sender import EmailSender


class SendGridEmailSender(EmailSender):
    def __init__(self):
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is not set")
        self.client = SendGridAPIClient(api_key)

    async def send_email(self, sender: str, to: str, title: str, contents: str):
        """
        Send email using SendGrid API

        Args:
            sender: Email address of the sender
            to: Email address of the recipient
            title: Email subject
            contents: Email body (HTML supported)
        """
        message = Mail(
            from_email=sender,
            to_emails=to,
            subject=title,
            html_content=contents
        )

        try:
            # SendGrid SDK is synchronous, but it's I/O bound so acceptable in async context
            response = self.client.send(message)
            return response
        except Exception as e:
            # Re-raise with more context
            raise Exception(f"Failed to send email via SendGrid: {str(e)}") from e
