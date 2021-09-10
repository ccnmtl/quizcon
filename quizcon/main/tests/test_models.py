from django.test import TestCase
from quizcon.main.tests.factories import (
    CourseTestMixin, QuizFactory, QuestionFactory, QuestionResponseFactory,
    QuizSubmissionFactory
)


class BasicModelTest(TestCase):
    def test_dummy(self):
        self.assertTrue(True)


class QuizTest(CourseTestMixin, TestCase):

    def setUp(self):
        self.setup_course()

    def test_total_points(self):
        quiz = QuizFactory(course=self.course, scoring_scheme=0)
        QuestionFactory(quiz=quiz)
        QuestionFactory(quiz=quiz)
        self.assertEqual(quiz.total_points(), 10)

        quiz.scoring_scheme = 1
        quiz.save()
        self.assertEqual(quiz.total_points(), 6)

        quiz.scoring_scheme = 2
        quiz.save()
        self.assertEqual(quiz.total_points(), 6)

    def test_clone(self):
        q = QuizFactory(course=self.course, title='cloned quiz')
        q.question = QuestionFactory(quiz=q)

        c = q.clone()

        self.assertNotEqual(q.pk, c.pk)
        self.assertEqual(q.title, 'cloned quiz')
        self.assertEqual(c.title, 'cloned quiz (clone)')
        self.assertEqual(q.scoring_scheme, c.scoring_scheme)
        self.assertEqual(q.question_set.count(),
                         c.question_set.count())
        self.assertNotEqual(q.question_set.first().pk,
                            c.question_set.first().pk)
        quiz_q = q.question_set.first()
        clone_q = c.question_set.first()

        self.assertEqual(quiz_q.marker_set.count(),
                         clone_q.marker_set.count())
        self.assertNotEqual(quiz_q.marker_set.first().pk,
                            clone_q.marker_set.first().pk)

    def test_show_answers_verbose(self):
        quiz = QuizFactory(course=self.course, show_answers=0)
        self.assertEqual(quiz.show_answers_verbose(), 'Never')
        quiz.show_answers = 1
        self.assertEqual(quiz.show_answers_verbose(),
                         'Immediately after quiz submission')

    def test_ordered_questions(self):
        quiz = QuizFactory(course=self.course, scoring_scheme=0)
        QuestionFactory(quiz=quiz)
        QuestionFactory(quiz=quiz)

        q1 = quiz.question_set.first()
        # ordinality of q2 is -1
        q2 = quiz.question_set.last()
        q1.ordinality = 1
        q1.save()
        first = quiz.ordered_questions().first()
        self.assertEqual(quiz.question_set.first().ordinality, 1)
        self.assertEqual(first, q2)

    def test_highest_question_points(self):
        quiz = QuizFactory(course=self.course, scoring_scheme=0)
        QuestionFactory(quiz=quiz)

        q1 = quiz.question_set.first()
        self.assertEqual(q1.highest_question_points(), 5)


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
        self.assertEqual(response.user_question_points(), 0)

        response = submission.questionresponse_set.get(question=self.question2)
        response.selected_position = 4
        response.save()
        correct_marker = response.questionresponsemarker_set.get(
            marker__correct=True)
        correct_marker.ordinal = 1
        correct_marker.save()
        self.assertEqual(response.user_question_points(), 5)

        self.assertEqual(submission.user_points(), 5)
        self.assertEqual(submission.user_score(), 0.5)
        self.assertEqual(submission.user_score_percent(), 50)

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
        self.assertEqual(response.user_question_points(), -2)
        self.assertEqual(submission.questionresponse_set.count(), 2)

        response = submission.questionresponse_set.get(question=self.question2)
        response.selected_position = 5
        response.save()
        correct_marker = response.questionresponsemarker_set.get(
            marker__correct=True)
        correct_marker.ordinal = 1
        correct_marker.save()
        self.assertEqual(response.user_question_points(), 2)
        self.assertEqual(submission.questionresponse_set.count(), 2)

        self.assertEqual(submission.user_points(), 0)
        self.assertEqual(submission.user_score(), 0.0)
        self.assertEqual(submission.user_score_percent(), 0)

    def test_i_dont_know(self):
        submission = QuizSubmissionFactory(quiz=self.quiz, user=self.student)

        response = submission.questionresponse_set.get(question=self.question1)
        response.selected_position = 12
        response.save()
        correct_marker = response.questionresponsemarker_set.get(
            marker__correct=True)
        correct_marker.ordinal = 2
        correct_marker.save()
        self.assertEqual(response.user_question_points(), 0)

        response = submission.questionresponse_set.get(question=self.question2)
        response.selected_position = 12
        response.save()
        correct_marker = response.questionresponsemarker_set.get(
            marker__correct=True)
        correct_marker.ordinal = 1
        correct_marker.save()
        self.assertEqual(response.user_question_points(), 0)

        self.assertEqual(submission.user_points(), 0)
        self.assertEqual(submission.user_score(), 0.0)
        self.assertEqual(submission.user_score_percent(), 0)


class QuestionResponseTest(CourseTestMixin, TestCase):

    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)
        self.question1 = QuestionFactory(quiz=self.quiz)
        self.question2 = QuestionFactory(quiz=self.quiz)

    def test_user_question_points(self):
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
        self.assertEqual(response.user_question_points(), 5)
        correct_marker.ordinal = 1
        correct_marker.save()
        self.assertEqual(response.user_question_points(), 0)

        # Medium Scoring Scheme
        response.question.quiz.scoring_scheme = 1
        response.save()
        self.assertEqual(response.user_question_points(), -2)
        correct_marker.ordinal = 0
        correct_marker.save()
        self.assertEqual(response.user_question_points(), 3)

        # Hard Scoring Scheme
        response.question.quiz.scoring_scheme = 2
        response.save()
        self.assertEqual(response.user_question_points(), 3)
        correct_marker.ordinal = 2
        correct_marker.save()
        self.assertEqual(response.user_question_points(), -5)

        # I Don't Knows
        response.selected_position = 12
        response.save()

        # Easy
        # correct_marker_position = 2
        response.question.quiz.scoring_scheme = 0
        response.question.quiz.save()
        self.assertEqual(response.user_question_points(), 2)

        # Hard
        correct_marker.ordinal = 0
        correct_marker.save()
        response.question.quiz.scoring_scheme = 2
        response.question.quiz.save()
        self.assertEqual(response.user_question_points(), 0)
