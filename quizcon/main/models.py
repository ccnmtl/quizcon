from courseaffils.models import Course
from django.contrib.auth.models import User
from django.db import models


class Quiz(models.Model):
    SCORING_SCHEMES = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
        (4, 'Custom')
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField()
    multiple_attempts = models.IntegerField(default=0)
    show_answers = models.BooleanField(
        default=False,
        verbose_name="Show the correct answers on submission")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    randomize = models.BooleanField(
        default=False,
        verbose_name="Randomize the quiz questions")
    scoring_scheme = models.PositiveSmallIntegerField(
        choices=SCORING_SCHEMES,
        default=1
    )
    created_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL,
        related_name='quiz_created_by')
    modified_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL,
        related_name='quiz_modified_by')

    display_name = "Quiz"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    text = models.TextField()
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    ordinality = models.IntegerField(default=-1)

    def random_markers(self):
        return self.marker_set.all().order_by('?')


class Marker(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.IntegerField()
    label = models.TextField(blank=True, null=True)
    correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class QuizSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class QuestionResponse(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE)
    selected_position = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class QuestionResponseMarker(models.Model):
    response = models.ForeignKey(QuestionResponse, on_delete=models.CASCADE)
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    ordinal = models.IntegerField()

    class Meta:
        ordering = ['ordinal']
