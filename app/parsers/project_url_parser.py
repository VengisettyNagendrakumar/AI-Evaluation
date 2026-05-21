from urllib.parse import urlparse

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "project_url_parser"
)


class ProjectURLParser:

    @classmethod
    def validate_project_url(
        cls,
        project_url: str
    ) -> bool:

        if not project_url:
            return False

        parsed = urlparse(
            project_url
        )

        return all([
            parsed.scheme,
            parsed.netloc
        ])

    @classmethod
    def extract_project_metadata(
        cls,
        project_url: str
    ) -> dict:

        logger.info(
            f"Parsing project URL: {project_url}"
        )

        if not cls.validate_project_url(
            project_url
        ):

            raise ValueError(
                "Invalid project URL"
            )

        parsed = urlparse(
            project_url
        )

        return {
            "domain": parsed.netloc,
            "url": project_url
        }