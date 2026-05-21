from app.logging.logger import (
    get_logger
)

from app.repositories.audit_repository import (
    AuditRepository
)


logger = get_logger(
    "moderation_workflow"
)


class ModerationWorkflow:

    async def submit_for_review(
        self,
        evaluation_id: str,
        reason: str
    ) -> dict:

        logger.info(
            f"Evaluation submitted for review: {evaluation_id}"
        )

        await AuditRepository.log_event(
            event_type="submitted_for_review",
            details={
                "evaluation_id": evaluation_id,
                "reason": reason
            }
        )

        return {
            "evaluation_id": evaluation_id,
            "review_status": "pending",
            "reason": reason
        }

    async def approve_evaluation(
        self,
        evaluation_id: str,
        reviewer: str
    ) -> dict:

        logger.info(
            f"Evaluation approved: {evaluation_id}"
        )

        await AuditRepository.log_event(
            event_type="evaluation_approved",
            details={
                "evaluation_id": evaluation_id,
                "reviewer": reviewer
            }
        )

        return {
            "evaluation_id": evaluation_id,
            "review_status": "approved",
            "reviewer": reviewer
        }

    async def reject_evaluation(
        self,
        evaluation_id: str,
        reviewer: str,
        feedback: str
    ) -> dict:

        logger.info(
            f"Evaluation rejected: {evaluation_id}"
        )

        await AuditRepository.log_event(
            event_type="evaluation_rejected",
            details={
                "evaluation_id": evaluation_id,
                "reviewer": reviewer,
                "feedback": feedback
            }
        )

        return {
            "evaluation_id": evaluation_id,
            "review_status": "rejected",
            "reviewer": reviewer,
            "feedback": feedback
        }