"""Helper functions that turn a YouTube video into a saved quiz."""

import json
import logging
import re
import tempfile
from functools import lru_cache
from pathlib import Path

import whisper
import yt_dlp
from django.conf import settings
from django.db import transaction
from google import genai
from google.genai import errors, types

from quiz_app.exceptions import QuizGenerationError, VideoDownloadError
from quiz_app.models import Question, Quiz

logger = logging.getLogger(__name__)

YOUTUBE_ID_PATTERN = re.compile(
    r'(?:youtube\.com/(?:watch\?(?:.*&)?v=|shorts/|embed/)|youtu\.be/)'
    r'([\w-]{11})'
)

QUIZ_PROMPT = """
Create a quiz based on the transcript below.
Write it in the same language as the transcript.
Return only valid JSON in exactly this format:
{
  "title": "A short, fitting quiz title",
  "description": "One or two sentences that summarize the quiz",
  "questions": [
    {
      "question_title": "The question",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct option"
    }
  ]
}
Rules:
- Exactly 10 questions.
- Exactly 4 different options per question.
- "answer" must be identical to one of its 4 options.

Transcript:
"""


def get_video_url(url):
    """Return the normalized YouTube watch URL, or None if it is invalid."""
    match = YOUTUBE_ID_PATTERN.search(url)
    if match is None:
        return None
    return f'https://www.youtube.com/watch?v={match.group(1)}'


def get_download_options(target_dir):
    """Return the yt-dlp options to download only the audio track."""
    return {
        'format': 'bestaudio/best',
        'outtmpl': str(Path(target_dir) / 'audio.%(ext)s'),
        'quiet': True,
        'noprogress': True,
        'noplaylist': True,
    }


def download_audio(video_url, target_dir):
    """Download the audio track of the video and return its file path."""
    options = get_download_options(target_dir)
    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(video_url, download=True)
            return downloader.prepare_filename(info)
    except yt_dlp.utils.DownloadError as error:
        raise VideoDownloadError() from error


@lru_cache(maxsize=1)
def get_whisper_model():
    """Load the Whisper model once and reuse it for later requests."""
    return whisper.load_model(settings.WHISPER_MODEL)


def transcribe_audio(audio_path):
    """Return the spoken text of the audio file using Whisper."""
    result = get_whisper_model().transcribe(audio_path, fp16=False)
    return result['text'].strip()


def request_quiz_json(transcript, model):
    """Ask a Gemini model for a quiz and return its JSON answer as text."""
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    config = types.GenerateContentConfig(
        response_mime_type='application/json'
    )
    response = client.models.generate_content(
        model=model,
        contents=QUIZ_PROMPT + transcript,
        config=config,
    )
    return response.text


def is_valid_question(question):
    """Return True if the question has four options including the answer."""
    options = question.get('question_options')
    if not isinstance(options, list) or len(options) != 4:
        return False
    has_title = bool(question.get('question_title'))
    return has_title and question.get('answer') in options


def is_valid_quiz(quiz_data):
    """Return True if the quiz has a title and ten valid questions."""
    questions = quiz_data.get('questions')
    if not quiz_data.get('title') or not isinstance(questions, list):
        return False
    return len(questions) == 10 and all(map(is_valid_question, questions))


def try_generate_quiz(transcript, model):
    """Return valid quiz data from the given model, or None if it fails."""
    try:
        quiz_data = json.loads(request_quiz_json(transcript, model))
        return quiz_data if is_valid_quiz(quiz_data) else None
    except (errors.APIError, AttributeError, TypeError, ValueError):
        logger.warning('Quiz generation with %s failed.', model, exc_info=True)
        return None


def generate_quiz_data(transcript):
    """Return quiz data from the first Gemini model that delivers a quiz."""
    for model in settings.GEMINI_MODELS:
        quiz_data = try_generate_quiz(transcript, model)
        if quiz_data is not None:
            return quiz_data
    raise QuizGenerationError()


def build_question(quiz, question_data):
    """Return an unsaved Question for the quiz from the generated data."""
    return Question(
        quiz=quiz,
        question_title=question_data['question_title'][:500],
        question_options=question_data['question_options'],
        answer=question_data['answer'],
    )


@transaction.atomic
def save_quiz(owner, video_url, quiz_data):
    """Store the quiz with all its questions and return the quiz."""
    quiz = Quiz.objects.create(
        owner=owner,
        title=quiz_data['title'][:255],
        description=quiz_data.get('description', ''),
        video_url=video_url,
    )
    questions = [build_question(quiz, q) for q in quiz_data['questions']]
    Question.objects.bulk_create(questions)
    return quiz


def create_quiz_from_video(owner, video_url):
    """Run the full pipeline: download, transcribe, generate and save."""
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = download_audio(video_url, temp_dir)
        transcript = transcribe_audio(audio_path)
    quiz_data = generate_quiz_data(transcript)
    return save_quiz(owner, video_url, quiz_data)
