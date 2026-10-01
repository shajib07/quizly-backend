"""API views for creating, listing, updating and deleting quizzes."""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quiz_app.models import Quiz
from quiz_app.utils import create_quiz_from_video
from .permissions import IsQuizOwner
from .serializers import (
    QuizCreatedSerializer,
    QuizCreateSerializer,
    QuizSerializer,
)


class QuizListCreateView(generics.ListAPIView):
    """List the user's quizzes or create a new one from a YouTube URL."""

    serializer_class = QuizSerializer

    def get_queryset(self):
        """Return only the quizzes owned by the requesting user."""
        user_quizzes = Quiz.objects.filter(owner=self.request.user)
        return user_quizzes.prefetch_related('questions')

    def post(self, request):
        """Generate a quiz from the given video and return it."""
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video_url = serializer.validated_data['url']
        quiz = create_quiz_from_video(request.user, video_url)
        quiz_data = QuizCreatedSerializer(quiz).data
        return Response(quiz_data, status=status.HTTP_201_CREATED)


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, partially update or delete a single quiz of its owner."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]
    queryset = Quiz.objects.prefetch_related('questions')
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
