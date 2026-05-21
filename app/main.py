

from fastapi import (
    FastAPI,
    Depends
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from app.api.evaluate import (
    router as evaluation_router
)


from app.api.health import (
    router as health_router
)

from app.config.settings import (
    settings
)

from app.core.security import (
    verify_api_key
)

from app.exceptions.provider_exceptions import (
    ProviderException
)

from app.exceptions.evaluation_exceptions import (
    EvaluationException
)

from app.exceptions.global_exceptions import (
    provider_exception_handler,
    evaluation_exception_handler,
    generic_exception_handler
)

from app.middleware.logging_middleware import (
    LoggingMiddleware
)

from app.middleware.request_id_middleware import (
    RequestIDMiddleware
)

from app.middleware.rate_limit_middleware import (
    RateLimitMiddleware
)


app = FastAPI(

    title=settings.APP_NAME,

    version=settings.APP_VERSION,

    debug=settings.DEBUG
)


# EXCEPTION HANDLERS

app.add_exception_handler(
    ProviderException,
    provider_exception_handler
)

app.add_exception_handler(
    EvaluationException,
    evaluation_exception_handler
)

app.add_exception_handler(
    Exception,
    generic_exception_handler
)


# CORS

app.add_middleware(

    CORSMiddleware,

    allow_origins=settings.ALLOWED_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# MIDDLEWARE

app.add_middleware(
    RequestIDMiddleware
)

app.add_middleware(
    LoggingMiddleware
)

app.add_middleware(
    RateLimitMiddleware
)


# ROUTES

app.include_router(

    health_router,

    prefix=settings.API_PREFIX
)


app.include_router(

    evaluation_router,

    prefix=settings.API_PREFIX,

    dependencies=[
        Depends(verify_api_key)
    ]
)


# ROOT ROUTE

@app.get("/")
async def root():

    return {

        "message": (
            "AI Evaluation System Running"
        )
    }