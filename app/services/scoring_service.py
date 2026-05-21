class ScoringService:

    MAX_SCORE = 100

    @classmethod
    def calculate_weighted_score(
        cls,
        scores: dict,
        weights: dict
    ) -> float:

        if not scores:
            return 0.0

        total_score = 0.0

        total_weight = 0.0

        for category, score in scores.items():

            weight = weights.get(
                category,
                0
            )

            total_score += (
                score * weight
            )

            total_weight += weight

        if total_weight == 0:
            return 0.0

        final_score = (
            total_score
            / total_weight
        )

        final_score = min(
            final_score,
            cls.MAX_SCORE
        )

        return round(
            final_score,
            2
        )

    @classmethod
    def calculate_deduction_score(
        cls,
        deductions: list
    ) -> float:

        total_deduction = sum(

            deduction.get(
                "marks_deducted",
                0
            )

            for deduction in deductions
        )

        final_score = (
            cls.MAX_SCORE
            - total_deduction
        )

        return max(
            0,
            round(final_score, 2)
        )

    @classmethod
    def normalize_score(
        cls,
        score: float
    ) -> float:

        score = max(
            0,
            score
        )

        score = min(
            score,
            cls.MAX_SCORE
        )

        return round(
            score,
            2
        )