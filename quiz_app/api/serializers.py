"""Serializers for quizzes and their questions."""

from rest_framework import serializers

from quiz_app.models import Question, Quiz


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize a single question with its options and answer."""

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer']


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