from abc import ABC, abstractmethod
from typing import Any


class EmailSender(ABC):
    @abstractmethod
    async def send_email(self, sender: str, to: str, title: str, contents: str):
        """
        Send email to recipient

        Args:
            sender: Email address of the sender
            to: Email address of the recipient
            title: Email subject
            contents: Email body (HTML supported)

        Returns:
            Response from email service provider (type varies by implementation)
        """
        pass
