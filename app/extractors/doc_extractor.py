import textract

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "doc_extractor"
)


class DOCExtractor:

    # MINIMUM TEXT REQUIREMENT

    MIN_EXTRACTED_TEXT_LENGTH = 15

    @staticmethod
    def extract_text(
        file_path: str
    ) -> dict:

        try:

            logger.info(
                (
                    "Starting DOC extraction: "
                    f"{file_path}"
                )
            )

            text = textract.process(
                file_path
            )

            decoded_text = text.decode(

                "utf-8",

                errors="ignore"
            ).strip()

            # EMPTY EXTRACTION

            if not decoded_text:

                logger.warning(
                    (
                        "No readable DOC content "
                        f"found: {file_path}"
                    )
                )

                return {

                    "text": "",

                    "success": False,

                    "warning": (
                        "No readable DOC content extracted."
                    )
                }

            # LOW QUALITY EXTRACTION

            if (
                len(decoded_text)
                < DOCExtractor
                .MIN_EXTRACTED_TEXT_LENGTH
            ):

                logger.warning(
                    (
                        "Very little DOC content extracted: "
                        f"{file_path}"
                    )
                )

                return {

                    "text": decoded_text,

                    "success": False,

                    "warning": (
                        "DOC content appears incomplete "
                        "or unclear."
                    )
                }

            logger.info(
                (
                    "DOC extraction completed | "
                    f"Characters Extracted: "
                    f"{len(decoded_text)}"
                )
            )

            return {

                "text": decoded_text,

                "success": True,

                "warning": None
            }

        except Exception as error:

            logger.exception(
                (
                    "DOC extraction failed: "
                    f"{str(error)}"
                )
            )

            return {

                "text": "",

                "success": False,

                "warning": (
                    "DOC extraction failed."
                )
            }