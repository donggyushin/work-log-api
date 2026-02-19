from datetime import datetime, timedelta, timezone

import jwt

from src.domain.interfaces.jwt_provider import JWTProvider


class PyJWTProvider(JWTProvider):
    """JWT token provider implementation using PyJWT"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expires_minutes: int = 15,
        refresh_token_expires_days: int = 15,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expires_minutes = access_token_expires_minutes
        self.refresh_token_expires_days = refresh_token_expires_days

    def generate_access_token(self, user_id: str) -> str:
        """Generate short-lived access token (15 minutes)"""
        payload = {
            "user_id": user_id,
            "type": "access",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=self.access_token_expires_minutes),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_refresh_token(self, user_id: str) -> str:
        """Generate long-lived refresh token (7 days)"""
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.now(timezone.utc)
            + timedelta(days=self.refresh_token_expires_days),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        """Verify token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
