import re
from urllib.parse import urlparse

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "github_parser"
)


class GitHubParser:

    GITHUB_REGEX = (
        r"^https://github\\.com/"
        r"([A-Za-z0-9_.-]+)/"
        r"([A-Za-z0-9_.-]+)"
    )

    @classmethod
    def validate_github_url(
        cls,
        github_url: str
    ) -> bool:

        if not github_url:
            return False

        return bool(
            re.match(
                cls.GITHUB_REGEX,
                github_url
            )
        )

    @classmethod
    def extract_repo_details(
        cls,
        github_url: str
    ) -> dict:

        logger.info(
            f"Parsing GitHub URL: {github_url}"
        )

        if not cls.validate_github_url(
            github_url
        ):

            raise ValueError(
                "Invalid GitHub repository URL"
            )

        parsed = urlparse(
            github_url
        )

        path_parts = (
            parsed.path.strip("/")
            .split("/")
        )

        owner = path_parts[0]

        repo_name = path_parts[1]

        return {
            "platform": "github",
            "owner": owner,
            "repository": repo_name,
            "repository_url": github_url
        }