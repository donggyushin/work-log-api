import bcrypt

from src.domain.interfaces.hasher import Hasher


class BcryptHasher(Hasher):
    """Password hasher using bcrypt algorithm"""

    def hash(self, value: str) -> str:
        """
        Hash a password using bcrypt

        Args:
            value: Plain text password

        Returns:
            Hashed password as string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(value.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify(self, value: str, hashed: str) -> bool:
        """
        Verify a password against a hash

        Args:
            value: Plain text password
            hashed: Hashed password from database

        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(value.encode("utf-8"), hashed.encode("utf-8"))
