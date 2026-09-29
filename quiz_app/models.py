"""Database models for quizzes and their questions."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Quiz(models.Model):
    """A quiz generated from a YouTube video and owned by one user."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quizzes',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'quizzes'

    def __str__(self):
        """Return the quiz title as its readable name."""
        return self.title


class Question(models.Model):
    """A single multiple-choice question that belongs to a quiz."""

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    question_title = models.CharField(max_length=500)
    question_options = models.JSONField(default=list)
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        """Return the question text as its readable name."""
        return self.question_title

    def clean(self):
        """Ensure there are four options and the answer is one of them."""
        options = self.question_options
        if not isinstance(options, list) or len(options) != 4:
            raise ValidationError(
                {'question_options': 'Exactly four options are required.'}
            )
        if self.answer not in options:
            raise ValidationError(
                {'answer': 'The answer must be one of the options.'}
            )
