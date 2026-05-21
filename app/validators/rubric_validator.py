from app.exceptions.evaluation_exceptions import (
    EvaluationException
)


class RubricValidator:

    MIN_RUBRIC_LENGTH = 20

    MAX_RUBRIC_LENGTH = 10000

    @classmethod
    def validate_rubric(
        cls,
        rubric: str
    ):

        if not rubric:

            raise EvaluationException(
                (
                    "Evaluation instructions are missing. "
                    "Provide evaluation criteria such as "
                    "'Evaluate authentication, scalability, "
                    "security, and documentation.'"
                )
            )

        cleaned_rubric = rubric.strip()

        if len(cleaned_rubric) < (
            cls.MIN_RUBRIC_LENGTH
        ):

            raise EvaluationException(
                (
                    "Evaluation instructions are too short. "
                    "Provide detailed evaluation criteria."
                )
            )

        if len(cleaned_rubric) > (
            cls.MAX_RUBRIC_LENGTH
        ):

            raise EvaluationException(
                (
                    "Evaluation instructions exceed "
                    "maximum allowed length."
                )
            )

        return True