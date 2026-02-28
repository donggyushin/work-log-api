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

    @abstractmethod
    async def delete(self, file_name_or_url: str) -> None:
        """
        Delete image from storage.

        Args:
            file_name_or_url: File name (e.g., "image.png") or full URL (e.g., "https://domain.com/image.png")

        Raises:
            Exception: If deletion fails
        """
        pass
