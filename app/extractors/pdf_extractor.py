from pypdf import PdfReader

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "pdf_extractor"
)


class PDFExtractor:

    # MINIMUM TEXT REQUIREMENT

    MIN_EXTRACTED_TEXT_LENGTH = 20

    @staticmethod
    def extract_text(
        file_path: str
    ) -> dict:

        try:

            logger.info(
                (
                    "Starting PDF extraction: "
                    f"{file_path}"
                )
            )

            reader = PdfReader(
                file_path
            )

            extracted_text = ""

            total_pages = len(
                reader.pages
            )

            logger.info(
                (
                    "PDF pages detected: "
                    f"{total_pages}"
                )
            )

            for page in reader.pages:

                try:

                    page_text = (
                        page.extract_text()
                    )

                    if page_text:

                        extracted_text += (
                            page_text + "\n"
                        )

                except Exception as page_error:

                    logger.exception(
                        (
                            "PDF page extraction failed: "
                            f"{str(page_error)}"
                        )
                    )

                    continue

            extracted_text = (
                extracted_text.strip()
            )

            # EMPTY EXTRACTION

            if not extracted_text:

                logger.warning(
                    (
                        "No readable PDF content "
                        f"found: {file_path}"
                    )
                )

                return {

                    "text": "",

                    "success": False,

                    "warning": (
                        "No readable PDF content extracted."
                    )
                }

            # LOW QUALITY EXTRACTION

            if (
                len(extracted_text)
                < PDFExtractor
                .MIN_EXTRACTED_TEXT_LENGTH
            ):

                logger.warning(
                    (
                        "Very little PDF content extracted: "
                        f"{file_path}"
                    )
                )

                return {

                    "text": extracted_text,

                    "success": False,

                    "warning": (
                        "PDF content appears incomplete "
                        "or unclear."
                    )
                }

            logger.info(
                (
                    "PDF extraction completed | "
                    f"Characters Extracted: "
                    f"{len(extracted_text)}"
                )
            )

            return {

                "text": extracted_text,

                "success": True,

                "warning": None
            }

        except Exception as error:

            logger.exception(
                (
                    "PDF extraction failed: "
                    f"{str(error)}"
                )
            )

            return {

                "text": "",

                "success": False,

                "warning": (
                    "PDF extraction failed."
                )
            }