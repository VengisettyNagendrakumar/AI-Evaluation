from pathlib import Path

from app.exceptions.evaluation_exceptions import (
    EvaluationException
)
from urllib.parse import urlparse

class SubmissionValidator:

    # TEXT LIMITS

    MIN_SUBMISSION_LENGTH = 5
    MAX_SUBMISSION_LENGTH = 50000

    MIN_QUESTION_LENGTH = 5
    MAX_QUESTION_LENGTH = 10000

    MIN_EXPECTED_OUTPUT_LENGTH = 5
    MAX_EXPECTED_OUTPUT_LENGTH = 10000

    MIN_EVALUATION_CRITERIA_LENGTH = 5
    MAX_EVALUATION_CRITERIA_LENGTH = 15000

    MIN_SCORING_PARAMETERS_LENGTH = 3
    MAX_SCORING_PARAMETERS_LENGTH = 10000

    # FILE LIMITS
    # 

    MAX_FILE_COUNT = 10
    MAX_FILE_SIZE_MB = 50

    # LINK LIMITS

    MAX_GITHUB_LINKS = 5
    MAX_IMAGE_LINKS = 20

    # ALLOWED FILE TYPES

    ALLOWED_FILE_EXTENSIONS = {

        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".md",
        ".zip",
        ".py",
        ".java",
        ".js",
        ".ts",
        ".json",
        ".csv",
        ".ppt",
        ".pptx",
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".webp"
    }

    @classmethod
    def _validate_file_reference(
        cls,
        file_path: str
    ) -> tuple[Path, str, bool]:

        parsed_url = urlparse(
            file_path
        )

        if parsed_url.scheme in {
            "http",
            "https"
        }:

            if parsed_url.scheme != "https":

                raise EvaluationException(
                    "Only HTTPS file URLs are allowed."
                )

            if not parsed_url.netloc:

                raise EvaluationException(
                    "Invalid file URL."
                )

            url_path = Path(
                parsed_url.path
            )

            return (
                url_path,
                url_path.suffix.lower(),
                True
            )

        if parsed_url.scheme:

            raise EvaluationException(
                "Unsupported file reference scheme."
            )

        local_path = Path(
            file_path
        )

        if local_path.is_absolute():

            raise EvaluationException(
                "Absolute local file paths are not allowed."
            )

        if ".." in local_path.parts:

            raise EvaluationException(
                "Parent directory traversal is not allowed."
            )

        return (
            local_path,
            local_path.suffix.lower(),
            False
        )

    @classmethod
    def validate_submission(
        cls,
        request
    ):

        # QUESTION VALIDATION

        cleaned_question = (
            request.question.strip()
        )

        if not cleaned_question:

            raise EvaluationException(
                "Question cannot be empty."
            )

        if len(cleaned_question) < (
            cls.MIN_QUESTION_LENGTH
        ):

            raise EvaluationException(
                (
                    "Question is too short "
                    "for meaningful evaluation."
                )
            )

        if len(cleaned_question) > (
            cls.MAX_QUESTION_LENGTH
        ):

            raise EvaluationException(
                (
                    "Question exceeds maximum "
                    "allowed length."
                )
            )

        # EXPECTED OUTPUT VALIDATION

        cleaned_expected_output = (
            request.expected_output.strip()
        )

        if not cleaned_expected_output:

            raise EvaluationException(
                "Expected output cannot be empty."
            )

        if len(
            cleaned_expected_output
        ) < (
            cls.MIN_EXPECTED_OUTPUT_LENGTH
        ):

            raise EvaluationException(
                (
                    "Expected output is too short."
                )
            )

        if len(
            cleaned_expected_output
        ) > (
            cls.MAX_EXPECTED_OUTPUT_LENGTH
        ):

            raise EvaluationException(
                (
                    "Expected output exceeds "
                    "maximum allowed length."
                )
            )

        # EVALUATION CRITERIA VALIDATION

        cleaned_criteria = (
            request.evaluation_criteria.strip()
        )

        if not cleaned_criteria:

            raise EvaluationException(
                (
                    "Evaluation criteria "
                    "cannot be empty."
                )
            )

        if len(
            cleaned_criteria
        ) < (
            cls.MIN_EVALUATION_CRITERIA_LENGTH
        ):

            raise EvaluationException(
                (
                    "Evaluation criteria "
                    "is too short."
                )
            )

        if len(
            cleaned_criteria
        ) > (
            cls.MAX_EVALUATION_CRITERIA_LENGTH
        ):

            raise EvaluationException(
                (
                    "Evaluation criteria exceeds "
                    "maximum allowed length."
                )
            )

        # SCORING PARAMETERS VALIDATION

        cleaned_scoring = (
            request.scoring_parameters.strip()
        )

        if not cleaned_scoring:

            raise EvaluationException(
                (
                    "Scoring parameters "
                    "cannot be empty."
                )
            )

        if len(
            cleaned_scoring
        ) < (
            cls.MIN_SCORING_PARAMETERS_LENGTH
        ):

            raise EvaluationException(
                (
                    "Scoring parameters "
                    "is too short."
                )
            )

        if len(
            cleaned_scoring
        ) > (
            cls.MAX_SCORING_PARAMETERS_LENGTH
        ):

            raise EvaluationException(
                (
                    "Scoring parameters exceeds "
                    "maximum allowed length."
                )
            )

        
        # WRITTEN SUBMISSION

        has_submission_text = False

        if request.submission_text:

            cleaned_submission = (
                request.submission_text.strip()
            )

            if cleaned_submission:

                if len(cleaned_submission) < (
                    cls.MIN_SUBMISSION_LENGTH
                ):

                    raise EvaluationException(
                        (
                            "Submission text is too short "
                            "for meaningful evaluation."
                        )
                    )

                if len(cleaned_submission) > (
                    cls.MAX_SUBMISSION_LENGTH
                ):

                    raise EvaluationException(
                        (
                            "Submission exceeds maximum "
                            "allowed length."
                        )
                    )

                has_submission_text = True

        # GITHUB LINKS

        github_links = (
            request.github_links or []
        )

        if len(github_links) > (
            cls.MAX_GITHUB_LINKS
        ):

            raise EvaluationException(
                (
                    "Too many GitHub links provided."
                )
            )

        has_github_links = False

        for github_link in github_links:

            cleaned_link = github_link.strip()

            if not cleaned_link:

                continue

            if not (

                cleaned_link.startswith(
                    "https://github.com/"
                )

                or cleaned_link.startswith(
                    "http://github.com/"
                )
            ):

                raise EvaluationException(
                    (
                        "Invalid GitHub repository URL."
                    )
                )

            has_github_links = True

        # FILE VALIDATION

        file_paths = (
            request.file_paths or []
        )

        if len(file_paths) > (
            cls.MAX_FILE_COUNT
        ):

            raise EvaluationException(
                (
                    "Too many uploaded files."
                )
            )

        has_files = False

        for file_path in file_paths:

            cleaned_path = (
                str(file_path).strip()
            )

            if not cleaned_path:

                continue

            file_reference_path, extension, is_remote_file = (
                cls._validate_file_reference(
                    cleaned_path
                )
            )

            if extension not in (
                cls.ALLOWED_FILE_EXTENSIONS
            ):

                raise EvaluationException(
                    (
                        f"Unsupported file type: "
                        f"{extension}"
                    )
                )

            # LOCAL FILE SIZE VALIDATION

            if (
                not is_remote_file
                and file_reference_path.exists()
            ):

                file_size_mb = (

                    file_reference_path
                    .stat()
                    .st_size

                    / (1024 * 1024)
                )

                if file_size_mb > (
                    cls.MAX_FILE_SIZE_MB
                ):

                    raise EvaluationException(
                        (
                            f"File size exceeds "
                            f"{cls.MAX_FILE_SIZE_MB} MB "
                            f"limit: {file_reference_path}"
                        )
                    )

            has_files = True

        # IMAGE LINKS

        image_links = (
            request.image_links or []
        )

        if len(image_links) > (
            cls.MAX_IMAGE_LINKS
        ):

            raise EvaluationException(
                (
                    "Too many image links."
                )
            )

        has_image_links = False

        for image_link in image_links:

            cleaned_image_link = (
                image_link.strip()
            )

            if not cleaned_image_link:

                continue

            if not (

                cleaned_image_link.startswith(
                    "https://"
                )

                or cleaned_image_link.startswith(
                    "http://"
                )
            ):

                raise EvaluationException(
                    (
                        "Invalid image URL."
                    )
                )

            has_image_links = True

        # VALID SUBMISSION COMBINATIONS

        if not any([

            has_submission_text,
            has_github_links,
            has_files,
            has_image_links

        ]):

            raise EvaluationException(
                (
                    "Provide at least one submission method. "
                    "Example: written answer, GitHub link, "
                    "uploaded file or image."
                )
            )

        
        # OPTIONAL TASK TYPE VALIDATION

        if request.task_type:

            cleaned_task_type = (
                request.task_type.strip()
            )

            if len(cleaned_task_type) < 2:

                raise EvaluationException(
                    (
                        "Task type is invalid."
                    )
                )

        return True
