from PIL import (
    Image,
    ImageFilter,
    ImageOps
)

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "image_extractor"
)


class ImageExtractor:

    # IMAGE LIMITS

    MAX_IMAGE_WIDTH = 2000

    MAX_IMAGE_HEIGHT = 2000

    MIN_EXTRACTED_TEXT_LENGTH = 15

    # PREPROCESS IMAGE

    @staticmethod
    def preprocess_image(
        file_path: str
    ) -> Image.Image:

        try:

            with Image.open(
                file_path
            ) as image:

                logger.info(
                    (
                        "Starting image preprocessing: "
                        f"{file_path}"
                    )
                )

                # RGB NORMALIZATION

                image = image.convert(
                    "RGB"
                )

                # RESIZE HUGE IMAGES

                image.thumbnail(

                    (
                        ImageExtractor
                        .MAX_IMAGE_WIDTH,

                        ImageExtractor
                        .MAX_IMAGE_HEIGHT
                    )
                )

                # GRAYSCALE

                image = ImageOps.grayscale(
                    image
                )

                # SHARPENING

                image = image.filter(
                    ImageFilter.UnsharpMask(

                        radius=1.5,

                        percent=200,

                        threshold=3
                    )
                )

                image = image.filter(
                    ImageFilter.SHARPEN
                )

                logger.info(
                    (
                        "Image preprocessing completed."
                    )
                )

                return image.copy()

        except Exception as error:

            logger.exception(
                (
                    "Image preprocessing failed: "
                    f"{str(error)}"
                )
            )

            raise error

    # OCR EXTRACTION

    @staticmethod
    def extract_text(
        file_path: str
    ) -> dict:

        try:

            logger.info(
                (
                    "Starting OCR extraction: "
                    f"{file_path}"
                )
            )

            image = (
                ImageExtractor
                .preprocess_image(
                    file_path
                )
            )

            # IMPORT PYTESSERACT

            try:

                import pytesseract

            except ImportError:

                logger.warning(
                    (
                        "pytesseract is not installed. "
                        "OCR extraction unavailable."
                    )
                )

                return {
                    "text": "",
                    "success": False,
                    "blurry_detected": False,
                    "warning": (
                        "OCR engine unavailable."
                    )
                }

            # OCR

            extracted_text = (
                pytesseract.image_to_string(

                    image,

                    lang="eng"
                )
            )

            cleaned_text = (
                ImageExtractor
                .extract_relevant_information(
                    extracted_text
                )
            )

            # LOW QUALITY DETECTION

            blurry_detected = False

            extraction_success = True

            warning_message = None

            if (
                len(cleaned_text)
                < ImageExtractor
                .MIN_EXTRACTED_TEXT_LENGTH
            ):

                blurry_detected = True

                extraction_success = False

                warning_message = (
                    "Image appears blurry or unclear."
                )

                logger.warning(
                    (
                        "Low quality OCR detected: "
                        f"{file_path}"
                    )
                )

            logger.info(
                (
                    "OCR extraction completed | "
                    f"Characters Extracted: "
                    f"{len(cleaned_text)}"
                )
            )

            return {

                "text": cleaned_text,

                "success": extraction_success,

                "blurry_detected": blurry_detected,

                "warning": warning_message
            }

        except Exception as error:

            logger.exception(
                (
                    "Image extraction failed: "
                    f"{str(error)}"
                )
            )

            return {

                "text": "",

                "success": False,

                "blurry_detected": True,

                "warning": (
                    "Image extraction failed."
                )
            }

    # CLEAN EXTRACTED TEXT
    # 

    @staticmethod
    def extract_relevant_information(
        raw_text: str
    ) -> str:

        try:

            if not raw_text:

                return ""

            lines = [

                line.strip()

                for line in raw_text.splitlines()

                if line.strip()
            ]

            cleaned_text = "\n".join(
                lines
            ).strip()

            return cleaned_text

        except Exception as error:

            logger.exception(
                (
                    "OCR text cleaning failed: "
                    f"{str(error)}"
                )
            )

            return raw_text