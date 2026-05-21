class EvaluationException(
    Exception
):

    def __init__(
        self,
        message: str
    ):

        self.message = message

        super().__init__(
            self.message
        )


class EvaluationParsingException(
    EvaluationException
):

    pass


class InvalidEvaluationSchemaException(
    EvaluationException
):

    pass


class ConfidenceValidationException(
    EvaluationException
):

    pass


class MaximumAttemptsExceededException(
    EvaluationException
):

    pass