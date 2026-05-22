from app.schemas.evaluation import (
    EvaluationResult
)


class AggregationService:

    @staticmethod
    def aggregate_results(
        results: list[EvaluationResult]
    ) -> dict:

        if not results:

            return {}

        total_score = sum(

            result.ai_score

            for result in results
        )

        average_score = (
            total_score
            / len(results)
        )

        combined_strengths = []
        combined_weaknesses = []
        combined_suggestions = []
        combined_deductions = []
        combined_skills = []

        confidence_scores = []

        providers = []
        models = []

        for result in results:

            combined_strengths.extend(
                result.strengths
            )

            combined_weaknesses.extend(
                result.weaknesses
            )

            combined_suggestions.extend(
                result.improvement_suggestions
            )

            combined_deductions.extend(
                result.deductions
            )

            combined_skills.extend(
                result.skill_breakdown
            )

            confidence_scores.append(
                result.confidence
            )

            providers.append(
                result.provider
            )

            models.append(
                result.model
            )

        average_confidence = (
            sum(confidence_scores)
            / len(confidence_scores)
        )

        unique_providers = list(set(

            provider
            for provider in providers
            if provider
        ))

        unique_models = list(set(

            model
            for model in models
            if model
        ))

        provider_text = (
            ", ".join(unique_providers)
        )

        model_text = (
            ", ".join(unique_models)
        )

        return {

            "ai_score": round(
                average_score,
                2
            ),

            "strengths": list(
                set(combined_strengths)
            ),

            "weaknesses": list(
                set(combined_weaknesses)
            ),

            "improvement_suggestions": list(
                set(combined_suggestions)
            ),

            "deductions": combined_deductions,

            "skill_breakdown": combined_skills,

            "confidence": round(
                average_confidence,
                2
            ),

            "final_feedback": (

                f"Evaluation completed using "
                f"{provider_text}."

                if provider_text

                else "Evaluation completed."
            ),

            "provider": provider_text,

            "model": model_text
        }