from abc import ABC, abstractmethod


class JWTProvider(ABC):
    @abstractmethod
    def generate_token(self, user_id: str) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str) -> dict:
        pass
