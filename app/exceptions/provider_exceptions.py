class ProviderException(Exception):

    def __init__(
        self,
        message: str
    ):

        self.message = message

        super().__init__(
            self.message
        )


class ProviderTimeoutException(
    ProviderException
):

    pass


class ProviderRateLimitException(
    ProviderException
):

    pass


class InvalidProviderResponseException(
    ProviderException
):

    pass