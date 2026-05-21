from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.schemas.request import (
    EvaluationRequest
)

from app.schemas.response import (
    APIResponse
)

from app.workflows.evaluation_workflow import (
    EvaluationWorkflow
)

from app.core.dependencies import (
    get_evaluation_workflow
)

from app.logging.logger import (
    get_logger
)


router = APIRouter(
    prefix="/evaluate",
    tags=["Evaluation"]
)


logger = get_logger(
    "evaluation_api"
)


# NORMAL EVALUATION

@router.post(
    "",
    response_model=APIResponse
)
async def evaluate_submission(
    request: EvaluationRequest,
    workflow: EvaluationWorkflow = Depends(
        get_evaluation_workflow
    )
):

    try:

        logger.info(
            "Evaluation request received"
        )

        # REEVALUATION DETECTION

        if request.previous_evaluation_id:

            logger.info(
                (
                    "Reevaluation request received | "
                    f"Previous Evaluation ID: "
                    f"{request.previous_evaluation_id}"
                )
            )

        workflow_result = (
            await workflow.execute(
                request
            )
        )

        logger.info(
            "Evaluation completed"
        )

        return APIResponse(

            success=(

                not workflow_result.get(
                    "requires_manual_review",
                    False
                )
            ),

            message=(

                workflow_result.get(
                    "manual_review_reason",
                    "Submission requires instructor review."
                )

                + " Submission forwarded "
                "for instructor review."

                if workflow_result.get(
                    "requires_manual_review",
                    False
                )

                else

                "Evaluation completed successfully"
            ),

            data=workflow_result
        )

    except HTTPException:

        raise

    except Exception as error:

        logger.exception(
            f"Evaluation failed: {str(error)}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Evaluation processing failed"
            )
        )


# REEVALUATION

@router.post(
    "/reevaluate",
    response_model=APIResponse
)
async def reevaluate_submission(
    request: EvaluationRequest,
    workflow: EvaluationWorkflow = Depends(
        get_evaluation_workflow
    )
):

    try:

        logger.info(
            "Reevaluation request received"
        )

        # REEVALUATION LOGGING

        if request.previous_evaluation_id:

            logger.info(
                (
                    "Reevaluation request received | "
                    f"Previous Evaluation ID: "
                    f"{request.previous_evaluation_id}"
                )
            )

        workflow_result = (
            await workflow.execute(
                request
            )
        )

        logger.info(
            "Reevaluation completed"
        )

        return APIResponse(

            success=(

                not workflow_result.get(
                    "requires_manual_review",
                    False
                )
            ),

            message=(

                workflow_result.get(
                    "manual_review_reason",
                    "Submission requires instructor review."
                )

                + " Submission forwarded "
                "for instructor review."

                if workflow_result.get(
                    "requires_manual_review",
                    False
                )

                else

                "Reevaluation completed successfully"
            ),

            data=workflow_result
        )

    except HTTPException:

        raise

    except Exception as error:

        logger.exception(
            (
                "Reevaluation failed: "
                f"{str(error)}"
            )
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Reevaluation processing failed"
            )
        )