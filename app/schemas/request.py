from typing import (
    Optional,
    List
)

from pydantic import (
    BaseModel,
    Field
)


class EvaluationRequest(
    BaseModel
):

    # QUESTION / ASSIGNMENT

    question: str = Field(
        ...,
        description=(
            "Original task question "
            "or assignment"
        )
    )

    # EXPECTED OUTPUT

    expected_output: str = Field(
        ...,
        description=(
            "Expected project outcome "
            "or expected answer"
        )
    )

    # EVALUATION CRITERIA

    evaluation_criteria: str = Field(
        ...,
        description=(
            "Evaluation criteria defined "
            "by instructor/admin"
        )
    )

    # SCORING PARAMETERS

    scoring_parameters: str = Field(
        ...,
        description=(
            "Scoring distribution "
            "and marking scheme"
        )
    )

    # WRITTEN ANSWER

    submission_text: Optional[str] = Field(
        default=None,
        description=(
            "Student submission text"
        )
    )

    # TASK TYPE

    task_type: Optional[str] = Field(
        default=None,
        description=(
            "Optional software domain"
        )
    )

    # FILES

    file_paths: List[str] = Field(
        default_factory=list,
        description=(
            "Uploaded file paths "
            "or temporary local file paths"
        )
    )

    # GITHUB LINKS

    github_links: List[str] = Field(
        default_factory=list,
        description=(
            "GitHub repository links"
        )
    )

    # IMAGE LINKS

    image_links: List[str] = Field(
        default_factory=list,
        description=(
            "Supporting image URLs"
        )
    )

    # REEVALUATION SUPPORT

    reevaluation_reason: Optional[str] = Field(
        default=None,
        description=(
            "Reason for reevaluation"
        )
    )

    previous_evaluation_id: Optional[str] = Field(
        default=None,
        description=(
            "Previous evaluation reference"
        )
    )