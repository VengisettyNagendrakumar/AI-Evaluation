class TokenCounter:

    @staticmethod
    def estimate_tokens(
        text: str
    ) -> int:

        if not text:
            return 0

        return len(text.split()) * 1.3