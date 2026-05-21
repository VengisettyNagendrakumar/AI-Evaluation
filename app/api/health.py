from fastapi import (
    APIRouter
)

from app.schemas.response import (
    APIResponse
)


router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get(
    "",
    response_model=APIResponse
)
async def health_check():

    return APIResponse(
        success=True,
        message="AI Evaluation System Running",
        data={
            "status": "healthy"
        }
    )