import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
import time

from starlette.middleware.base import (
    BaseHTTPMiddleware
)

from app.logging.logger import (
    get_logger
)

logger = get_logger(
    "request_logger"
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )
)


class LoggingMiddleware(
    BaseHTTPMiddleware
):

    async def dispatch(
        self,
        request,
        call_next
    ):

        start_time = time.time()

        response = await call_next(
            request
        )

        process_time = (
            time.time() - start_time
        )

        request_id = getattr(
            request.state,
            "request_id",
            "unknown"
        )

        logger.info(
            f"REQUEST_ID={request_id} | "
            f"{request.method} "
            f"{request.url.path} | "
            f"STATUS={response.status_code} | "
            f"TIME={process_time:.4f}s"
        )

        return response