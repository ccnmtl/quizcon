from courseaffils.models import Course
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

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
    (0, 'No Consequences'),
    (1, 'Moderate Consequences'),
    (2, 'High Consequences'),
    (3, 'Custom')
]

SHOW_ANSWERS_CHOICES = [
    (0, 'Never'),
    (1, 'Immediately after quiz submission'),
    (2, 'On given date')
]

LEVELS = [EASY, MEDIUM, HARD]


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    multiple_attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    randomize = models.BooleanField(
        default=False,
        verbose_name="Randomize the quiz questions")
    show_answers = models.PositiveSmallIntegerField(
        choices=SHOW_ANSWERS_CHOICES,
        default=1
    )
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
    show_answers_date = models.DateField(blank=True, null=True)
    time = models.PositiveSmallIntegerField(blank=True, null=True,
                                            validators=[
                                                        MinValueValidator(1),
                                                        MaxValueValidator(180)
                                                        ])

    display_name = "Quiz"

    def show_answers_verbose(self):
        return dict(SHOW_ANSWERS_CHOICES)[self.show_answers]

    def scoring_scheme_verbose(self):
        return dict(SCORING_SCHEMES)[self.scoring_scheme]

    def total_points(self):
        scheme = LEVELS[self.scoring_scheme]
        return self.question_set.count() * scheme['0']

    def ordered_questions(self):
        return self.question_set.all().order_by('ordinality')

    def randomize_questions(self):
        return self.question_set.all().order_by('?')

    # To be used for the student help modal
    def value_per_marker(self, value):
        scheme = LEVELS[self.scoring_scheme]
        value = str(value)
        return scheme[value]

    def clone(self):
        question_set = []
        # Clone the questions.
        cloned = Quiz.objects.create(
                    course=self.course,
                    title=self.title + ' (clone)',
                    description=self.description,
                    multiple_attempts=self.multiple_attempts,
                    scoring_scheme=self.scoring_scheme,
                    show_answers=self.show_answers,
                    randomize=self.randomize,
                    time=self.time,
                )
        for q in self.question_set.all():
            question = Question.objects.create(
                quiz=cloned,
                description=q.description,
                text=q.text,
                explanation=q.explanation,
                ordinality=q.ordinality
                )

            for marker in q.marker_set.all():
                marker.clone(question)

            question_set.append(question)

        cloned.question_set.add(*question_set)

        return cloned


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

    def correct_answer_label(self):
        correct_marker = self.correct_marker()
        return correct_marker.label

    def highest_question_points(self):
        scheme = LEVELS[self.quiz.scoring_scheme]
        return scheme['0']

    def lowest_question_points(self):
        scheme = LEVELS[self.quiz.scoring_scheme]
        return scheme['6']


class Marker(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.IntegerField()
    label = models.TextField(blank=True, null=True)
    correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def clone(self, question):
        return Marker.objects.create(
            question=question,
            value=self.value,
            label=self.label,
            correct=self.correct
        )


class QuizSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    time = models.IntegerField(blank=True, null=True)

    def user_points(self):
        """Add up the all the question points for a given submission"""
        points = 0
        for questionresponse in self.questionresponse_set.all():
            points += questionresponse.user_question_points()

        return points

    def user_score(self):
        """The user's total points divided by the possible score"""
        """All negative values are rounded up to 0"""
        score = round(self.user_points() / self.quiz.total_points(), 2)
        return 0 if score < 0 else score

    def user_score_percent(self):
        """The user's total points divided by the possible score times 100"""
        """All negative values are rounded up to 0"""
        score = round(self.user_points() / self.quiz.total_points(), 2) * 100
        return 0 if score < 0 else score

    def submitted(self):
        question_count = self.quiz.question_set.count()
        response_count = self.questionresponse_set.count()
        return question_count == response_count


class QuestionResponse(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE)
    selected_position = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def user_question_points(self):
        """Based on the correct marker position, determine the number of points
           the user earned for their response"""

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
