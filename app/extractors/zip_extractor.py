from pathlib import Path

import zipfile

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "zip_extractor"
)


class ZIPExtractor:

    ALLOWED_EXTENSIONS = {

        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".kt",
        ".go",
        ".cpp",
        ".c",
        ".rs",
        ".json",
        ".yaml",
        ".yml",
        ".sql",
        ".md"
    }

    SKIP_FOLDERS = {

        "node_modules",
        "venv",
        "myenv",
        "__pycache__",
        ".git",
        "dist",
        "build",
        ".next",
        ".env",
        "coverage"
    }

    MAX_FILES = 15

    MAX_CHARACTERS_PER_FILE = 4000

    MAX_FILE_SIZE = 200 * 1024

    MIN_EXTRACTED_TEXT_LENGTH = 20

    @classmethod
    def extract_text(
        cls,
        zip_path: str
    ) -> dict:

        combined_content = ""

        processed_files = 0

        try:

            logger.info(
                (
                    "Starting ZIP extraction: "
                    f"{zip_path}"
                )
            )

            with zipfile.ZipFile(
                zip_path,
                "r"
            ) as zip_file:

                file_list = (
                    zip_file.infolist()
                )

                logger.info(
                    (
                        "ZIP files detected: "
                        f"{len(file_list)}"
                    )
                )

                for file_info in file_list:

                    if (
                        processed_files
                        >= cls.MAX_FILES
                    ):

                        logger.warning(
                            (
                                "Maximum ZIP file limit "
                                "reached."
                            )
                        )

                        break

                    file_name = (
                        file_info.filename
                    )

                    path_parts = (
                        Path(file_name).parts
                    )

                    # SKIP FOLDERS

                    if any(

                        folder in path_parts

                        for folder in (
                            cls.SKIP_FOLDERS
                        )
                    ):

                        continue

                    extension = (
                        Path(file_name)
                        .suffix
                        .lower()
                    )

                    # SKIP UNKNOWN FILES

                    if extension not in (
                        cls.ALLOWED_EXTENSIONS
                    ):

                        continue

                    # SKIP LARGE FILES

                    if (
                        file_info.file_size
                        > cls.MAX_FILE_SIZE
                    ):

                        logger.warning(
                            (
                                "Large ZIP file skipped: "
                                f"{file_name}"
                            )
                        )

                        continue

                    try:

                        with zip_file.open(
                            file_info
                        ) as file:

                            content = (
                                file.read()
                                .decode(
                                    "utf-8",
                                    errors="ignore"
                                )
                            )

                            if not content.strip():

                                continue

                            # LIMIT CONTENT

                            content = content[
                                :cls
                                .MAX_CHARACTERS_PER_FILE
                            ]

                            combined_content += f"""

==================================================
ZIP FILE: {file_name}
==================================================

{content}

"""

                            processed_files += 1

                    except Exception as error:

                        logger.exception(
                            (
                                "ZIP file read failed: "
                                f"{str(error)}"
                            )
                        )

                        continue

            combined_content = (
                combined_content.strip()
            )

            # EMPTY EXTRACTION

            if not combined_content:

                logger.warning(
                    (
                        "No readable ZIP content "
                        f"found: {zip_path}"
                    )
                )

                return {

                    "text": "",

                    "success": False,

                    "warning": (
                        "No readable ZIP content extracted."
                    )
                }

            # LOW QUALITY EXTRACTION

            if (
                len(combined_content)
                < cls.MIN_EXTRACTED_TEXT_LENGTH
            ):

                logger.warning(
                    (
                        "Very little ZIP content extracted: "
                        f"{zip_path}"
                    )
                )

                return {

                    "text": combined_content,

                    "success": False,

                    "warning": (
                        "ZIP content appears incomplete "
                        "or unclear."
                    )
                }

            logger.info(
                (
                    "ZIP extraction completed | "
                    f"Processed Files: "
                    f"{processed_files} | "
                    f"Characters Extracted: "
                    f"{len(combined_content)}"
                )
            )

            return {

                "text": combined_content,

                "success": True,

                "warning": None
            }

        except Exception as error:

            logger.exception(
                (
                    "ZIP extraction failed: "
                    f"{str(error)}"
                )
            )

            return {

                "text": "",

                "success": False,

                "warning": (
                    "ZIP extraction failed."
                )
            }