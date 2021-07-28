from django.test import TestCase
from quizcon.main.tests.factories import (
    CourseTestMixin, QuizFactory, QuestionFactory, QuestionResponseFactory,
    QuizSubmissionFactory
)
from quizcon.main.models import Quiz


class BasicModelTest(TestCase):
    def test_dummy(self):
        self.assertTrue(True)


class QuizCloneTest(CourseTestMixin, TestCase):
    def setUp(self):
        self.setup_course()

    def test_clone(self):
        original = QuizFactory(course=self.course, title='cloned quiz')
        original.question = QuestionFactory(quiz=original)

        cloned_pk = original.clone().pk
        cloned = Quiz.objects.get(pk=cloned_pk)

        self.assertNotEqual(original.pk, cloned.pk)
        self.assertEqual(original.title, 'cloned quiz')
        self.assertEqual(cloned.title, 'cloned quiz')

        cloned.title = 'new title'
        original.save()
        cloned.save()

        original.refresh_from_db()
        cloned.refresh_from_db()

        self.assertNotEqual(original.pk, cloned.pk)
        self.assertEqual(original.title, 'cloned quiz')
        self.assertEqual(cloned.title, 'new title')
        self.assertEqual(original.scoring_scheme, cloned.scoring_scheme)

        cloned.scoring_scheme = 0
        cloned.save()
        cloned.refresh_from_db()
        self.assertEqual(cloned.scoring_scheme, 0)
        self.assertNotEqual(original.scoring_scheme, cloned.scoring_scheme)

        self.assertEqual(original.question_set.count(),
                         cloned.question_set.count())


class QuizSubmissionTest(CourseTestMixin, TestCase):

    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)
        self.question1 = QuestionFactory(quiz=self.quiz)
        self.question2 = QuestionFactory(quiz=self.quiz)

    def test_score_easy_quiz(self):
        self.quiz.scoring_scheme = 0
        self.quiz.save()

        submission = QuizSubmissionFactory(quiz=self.quiz, user=self.student)

        response = submission.questionresponse_set.get(question=self.question1)
        response.selected_position = 4
        response.save()
        correct_marker = response.questionresponsemarker_set.get(
            marker__correct=True)
        correct_marker.ordinal = 2
        correct_marker.save()
        self.assertEqual(response.score_question(), 0)

        response = submission.questionresponse_set.get(question=self.question2)
        response.selected_position = 4
        response.save()
        correct_marker = response.questionresponsemarker_set.get(
            marker__correct=True)
        correct_marker.ordinal = 1
        correct_marker.save()
        self.assertEqual(response.score_question(), 5)

        self.assertEqual(submission.score_quiz(), 5)

    def test_score_medium_quiz(self):
        self.quiz.scoring_scheme = 1
        self.quiz.save()
        self.assertEqual(self.quiz.question_set.count(), 2)

        submission = QuizSubmissionFactory(quiz=self.quiz, user=self.student)

        response = submission.questionresponse_set.get(question=self.question1)
        response.selected_position = 1
        response.save()
        correct_marker = response.questionresponsemarker_set.get(
            marker__correct=True)
        correct_marker.ordinal = 2
        correct_marker.save()
        self.assertEqual(response.score_question(), -2)
        self.assertEqual(submission.questionresponse_set.count(), 2)

        response = submission.questionresponse_set.get(question=self.question2)
        response.selected_position = 5
        response.save()
        correct_marker = response.questionresponsemarker_set.get(
            marker__correct=True)
        correct_marker.ordinal = 1
        correct_marker.save()
        self.assertEqual(response.score_question(), 2)
        self.assertEqual(submission.questionresponse_set.count(), 2)

        self.assertEqual(submission.score_quiz(), 0)

    def test_i_dont_know(self):
        submission = QuizSubmissionFactory(quiz=self.quiz, user=self.student)

        response = submission.questionresponse_set.get(question=self.question1)
        response.selected_position = 12
        response.save()
        correct_marker = response.questionresponsemarker_set.get(
            marker__correct=True)
        correct_marker.ordinal = 2
        correct_marker.save()
        self.assertEqual(response.score_question(), 0)

        response = submission.questionresponse_set.get(question=self.question2)
        response.selected_position = 12
        response.save()
        correct_marker = response.questionresponsemarker_set.get(
            marker__correct=True)
        correct_marker.ordinal = 1
        correct_marker.save()
        self.assertEqual(response.score_question(), 0)

        self.assertEqual(submission.score_quiz(), 0)


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

        # Easy Scoring Scheme
        response.question.quiz.scoring_scheme = 0
        response.save()
        self.assertEqual(response.score_question(), 5)
        correct_marker.ordinal = 1
        correct_marker.save()
        self.assertEqual(response.score_question(), 0)

        # Medium Scoring Scheme
        response.question.quiz.scoring_scheme = 1
        response.save()
        self.assertEqual(response.score_question(), -2)
        correct_marker.ordinal = 0
        correct_marker.save()
        self.assertEqual(response.score_question(), 3)

        # Hard Scoring Scheme
        response.question.quiz.scoring_scheme = 2
        response.save()
        self.assertEqual(response.score_question(), 3)
        correct_marker.ordinal = 2
        correct_marker.save()
        self.assertEqual(response.score_question(), -5)

        # I Don't Knows
        response.selected_position = 12
        response.save()

        # Easy
        # correct_marker_position = 2
        response.question.quiz.scoring_scheme = 0
        response.question.quiz.save()
        self.assertEqual(response.score_question(), 2)

        # Hard
        correct_marker.ordinal = 0
        correct_marker.save()
        response.question.quiz.scoring_scheme = 2
        response.question.quiz.save()
        self.assertEqual(response.score_question(), 0)
