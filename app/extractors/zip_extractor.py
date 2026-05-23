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
        ".swift",

        ".go",

        ".cpp",
        ".c",
        ".h",

        ".rs",

        ".cs",

        ".php",

        ".rb",

        ".scala",

        ".html",
        ".css",
        ".scss",

        ".sql",

        ".json",

        ".yaml",
        ".yml",

        ".xml",

        ".md",

        ".txt",
        ".ipynb"
    }

    SKIP_FOLDERS = {

        "node_modules",

        "venv",
        "myenv",
        ".venv",

        "__pycache__",

        ".git",

        "dist",
        "build",

        ".next",

        "coverage",

        "target",

        "bin",
        "obj",

        ".idea",
        ".vscode",

        "vendor",

        "Pods",

        ".gradle",

        "out",

        "tmp",

        "logs",
         ".github",
        ".gitlab-ci",
        ".circleci",
        "docker", ".docker",
        "kubernetes", ".k8s",
        "migrations",
        "static", "public", "assets", "media",
        "uploads",
        ".cache", "cache", ".npm", ".yarn", ".pnpm",
        ".m2",
        "temp", ".temp",
        ".aws",
        "venv_backup", "env_backup",
        "scripts",
    }

    SKIP_FILES = {

        "package-lock.json",
        "requirements.txt",
        "yarn.lock",
        ".gitignore",
        ".env",
        "pnpm-lock.yaml",

        "bun.lockb",

        "poetry.lock",

        "Pipfile.lock",

        ".DS_Store",
         "Gemfile.lock",
        ".npmrc", ".nvmrc", ".python-version", ".node-version",
        "Makefile",
        ".editorconfig",
        ".eslintrc", ".eslintrc.json", ".eslintrc.js",
        ".prettierrc", ".prettierrc.json",
        "tsconfig.json", "webpack.config.js", "babel.config.js",
        ".babelrc",
        "docker-compose.yml", "Dockerfile",
        ".env.example",
        "LICENSE", "AUTHORS",
        ".gitattributes",
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

                    if any(

                        folder in path_parts

                        for folder in (
                            cls.SKIP_FOLDERS
                        )
                    ):

                        continue

                    clean_file_name = (
                        Path(file_name).name
                    )

                    if clean_file_name in (
                        cls.SKIP_FILES
                    ):

                        continue

                    extension = (
                        Path(file_name)
                        .suffix
                        .lower()
                    )

                    if extension not in (
                        cls.ALLOWED_EXTENSIONS
                    ):

                        continue

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