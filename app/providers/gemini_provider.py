from pathlib import Path

import google.generativeai as genai

from app.config.gemini_config import (
    GeminiConfig
)

from app.providers.base_provider import (
    BaseProvider
)

from app.schemas.provider import (
    ProviderResponse
)

from app.logging.logger import (
    get_logger
)

from app.exceptions.provider_exceptions import (
    ProviderException
)


logger = get_logger(
    "gemini_provider"
)


class GeminiProvider(
    BaseProvider
):

    SUPPORTED_FILE_EXTENSIONS = [
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".doc",
        ".docx"
    ]

    def __init__(self):

        genai.configure(
            api_key=GeminiConfig.API_KEY
        )

        self.model_name = (
            GeminiConfig.MODEL_NAME
        )

        self.model = (
            genai.GenerativeModel(
                self.model_name
            )
        )

    def _is_multimodal_request(
        self,
        file_paths: list[str]
    ) -> bool:

        if not file_paths:
            return False

        for file_path in file_paths:

            extension = (
                Path(file_path)
                .suffix
                .lower()
            )

            if (
                extension
                in self.SUPPORTED_FILE_EXTENSIONS
            ):

                return True

        return False

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        file_paths: list[str] | None = None
    ) -> ProviderResponse:

        try:

            final_prompt = f"""
            SYSTEM:
            {system_prompt}

            USER:
            {prompt}
            """

            # MULTIMODAL FLOW

            if self._is_multimodal_request(
                file_paths or []
            ):

                logger.info(
                    "Gemini multimodal request detected"
                )

                uploaded_files = []

                for file_path in file_paths:

                    extension = (
                        Path(file_path)
                        .suffix
                        .lower()
                    )

                    if (
                        extension
                        not in self.SUPPORTED_FILE_EXTENSIONS
                    ):

                        continue

                    logger.info(
                        f"Uploading file to Gemini: {file_path}"
                    )

                    uploaded_file = (
                        genai.upload_file(
                            path=file_path
                        )
                    )

                    uploaded_files.append(
                        uploaded_file
                    )

                response = (
                    self.model.generate_content(
                        [
                            *uploaded_files,
                            final_prompt
                        ]
                    )
                )

            # TEXT FLOW

            else:

                response = (
                    self.model.generate_content(
                        final_prompt
                    )
                )

            logger.info(
                "Gemini response received"
            )

            return ProviderResponse(
                provider="gemini",
                model=self.model_name,
                raw_response=response.text
            )

        except Exception as error:

            logger.exception(
                f"Gemini provider failed: {str(error)}"
            )

            raise ProviderException(
                f"Gemini provider failed: {str(error)}"
            )