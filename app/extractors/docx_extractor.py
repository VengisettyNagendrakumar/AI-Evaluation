from docx import Document

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "docx_extractor"
)


class DOCXExtractor:

    # MINIMUM TEXT REQUIREMENT

    MIN_EXTRACTED_TEXT_LENGTH = 15

    @staticmethod
    def extract_text(
        file_path: str
    ) -> dict:

        try:

            logger.info(
                (
                    "Starting DOCX extraction: "
                    f"{file_path}"
                )
            )

            document = Document(
                file_path
            )

            extracted_text = "\n".join(

                paragraph.text

                for paragraph in (
                    document.paragraphs
                )
            ).strip()

            # EMPTY EXTRACTION
            

            if not extracted_text:

                logger.warning(
                    (
                        "No readable DOCX content "
                        f"found: {file_path}"
                    )
                )

                return {

                    "text": "",

                    "success": False,

                    "warning": (
                        "No readable DOCX content extracted."
                    )
                }

            # LOW QUALITY EXTRACTION

            if (
                len(extracted_text)
                < DOCXExtractor
                .MIN_EXTRACTED_TEXT_LENGTH
            ):

                logger.warning(
                    (
                        "Very little DOCX content extracted: "
                        f"{file_path}"
                    )
                )

                return {

                    "text": extracted_text,

                    "success": False,

                    "warning": (
                        "DOCX content appears incomplete "
                        "or unclear."
                    )
                }

            logger.info(
                (
                    "DOCX extraction completed | "
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
                    "DOCX extraction failed: "
                    f"{str(error)}"
                )
            )

            return {

                "text": "",

                "success": False,

                "warning": (
                    "DOCX extraction failed."
                )
            }