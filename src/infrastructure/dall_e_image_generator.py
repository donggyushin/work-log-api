import os

from openai import AsyncOpenAI

from src.domain.exceptions import NotFoundError
from src.domain.interfaces.image_generator import ImageGenerator


class DallEImageGenerator(ImageGenerator):
    def __init__(self):
        api_key = os.getenv("OPEN_AI_API_KEY")
        if not api_key:
            raise ValueError("OPEN_AI_API_KEY environment variable is not set")
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(self, prompt: str) -> str:
        """
        Generate an image using OpenAI DALL-E 3 API.

        Args:
            prompt: Text description for image generation

        Returns:
            str: URL of the generated image

        Raises:
            Exception: If image generation fails
        """
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        if not response.data or not response.data[0].url:
            raise NotFoundError()

        return response.data[0].url
