"""Serializers for quizzes and their questions."""

from rest_framework import serializers

from quiz_app.models import Question, Quiz
from quiz_app.utils import get_video_url


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize a single question with its options and answer."""

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer']


class QuestionCreatedSerializer(QuestionSerializer):
    """Serialize a newly created question including its timestamps."""

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ['created_at', 'updated_at']


class QuizSerializer(serializers.ModelSerializer):
    """Serialize a quiz with its questions.

    Only title and description can be changed by the client.
    """

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'created_at',
            'updated_at', 'video_url', 'questions',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'video_url']


class QuizCreatedSerializer(QuizSerializer):
    """Serialize a newly created quiz with timestamps on its questions."""

    questions = QuestionCreatedSerializer(many=True, read_only=True)


class QuizCreateSerializer(serializers.Serializer):
    """Validate the YouTube URL a new quiz should be generated from."""

    url = serializers.CharField()

    def validate_url(self, value):
        """Return the normalized video URL or reject a non-YouTube URL."""
        video_url = get_video_url(value)
        if video_url is None:
            raise serializers.ValidationError('Enter a valid YouTube URL.')
        return video_url
