import time
import threading

from pathlib import Path

from app.extractors.pdf_extractor import (
    PDFExtractor
)

from app.extractors.docx_extractor import (
    DOCXExtractor
)

from app.extractors.doc_extractor import (
    DOCExtractor
)

from app.extractors.zip_extractor import (
    ZIPExtractor
)

from app.extractors.image_extractor import (
    ImageExtractor
)

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "file_extractor"
)


class FileExtractor:

    # EXTRACTION LIMITS

    MAX_EXTRACTED_CHARACTERS = 20000

    MAX_TEXT_FILE_SIZE_MB = 5

    MAX_IMAGE_FILE_SIZE_MB = 10

    MIN_TEXT_LENGTH = 15

    # SUPPORTED FILE TYPES

    SUPPORTED_EXTENSIONS = {

        ".pdf",
        ".docx",
        ".doc",
        ".zip",
        ".txt",
        ".md",
        ".py",
        ".java",
        ".js",
        ".ts",
        ".json",
        ".csv",
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".webp"
    }

    # IMAGE FILE TYPES

    IMAGE_EXTENSIONS = {

        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".webp"
    }

    # TEXT FILE TYPES

    TEXT_EXTENSIONS = {

        ".txt",
        ".md",
        ".py",
        ".java",
        ".js",
        ".ts",
        ".json",
        ".csv"
    }

    # THREAD LOCK

    extraction_lock = threading.Lock()

    # FILE EXTRACTION

    @staticmethod
    def extract(
        file_path: str
    ) -> dict:

        extraction_start_time = (
            time.time()
        )

        try:

            if not file_path:

                logger.warning(
                    "Empty file path received."
                )

                return {

                    "text": "",

                    "success": False,

                    "warning": (
                        "Empty file path received."
                    ),

                    "blurry_detected": False
                }

            path_object = Path(
                file_path
            )

            extension = (
                path_object
                .suffix
                .lower()
            )

            logger.info(
                (
                    "Starting extraction | "
                    f"File: {path_object.name} | "
                    f"Thread: "
                    f"{threading.current_thread().name}"
                )
            )

            # UNSUPPORTED FILE TYPES

            if extension not in (
                FileExtractor.SUPPORTED_EXTENSIONS
            ):

                logger.warning(
                    (
                        "Unsupported file type: "
                        f"{extension}"
                    )
                )

                return {

                    "text": "",

                    "success": False,

                    "warning": (
                        f"Unsupported file type: "
                        f"{extension}"
                    ),

                    "blurry_detected": False
                }

            # FILE EXISTS CHECK

            if not path_object.exists():

                logger.warning(
                    (
                        "File does not exist: "
                        f"{file_path}"
                    )
                )

                return {

                    "text": "",

                    "success": False,

                    "warning": (
                        "Uploaded file does not exist."
                    ),

                    "blurry_detected": False
                }

            # FILE SIZE CHECK

            file_size_mb = round(

                path_object.stat().st_size
                / (1024 * 1024),

                2
            )

            logger.info(
                (
                    "File size detected: "
                    f"{file_size_mb} MB"
                )
            )

            # LARGE TEXT FILE PROTECTION

            if (

                extension in (
                    FileExtractor.TEXT_EXTENSIONS
                )

                and file_size_mb >
                FileExtractor.MAX_TEXT_FILE_SIZE_MB
            ):

                logger.warning(
                    (
                        "Large text file skipped: "
                        f"{path_object.name}"
                    )
                )

                return {

                    "text": "",

                    "success": False,

                    "warning": (
                        "Large text file skipped."
                    ),

                    "blurry_detected": False
                }

            # LARGE IMAGE PROTECTION

            if (

                extension in (
                    FileExtractor.IMAGE_EXTENSIONS
                )

                and file_size_mb >
                FileExtractor.MAX_IMAGE_FILE_SIZE_MB
            ):

                logger.warning(
                    (
                        "Large image skipped: "
                        f"{path_object.name}"
                    )
                )

                return {

                    "text": "",

                    "success": False,

                    "warning": (
                        "Large image skipped."
                    ),

                    "blurry_detected": True
                }

            extraction_result = {

                "text": "",

                "success": False,

                "warning": None,

                "blurry_detected": False
            }

            # PDF

            if extension == ".pdf":

                extraction_result = (
                    PDFExtractor.extract_text(
                        file_path
                    )
                )

            # DOCX

            elif extension == ".docx":

                extraction_result = (
                    DOCXExtractor.extract_text(
                        file_path
                    )
                )

            # DOC

            elif extension == ".doc":

                extraction_result = (
                    DOCExtractor.extract_text(
                        file_path
                    )
                )

            # ZIP

            elif extension == ".zip":

                extraction_result = (
                    ZIPExtractor.extract_text(
                        file_path
                    )
                )

            # IMAGE OCR EXTRACTION

            elif extension in (
                FileExtractor.IMAGE_EXTENSIONS
            ):

                extraction_result = (
                    ImageExtractor.extract_text(
                        file_path
                    )
                )

            # TEXT FILES

            elif extension in (
                FileExtractor.TEXT_EXTENSIONS
            ):

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as file:

                    extracted_text = (
                        file.read()
                    ).strip()

                if not extracted_text:

                    extraction_result = {

                        "text": "",

                        "success": False,

                        "warning": (
                            "No readable text extracted."
                        ),

                        "blurry_detected": False
                    }

                elif (
                    len(extracted_text)
                    < FileExtractor.MIN_TEXT_LENGTH
                ):

                    extraction_result = {

                        "text": extracted_text,

                        "success": False,

                        "warning": (
                            "Text content appears incomplete."
                        ),

                        "blurry_detected": False
                    }

                else:

                    extraction_result = {

                        "text": extracted_text,

                        "success": True,

                        "warning": None,

                        "blurry_detected": False
                    }

            extracted_text = (
                extraction_result.get(
                    "text",
                    ""
                )
            )

            # EMPTY EXTRACTION

            if not extracted_text:

                logger.warning(
                    (
                        "No text extracted from: "
                        f"{path_object.name}"
                    )
                )

                extraction_result[
                    "success"
                ] = False

                extraction_result[
                    "warning"
                ] = (
                    "No readable content extracted."
                )

                if extension in (
                    FileExtractor.IMAGE_EXTENSIONS
                ):

                    extraction_result[
                        "blurry_detected"
                    ] = True

                return extraction_result

            # MEMORY PROTECTION

            extracted_text = (
                extracted_text[
                    :FileExtractor
                    .MAX_EXTRACTED_CHARACTERS
                ]
            )

            extraction_result[
                "text"
            ] = extracted_text

            extraction_duration = round(

                time.time()
                - extraction_start_time,

                2
            )

            logger.info(
                (
                    "Extraction completed | "
                    f"File: {path_object.name} | "
                    f"Extension: {extension} | "
                    f"Characters: "
                    f"{len(extracted_text)} | "
                    f"Duration: "
                    f"{extraction_duration}s"
                )
            )

            return extraction_result

        except Exception as error:

            logger.exception(
                (
                    "File extraction failed: "
                    f"{str(error)}"
                )
            )

            return {

                "text": "",

                "success": False,

                "warning": (
                    "File extraction failed."
                ),

                "blurry_detected": False
            }