from openai import AsyncOpenAI

from app.config.groq_config import (
    GroqConfig
)

from app.providers.base_provider import (
    BaseProvider
)

from app.schemas.provider import (
    ProviderResponse
)

from app.core.enums import (
    ModelComplexity
)

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "groq_provider"
)


class GroqProvider(
    BaseProvider
):

    def __init__(self):

        self.client = AsyncOpenAI(

            api_key=GroqConfig.API_KEY,

            base_url=GroqConfig.BASE_URL,

            timeout=120.0
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = None,
        complexity: str = (
            ModelComplexity.SIMPLE
        )
    ) -> ProviderResponse:

        # MODEL SELECTION

        if model:

            selected_model = model

        else:

            if complexity == (
                ModelComplexity.COMPLEX
            ):

                selected_model = (
                    GroqConfig.COMPLEX_MODEL
                )

            else:

                selected_model = (
                    GroqConfig.SIMPLE_MODEL
                )

        logger.info(
            (
                "Using model: "
                f"{selected_model}"
            )
        )

        logger.info(
            (
                "Prompt size: "
                f"{len(prompt)} characters"
            )
        )

        
        # PRIMARY REQUEST

        try:

            response = (
                await self.client.chat.completions.create(

                    model=selected_model,

                    temperature=(
                        GroqConfig.TEMPERATURE
                    ),

                    max_tokens=(
                        GroqConfig.MAX_TOKENS
                    ),

                    messages=[

                        {
                            "role": "system",
                            "content": system_prompt
                        },

                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
            )

        # AUTO FALLBACK TO COMPLEX MODEL

        except Exception as error:

            error_text = str(error).lower()

            logger.exception(
                (
                    "Groq generation failed: "
                    f"{error_text}"
                )
            )

            # FALLBACK CONDITIONS

            if (

                selected_model
                == GroqConfig.SIMPLE_MODEL

                and (

                    "token" in error_text
                    or "context" in error_text
                    or "length" in error_text
                    or "rate" in error_text
                    or "timeout" in error_text
                )
            ):

                logger.warning(
                    (
                        "Switching to fallback "
                        "complex model."
                    )
                )

                try:

                    response = (
                        await self.client.chat.completions.create(

                            model=(
                                GroqConfig.COMPLEX_MODEL
                            ),

                            temperature=(
                                GroqConfig.TEMPERATURE
                            ),

                            max_tokens=(
                                GroqConfig.MAX_TOKENS
                            ),

                            messages=[

                                {
                                    "role": "system",
                                    "content": system_prompt
                                },

                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        )
                    )

                    selected_model = (
                        GroqConfig.COMPLEX_MODEL
                    )

                    logger.info(
                        (
                            "Fallback model "
                            "evaluation succeeded."
                        )
                    )

                except Exception as fallback_error:

                    logger.exception(
                        (
                            "Fallback model failed: "
                            f"{str(fallback_error)}"
                        )
                    )

                    raise fallback_error

            else:

                raise error

        # RESPONSE EXTRACTION

        content = (
            response
            .choices[0]
            .message.content
        )

        usage = response.usage

        prompt_tokens = (
            usage.prompt_tokens
            if usage else 0
        )

        completion_tokens = (
            usage.completion_tokens
            if usage else 0
        )

        total_tokens = (
            usage.total_tokens
            if usage else 0
        )

        logger.info(
            (
                "Groq completion successful | "
                f"Prompt Tokens: "
                f"{prompt_tokens} | "
                f"Completion Tokens: "
                f"{completion_tokens} | "
                f"Total Tokens: "
                f"{total_tokens}"
            )
        )

        # =====================================
        # RETURN RESPONSE
        # =====================================

        return ProviderResponse(

            provider="groq",

            model=selected_model,

            raw_response=content,

            prompt_tokens=(
                prompt_tokens
            ),

            completion_tokens=(
                completion_tokens
            ),

            total_tokens=(
                total_tokens
            )
        )