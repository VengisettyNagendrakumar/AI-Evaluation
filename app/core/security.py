import re
import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config.settings import settings


api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


async def verify_api_key(
    api_key: str = Security(api_key_header)
):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key missing"
        )

    expected_api_key = settings.API_KEY

    if (
        not expected_api_key
        or expected_api_key == "change-this-dev-key"
        or not secrets.compare_digest(api_key, expected_api_key)
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )

    return True


class SecurityUtils:

    @staticmethod
    def sanitize_input(
        text: str
    ) -> str:

        if not text:
            return ""

        cleaned = re.sub(
            r"<script.*?>.*?</script>",
            "",
            text,
            flags=re.IGNORECASE
        )

        cleaned = cleaned.strip()

        return cleaned