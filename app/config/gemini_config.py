from app.config.settings import settings


class GeminiConfig:

    API_KEY = settings.GEMINI_API_KEY

    MODEL_NAME = "gemini-2.0-flash"

    TEMPERATURE = 0.2

    MAX_OUTPUT_TOKENS = 4000

    TIMEOUT = 60