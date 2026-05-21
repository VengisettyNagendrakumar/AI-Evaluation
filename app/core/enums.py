from enum import Enum


class ProviderType(
    str,
    Enum
):

    GROQ = "groq"

    GEMINI = "gemini"


class EvaluationStatus(
    str,
    Enum
):

    SUCCESS = "success"

    FAILED = "failed"

    PENDING = "pending"

    REQUIRES_REVIEW = (
        "requires_review"
    )


# MODEL COMPLEXITY

class ModelComplexity(
    str,
    Enum
):

    SIMPLE = "simple"

    COMPLEX = "complex"