class RoutingService:

    @classmethod
    def requires_groq(
        cls,
        request
    ) -> bool:

        return True

    @classmethod
    def requires_gemini(
        cls,
        request
    ) -> bool:

        return False