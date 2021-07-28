from courseaffils.models import Course
from django.contrib.auth.models import User
from django.db import models
import copy

TRIANGLE_SIDE = 4
I_DONT_KNOW_POSITION = 12

EASY = {
    "0": 5,
    "1": 4,
    "2": 3,
    "3": 1,
    "4": 0,
    "5": 0,
    "6": 0,
    "7": 0,
    "8": 0,
    "9": 1,
    "10": 3,
    "11": 4,
    "12": 2
    }
MEDIUM = {
    "0": 3,
    "1": 2,
    "2": 1,
    "3": -1,
    "4": -2,
    "5": -2,
    "6": -2,
    "7": -2,
    "8": -2,
    "9": -1,
    "10": 1,
    "11": 2,
    "12": 0
    }
HARD = {
    "0": 3,
    "1": 2,
    "2": 1,
    "3": -1,
    "4": -5,
    "5": -5,
    "6": -5,
    "7": -5,
    "8": -5,
    "9": -1,
    "10": 1,
    "11": 2,
    "12": 0
    }

SCORING_SCHEMES = [
    (0, 'Easy'),
    (1, 'Medium'),
    (2, 'Hard'),
    (3, 'Custom')
]

LEVELS = [EASY, MEDIUM, HARD]


class Quiz(models.Model):

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

    def clone(self):
        c = copy.copy(self)
        c.pk = None
        c.save()
        # Clone the questions.
        for question in self.question_set.all():
            Question.objects.create(quiz=c)

            for marker in question.marker_set.all():
                cloned_marker = marker.clone()
                cloned_marker.save()
        return c


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

    def correct_marker(self):
        return self.marker_set.get(correct=True)


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

    def score_quiz(self):
        score = 0
        for questionresponse in self.questionresponse_set.all():
            score += questionresponse.score_question()

        return score


class QuestionResponse(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE)
    selected_position = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def score_question(self):
        scheme = LEVELS[self.question.quiz.scoring_scheme]

        if self.selected_position == I_DONT_KNOW_POSITION:
            return scheme[str(self.selected_position)]
        else:
            correct_marker = self.correct_marker_position()
            distance = abs(self.selected_position - correct_marker)
            return scheme[str(distance)]

    def correct_marker_position(self):
        correct_marker = self.question.correct_marker()
        qrm = self.questionresponsemarker_set.get(marker=correct_marker)
        triangle_position = qrm.ordinal * TRIANGLE_SIDE

        return triangle_position

    def is_correct(self):
        return self.correct_marker_position() == self.selected_position


class QuestionResponseMarker(models.Model):
    response = models.ForeignKey(QuestionResponse, on_delete=models.CASCADE)
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    ordinal = models.IntegerField()

    class Meta:
        ordering = ['ordinal']
