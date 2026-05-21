from datetime import datetime

from app.models.evaluation_model import (
    EvaluationModel
)

from app.schemas.evaluation import (
    EvaluationResult
)

from app.logging.logger import (
    get_logger
)


logger = get_logger(
    "evaluation_repository"
)


class EvaluationRepository:

    # IN-MEMORY STORAGE

    evaluations = []

    # SAVE EVALUATION

    @classmethod
    async def save_evaluation(
        cls,
        request_data: dict,
        evaluation_result: EvaluationResult
    ) -> EvaluationModel:

        logger.info(
            (
                "Saving evaluation: "
                f"{evaluation_result.evaluation_id}"
            )
        )

        evaluation_record = (
            EvaluationModel.create(

                request_data=request_data,

                result_data=(
                    evaluation_result.model_dump()
                )
            )
        )

        cls.evaluations.append(
            evaluation_record
        )

        logger.info(
            (
                "Evaluation saved successfully | "
                f"Total evaluations: "
                f"{len(cls.evaluations)}"
            )
        )

        return evaluation_record

    # GET ALL EVALUATIONS
    

    @classmethod
    async def get_all_evaluations(
        cls
    ):

        logger.info(
            (
                "Fetching all evaluations | "
                f"Count: {len(cls.evaluations)}"
            )
        )

        return cls.evaluations

    # GET EVALUATION BY ID

    @classmethod
    async def get_evaluation_by_id(
        cls,
        evaluation_id: str
    ):

        logger.info(
            (
                "Searching evaluation by id: "
                f"{evaluation_id}"
            )
        )

        for evaluation in cls.evaluations:

            if (
                evaluation.evaluation_id
                == evaluation_id
            ):

                logger.info(
                    (
                        "Evaluation found: "
                        f"{evaluation_id}"
                    )
                )

                return evaluation

        logger.warning(
            (
                "Evaluation not found: "
                f"{evaluation_id}"
            )
        )

        return None

    # GET REEVALUATION COUNT

    @classmethod
    async def get_reevaluation_count(
        cls,
        previous_evaluation_id: str
    ) -> int:

        reevaluation_count = 0

        for evaluation in cls.evaluations:

            result_data = getattr(
                evaluation,
                "result_data",
                {}
            )

            if (

                result_data.get(
                    "previous_evaluation_id"
                )

                == previous_evaluation_id
            ):

                reevaluation_count += 1

        logger.info(
            (
                "Reevaluation count fetched | "
                f"Evaluation ID: "
                f"{previous_evaluation_id} | "
                f"Count: {reevaluation_count}"
            )
        )

        return reevaluation_count

    # GET LATEST EVALUATION VERSION

    @classmethod
    async def get_latest_evaluation_version(
        cls,
        previous_evaluation_id: str
    ) -> int:

        latest_version = 1

        for evaluation in cls.evaluations:

            result_data = getattr(
                evaluation,
                "result_data",
                {}
            )

            if (

                result_data.get(
                    "previous_evaluation_id"
                )

                == previous_evaluation_id
            ):

                version = result_data.get(
                    "evaluation_version",
                    1
                )

                if version > latest_version:

                    latest_version = version

        logger.info(
            (
                "Latest evaluation version fetched | "
                f"Evaluation ID: "
                f"{previous_evaluation_id} | "
                f"Version: {latest_version}"
            )
        )

        return latest_version

    # GET EVALUATION HISTORY

    @classmethod
    async def get_evaluation_history(
        cls,
        evaluation_id: str
    ):

        history = []

        for evaluation in cls.evaluations:

            result_data = getattr(
                evaluation,
                "result_data",
                {}
            )

            if (

                result_data.get(
                    "evaluation_id"
                ) == evaluation_id

                or

                result_data.get(
                    "previous_evaluation_id"
                ) == evaluation_id
            ):

                history.append(
                    evaluation
                )

        logger.info(
            (
                "Evaluation history fetched | "
                f"Evaluation ID: "
                f"{evaluation_id} | "
                f"History Count: "
                f"{len(history)}"
            )
        )

        return history

    # DELETE EVALUATION

    @classmethod
    async def delete_evaluation(
        cls,
        evaluation_id: str
    ) -> bool:

        for index, evaluation in enumerate(
            cls.evaluations
        ):

            if (
                evaluation.evaluation_id
                == evaluation_id
            ):

                del cls.evaluations[index]

                logger.info(
                    (
                        "Evaluation deleted: "
                        f"{evaluation_id}"
                    )
                )

                return True

        logger.warning(
            (
                "Delete failed. "
                f"Evaluation not found: "
                f"{evaluation_id}"
            )
        )

        return False

    # REPOSITORY HEALTH

    @classmethod
    async def get_repository_stats(
        cls
    ) -> dict:

        total_evaluations = len(
            cls.evaluations
        )

        reevaluation_total = 0

        for evaluation in cls.evaluations:

            result_data = getattr(
                evaluation,
                "result_data",
                {}
            )

            if result_data.get(
                "previous_evaluation_id"
            ):

                reevaluation_total += 1

        stats = {

            "total_evaluations":
                total_evaluations,

            "total_reevaluations":
                reevaluation_total,

            "generated_at":
                datetime.utcnow().isoformat()
        }

        logger.info(
            (
                "Repository stats generated | "
                f"{stats}"
            )
        )

        return stats