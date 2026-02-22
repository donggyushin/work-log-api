import os
import urllib3
from io import BytesIO

import boto3
from botocore.exceptions import ClientError
from src.domain.interfaces.image_storage import ImageStorage

# Disable SSL warnings in development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CloudflareR2Storage(ImageStorage):
    def __init__(self):
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        access_key_id = os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID")
        secret_access_key = os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
        bucket_name = os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
        public_domain = os.getenv("CLOUDFLARE_R2_PUBLIC_DOMAIN")

        if not all([account_id, access_key_id, secret_access_key, bucket_name]):
            raise ValueError(
                "Cloudflare R2 credentials are not properly configured in environment variables"
            )

        self.bucket_name = bucket_name
        self.public_domain = public_domain

        # R2 endpoint format: https://<account_id>.r2.cloudflarestorage.com
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

        # Create boto3 config to disable SSL verification in development
        from botocore.config import Config

        config = Config(
            signature_version="s3v4",
        )

        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name="auto",  # R2 uses "auto" as region
            config=config,
            verify=False,  # Disable SSL verification for Docker environment
        )

    async def upload(self, image_data: bytes, file_name: str) -> str:
        """
        Upload image to Cloudflare R2.

        Args:
            image_data: Image file binary data
            file_name: Name for the uploaded file

        Returns:
            str: Public URL of the uploaded image

        Raises:
            Exception: If upload fails
        """
        try:
            # Upload to R2
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=BytesIO(image_data),
                ContentType="image/png",  # DALL-E generates PNG
            )

            # Return public URL
            if self.public_domain:
                # Use custom domain if configured
                return f"https://{self.public_domain}/{file_name}"
            else:
                # https://pub-7241c825b0804fa08eb47ae5e9934e0f.r2.dev/
                # Use R2.dev public URL
                return (
                    f"https://pub-7241c825b0804fa08eb47ae5e9934e0f.r2.dev/{file_name}"
                )

        except ClientError as e:
            raise Exception(f"Failed to upload image to R2: {str(e)}")
