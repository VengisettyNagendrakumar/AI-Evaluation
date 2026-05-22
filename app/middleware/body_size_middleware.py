import json

from starlette.types import (
    ASGIApp,
    Message,
    Receive,
    Scope,
    Send
)


class BodySizeLimitMiddleware:

    def __init__(
        self,
        app: ASGIApp,
        max_body_size: int = 2 * 1024 * 1024
    ):

        self.app = app
        self.max_body_size = max_body_size

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send
    ):

        if scope["type"] != "http":

            await self.app(
                scope,
                receive,
                send
            )

            return

        content_length = self._get_content_length(
            scope
        )

        if (
            content_length is not None
            and content_length > self.max_body_size
        ):

            await self._send_too_large_response(
                send
            )

            return

        received_body_size = 0
        response_sent = False

        async def limited_receive() -> Message:

            nonlocal received_body_size
            nonlocal response_sent

            message = await receive()

            if message["type"] != "http.request":

                return message

            body = message.get(
                "body",
                b""
            )

            received_body_size += len(
                body
            )

            if received_body_size > self.max_body_size:

                response_sent = True

                await self._send_too_large_response(
                    send
                )

                return {
                    "type": "http.disconnect"
                }

            return message

        await self.app(
            scope,
            limited_receive,
            self._guard_send(
                send,
                lambda: response_sent
            )
        )

    @staticmethod
    def _get_content_length(
        scope: Scope
    ) -> int | None:

        for header_name, header_value in scope.get(
            "headers",
            []
        ):

            if header_name.lower() != b"content-length":

                continue

            try:

                return int(
                    header_value.decode(
                        "latin-1"
                    )
                )

            except ValueError:

                return None

        return None

    @staticmethod
    def _guard_send(
        send: Send,
        response_sent
    ) -> Send:

        async def guarded_send(
            message: Message
        ):

            if response_sent():

                return

            await send(
                message
            )

        return guarded_send

    @staticmethod
    async def _send_too_large_response(
        send: Send
    ):

        response_body = json.dumps(
            {
                "success": False,
                "message": "Request body too large",
                "error_type": "request_too_large"
            }
        ).encode(
            "utf-8"
        )

        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [
                    (
                        b"content-type",
                        b"application/json"
                    ),
                    (
                        b"content-length",
                        str(len(response_body)).encode(
                            "latin-1"
                        )
                    )
                ]
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": response_body,
                "more_body": False
            }
        )
