"""Admin panel configuration for quizzes and questions."""

from django.contrib import admin

from .models import Question, Quiz


class QuestionInline(admin.StackedInline):
    """Edit the questions of a quiz directly on the quiz page."""

    model = Question
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin view to list, search and edit quizzes."""

    list_display = ['title', 'owner', 'created_at', 'updated_at']
    list_filter = ['created_at', 'owner']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin view to list, search and edit single questions."""

    list_display = ['question_title', 'quiz', 'answer']
    list_filter = ['quiz']
    search_fields = ['question_title']
