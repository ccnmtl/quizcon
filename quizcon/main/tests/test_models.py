from django.test import TestCase
from quizcon.main.tests.factories import (
    CourseTestMixin, QuizFactory, QuestionFactory, QuestionResponseFactory,
    QuizSubmissionFactory
)


class BasicModelTest(TestCase):
    def test_dummy(self):
        self.assertTrue(True)


class QuestionResponseTest(CourseTestMixin, TestCase):
    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)
        self.question1 = QuestionFactory(quiz=self.quiz)
        self.question2 = QuestionFactory(quiz=self.quiz)

    def test_score_question(self):
        submission = QuizSubmissionFactory(quiz=self.quiz, user=self.student)
        response = QuestionResponseFactory(
            submission=submission, question=self.question1)
        correct_marker = response.questionresponsemarker_set.get(
            marker__correct=True)
        correct_marker.ordinal = 0
        correct_marker.save()
        # selected = response.selected_position

        # Easy Scoring Scheme
        response.question.quiz.scoring_scheme = 1
        response.save()
        self.assertEqual(response.score_question(), 5)
        correct_marker.ordinal = 1
        correct_marker.save()
        self.assertEqual(response.score_question(), 0)

        # Medium Scoring Scheme
        response.question.quiz.scoring_scheme = 2
        response.save()
        self.assertEqual(response.score_question(), -2)
        correct_marker.ordinal = 0
        correct_marker.save()
        self.assertEqual(response.score_question(), 3)

        # Hard Scoring Scheme
        response.question.quiz.scoring_scheme = 3
        response.save()
        self.assertEqual(response.score_question(), 3)
        correct_marker.ordinal = 2
        correct_marker.save()
        self.assertEqual(response.score_question(), -5)
