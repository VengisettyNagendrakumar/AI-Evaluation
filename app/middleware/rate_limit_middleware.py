import time

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(
    BaseHTTPMiddleware
):

    RATE_LIMIT = 30

    WINDOW_SECONDS = 60

    requests = {}

    async def dispatch(
        self,
        request,
        call_next
    ):

        client_ip = (
            request.client.host
        )

        current_time = time.time()

        if client_ip not in self.requests:

            self.requests[client_ip] = []

        self.requests[client_ip] = [

            timestamp

            for timestamp in self.requests[
                client_ip
            ]

            if current_time - timestamp
            < self.WINDOW_SECONDS
        ]

        if len(
            self.requests[client_ip]
        ) >= self.RATE_LIMIT:

            raise HTTPException(
                status_code=429,
                detail=(
                    "Rate limit exceeded"
                )
            )

        self.requests[client_ip].append(
            current_time
        )

        response = await call_next(
            request
        )

        return response