from typing import Optional

from pydantic import BaseModel


class ProviderResponse(BaseModel):

    provider: str

    model: str

    raw_response: str

    prompt_tokens: Optional[int] = 0

    completion_tokens: Optional[int] = 0

    total_tokens: Optional[int] = 0