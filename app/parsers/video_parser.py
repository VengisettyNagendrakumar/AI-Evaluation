from urllib.parse import urlparse

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "video_parser"
)


class VideoParser:

    SUPPORTED_DOMAINS = [
        "loom.com",
        "youtube.com",
        "youtu.be",
        "drive.google.com"
    ]

    @classmethod
    def validate_video_url(
        cls,
        video_url: str
    ) -> bool:

        if not video_url:
            return False

        parsed = urlparse(
            video_url
        )

        domain = parsed.netloc.lower()

        return any(

            supported_domain in domain

            for supported_domain in (
                cls.SUPPORTED_DOMAINS
            )
        )

    @classmethod
    def extract_video_metadata(
        cls,
        video_url: str
    ) -> dict:

        logger.info(
            f"Parsing video URL: {video_url}"
        )

        if not cls.validate_video_url(
            video_url
        ):

            raise ValueError(
                "Unsupported video URL"
            )

        parsed = urlparse(
            video_url
        )

        return {
            "platform": parsed.netloc,
            "video_url": video_url
        }