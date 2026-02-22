from abc import ABC, abstractmethod


class ImageStorage(ABC):
    @abstractmethod
    async def upload(self, image_data: bytes, file_name: str) -> str:
        """
        Upload image to storage.

        Args:
            image_data: Image file binary data
            file_name: Name for the uploaded file

        Returns:
            str: Public URL of the uploaded image
        """
        pass
