# import os
# import time
# import asyncio

# from pathlib import Path

# from datetime import datetime

# from app.providers.groq_provider import (
#     GroqProvider
# )

# from app.schemas.evaluation import (
#     EvaluationResult
# )

# from app.schemas.request import (
#     EvaluationRequest
# )

# from app.validators.submission_validator import (
#     SubmissionValidator
# )

# from app.utils.json_parser import (
#     JSONParser
# )

# from app.utils.retry import (
#     RetryHandler
# )
# from app.repositories.evaluation_repository import (
#     EvaluationRepository
# )

# from app.repositories.audit_repository import (
#     AuditRepository
# )

# from app.services.aggregation import (
#     AggregationService
# )
# from app.utils.file_downloader import (
#     FileDownloader
# )

# from app.extractors.file_extractor import (
#     FileExtractor
# )

# from app.logging.logger import (
#     get_logger
# )

# from app.core.enums import (
#     ModelComplexity
# )


# logger = get_logger(
#     "evaluation_service"
# )


# class EvaluationService:

#     # CONFIG

#     MAX_TOTAL_CONTENT = 30000

#     MAX_FILE_CONTENT = 15000

#     EXTRACTION_TIMEOUT_SECONDS = 30

#     MAX_CONCURRENT_EXTRACTIONS = 3

#     PROMPT_VERSION = "v1"

#     EVALUATOR_VERSION = "v1"

#     def __init__(self):

#         self.groq_provider = (
#             GroqProvider()
#         )
#         self.base_prompt_path = Path(
#             "prompts"
#         )

#     # LOAD PROMPTS

#     def _load_prompt(
#         self,
#         category: str,
#         filename: str
#     ) -> str:

#         prompt_path = (
#             self.base_prompt_path
#             / category
#             / filename
#         )

#         with open(
#             prompt_path,
#             "r",
#             encoding="utf-8"
#         ) as file:

#             return file.read()

#     # SAFE FILE EXTRACTION

#     async def _safe_extract_file(
#         self,
#         file_path: str,
#         semaphore: asyncio.Semaphore
#     ) -> dict:

#         async with semaphore:

#             extraction_start_time = (
#                 time.time()
#             )

#             try:

#                 logger.info(
#                     (
#                         "Starting extraction for file: "
#                         f"{file_path}"
#                     )
#                 )
                
#                 local_file_path = file_path

#                 # DOWNLOAD S3 PRESIGNED URL

#                 if (
#                     str(file_path).startswith("http://")
#                     or str(file_path).startswith("https://")
#                 ):

#                     logger.info(
#                         (
#                             "Downloading remote file: "
#                             f"{file_path}"
#                         )
#                     )

#                     downloaded_file = (
#                         await FileDownloader.download_file(
#                             file_path
#                         )
#                     )

#                     if not downloaded_file:

#                         return {

#                             "file_path": file_path,

#                             "content": "",

#                             "success": False,

#                             "warning": (
#                                 "Failed to download remote file."
#                             ),

#                             "blurry_detected": False,

#                             "timeout": False,

#                             "duration": None
#                         }

#                     local_file_path = downloaded_file

#                 # EXTRACT FILE

#                 extracted_content = (
#                     await asyncio.wait_for(

#                         asyncio.to_thread(
#                             FileExtractor.extract,
#                             local_file_path
#                         ),

#                         timeout=(
#                             self
#                             .EXTRACTION_TIMEOUT_SECONDS
#                         )
#                     )
#                 )
#                 extracted_text = extracted_content.get(
#                     "text",
#                     ""
#                 )

#                 extraction_success = extracted_content.get(
#                     "success",
#                     False
#                 )

#                 extraction_warning = extracted_content.get(
#                     "warning"
#                 )

#                 blurry_detected = extracted_content.get(
#                     "blurry_detected",
#                     False
#                 )
                

#                 extraction_duration = round(

#                     time.time()
#                     - extraction_start_time,

#                     2
#                 )

#                 logger.info(
#                     (
#                         "Extraction completed | "
#                         f"File: {file_path} | "
#                         f"Duration: "
#                         f"{extraction_duration}s"
#                     )
#                 )

                
#                 return {

#                     "file_path": file_path,

#                     "content": (
#                         extracted_text or ""
#                     ),

#                     "success": (
#                         extraction_success
#                         and bool(extracted_text)
#                     ),

#                     "warning": extraction_warning,

#                     "blurry_detected": blurry_detected,

#                     "timeout": False,

#                     "duration": (
#                         extraction_duration
#                     )
#                }

#             except asyncio.TimeoutError:

#                 logger.exception(
#                     (
#                         "File extraction timeout exceeded for: "
#                         f"{file_path}"
#                     )
#                 )

#                 return {

#                     "file_path": file_path,

#                     "content": "",

#                     "success": False,

#                     "timeout": True,

#                     "duration": None
#                 }

#             except Exception as error:

#                 logger.exception(
#                     (
#                         "File extraction failed: "
#                         f"{str(error)}"
#                     )
#                 )

#                 return {

#                     "file_path": file_path,

#                     "content": "",

#                     "success": False,

#                     "timeout": False,

#                     "duration": None
#                 }

#             finally:

#                 # DELETE TEMP FILE

#                 try:

                    
#                     if (
#                         'local_file_path' in locals()
#                         and local_file_path
#                         and os.path.exists(local_file_path)
#                     ):

#                         os.remove(
#                             local_file_path
#                         )

#                         logger.info(
#                             (
#                                 "Temporary uploaded "
#                                 f"file deleted: {local_file_path}"
#                             )
#                         )

#                 except Exception as cleanup_error:

#                     logger.exception(
#                         (
#                             "Failed to delete "
#                             "temporary file: "
#                             f"{str(cleanup_error)}"
#                         )
#                     )

#     # EXTRACT FILE CONTENT

#     async def _extract_uploaded_files(
#         self,
#         request: EvaluationRequest
#     ) -> tuple[str, dict]:

#         combined_content = ""

#         extraction_failures_count = 0

#         extraction_timeout_count = 0

#         extracted_files_count = 0

#         extraction_start_time = (
#             time.time()
#         )

#         semaphore = asyncio.Semaphore(
#             self.MAX_CONCURRENT_EXTRACTIONS
#         )

#         extraction_tasks = [

#             self._safe_extract_file(
#                 file_path=file_path,
#                 semaphore=semaphore
#             )

#             for file_path in request.file_paths
#         ]

#         extraction_results = (
#             await asyncio.gather(
#                 *extraction_tasks
#             )
#         )

#         for result in extraction_results:

#             file_path = result[
#                 "file_path"
#             ]

#             extracted_content = result[
#                 "content"
#             ]

#             success = result[
#                 "success"
#             ]

#             timeout = result[
#                 "timeout"
#             ]

#             if timeout:

#                 extraction_timeout_count += 1

#             if not success:

#                 extraction_failures_count += 1

#             if not extracted_content:

#                 logger.warning(
#                     (
#                         "No content extracted "
#                         f"from: {file_path}"
#                     )
#                 )

#                 continue

#             extracted_files_count += 1

#             extracted_content = (
#                 extracted_content[
#                     :self.MAX_FILE_CONTENT
#                 ]
#             )

#             file_section = f"""

# ==================================================
# FILE NAME: {Path(file_path).name}
# FILE TYPE: {Path(file_path).suffix}
# ==================================================

# {extracted_content}

# """

#             if len(
#                 combined_content + file_section
#             ) > (
#                 self.MAX_TOTAL_CONTENT
#             ):

#                 logger.warning(
#                     (
#                         "Maximum extracted "
#                         "content limit reached."
#                     )
#                 )

#                 break

#             combined_content += (
#                 file_section
#             )

#         extraction_duration = round(

#             time.time()
#             - extraction_start_time,

#             2
#         )

#         extraction_metadata = {

#             "extracted_files_count": (
#                 extracted_files_count
#             ),

#             "extraction_failures_count": (
#                 extraction_failures_count
#             ),

#             "extraction_timeout_count": (
#                 extraction_timeout_count
#             ),

#             "extraction_duration_seconds": (
#                 extraction_duration
#             )
#         }

#         return (
#             combined_content.strip(),
#             extraction_metadata
#         )

#     # BUILD PROMPT

#     def _build_prompt(
#         self,
#         request: EvaluationRequest,
#         extracted_file_content: str
#     ) -> tuple[str, str]:

#         system_prompt = self._load_prompt(
#             "system",
#             "evaluator_system.txt"
#         )

#         evaluation_prompt = self._load_prompt(
#             "evaluation",
#             "universal_evaluation.txt"
#         )

#         json_template = self._load_prompt(
#             "templates",
#             "json_output_template.txt"
#         )

#         detected_task_type = (
#             request.task_type
#             if request.task_type
#             else "Auto Detect"
#         )

#         question = (
#             request.question
#             if request.question
#             else "Not Provided"
#         )

#         expected_output = (
#             request.expected_output
#             if request.expected_output
#             else "Not Provided"
#         )

#         evaluation_criteria = (
#             request.evaluation_criteria
#             if request.evaluation_criteria
#             else "Not Provided"
#         )

#         scoring_parameters = (
#             request.scoring_parameters
#             if request.scoring_parameters
#             else "Not Provided"
#         )

#         submission_text = (
#             request.submission_text
#             if request.submission_text
#             else "Not Provided"
#         )

#         github_links = (
#             request.github_links
#             if request.github_links
#             else []
#         )

#         image_links = (
#             request.image_links
#             if request.image_links
#             else []
#         )

#         if not extracted_file_content:

#             extracted_file_content = (
#                 "No uploaded file content."
#             )

#         user_prompt = f"""
# TASK TYPE:
# {detected_task_type}

# ==================================================
# QUESTION
# ==================================================

# {question}

# ==================================================
# EXPECTED OUTPUT
# ==================================================

# {expected_output}

# ==================================================
# EVALUATION CRITERIA
# ==================================================

# {evaluation_criteria}

# ==================================================
# SCORING PARAMETERS
# ==================================================

# {scoring_parameters}



# ==================================================
# WRITTEN SUBMISSION
# ==================================================

# {submission_text}

# ==================================================
# GITHUB LINKS
# ==================================================

# {github_links}

# ==================================================
# IMAGE LINKS
# ==================================================

# {image_links}

# ==================================================
# EXTRACTED FILE CONTENT
# ==================================================

# {extracted_file_content}

# IMPORTANT EVALUATION INSTRUCTIONS:

# 1. Evaluate ONLY based on actual evidence.

# Submission may contain:
# - only written answer
# - written answer + PDF
# - written answer + DOCX
# - written answer + GitHub link
# - only ZIP project
# - GitHub + files
# - answer + GitHub + file
# - any combination of evidence

# Evaluate using ALL provided evidence together.

# Do NOT penalize missing GitHub
# if the assignment does not require source code.

# Do NOT penalize missing files
# if written answer sufficiently answers the question.

# If multiple evidence sources exist,
# combine them for final evaluation.

# 2. Compare the submission against:
# - QUESTION
# - EXPECTED OUTPUT
# - EVALUATION CRITERIA
# - SCORING PARAMETERS
# - RUBRIC

# 3. Determine whether the submission
# correctly answers the question.

# 4. Follow instructor-defined
# evaluation criteria strictly.

# 5. Follow scoring parameters strictly.

# 6. Determine whether uploaded files,
# written answers and GitHub links
# support each other consistently.

# 7. DO NOT hallucinate technologies.

# 8. DO NOT mention missing GitHub
# unless source code evaluation
# is actually relevant.

# 9. If submission is a resume:
# - evaluate resume quality
# - technical relevance
# - project quality
# - clarity

# 10. If submission contains source code:
# - evaluate implementation
# - engineering quality
# - maintainability
# - code structure
# - architecture if visible

# 11. If submission contains documentation:
# - evaluate technical clarity
# - implementation understanding
# - explanation quality

# 12. If submission partially answers
# the question:
# - reduce score appropriately

# 13. Weaknesses must be contextual.

# 14. Strengths should not be empty
# if meaningful content exists.

# 15. NEVER generate generic feedback like:
# - "No GitHub provided"

# 16. Feedback must directly relate
# to the actual submission.

# 17. If content is weak or incomplete:
# - reduce score
# - reduce confidence

# 18. Scoring must remain explainable.

# 19. Deductions must align with:
# - evaluation criteria
# - scoring parameters
# - actual evidence

# 20. Evaluate based on evidence quality,
# not evidence quantity.

# {evaluation_prompt}

# IMPORTANT RULES:
# - Generate ONLY valid JSON
# - Do not generate markdown
# - Do not wrap JSON in backticks
# - ai_score must always exist
# - confidence must be between 0 and 1
# - strengths must never be null
# - weaknesses must never be null
# - improvement_suggestions must never be null
# - deductions must never be null
# - skill_breakdown must never be null
# - final_feedback must never be null

# RETURN JSON IN THIS FORMAT:
# {json_template}
# """

#         return (
#             system_prompt,
#             user_prompt
#         )

#     # SAFE LIST

#     def _safe_list(
#         self,
#         value,
#         fallback
#     ):

#         if (
#             isinstance(value, list)
#             and len(value) > 0
#         ):

#             return value

#         return fallback

#     # SAFE FLOAT

#     def _safe_float(
#         self,
#         value,
#         fallback
#     ):

#         try:

#             return float(value)

#         except:

#             return fallback

#     def _manual_review_result(
#         self,
#         request: EvaluationRequest,
#         reason: str,
#         evaluation_version: int = 1,
#         reevaluation_count: int = 0,
#         is_reevaluated: bool = False,
#         reevaluated_at = None,
#         evaluation_duration_seconds: float = 0
#     ) -> EvaluationResult:

#         return EvaluationResult(

#             ai_score=0,

#             confidence=0.0,

#             strengths=[],

#             weaknesses=[],

#             improvement_suggestions=[],

#             final_feedback=(
#                 f"{reason} Submission forwarded "
#                 "for instructor review."
#             ),

#             deductions=[],

#             skill_breakdown=[],

#             provider=None,

#             model=None,

#             prompt_tokens=0,

#             completion_tokens=0,

#             total_tokens=0,

#             evaluation_id=(
#                 f"eval_{int(time.time() * 1000)}"
#             ),

#             evaluation_version=(
#                 evaluation_version
#             ),

#             reevaluation_count=(
#                 reevaluation_count
#             ),

#             previous_evaluation_id=(
#                 request.previous_evaluation_id
#             ),

#             reevaluated_at=(
#                 reevaluated_at
#             ),

#             is_reevaluated=(
#                 is_reevaluated
#             ),

#             prompt_version=(
#                 self.PROMPT_VERSION
#             ),

#             evaluator_version=(
#                 self.EVALUATOR_VERSION
#             ),

#             provider_latency_seconds=0,

#             evaluation_duration_seconds=(
#                 evaluation_duration_seconds
#             ),

#             evaluation_status=(
#                 "manual_review"
#             ),

#             requires_manual_review=True,

#             manual_review_reason=(
#                 reason
#             ),

#             blurry_file_detected=False
#         )

#     # GROQ EVALUATION

#     async def _evaluate_with_provider(
#         self,
#         request: EvaluationRequest,
#         evaluation_version: int = 1,
#         reevaluation_count: int = 0,
#         is_reevaluated: bool = False,
#         reevaluated_at = None
#     ) -> EvaluationResult:

#         evaluation_start_time = time.time()

#         extracted_file_content, extraction_metadata = (
#             await self._extract_uploaded_files(
#                 request
#             )
#         )

#         system_prompt, user_prompt = (
#             self._build_prompt(
#                 request,
#                 extracted_file_content
#             )
#         )

#         complexity = (
#             ModelComplexity.SIMPLE
#         )

#         total_content_length = len(
#             user_prompt
#         )

#         logger.info(
#             (
#                 "Total prompt length: "
#                 f"{total_content_length}"
#             )
#         )

#         if total_content_length > 20000:

#             complexity = (
#                 ModelComplexity.COMPLEX
#             )

#         logger.info(
#             (
#                 "Selected complexity: "
#                 f"{complexity}"
#             )
#         )
#         # SKIP AI EVALUATION
#         # FOR FAILED EXTRACTION

#         if (

#             request.file_paths

#             and (

#                 extraction_metadata[
#                     "extracted_files_count"
#                 ] == 0

#                 or

#                 extraction_metadata[
#                     "extraction_failures_count"
#                 ] > 0

#                 or

#                 extraction_metadata[
#                     "extraction_timeout_count"
#                 ] > 0
#             )
#         ):

#             logger.warning(
#                 (
#                     "Extraction failed. "
#                     "Skipping AI evaluation "
#                     "and forwarding for "
#                     "manual instructor review."
#                 )
#             )

#             evaluation_duration = round(

#                 time.time()
#                 - evaluation_start_time,

#                 2
#             )

#             return EvaluationResult(

#                 ai_score=0,

#                 confidence=0.0,

#                 strengths=[],

#                 weaknesses=[],

#                 improvement_suggestions=[],

#                 final_feedback=(

#                     "Uploaded file is unclear "
#                     "or unreadable. Submission "
#                     "forwarded for instructor "
#                     "review."
#                 ),

#                 deductions=[],

#                 skill_breakdown=[],

#                 provider=None,

#                 model=None,

#                 prompt_tokens=0,

#                 completion_tokens=0,

#                 total_tokens=0,

#                 evaluation_id=(
#                     f"eval_{int(time.time() * 1000)}"
#                 ),

#                 evaluation_version=(
#                     evaluation_version
#                 ),

#                 reevaluation_count=(
#                     reevaluation_count
#                 ),

#                 previous_evaluation_id=(
#                     request.previous_evaluation_id
#                 ),

#                 reevaluated_at=(
#                     reevaluated_at
#                 ),

#                 is_reevaluated=(
#                     is_reevaluated
#                 ),

#                 prompt_version=(
#                     self.PROMPT_VERSION
#                 ),

#                 evaluator_version=(
#                     self.EVALUATOR_VERSION
#                 ),

#                 extracted_files_count=(

#                     extraction_metadata[
#                         "extracted_files_count"
#                     ]
#                 ),

#                 extraction_failures_count=(

#                     extraction_metadata[
#                         "extraction_failures_count"
#                     ]
#                 ),

#                 extraction_timeout_count=(

#                     extraction_metadata[
#                         "extraction_timeout_count"
#                     ]
#                 ),

#                 extraction_duration_seconds=(

#                     extraction_metadata[
#                         "extraction_duration_seconds"
#                     ]
#                 ),

#                 provider_latency_seconds=0,

#                 evaluation_duration_seconds=(
#                     evaluation_duration
#                 ),

#                 evaluation_status=(
#                     "manual_review"
#                 ),

#                 requires_manual_review=True,

#                 manual_review_reason=(

#                     "Uploaded file is unclear "
#                     "or unreadable."
#                 ),

#                 blurry_file_detected=True
#             )

#         provider_start_time = (
#             time.time()
#         )

#         try:

#             provider_response = (
#                 await RetryHandler.retry_async(

#                     self.groq_provider.generate,

#                     prompt=user_prompt,

#                     system_prompt=system_prompt,

#                     complexity=complexity
#                 )
#             )
            
            

#         except Exception as provider_error:

#             logger.exception(
#                 (
#                     "Provider evaluation failed: "
#                     f"{str(provider_error)}"
#                 )
#             )

#             raise

#         provider_latency = round(

#             time.time()
#             - provider_start_time,

#             2
#         )

#         logger.info(
#             (
#                 "Raw provider response received successfully."
#             )
#         )

#         parsed_response = (
#             JSONParser.parse_json(
#                 provider_response.raw_response
#             )
#         )

#         logger.info(
#             "Provider response parsed successfully."
#         )

#         ai_score = self._safe_float(

#             parsed_response.get(
#                 "ai_score"
#             ),

#             10
#         )

#         ai_score = max(
#             10,
#             min(
#                 ai_score,
#                 100
#             )
#         )

#         parsed_response[
#             "ai_score"
#         ] = ai_score

#         parsed_response[
#             "strengths"
#         ] = self._safe_list(

#             parsed_response.get(
#                 "strengths"
#             ),

#             [
#                 (
#                     "Submission contains "
#                     "relevant information."
#                 )
#             ]
#         )

#         parsed_response[
#             "weaknesses"
#         ] = self._safe_list(

#             parsed_response.get(
#                 "weaknesses"
#             ),

#             [
#                 (
#                     "Some areas could benefit "
#                     "from deeper technical detail."
#                 )
#             ]
#         )

#         parsed_response[
#             "improvement_suggestions"
#         ] = self._safe_list(

#             parsed_response.get(
#                 "improvement_suggestions"
#             ),

#             [
#                 (
#                     "Provide more implementation "
#                     "details and technical evidence."
#                 )
#             ]
#         )

#         deductions = parsed_response.get(
#             "deductions"
#         )

#         if not isinstance(
#             deductions,
#             list
#         ):

#             deductions = []

#         parsed_response[
#             "deductions"
#         ] = deductions

#         skill_breakdown = (
#             parsed_response.get(
#                 "skill_breakdown"
#             )
#         )

#         if (
#             not isinstance(
#                 skill_breakdown,
#                 list
#             )
#             or not skill_breakdown
#         ):

#             skill_breakdown = [
#                 {
#                     "skill": (
#                         "Technical Understanding"
#                     ),
#                     "score": ai_score
#                 }
#             ]

#         parsed_response[
#             "skill_breakdown"
#         ] = skill_breakdown

#         confidence = self._safe_float(

#             parsed_response.get(
#                 "confidence"
#             ),

#             0.5
#         )

#         confidence = max(
#             0.1,
#             min(
#                 confidence,
#                 1.0
#             )
#         )

#         parsed_response[
#             "confidence"
#         ] = confidence
#         # MANUAL REVIEW DETECTION

#         requires_manual_review = False

#         manual_review_reason = None

#         blurry_file_detected = False

#         # LOW CONFIDENCE

#         if confidence < 0.5:

#             requires_manual_review = True

#             manual_review_reason = (
#                 "Low confidence evaluation."
#             )

#         # EXTRACTION FAILURES

        
#         if (

#             request.file_paths

#             and (

#                 extraction_metadata[
#                     "extracted_files_count"
#                 ] == 0

#                 or

#                 extraction_metadata[
#                     "extraction_failures_count"
#                 ] > 0
#             )
#         ):

#             requires_manual_review = True

#             blurry_file_detected = True

#             manual_review_reason = (
#                 "Uploaded file is unclear "
#                 "or unreadable."
#             )

#         # TIMEOUT FAILURES

#         if (
#             extraction_metadata[
#                 "extraction_timeout_count"
#             ] > 0
#         ):

#             requires_manual_review = True

#             manual_review_reason = (
#                 "File extraction timeout occurred."
#             )

#         # HIDE AI SCORE
#         # FOR LOW CONFIDENCE

#         if requires_manual_review:

#             parsed_response[
#                 "ai_score"
#             ] = 0

#             parsed_response[
#                 "strengths"
#             ] = []

#             parsed_response[
#                 "weaknesses"
#             ] = []

#             parsed_response[
#                 "improvement_suggestions"
#             ] = []

#             parsed_response[
#                 "skill_breakdown"
#             ] = []

#             parsed_response[
#                 "final_feedback"
#             ] = (
#                 manual_review_reason
#                 + " Submission forwarded "
#                 "for instructor review."
#             )

#         final_feedback = (
#             parsed_response.get(
#                 "final_feedback"
#             )
#         )

#         if (
#             not isinstance(
#                 final_feedback,
#                 str
#             )
#             or not final_feedback.strip()
#         ):

#             final_feedback = (
#                 "Evaluation completed successfully."
#             )

#         parsed_response[
#             "final_feedback"
#         ] = final_feedback

#         evaluation_duration = (
#             round(
#                 time.time()
#                 - evaluation_start_time,
#                 2
#             )
#         )

#         logger.info(
#             (
#                 "Evaluation completed in "
#                 f"{evaluation_duration} seconds"
#             )
#         )

#         return EvaluationResult(

#             **parsed_response,

#             provider=(
#                 provider_response.provider
#             ),

#             model=(
#                 provider_response.model
#             ),

#             prompt_tokens=(
#                 provider_response.prompt_tokens
#             ),

#             completion_tokens=(
#                 provider_response.completion_tokens
#             ),

#             total_tokens=(
#                 provider_response.total_tokens
#             ),

#             evaluation_id=(
#                 f"eval_{int(time.time() * 1000)}"
#             ),

#             evaluation_version=(
#                 evaluation_version
#             ),

#             reevaluation_count=(
#                 reevaluation_count
#             ),

#             previous_evaluation_id=(
#                 request.previous_evaluation_id
#             ),

#             reevaluated_at=(
#                 reevaluated_at
#             ),

#             is_reevaluated=(
#                 is_reevaluated
#             ),

#             prompt_version=(
#                 self.PROMPT_VERSION
#             ),

#             evaluator_version=(
#                 self.EVALUATOR_VERSION
#             ),

#             extracted_files_count=(
#                 extraction_metadata[
#                     "extracted_files_count"
#                 ]
#             ),

#             extraction_failures_count=(
#                 extraction_metadata[
#                     "extraction_failures_count"
#                 ]
#             ),

#             extraction_timeout_count=(
#                 extraction_metadata[
#                     "extraction_timeout_count"
#                 ]
#             ),

#             extraction_duration_seconds=(
#                 extraction_metadata[
#                     "extraction_duration_seconds"
#                 ]
#             ),

#             provider_latency_seconds=(
#                 provider_latency
#             ),

#             evaluation_duration_seconds=(
#                 evaluation_duration
#             ),

#             evaluation_status=(

#                 "manual_review"

#                 if requires_manual_review

#                 else "completed"
#             ),

#             requires_manual_review=(
#                 requires_manual_review
#             ),

#             manual_review_reason=(
#                 manual_review_reason
#             ),

#             blurry_file_detected=(
#                 blurry_file_detected
#             )
            
#         )

#     # MAIN EVALUATION

#     async def evaluate(
#         self,
#         request: EvaluationRequest,
#         requires_gemini: bool,
#         requires_groq: bool
#     ) -> EvaluationResult:

#         SubmissionValidator.validate_submission(
#             request
#         )

       

#         logger.info(
#             "Starting evaluation"
#         )

#         evaluation_start_time = (
#             time.time()
#         )

#         # REEVALUATION LOOKUP

#         previous_evaluation = None

#         evaluation_version = 1

#         reevaluation_count = 0

#         is_reevaluated = False

#         reevaluated_at = None

#         if request.previous_evaluation_id:

#             previous_evaluation = (
#                 await EvaluationRepository
#                 .get_evaluation_by_id(
#                     request.previous_evaluation_id
#                 )
#             )

#             if previous_evaluation:

#                 previous_result = (
#                     previous_evaluation.result_data
#                 )

#                 evaluation_version = (

#                     previous_result.get(
#                         "evaluation_version",
#                         1
#                     ) + 1
#                 )

#                 reevaluation_count = (

#                     previous_result.get(
#                         "reevaluation_count",
#                         0
#                     ) + 1
#                 )

#                 is_reevaluated = True

#                 reevaluated_at = (
#                     datetime.utcnow()
#                 )

#                 logger.info(
#                     (
#                         "Reevaluation detected | "
#                         f"Previous Evaluation ID: "
#                         f"{request.previous_evaluation_id}"
#                     )
#                 )

#         try:

#             groq_result = (
#                 await self._evaluate_with_provider(

#                     request=request,

#                     evaluation_version=(
#                         evaluation_version
#                     ),

#                     reevaluation_count=(
#                         reevaluation_count
#                     ),

#                     is_reevaluated=(
#                         is_reevaluated
#                     ),

#                     reevaluated_at=(
#                         reevaluated_at
#                     )
#                 )
#             )
            
#             # AUTO REEVALUATION
#             # FOR SUSPICIOUS LOW SCORES

#             if (
#                 groq_result.ai_score <= 10

#                 and not groq_result
#                 .requires_manual_review
#             ):

#                 logger.warning(
#                     (
#                         "Suspicious low score detected. "
#                         "Starting automatic reevaluation."
#                     )
#                 )
#                 reevaluated_result = (
#                     await self._evaluate_with_provider(

#                         request=request,

#                         evaluation_version=(
#                             evaluation_version + 1
#                         ),

#                         reevaluation_count=1,

#                         is_reevaluated=True,

#                         reevaluated_at=(
#                             datetime.utcnow()
#                         )
#                     )
#                 )

#                 reevaluated_result.reevaluation_count = 1

#                 reevaluated_result.previous_evaluation_id = (
#                     groq_result.evaluation_id
#                 )

#                 reevaluated_result.is_reevaluated = True

#                 reevaluated_result.reevaluation_reason = (
#                     "Automatic reevaluation "
#                     "triggered due to very low score."
#                 )

#                 # USE BETTER SCORE

#                 if (
#                     reevaluated_result.ai_score
#                     > groq_result.ai_score
#                 ):

#                     logger.info(
#                         (
#                             "Reevaluation improved score "
#                             f"from {groq_result.ai_score} "
#                             f"to "
#                             f"{reevaluated_result.ai_score}"
#                         )
#                     )

#                     groq_result = (
#                         reevaluated_result
#                     )

#                 else:

#                     logger.warning(
#                         (
#                             "Reevaluation did not improve "
#                             "score significantly."
#                         )
#                     )
#                     if reevaluated_result.ai_score <= 10:

#                         groq_result.requires_manual_review = True

#                         groq_result.manual_review_reason = (
#                             "Repeated low score detected "
#                             "after automatic reevaluation."
#                         )

#                         groq_result.evaluation_status = (
#                             "manual_review"
#                         )

#                         groq_result.final_feedback = (
#                             "Evaluation confidence is too low. "
#                             "Submission forwarded for "
#                             "instructor review."
#                         )

#                         groq_result.ai_score = 0

#                         groq_result.strengths = []

#                         groq_result.weaknesses = []

#                         groq_result.improvement_suggestions = []

#                         groq_result.skill_breakdown = []

#         except Exception as evaluation_error:

#             logger.exception(
#                 (
#                     "Evaluation pipeline failed. "
#                     "Forwarding to manual review: "
#                     f"{str(evaluation_error)}"
#                 )
#             )

#             evaluation_duration = round(

#                 time.time()
#                 - evaluation_start_time,

#                 2
#             )

#             groq_result = (
#                 self._manual_review_result(

#                     request=request,

#                     reason=(
#                         "AI provider is temporarily "
#                         "unavailable or failed to "
#                         "complete the evaluation."
#                     ),

#                     evaluation_version=(
#                         evaluation_version
#                     ),

#                     reevaluation_count=(
#                         reevaluation_count
#                     ),

#                     is_reevaluated=(
#                         is_reevaluated
#                     ),

#                     reevaluated_at=(
#                         reevaluated_at
#                     ),

#                     evaluation_duration_seconds=(
#                         evaluation_duration
#                     )
#                 )
#             )

#         logger.info(
#             "Evaluation completed"
#         )

#         evaluation_results = [
#             groq_result
#         ]

#         final_result_data = (
#             AggregationService.aggregate_results(
#                 evaluation_results
#             )
#         )

#         final_result_data.update({

#             "evaluation_id": (
#                 groq_result.evaluation_id
#             ),

#             "evaluation_version": (
#                 groq_result.evaluation_version
#             ),

#             "reevaluation_count": (
#                 groq_result.reevaluation_count
#             ),

#             "previous_evaluation_id": (
#                 groq_result.previous_evaluation_id
#             ),

#             "is_reevaluated": (
#                 groq_result.is_reevaluated
#             ),

#             "reevaluated_at": (
#                 groq_result.reevaluated_at
#             ),

#             "prompt_version": (
#                 groq_result.prompt_version
#             ),

#             "evaluator_version": (
#                 groq_result.evaluator_version
#             ),

#             "prompt_tokens": (
#                 groq_result.prompt_tokens
#             ),

#             "completion_tokens": (
#                 groq_result.completion_tokens
#             ),

#             "total_tokens": (
#                 groq_result.total_tokens
#             ),

#             "final_feedback": (
#                 groq_result.final_feedback
#             ),

#             "extracted_files_count": (
#                 groq_result.extracted_files_count
#             ),

#             "extraction_failures_count": (
#                 groq_result
#                 .extraction_failures_count
#             ),

#             "extraction_timeout_count": (
#                 groq_result
#                 .extraction_timeout_count
#             ),

#             "extraction_duration_seconds": (
#                 groq_result
#                 .extraction_duration_seconds
#             ),

#             "provider_latency_seconds": (
#                 groq_result
#                 .provider_latency_seconds
#             ),

#             "evaluation_duration_seconds": (
#                 groq_result
#                 .evaluation_duration_seconds
#             ),

#             "evaluation_status": (
#                 groq_result.evaluation_status
#             ),
#             "requires_manual_review": (
#                 groq_result.requires_manual_review
#             ),

#             "manual_review_reason": (
#                 groq_result.manual_review_reason
#             ),

#             "blurry_file_detected": (
#                 groq_result.blurry_file_detected
#             ),
            
#         })

#         evaluation_result = (
#             EvaluationResult(
#                 **final_result_data
#             )
#         )

#         await EvaluationRepository.save_evaluation(

#             request_data=(
#                 request.model_dump()
#             ),

#             evaluation_result=(
#                 evaluation_result
#             )
#         )

#         await AuditRepository.log_event(

#             event_type=(
#                 "evaluation_completed"
#             ),

#             details={

#                 "evaluation_id": (
#                     evaluation_result
#                     .evaluation_id
#                 ),

#                 "providers": (
#                     final_result_data.get(
#                         "provider"
#                     )
#                 ),

#                 "models": (
#                     final_result_data.get(
#                         "model"
#                     )
#                 ),

#                 "score": (
#                     final_result_data.get(
#                         "ai_score"
#                     )
#                 ),

#                 "is_reevaluated": (
#                     evaluation_result
#                     .is_reevaluated
#                 ),

#                 "evaluation_version": (
#                     evaluation_result
#                     .evaluation_version
#                 )
#             }
#         )

#         return evaluation_result
import os
import time
import asyncio

from pathlib import Path

from datetime import datetime

from app.providers.groq_provider import (
    GroqProvider
)

from app.schemas.evaluation import (
    EvaluationResult
)

from app.schemas.request import (
    EvaluationRequest
)

from app.validators.submission_validator import (
    SubmissionValidator
)

from app.utils.json_parser import (
    JSONParser
)

from app.utils.retry import (
    RetryHandler
)
from app.repositories.evaluation_repository import (
    EvaluationRepository
)

from app.repositories.audit_repository import (
    AuditRepository
)

from app.services.aggregation import (
    AggregationService
)
from app.utils.file_downloader import (
    FileDownloader
)

from app.extractors.file_extractor import (
    FileExtractor
)

from app.logging.logger import (
    get_logger
)

from app.core.enums import (
    ModelComplexity
)


logger = get_logger(
    "evaluation_service"
)


class EvaluationService:

    # CONFIG

    MAX_TOTAL_CONTENT = 35000

    MAX_FILE_CONTENT = 20000

    EXTRACTION_TIMEOUT_SECONDS = 30

    MAX_CONCURRENT_EXTRACTIONS = 3
    
    SUMMARY_TRIGGER_LENGTH = 8000

    SUMMARY_MAX_OUTPUT = 5000

    PROMPT_VERSION = "v1"

    EVALUATOR_VERSION = "v1"

    def __init__(self):

        self.groq_provider = (
            GroqProvider()
        )
        self.base_prompt_path = Path(
            "prompts"
        )

    # LOAD PROMPTS

    def _load_prompt(
        self,
        category: str,
        filename: str
    ) -> str:

        prompt_path = (
            self.base_prompt_path
            / category
            / filename
        )

        with open(
            prompt_path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    # SAFE FILE EXTRACTION
    async def _summarize_large_content(
        self,
        content: str
    ) -> str:

        try:

            logger.info(
                "Starting large content summarization."
            )
            content = content[:15000]

            summary_prompt = f"""
            You are a technical summarization AI.

            Summarize the following student submission.

            IMPORTANT:
            - Preserve important implementation details
            - Preserve architecture
            - Preserve APIs
            - Preserve technical decisions
            - Preserve business logic
            - Preserve important algorithms
            - Preserve project structure
            - Preserve technologies used
            - Preserve database details
            - Preserve deployment details
            - Preserve evaluation-relevant information

            DO NOT:
            - Add hallucinations
            - Add assumptions
            - Remove important technical content
            - Generate generic summaries

            Generate a concise but technically complete summary.

            CONTENT:
            {content}
            """

            response = await self.groq_provider.generate(

                prompt=summary_prompt,

                system_prompt=(
                    "You are an expert technical summarizer."
                ),

                complexity=(
                    ModelComplexity.SIMPLE
                )
            )

            summarized_content = (
                response.raw_response.strip()
            )

            summarized_content = (
                summarized_content[
                    :self.SUMMARY_MAX_OUTPUT
                ]
            )

            logger.info(
                (
                    "Content summarization completed | "
                    f"Original Length: {len(content)} | "
                    f"Summary Length: "
                    f"{len(summarized_content)}"
                )
            )

            return summarized_content

        except Exception as error:

            logger.exception(
                (
                    "Content summarization failed: "
                    f"{str(error)}"
                )
            )

            return content[
                :self.SUMMARY_MAX_OUTPUT
            ]

    async def _safe_extract_file(
        self,
        file_path: str,
        semaphore: asyncio.Semaphore
    ) -> dict:

        async with semaphore:

            extraction_start_time = (
                time.time()
            )

            try:

                logger.info(
                    (
                        "Starting extraction for file: "
                        f"{file_path}"
                    )
                )
                
                local_file_path = file_path

                # DOWNLOAD S3 PRESIGNED URL

                if (
                    str(file_path).startswith("http://")
                    or str(file_path).startswith("https://")
                ):

                    logger.info(
                        (
                            "Downloading remote file: "
                            f"{file_path}"
                        )
                    )

                    downloaded_file = (
                        await FileDownloader.download_file(
                            file_path
                        )
                    )

                    if not downloaded_file:

                        return {

                            "file_path": file_path,

                            "content": "",

                            "success": False,

                            "warning": (
                                "Failed to download remote file."
                            ),

                            "blurry_detected": False,

                            "timeout": False,

                            "duration": None
                        }

                    local_file_path = downloaded_file

                # EXTRACT FILE

                extracted_content = (
                    await asyncio.wait_for(

                        asyncio.to_thread(
                            FileExtractor.extract,
                            local_file_path
                        ),

                        timeout=(
                            self
                            .EXTRACTION_TIMEOUT_SECONDS
                        )
                    )
                )
                extracted_text = extracted_content.get(
                    "text",
                    ""
                )

                extraction_success = extracted_content.get(
                    "success",
                    False
                )

                extraction_warning = extracted_content.get(
                    "warning"
                )

                blurry_detected = extracted_content.get(
                    "blurry_detected",
                    False
                )
                

                extraction_duration = round(

                    time.time()
                    - extraction_start_time,

                    2
                )

                logger.info(
                    (
                        "Extraction completed | "
                        f"File: {file_path} | "
                        f"Duration: "
                        f"{extraction_duration}s"
                    )
                )

                
                return {

                    "file_path": file_path,

                    "content": (
                        extracted_text or ""
                    ),

                    "success": (
                        extraction_success
                        and bool(extracted_text)
                    ),

                    "warning": extraction_warning,

                    "blurry_detected": blurry_detected,

                    "timeout": False,

                    "duration": (
                        extraction_duration
                    )
               }

            except asyncio.TimeoutError:

                logger.exception(
                    (
                        "File extraction timeout exceeded for: "
                        f"{file_path}"
                    )
                )

                return {

                    "file_path": file_path,

                    "content": "",

                    "success": False,

                    "timeout": True,

                    "duration": None
                }

            except Exception as error:

                logger.exception(
                    (
                        "File extraction failed: "
                        f"{str(error)}"
                    )
                )

                return {

                    "file_path": file_path,

                    "content": "",

                    "success": False,

                    "timeout": False,

                    "duration": None
                }

            finally:

                # DELETE TEMP FILE

                try:

                    
                    if (
                        'local_file_path' in locals()
                        and local_file_path
                        and os.path.exists(local_file_path)
                    ):

                        os.remove(
                            local_file_path
                        )

                        logger.info(
                            (
                                "Temporary uploaded "
                                f"file deleted: {local_file_path}"
                            )
                        )

                except Exception as cleanup_error:

                    logger.exception(
                        (
                            "Failed to delete "
                            "temporary file: "
                            f"{str(cleanup_error)}"
                        )
                    )

    # EXTRACT FILE CONTENT

    async def _extract_uploaded_files(
        self,
        request: EvaluationRequest
    ) -> tuple[str, dict]:

        combined_content = ""

        extraction_failures_count = 0

        extraction_timeout_count = 0

        extracted_files_count = 0

        extraction_start_time = (
            time.time()
        )

        semaphore = asyncio.Semaphore(
            self.MAX_CONCURRENT_EXTRACTIONS
        )

        extraction_tasks = [

            self._safe_extract_file(
                file_path=file_path,
                semaphore=semaphore
            )

            for file_path in request.file_paths
        ]

        extraction_results = (
            await asyncio.gather(
                *extraction_tasks
            )
        )

        for result in extraction_results:

            file_path = result[
                "file_path"
            ]

            extracted_content = result[
                "content"
            ]

            success = result[
                "success"
            ]

            timeout = result[
                "timeout"
            ]

            if timeout:

                extraction_timeout_count += 1

            if not success:

                extraction_failures_count += 1

            if not extracted_content:

                logger.warning(
                    (
                        "No content extracted "
                        f"from: {file_path}"
                    )
                )

                continue

            extracted_files_count += 1

            extracted_content = (
                extracted_content[
                    :self.MAX_FILE_CONTENT
                ]
            )

            file_section = f"""

==================================================
FILE NAME: {Path(file_path).name}
FILE TYPE: {Path(file_path).suffix}
==================================================

{extracted_content}

"""

            if len(
                combined_content + file_section
            ) > (
                self.MAX_TOTAL_CONTENT
            ):

                logger.warning(
                    (
                        "Maximum extracted "
                        "content limit reached."
                    )
                )

                break

            combined_content += (
                file_section
            )

        extraction_duration = round(

            time.time()
            - extraction_start_time,

            2
        )

        extraction_metadata = {

            "extracted_files_count": (
                extracted_files_count
            ),

            "extraction_failures_count": (
                extraction_failures_count
            ),

            "extraction_timeout_count": (
                extraction_timeout_count
            ),

            "extraction_duration_seconds": (
                extraction_duration
            )
        }

        return (
            combined_content.strip(),
            extraction_metadata
        )

    # BUILD PROMPT

    def _build_prompt(
        self,
        request: EvaluationRequest,
        extracted_file_content: str
    ) -> tuple[str, str]:

        system_prompt = self._load_prompt(
            "system",
            "evaluator_system.txt"
        )

        evaluation_prompt = self._load_prompt(
            "evaluation",
            "universal_evaluation.txt"
        )

        json_template = self._load_prompt(
            "templates",
            "json_output_template.txt"
        )

        detected_task_type = (
            request.task_type
            if request.task_type
            else "Auto Detect"
        )

        question = (
            request.question
            if request.question
            else "Not Provided"
        )

        expected_output = (
            request.expected_output
            if request.expected_output
            else "Not Provided"
        )

        evaluation_criteria = (
            request.evaluation_criteria
            if request.evaluation_criteria
            else "Not Provided"
        )

        scoring_parameters = (
            request.scoring_parameters
            if request.scoring_parameters
            else "Not Provided"
        )

        submission_text = (
            request.submission_text
            if request.submission_text
            else "Not Provided"
        )

        github_links = (
            request.github_links
            if request.github_links
            else []
        )

        image_links = (
            request.image_links
            if request.image_links
            else []
        )

        if not extracted_file_content:

            extracted_file_content = (
                "No uploaded file content."
            )

        user_prompt = f"""
TASK TYPE:
{detected_task_type}

==================================================
QUESTION
==================================================

{question}

==================================================
EXPECTED OUTPUT
==================================================

{expected_output}

==================================================
EVALUATION CRITERIA
==================================================

{evaluation_criteria}

==================================================
SCORING PARAMETERS
==================================================

{scoring_parameters}



==================================================
WRITTEN SUBMISSION
==================================================

{submission_text}

==================================================
GITHUB LINKS
==================================================

{github_links}

==================================================
IMAGE LINKS
==================================================

{image_links}

==================================================
EXTRACTED FILE CONTENT
==================================================

{extracted_file_content}

IMPORTANT EVALUATION INSTRUCTIONS:

1. Evaluate ONLY based on actual evidence.

Submission may contain:
- only written answer
- written answer + PDF
- written answer + DOCX
- written answer + GitHub link
- only ZIP project
- GitHub + files
- answer + GitHub + file
- any combination of evidence

Evaluate using ALL provided evidence together.

Do NOT penalize missing GitHub
if the assignment does not require source code.

Do NOT penalize missing files
if written answer sufficiently answers the question.

If multiple evidence sources exist,
combine them for final evaluation.

2. Compare the submission against:
- QUESTION
- EXPECTED OUTPUT
- EVALUATION CRITERIA
- SCORING PARAMETERS
- RUBRIC

3. Determine whether the submission
correctly answers the question.

4. Follow instructor-defined
evaluation criteria strictly.

5. Follow scoring parameters strictly.

6. Determine whether uploaded files,
written answers and GitHub links
support each other consistently.

7. DO NOT hallucinate technologies.

8. DO NOT mention missing GitHub
unless source code evaluation
is actually relevant.

9. If submission is a resume:
- evaluate resume quality
- technical relevance
- project quality
- clarity

10. If submission contains source code:
- evaluate implementation
- engineering quality
- maintainability
- code structure
- architecture if visible

11. If submission contains documentation:
- evaluate technical clarity
- implementation understanding
- explanation quality

12. If submission partially answers
the question:
- reduce score appropriately

13. Weaknesses must be contextual.

14. Strengths should not be empty
if meaningful content exists.

15. NEVER generate generic feedback like:
- "No GitHub provided"

16. Feedback must directly relate
to the actual submission.

17. If content is weak or incomplete:
- reduce score
- reduce confidence

18. Scoring must remain explainable.

19. Deductions must align with:
- evaluation criteria
- scoring parameters
- actual evidence

20. Evaluate based on evidence quality,
not evidence quantity.

{evaluation_prompt}

IMPORTANT RULES:
- Generate ONLY valid JSON
- Do not generate markdown
- Do not wrap JSON in backticks
- ai_score must always exist
- confidence must be between 0 and 1
- strengths must never be null
- weaknesses must never be null
- improvement_suggestions must never be null
- deductions must never be null
- skill_breakdown must never be null
- final_feedback must never be null

RETURN JSON IN THIS FORMAT:
{json_template}
"""

        return (
            system_prompt,
            user_prompt
        )

    # SAFE LIST

    def _safe_list(
        self,
        value,
        fallback
    ):

        if (
            isinstance(value, list)
            and len(value) > 0
        ):

            return value

        return fallback

    # SAFE FLOAT

    def _safe_float(
        self,
        value,
        fallback
    ):

        try:

            return float(value)

        except:

            return fallback

    def _manual_review_result(
        self,
        request: EvaluationRequest,
        reason: str,
        evaluation_version: int = 1,
        reevaluation_count: int = 0,
        is_reevaluated: bool = False,
        reevaluated_at = None,
        evaluation_duration_seconds: float = 0
    ) -> EvaluationResult:

        return EvaluationResult(

            ai_score=0,

            confidence=0.0,

            strengths=[],

            weaknesses=[],

            improvement_suggestions=[],

            final_feedback=(
                f"{reason} Submission forwarded "
                "for instructor review."
            ),

            deductions=[],

            skill_breakdown=[],

            provider=None,

            model=None,

            prompt_tokens=0,

            completion_tokens=0,

            total_tokens=0,

            evaluation_id=(
                f"eval_{int(time.time() * 1000)}"
            ),

            evaluation_version=(
                evaluation_version
            ),

            reevaluation_count=(
                reevaluation_count
            ),

            previous_evaluation_id=(
                request.previous_evaluation_id
            ),

            reevaluated_at=(
                reevaluated_at
            ),

            is_reevaluated=(
                is_reevaluated
            ),

            prompt_version=(
                self.PROMPT_VERSION
            ),

            evaluator_version=(
                self.EVALUATOR_VERSION
            ),

            provider_latency_seconds=0,

            evaluation_duration_seconds=(
                evaluation_duration_seconds
            ),

            evaluation_status=(
                "manual_review"
            ),

            requires_manual_review=True,

            manual_review_reason=(
                reason
            ),

            blurry_file_detected=False
        )

    # GROQ EVALUATION

    async def _evaluate_with_provider(
        self,
        request: EvaluationRequest,
        evaluation_version: int = 1,
        reevaluation_count: int = 0,
        is_reevaluated: bool = False,
        reevaluated_at = None
    ) -> EvaluationResult:

        evaluation_start_time = time.time()

        extracted_file_content, extraction_metadata = (
            await self._extract_uploaded_files(
                request
            )
        )
        if (
            len(extracted_file_content)
            > self.SUMMARY_TRIGGER_LENGTH
        ):

            logger.info(
                (
                    "Large extracted content detected. "
                    "Starting summarization."
                )
            )

            extracted_file_content = (
                await self._summarize_large_content(
                    extracted_file_content
                )
            )

        system_prompt, user_prompt = (
            self._build_prompt(
                request,
                extracted_file_content
            )
        )

        complexity = (
            ModelComplexity.SIMPLE
        )

        total_content_length = len(
            user_prompt
        )

        logger.info(
            (
                "Total prompt length: "
                f"{total_content_length}"
            )
        )

        if total_content_length > 20000:

            complexity = (
                ModelComplexity.COMPLEX
            )

        logger.info(
            (
                "Selected complexity: "
                f"{complexity}"
            )
        )
        # SKIP AI EVALUATION
        # FOR FAILED EXTRACTION

        if (

            request.file_paths

            and (

                extraction_metadata[
                    "extracted_files_count"
                ] == 0

                or

                extraction_metadata[
                    "extraction_failures_count"
                ] > 0

                or

                extraction_metadata[
                    "extraction_timeout_count"
                ] > 0
            )
        ):

            logger.warning(
                (
                    "Extraction failed. "
                    "Skipping AI evaluation "
                    "and forwarding for "
                    "manual instructor review."
                )
            )

            evaluation_duration = round(

                time.time()
                - evaluation_start_time,

                2
            )

            return EvaluationResult(

                ai_score=0,

                confidence=0.0,

                strengths=[],

                weaknesses=[],

                improvement_suggestions=[],

                final_feedback=(

                    "Uploaded file is unclear "
                    "or unreadable. Submission "
                    "forwarded for instructor "
                    "review."
                ),

                deductions=[],

                skill_breakdown=[],

                provider=None,

                model=None,

                prompt_tokens=0,

                completion_tokens=0,

                total_tokens=0,

                evaluation_id=(
                    f"eval_{int(time.time() * 1000)}"
                ),

                evaluation_version=(
                    evaluation_version
                ),

                reevaluation_count=(
                    reevaluation_count
                ),

                previous_evaluation_id=(
                    request.previous_evaluation_id
                ),

                reevaluated_at=(
                    reevaluated_at
                ),

                is_reevaluated=(
                    is_reevaluated
                ),

                prompt_version=(
                    self.PROMPT_VERSION
                ),

                evaluator_version=(
                    self.EVALUATOR_VERSION
                ),

                extracted_files_count=(

                    extraction_metadata[
                        "extracted_files_count"
                    ]
                ),

                extraction_failures_count=(

                    extraction_metadata[
                        "extraction_failures_count"
                    ]
                ),

                extraction_timeout_count=(

                    extraction_metadata[
                        "extraction_timeout_count"
                    ]
                ),

                extraction_duration_seconds=(

                    extraction_metadata[
                        "extraction_duration_seconds"
                    ]
                ),

                provider_latency_seconds=0,

                evaluation_duration_seconds=(
                    evaluation_duration
                ),

                evaluation_status=(
                    "manual_review"
                ),

                requires_manual_review=True,

                manual_review_reason=(

                    "Uploaded file is unclear "
                    "or unreadable."
                ),

                blurry_file_detected=True
            )

        provider_start_time = (
            time.time()
        )

        try:

            provider_response = (
                await RetryHandler.retry_async(

                    self.groq_provider.generate,

                    prompt=user_prompt,

                    system_prompt=system_prompt,

                    complexity=complexity
                )
            )
            
            

        except Exception as provider_error:

            logger.exception(
                (
                    "Provider evaluation failed: "
                    f"{str(provider_error)}"
                )
            )

            raise

        provider_latency = round(

            time.time()
            - provider_start_time,

            2
        )

        logger.info(
            (
                "Raw provider response received successfully."
            )
        )

        parsed_response = (
            JSONParser.parse_json(
                provider_response.raw_response
            )
        )

        logger.info(
            "Provider response parsed successfully."
        )

        ai_score = self._safe_float(

            parsed_response.get(
                "ai_score"
            ),

            10
        )

        ai_score = max(
            10,
            min(
                ai_score,
                100
            )
        )

        parsed_response[
            "ai_score"
        ] = ai_score

        parsed_response[
            "strengths"
        ] = self._safe_list(

            parsed_response.get(
                "strengths"
            ),

            [
                (
                    "Submission contains "
                    "relevant information."
                )
            ]
        )

        parsed_response[
            "weaknesses"
        ] = self._safe_list(

            parsed_response.get(
                "weaknesses"
            ),

            [
                (
                    "Some areas could benefit "
                    "from deeper technical detail."
                )
            ]
        )

        parsed_response[
            "improvement_suggestions"
        ] = self._safe_list(

            parsed_response.get(
                "improvement_suggestions"
            ),

            [
                (
                    "Provide more implementation "
                    "details and technical evidence."
                )
            ]
        )

        deductions = parsed_response.get(
            "deductions"
        )

        if not isinstance(
            deductions,
            list
        ):

            deductions = []

        parsed_response[
            "deductions"
        ] = deductions

        skill_breakdown = (
            parsed_response.get(
                "skill_breakdown"
            )
        )

        if (
            not isinstance(
                skill_breakdown,
                list
            )
            or not skill_breakdown
        ):

            skill_breakdown = [
                {
                    "skill": (
                        "Technical Understanding"
                    ),
                    "score": ai_score
                }
            ]

        parsed_response[
            "skill_breakdown"
        ] = skill_breakdown

        confidence = self._safe_float(

            parsed_response.get(
                "confidence"
            ),

            0.5
        )

        confidence = max(
            0.1,
            min(
                confidence,
                1.0
            )
        )

        parsed_response[
            "confidence"
        ] = confidence
        # MANUAL REVIEW DETECTION

        requires_manual_review = False

        manual_review_reason = None

        blurry_file_detected = False

        # LOW CONFIDENCE

        if confidence < 0.5:

            requires_manual_review = True

            manual_review_reason = (
                "Low confidence evaluation."
            )

        # EXTRACTION FAILURES

        
        if (

            request.file_paths

            and (

                extraction_metadata[
                    "extracted_files_count"
                ] == 0

                or

                extraction_metadata[
                    "extraction_failures_count"
                ] > 0
            )
        ):

            requires_manual_review = True

            blurry_file_detected = True

            manual_review_reason = (
                "Uploaded file is unclear "
                "or unreadable."
            )

        # TIMEOUT FAILURES

        if (
            extraction_metadata[
                "extraction_timeout_count"
            ] > 0
        ):

            requires_manual_review = True

            manual_review_reason = (
                "File extraction timeout occurred."
            )

        # HIDE AI SCORE
        # FOR LOW CONFIDENCE

        if requires_manual_review:

            parsed_response[
                "ai_score"
            ] = 0

            parsed_response[
                "strengths"
            ] = []

            parsed_response[
                "weaknesses"
            ] = []

            parsed_response[
                "improvement_suggestions"
            ] = []

            parsed_response[
                "skill_breakdown"
            ] = []

            parsed_response[
                "final_feedback"
            ] = (
                manual_review_reason
                + " Submission forwarded "
                "for instructor review."
            )

        final_feedback = (
            parsed_response.get(
                "final_feedback"
            )
        )

        if (
            not isinstance(
                final_feedback,
                str
            )
            or not final_feedback.strip()
        ):

            final_feedback = (
                "Evaluation completed successfully."
            )

        parsed_response[
            "final_feedback"
        ] = final_feedback

        evaluation_duration = (
            round(
                time.time()
                - evaluation_start_time,
                2
            )
        )

        logger.info(
            (
                "Evaluation completed in "
                f"{evaluation_duration} seconds"
            )
        )

        return EvaluationResult(

            **parsed_response,

            provider=(
                provider_response.provider
            ),

            model=(
                provider_response.model
            ),

            prompt_tokens=(
                provider_response.prompt_tokens
            ),

            completion_tokens=(
                provider_response.completion_tokens
            ),

            total_tokens=(
                provider_response.total_tokens
            ),

            evaluation_id=(
                f"eval_{int(time.time() * 1000)}"
            ),

            evaluation_version=(
                evaluation_version
            ),

            reevaluation_count=(
                reevaluation_count
            ),

            previous_evaluation_id=(
                request.previous_evaluation_id
            ),

            reevaluated_at=(
                reevaluated_at
            ),

            is_reevaluated=(
                is_reevaluated
            ),

            prompt_version=(
                self.PROMPT_VERSION
            ),

            evaluator_version=(
                self.EVALUATOR_VERSION
            ),

            extracted_files_count=(
                extraction_metadata[
                    "extracted_files_count"
                ]
            ),

            extraction_failures_count=(
                extraction_metadata[
                    "extraction_failures_count"
                ]
            ),

            extraction_timeout_count=(
                extraction_metadata[
                    "extraction_timeout_count"
                ]
            ),

            extraction_duration_seconds=(
                extraction_metadata[
                    "extraction_duration_seconds"
                ]
            ),

            provider_latency_seconds=(
                provider_latency
            ),

            evaluation_duration_seconds=(
                evaluation_duration
            ),

            evaluation_status=(

                "manual_review"

                if requires_manual_review

                else "completed"
            ),

            requires_manual_review=(
                requires_manual_review
            ),

            manual_review_reason=(
                manual_review_reason
            ),

            blurry_file_detected=(
                blurry_file_detected
            )
            
        )

    # MAIN EVALUATION

    async def evaluate(
        self,
        request: EvaluationRequest,
        requires_gemini: bool,
        requires_groq: bool
    ) -> EvaluationResult:

        SubmissionValidator.validate_submission(
            request
        )

       

        logger.info(
            "Starting evaluation"
        )

        evaluation_start_time = (
            time.time()
        )

        # REEVALUATION LOOKUP

        previous_evaluation = None

        evaluation_version = 1

        reevaluation_count = 0

        is_reevaluated = False

        reevaluated_at = None

        if request.previous_evaluation_id:

            previous_evaluation = (
                await EvaluationRepository
                .get_evaluation_by_id(
                    request.previous_evaluation_id
                )
            )

            if previous_evaluation:

                previous_result = (
                    previous_evaluation.result_data
                )

                evaluation_version = (

                    previous_result.get(
                        "evaluation_version",
                        1
                    ) + 1
                )

                reevaluation_count = (

                    previous_result.get(
                        "reevaluation_count",
                        0
                    ) + 1
                )

                is_reevaluated = True

                reevaluated_at = (
                    datetime.utcnow()
                )

                logger.info(
                    (
                        "Reevaluation detected | "
                        f"Previous Evaluation ID: "
                        f"{request.previous_evaluation_id}"
                    )
                )

        try:

            groq_result = (
                await self._evaluate_with_provider(

                    request=request,

                    evaluation_version=(
                        evaluation_version
                    ),

                    reevaluation_count=(
                        reevaluation_count
                    ),

                    is_reevaluated=(
                        is_reevaluated
                    ),

                    reevaluated_at=(
                        reevaluated_at
                    )
                )
            )
            
            # AUTO REEVALUATION
            # FOR SUSPICIOUS LOW SCORES

            if (
                groq_result.ai_score <= 10

                and not groq_result
                .requires_manual_review
            ):

                logger.warning(
                    (
                        "Suspicious low score detected. "
                        "Starting automatic reevaluation."
                    )
                )
                reevaluated_result = (
                    await self._evaluate_with_provider(

                        request=request,

                        evaluation_version=(
                            evaluation_version + 1
                        ),

                        reevaluation_count=1,

                        is_reevaluated=True,

                        reevaluated_at=(
                            datetime.utcnow()
                        )
                    )
                )

                reevaluated_result.reevaluation_count = 1

                reevaluated_result.previous_evaluation_id = (
                    groq_result.evaluation_id
                )

                reevaluated_result.is_reevaluated = True

                reevaluated_result.reevaluation_reason = (
                    "Automatic reevaluation "
                    "triggered due to very low score."
                )

                # USE BETTER SCORE

                if (
                    reevaluated_result.ai_score
                    > groq_result.ai_score
                ):

                    logger.info(
                        (
                            "Reevaluation improved score "
                            f"from {groq_result.ai_score} "
                            f"to "
                            f"{reevaluated_result.ai_score}"
                        )
                    )

                    groq_result = (
                        reevaluated_result
                    )

                else:

                    logger.warning(
                        (
                            "Reevaluation did not improve "
                            "score significantly."
                        )
                    )
                    if reevaluated_result.ai_score <= 10:

                        groq_result.requires_manual_review = True

                        groq_result.manual_review_reason = (
                            "Repeated low score detected "
                            "after automatic reevaluation."
                        )

                        groq_result.evaluation_status = (
                            "manual_review"
                        )

                        groq_result.final_feedback = (
                            "Evaluation confidence is too low. "
                            "Submission forwarded for "
                            "instructor review."
                        )

                        groq_result.ai_score = 0

                        groq_result.strengths = []

                        groq_result.weaknesses = []

                        groq_result.improvement_suggestions = []

                        groq_result.skill_breakdown = []

        except Exception as evaluation_error:

            logger.exception(
                (
                    "Evaluation pipeline failed. "
                    "Forwarding to manual review: "
                    f"{str(evaluation_error)}"
                )
            )

            evaluation_duration = round(

                time.time()
                - evaluation_start_time,

                2
            )

            groq_result = (
                self._manual_review_result(

                    request=request,

                    reason=(
                        "AI provider is temporarily "
                        "unavailable or failed to "
                        "complete the evaluation."
                    ),

                    evaluation_version=(
                        evaluation_version
                    ),

                    reevaluation_count=(
                        reevaluation_count
                    ),

                    is_reevaluated=(
                        is_reevaluated
                    ),

                    reevaluated_at=(
                        reevaluated_at
                    ),

                    evaluation_duration_seconds=(
                        evaluation_duration
                    )
                )
            )

        logger.info(
            "Evaluation completed"
        )

        evaluation_results = [
            groq_result
        ]

        final_result_data = (
            AggregationService.aggregate_results(
                evaluation_results
            )
        )

        final_result_data.update({

            "evaluation_id": (
                groq_result.evaluation_id
            ),

            "evaluation_version": (
                groq_result.evaluation_version
            ),

            "reevaluation_count": (
                groq_result.reevaluation_count
            ),

            "previous_evaluation_id": (
                groq_result.previous_evaluation_id
            ),

            "is_reevaluated": (
                groq_result.is_reevaluated
            ),

            "reevaluated_at": (
                groq_result.reevaluated_at
            ),

            "prompt_version": (
                groq_result.prompt_version
            ),

            "evaluator_version": (
                groq_result.evaluator_version
            ),

            "prompt_tokens": (
                groq_result.prompt_tokens
            ),

            "completion_tokens": (
                groq_result.completion_tokens
            ),

            "total_tokens": (
                groq_result.total_tokens
            ),

            "final_feedback": (
                groq_result.final_feedback
            ),

            "extracted_files_count": (
                groq_result.extracted_files_count
            ),

            "extraction_failures_count": (
                groq_result
                .extraction_failures_count
            ),

            "extraction_timeout_count": (
                groq_result
                .extraction_timeout_count
            ),

            "extraction_duration_seconds": (
                groq_result
                .extraction_duration_seconds
            ),

            "provider_latency_seconds": (
                groq_result
                .provider_latency_seconds
            ),

            "evaluation_duration_seconds": (
                groq_result
                .evaluation_duration_seconds
            ),

            "evaluation_status": (
                groq_result.evaluation_status
            ),
            "requires_manual_review": (
                groq_result.requires_manual_review
            ),

            "manual_review_reason": (
                groq_result.manual_review_reason
            ),

            "blurry_file_detected": (
                groq_result.blurry_file_detected
            ),
            
        })

        evaluation_result = (
            EvaluationResult(
                **final_result_data
            )
        )

        await EvaluationRepository.save_evaluation(

            request_data=(
                request.model_dump()
            ),

            evaluation_result=(
                evaluation_result
            )
        )

        await AuditRepository.log_event(

            event_type=(
                "evaluation_completed"
            ),

            details={

                "evaluation_id": (
                    evaluation_result
                    .evaluation_id
                ),

                "providers": (
                    final_result_data.get(
                        "provider"
                    )
                ),

                "models": (
                    final_result_data.get(
                        "model"
                    )
                ),

                "score": (
                    final_result_data.get(
                        "ai_score"
                    )
                ),

                "is_reevaluated": (
                    evaluation_result
                    .is_reevaluated
                ),

                "evaluation_version": (
                    evaluation_result
                    .evaluation_version
                )
            }
        )

        return evaluation_result
