import asyncio

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "retry_handler"
)


class RetryHandler:

    @staticmethod
    async def retry_async(
        function,
        retries: int = 3,
        delay: int = 1,
        backoff_multiplier: int = 2,
        *args,
        **kwargs
    ):

        last_error = None

        current_delay = delay

        for attempt in range(
            1,
            retries + 1
        ):

            try:

                logger.info(
                    (
                        f"Retry attempt "
                        f"{attempt}/{retries}"
                    )
                )

                result = await function(
                    *args,
                    **kwargs
                )

                logger.info(
                    (
                        "Retry operation "
                        "succeeded."
                    )
                )

                return result

            except Exception as error:

                last_error = error

                logger.exception(
                    (
                        "Retry attempt failed: "
                        f"{str(error)}"
                    )
                )

                # LAST ATTEMPT FAILED

                if attempt == retries:

                    logger.exception(
                        (
                            "Maximum retry attempts "
                            "reached."
                        )
                    )

                    break

                # WAIT BEFORE RETRY

                logger.info(
                    (
                        "Waiting "
                        f"{current_delay} seconds "
                        "before retry."
                    )
                )

                await asyncio.sleep(
                    current_delay
                )

                # EXPONENTIAL BACKOFF

                current_delay *= (
                    backoff_multiplier
                )

        raise last_error