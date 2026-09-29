"""API views for listing, retrieving, updating and deleting quizzes."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from quiz_app.models import Quiz
from .permissions import IsQuizOwner
from .serializers import QuizSerializer


class QuizListView(generics.ListAPIView):
    """List all quizzes of the authenticated user."""

    serializer_class = QuizSerializer

    def get_queryset(self):
        """Return only the quizzes owned by the requesting user."""
        user_quizzes = Quiz.objects.filter(owner=self.request.user)
        return user_quizzes.prefetch_related('questions')


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, partially update or delete a single quiz of its owner."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]
    queryset = Quiz.objects.prefetch_related('questions')
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']