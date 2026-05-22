import uuid
import aiohttp

from pathlib import Path

from urllib.parse import (
    urlparse
)

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "file_downloader"
)


class FileDownloader:

    TEMP_DOWNLOAD_DIR = Path(
        "temp_downloads"
    )

    MAX_DOWNLOAD_SIZE_MB = 50

    ALLOWED_CONTENT_TYPES = {

        "application/pdf",

        "application/msword",

        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

        "application/zip",

        "text/plain",

        "text/markdown",

        "application/json",

        "image/png",

        "image/jpeg",

        "image/jpg",

        "image/webp",

        "image/avif",

        "image/svg+xml"
    }

    ALLOWED_DOMAINS = {

        "amazonaws.com",

        "cloudfront.net",

        "your-company-domain.com"
    }

    CHUNK_SIZE = 1024 * 1024

    @classmethod
    def _is_allowed_domain(
        cls,
        domain: str
    ) -> bool:

        domain = (
            domain
            .lower()
            .strip()
        )

        return any(

            domain == allowed

            or domain.endswith(
                f".{allowed}"
            )

            for allowed in (
                cls.ALLOWED_DOMAINS
            )
        )

    @classmethod
    async def download_file(
        cls,
        file_url: str
    ) -> str:

        try:

            logger.info(
                (
                    "Starting file download: "
                    f"{file_url}"
                )
            )

            parsed_url = urlparse(
                file_url
            )

            if parsed_url.scheme != "https":

                logger.warning(
                    "Blocked non-HTTPS file URL."
                )

                return ""

            domain = (
                parsed_url.hostname
                or ""
            )

            if not cls._is_allowed_domain(
                domain
            ):

                logger.warning(
                    (
                        "Blocked download domain: "
                        f"{domain}"
                    )
                )

                return ""

            cls.TEMP_DOWNLOAD_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

            original_name = (
                file_url.split("?")[0]
                .split("/")[-1]
            )

            extension = Path(
                original_name
            ).suffix

            temp_filename = (
                f"{uuid.uuid4()}"
                f"{extension}"
            )

            temp_file_path = (
                cls.TEMP_DOWNLOAD_DIR
                / temp_filename
            )

            timeout = aiohttp.ClientTimeout(
                total=60
            )

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    file_url
                ) as response:

                    if response.status != 200:

                        logger.warning(
                            (
                                "File download failed | "
                                f"Status: "
                                f"{response.status}"
                            )
                        )

                        return ""

                    content_type = (
                        response.headers.get(
                            "Content-Type",
                            ""
                        ).split(";")[0]
                        .strip()
                    )

                    if content_type not in (
                        cls.ALLOWED_CONTENT_TYPES
                    ):

                        logger.warning(
                            (
                                "Invalid content type: "
                                f"{content_type}"
                            )
                        )

                        return ""

                    total_downloaded = 0

                    with open(
                        temp_file_path,
                        "wb"
                    ) as file:

                        async for chunk in (
                            response.content.iter_chunked(
                                cls.CHUNK_SIZE
                            )
                        ):

                            total_downloaded += len(
                                chunk
                            )

                            file.write(
                                chunk
                            )

                            if (

                                total_downloaded
                                >

                                cls.MAX_DOWNLOAD_SIZE_MB
                                * 1024
                                * 1024
                            ):

                                logger.warning(
                                    (
                                        "Downloaded file "
                                        "exceeded max size."
                                    )
                                )

                                file.close()

                                temp_file_path.unlink(
                                    missing_ok=True
                                )

                                return ""

            logger.info(
                (
                    "File download completed | "
                    f"Saved To: "
                    f"{temp_file_path}"
                )
            )

            return str(
                temp_file_path
            )

        except Exception as error:

            if 'temp_file_path' in locals():

                temp_file_path.unlink(
                    missing_ok=True
                )

            logger.exception(
                (
                    "File download failed: "
                    f"{str(error)}"
                )
            )

            return ""
