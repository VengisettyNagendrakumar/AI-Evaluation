from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.provider_exceptions import (
    ProviderException
)

from app.exceptions.evaluation_exceptions import (
    EvaluationException
)


async def provider_exception_handler(
    request: Request,
    exc: ProviderException
):

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": exc.message,
            "error_type": "provider_error"
        }
    )


async def evaluation_exception_handler(
    request: Request,
    exc: EvaluationException
):

    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": exc.message,
            "error_type": "evaluation_error"
        }
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
):

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_type": "internal_error"
        }
    )