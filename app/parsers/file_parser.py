from pathlib import Path

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "file_parser"
)


class FileParser:

    IMAGE_EXTENSIONS = [
        ".png",
        ".jpg",
        ".jpeg"
    ]

    DOCUMENT_EXTENSIONS = [
        ".pdf",
        ".doc",
        ".docx",
        ".txt"
    ]

    ARCHIVE_EXTENSIONS = [
        ".zip"
    ]

    @classmethod
    def classify_file(
        cls,
        file_path: str
    ) -> dict:

        logger.info(
            f"Classifying file: {file_path}"
        )

        extension = (
            Path(file_path)
            .suffix
            .lower()
        )

        if extension in (
            cls.IMAGE_EXTENSIONS
        ):

            return {
                "file_type": "image",
                "extension": extension
            }

        if extension in (
            cls.DOCUMENT_EXTENSIONS
        ):

            return {
                "file_type": "document",
                "extension": extension
            }

        if extension in (
            cls.ARCHIVE_EXTENSIONS
        ):

            return {
                "file_type": "archive",
                "extension": extension
            }

        return {
            "file_type": "unknown",
            "extension": extension
        }