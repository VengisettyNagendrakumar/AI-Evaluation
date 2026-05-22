from app.logging.logger import (
    get_logger
)

from app.schemas.request import (
    EvaluationRequest
)

from app.services.evaluation_service import (
    EvaluationService
)

from app.services.confidence_service import (
    ConfidenceService
)

from app.services.routing_service import (
    RoutingService
)


logger = get_logger(
    "evaluation_workflow"
)


class EvaluationWorkflow:

    def __init__(self):

        self.evaluation_service = (
            EvaluationService()
        )

    async def execute(
        self,
        request: EvaluationRequest
    ) -> dict:

        logger.info(
            "Evaluation workflow started"
        )

        requires_gemini = (
            RoutingService.requires_gemini(
                request
            )
        )

        requires_groq = (
            RoutingService.requires_groq(
                request
            )
        )

        logger.info(
            f"Gemini Required: {requires_gemini}"
        )

        logger.info(
            f"Groq Required: {requires_groq}"
        )

        evaluation_result = (
            await self.evaluation_service.evaluate(
                request=request,
                requires_gemini=requires_gemini,
                requires_groq=requires_groq
            )
        )

        requires_review = (
            ConfidenceService.requires_human_review(
                evaluation_result.confidence
            )
            or evaluation_result.requires_manual_review
        )

        workflow_result = {

            "evaluation_result": (
                evaluation_result.model_dump()
            ),

            "requires_human_review": (
                requires_review
            ),

            "requires_manual_review": (
                requires_review
            ),

            "manual_review_reason": (
                evaluation_result.manual_review_reason
            ),

            "workflow_status": "completed",

            "models_used": (
                evaluation_result.model
            ),

            "providers_used": (
                evaluation_result.provider
            )
        }

        logger.info(
            "Evaluation workflow completed"
        )

        return workflow_result
