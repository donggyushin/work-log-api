from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    async def send_email(self, sender: str, to: str, title: str, contents: str):
        pass
