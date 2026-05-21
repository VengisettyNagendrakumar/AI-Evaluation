import json

from app.exceptions.evaluation_exceptions import (
    EvaluationParsingException
)


class JSONParser:

    # CLEAN RAW RESPONSE

    @staticmethod
    def clean_json_response(
        raw_response: str
    ) -> str:

        if not raw_response:

            return ""

        cleaned = raw_response.strip()

        # REMOVE MARKDOWN JSON BLOCKS

        cleaned = cleaned.replace(
            "```json",
            ""
        )

        cleaned = cleaned.replace(
            "```",
            ""
        )

        cleaned = cleaned.strip()

        return cleaned

    # EXTRACT FIRST VALID JSON OBJECT

    @staticmethod
    def extract_json_block(
        raw_response: str
    ) -> str:

        try:

            start_index = raw_response.find(
                "{"
            )

            if start_index == -1:

                return ""

            brace_count = 0

            json_characters = []

            for character in raw_response[
                start_index:
            ]:

                json_characters.append(
                    character
                )

                # OPEN BRACE

                if character == "{":

                    brace_count += 1

                # CLOSE BRACE

                elif character == "}":

                    brace_count -= 1

                    # JSON COMPLETED

                    if brace_count == 0:

                        break

            extracted_json = "".join(
                json_characters
            )

            return extracted_json.strip()

        except Exception:

            return ""

    # PARSE JSON

    @classmethod
    def parse_json(
        cls,
        raw_response: str
    ) -> dict:

        try:

            cleaned_response = (
                cls.clean_json_response(
                    raw_response
                )
            )

            if not cleaned_response:

                raise EvaluationParsingException(
                    (
                        "Empty AI response received."
                    )
                )

            json_content = (
                cls.extract_json_block(
                    cleaned_response
                )
            )

            if not json_content:

                raise EvaluationParsingException(
                    (
                        "No valid JSON object found."
                    )
                )

            parsed_json = json.loads(
                json_content
            )

            if not isinstance(
                parsed_json,
                dict
            ):

                raise EvaluationParsingException(
                    (
                        "AI response is not "
                        "a valid JSON object."
                    )
                )

            return parsed_json

        except Exception as error:

            raise EvaluationParsingException(
                (
                    "Failed to parse AI "
                    "evaluation response."
                )
            ) from error