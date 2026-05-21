from typing import (
    List,
    Optional
)

from datetime import (
    datetime
)

from pydantic import (
    BaseModel,
    Field
)


# DEDUCTIONS

class Deduction(
    BaseModel
):

    reason: str

    marks_deducted: float


# SKILL SCORES

class SkillScore(
    BaseModel
):

    skill: str

    score: float


# MAIN EVALUATION RESULT

class EvaluationResult(
    BaseModel
):

    # SUCCESS STATUS

    success: bool = True

    requires_manual_review: bool = False

    manual_review_reason: Optional[
        str
    ] = None

    # CORE SCORE

    ai_score: Optional[
        float
    ] = None

    confidence: float

    # FEEDBACK

    strengths: List[str]

    weaknesses: List[str]

    improvement_suggestions: List[str]

    final_feedback: str

    # DEDUCTIONS

    deductions: List[
        Deduction
    ]

    # SKILL BREAKDOWN

    skill_breakdown: List[
        SkillScore
    ]

    # PROVIDER INFO

    provider: Optional[str] = None

    model: Optional[str] = None

    # TOKEN METADATA

    prompt_tokens: Optional[
        int
    ] = None

    completion_tokens: Optional[
        int
    ] = None

    total_tokens: Optional[
        int
    ] = None

    # EVALUATION METADATA

    evaluation_id: Optional[
        str
    ] = None

    evaluation_version: int = 1

    reevaluation_count: int = 0

    previous_evaluation_id: Optional[
        str
    ] = None

    reevaluation_reason: Optional[
        str
    ] = None

    # VERSION TRACKING

    prompt_version: str = "v1"

    evaluator_version: str = "v1"

    # EXTRACTION METADATA

    extracted_files_count: int = 0

    extraction_failures_count: int = 0

    extraction_timeout_count: int = 0

    # EXTRACTION QUALITY

    extraction_success: bool = True

    extraction_warning: Optional[
        str
    ] = None

    blurry_file_detected: bool = False

    low_quality_extraction: bool = False

    # TIMING

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    reevaluated_at: Optional[
        datetime
    ] = None

    evaluation_duration_seconds: Optional[
        float
    ] = None

    # MONITORING

    provider_latency_seconds: Optional[
        float
    ] = None

    extraction_duration_seconds: Optional[
        float
    ] = None

    # STATUS FLAGS

    evaluation_status: str = (
        "completed"
    )

    is_reevaluated: bool = False
    
    # MANUAL REVIEW FLAGS

    requires_manual_review: bool = False

    manual_review_reason: Optional[
        str
    ] = None

    blurry_file_detected: bool = False