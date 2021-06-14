from django.db import models
from django.contrib.auth.models import User
from courseaffils.models import Course


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField()
    multiple_attempts = models.BooleanField(default=False)
    show_answers = models.BooleanField(
        default=True,
        help_text="Show the correct answers and explanation on submission.")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    randomize = models.BooleanField(
        default=False,
        help_text="Randomize the quiz questions")

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
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
