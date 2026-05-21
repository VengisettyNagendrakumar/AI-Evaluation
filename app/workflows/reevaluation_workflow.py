from app.logging.logger import (
    get_logger
)

from app.schemas.request import (
    EvaluationRequest
)

from app.services.evaluation_service import (
    EvaluationService
)

from app.repositories.audit_repository import (
    AuditRepository
)


logger = get_logger(
    "reevaluation_workflow"
)


class ReevaluationWorkflow:

    def __init__(self):

        self.evaluation_service = (
            EvaluationService()
        )

    async def reevaluate(
        self,
        request: EvaluationRequest,
        previous_evaluation_id: str,
        reason: str
    ) -> dict:

        logger.info(
            f"Reevaluation started: {previous_evaluation_id}"
        )

        # RUN NEW EVALUATION

        new_result = (
            await self.evaluation_service.evaluate(
                request
            )
        )

        # AUDIT EVENT

        await AuditRepository.log_event(
            event_type="reevaluation_completed",
            details={
                "previous_evaluation_id": (
                    previous_evaluation_id
                ),
                "reason": reason,
                "new_score": (
                    new_result.ai_score
                )
            }
        )

        logger.info(
            f"Reevaluation completed: {previous_evaluation_id}"
        )

        return {
            "previous_evaluation_id": (
                previous_evaluation_id
            ),
            "reason": reason,
            "new_evaluation": (
                new_result.model_dump()
            )
        }