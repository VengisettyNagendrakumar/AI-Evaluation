from app.config.settings import settings


class GroqConfig:

    API_KEY = settings.GROQ_API_KEY

    BASE_URL = (
        "https://api.groq.com/openai/v1"
    )

    # SMALL / FAST TASKS

    SIMPLE_MODEL = (
        "llama-3.1-8b-instant"
    )

    # LARGE PROJECTS / ZIPS / MULTI FILES

    COMPLEX_MODEL = (
        "meta-llama/llama-4-scout-17b-16e-instruct"
    )

    TEMPERATURE = 0.1

    MAX_TOKENS = 4000

    TIMEOUT = 60