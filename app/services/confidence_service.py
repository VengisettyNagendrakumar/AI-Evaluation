class ConfidenceService:

    REVIEW_THRESHOLD = 0.75

    @classmethod
    def requires_human_review(
        cls,
        confidence: float
    ) -> bool:

        confidence = cls.normalize_confidence(
            confidence
        )

        return (
            confidence
            < cls.REVIEW_THRESHOLD
        )

    @classmethod
    def aggregate_confidence(
        cls,
        confidence_scores: list[float]
    ) -> float:

        if not confidence_scores:
            return 0.0

        normalized_scores = [

            cls.normalize_confidence(
                score
            )

            for score in confidence_scores
        ]

        average_confidence = (
            sum(normalized_scores)
            / len(normalized_scores)
        )

        return round(
            average_confidence,
            2
        )

    @classmethod
    def normalize_confidence(
        cls,
        confidence: float
    ) -> float:

        confidence = max(
            0.0,
            confidence
        )

        confidence = min(
            confidence,
            1.0
        )

        return round(
            confidence,
            2
        )

    @classmethod
    def get_confidence_level(
        cls,
        confidence: float
    ) -> str:

        confidence = cls.normalize_confidence(
            confidence
        )

        if confidence >= 0.90:
            return "very_high"

        if confidence >= 0.75:
            return "high"

        if confidence >= 0.50:
            return "medium"

        return "low"