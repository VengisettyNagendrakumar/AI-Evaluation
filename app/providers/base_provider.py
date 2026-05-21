from abc import ABC, abstractmethod

from app.schemas.provider import ProviderResponse


class BaseProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = ""
    ) -> ProviderResponse:
        pass