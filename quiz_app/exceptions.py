"""Custom API exceptions for the quiz generation pipeline."""

from rest_framework.exceptions import APIException


class VideoDownloadError(APIException):
    """Raised when the audio of a YouTube video cannot be downloaded."""

    status_code = 400
    default_detail = 'The video could not be downloaded.'
    default_code = 'video_download_failed'


class QuizGenerationError(APIException):
    """Raised when no valid quiz could be generated from the transcript."""

    status_code = 500
    default_detail = 'The quiz could not be generated.'
    default_code = 'quiz_generation_failed'
