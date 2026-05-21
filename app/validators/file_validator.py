from pathlib import Path

from app.config.settings import settings

from app.exceptions.evaluation_exceptions import (
    EvaluationException
)


class FileValidator:

    ALLOWED_EXTENSIONS = [
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".txt",
        ".py",
        ".js",
        ".zip",
        ".docx"
    ]

    @classmethod
    def validate_file(
        cls,
        file_path: str
    ):

        path = Path(file_path)

        if not path.exists():

            raise EvaluationException(
                "Uploaded file does not exist"
            )

        extension = (
            path.suffix.lower()
        )

        if extension not in (
            cls.ALLOWED_EXTENSIONS
        ):

            raise EvaluationException(
                f"Unsupported file type: {extension}"
            )

        file_size_mb = (
            path.stat().st_size
            / (1024 * 1024)
        )

        if file_size_mb > (
            settings.MAX_FILE_SIZE_MB
        ):

            raise EvaluationException(
                "File exceeds maximum allowed size"
            )

        return True