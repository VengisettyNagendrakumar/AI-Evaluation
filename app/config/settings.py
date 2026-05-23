# app/config/settings.py

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # APP CONFIG
    APP_NAME: str = "AI Evaluation System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, bool):
            return value

        if value is None:
            return False

        value = str(value).strip().lower()

        if value in {"true", "1", "yes", "y", "on", "debug", "development", "dev"}:
            return True

        if value in {"false", "0", "no", "n", "off", "release", "production", "prod"}:
            return False

        return False

    # API CONFIG
    # API SECURITY
    API_KEY: str = ""
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = [
    "https://lms-backend-ra4z.onrender.com",
    "https://api.placemux.com",
    "http://localhost:3000",    
]

    # GROQ CONFIG
    GROQ_API_KEY: str

    # GEMINI CONFIG
    GEMINI_API_KEY: str

 

  

    # LOGGING CONFIG
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = False
    LOG_FILE: str = "logs/app.log"
    
    
    

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()