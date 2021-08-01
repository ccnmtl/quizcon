import json
from mock import patch

from django.http import Http404
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls.base import reverse
from quizcon.main.models import Quiz, Question, Marker
from quizcon.main.tests.factories import (
    CourseTestMixin, QuizFactory, QuestionFactory, QuizSubmissionFactory
)
from quizcon.main.views import LTIAssignmentView, LTISpeedGraderView


class BasicTest(TestCase):
    def test_root(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 302)

    def test_smoketest(self):
        response = self.client.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'PASS')


class CreateQuizTest(CourseTestMixin, TestCase):

    def setUp(self):
        self.setup_course()

    def test_create_quiz_student(self):
        url = reverse('create-quiz', kwargs={'pk': self.course.pk})

        self.client.login(username=self.student.username, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_create_flow(self):
        url = reverse('create-quiz', kwargs={'pk': self.course.pk})

        self.client.login(username=self.faculty.username, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            url,
            {'title': 'Lorem Ipsum', 'description': 'dolor sit amet',
             'multiple_attempts': 1, 'show_answers': False,
             'randomize': True, 'course': self.course.pk, 'scoring_scheme': 2})

        self.assertEqual(self.course.quiz_set.count(), 1)
        quiz = self.course.quiz_set.first()
        self.assertEqual(quiz.created_by, self.faculty)
        self.assertEqual(quiz.title, 'Lorem Ipsum')
        self.assertEqual(quiz.description, 'dolor sit amet')
        self.assertEqual(quiz.multiple_attempts, 1)
        self.assertFalse(quiz.show_answers)
        self.assertTrue(quiz.randomize)
        self.assertEqual(quiz.scoring_scheme, 2)

        self.assertTrue('<strong>Lorem Ipsum</strong> quiz created'
                        in response.cookies['messages'].value)


class UpdateQuizTest(CourseTestMixin, TestCase):
    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)

    def test_update_quiz(self):
        url = reverse('update-quiz', kwargs={'pk': self.quiz.pk})

        self.client.login(username=self.faculty.username, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            url,
            {'title': 'Alpha'})
        self.assertTrue(
            'This field is required' in
            response.context_data['form'].errors['description'][0])
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            url,
            {'title': 'Alpha',
             'description': 'Quiz updated.',
             'multiple_attempts': 3, 'show_answers': False,
             'randomize': True, 'scoring_scheme': 3,
             'course': self.quiz.course.pk})

        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, 'Alpha')
        self.assertEqual(self.quiz.description, 'Quiz updated.')
        self.assertEqual(self.quiz.multiple_attempts, 3)
        self.assertTrue(self.quiz.randomize)
        self.assertFalse(self.quiz.show_answers)
        self.assertEqual(self.quiz.scoring_scheme, 3)


class DeleteQuizTest(CourseTestMixin, TestCase):
    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)

    def test_delete_quiz(self):
        url = reverse('delete-quiz', kwargs={'pk': self.quiz.pk})

        self.client.login(username=self.faculty.username, password='test')

        response = self.client.post(url)
        self.assertRedirects(response, '/course/' + str(self.course.pk) + '/')
        with self.assertRaises(Quiz.DoesNotExist):
            Quiz.objects.get(id=self.quiz.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.course.quiz_set.count(), 0)


class CreateQuestionViewTest(CourseTestMixin, TestCase):

    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)

    def test_create_question_student(self):
        url = reverse('create-question', kwargs={'pk': self.quiz.pk})

        self.client.login(username=self.student.username, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_create_flow(self):
        url = reverse('create-question', kwargs={'pk': self.quiz.pk})

        self.client.login(username=self.faculty.username, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            url,
            {'text': 'Lorem Ipsum',
             'explanation': 'consectetur adipiscing elit',
             'quiz': self.quiz.pk, 'answer_label_1': 'Thor',
             'answer_label_2': 'Loki', 'answer_label_3': 'Odin', 'correct': 2})

        self.assertEqual(self.quiz.question_set.count(), 1)
        question = self.quiz.question_set.first()
        self.assertEqual(question.text, 'Lorem Ipsum')
        self.assertEqual(question.explanation, 'consectetur adipiscing elit')
        self.assertEqual(question.marker_set.count(), 3)
        self.assertEqual(question.marker_set.all()[0].label, 'Thor')
        self.assertEqual(question.marker_set.all()[1].label, 'Loki')
        self.assertEqual(question.marker_set.all()[2].label, 'Odin')
        self.assertFalse(question.marker_set.all()[0].correct)
        self.assertTrue(question.marker_set.all()[1].correct)
        self.assertFalse(question.marker_set.all()[2].correct)

        self.assertTrue('<strong>Lorem Ipsum</strong> question created'
                        in response.cookies['messages'].value)


class UpdateQuestionTest(CourseTestMixin, TestCase):
    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)
        self.question = QuestionFactory(quiz=self.quiz)

    def test_update_question(self):
        url = reverse('update-question', kwargs={'pk': self.question.pk})

        self.client.login(username=self.faculty.username, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            url,
            {'text': 'Alpha',
                'explanation': 'Ch-ch-changes',
                'quiz': self.quiz.pk, 'answer_label_1': 'Thor',
                'answer_label_2': 'Loki', 'answer_label_3': 'Odin',
                'correct': 2})

        self.question.refresh_from_db()
        self.assertEqual(self.question.text, 'Alpha')
        self.assertEqual(self.question.explanation, 'Ch-ch-changes')
        self.assertEqual(self.question.marker_set.count(), 3)
        self.assertEqual(self.question.marker_set.all()[0].label, 'Thor')
        self.assertEqual(self.question.marker_set.all()[1].label, 'Loki')
        self.assertEqual(self.question.marker_set.all()[2].label, 'Odin')
        self.assertFalse(self.question.marker_set.all()[0].correct)
        self.assertTrue(self.question.marker_set.all()[1].correct)
        self.assertFalse(self.question.marker_set.all()[2].correct)


class DeleteQuestionTest(CourseTestMixin, TestCase):
    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)
        self.question = QuestionFactory(quiz=self.quiz)

    def test_delete_question(self):
        url = reverse('delete-question', kwargs={'pk': self.question.pk})

        self.client.login(username=self.faculty.username, password='test')
        response = self.client.post(url)
        self.assertRedirects(response, '/quiz/' + str(self.quiz.pk)
                             + '/update/')
        with self.assertRaises(Question.DoesNotExist):
            Question.objects.get(id=self.question.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.quiz.question_set.count(), 0)


class LTIAssignmentViewTest(CourseTestMixin, TestCase):

    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)
        self.question1 = QuestionFactory(quiz=self.quiz)
        self.question2 = QuestionFactory(quiz=self.quiz)

        self.view = LTIAssignmentView()
        self.view.request = RequestFactory().get('/', {})
        self.view.request.user = self.student
        self.view.kwargs = {}

    def test_get_context_data_invalid_kwargs(self):
        # no course or assignment specified
        with self.assertRaises(Http404):
            self.view.get_context_data()

        # no assignment specified
        with self.assertRaises(Http404):
            self.view.get_context_data()

    def test_get_context_data(self):
        self.view.kwargs['pk'] = self.quiz.id

        ctx = self.view.get_context_data()
        self.assertFalse(ctx['is_faculty'])
        self.assertEqual(ctx['quiz'], self.quiz)
        self.assertEqual(ctx['submission'], None)

    def test_get_context_data_submitted(self):
        self.view.kwargs['pk'] = self.quiz.id

        # Create a submission
        submission = QuizSubmissionFactory(quiz=self.quiz, user=self.student)
        self.view.kwargs['submission_id'] = submission.id

        ctx = self.view.get_context_data()
        self.assertFalse(ctx['is_faculty'])
        self.assertEqual(ctx['quiz'], self.quiz)
        self.assertEqual(ctx['submission'], submission)

    def test_post_invalid_kwargs(self):
        # no course or assignment specified
        with self.assertRaises(Http404):
            self.view.post()

        # no assignment specified
        with self.assertRaises(Http404):
            self.view.post()

    def test_get_launch_url(self):
        submission = QuizSubmissionFactory(quiz=self.quiz, user=self.student)
        launch_url = \
            'http://testserver/lti/?assignment=grade&pk={}'.format(
                submission.id)
        self.assertEqual(self.view.get_launch_url(submission), launch_url)

    def mock_post_score(self, submission):
        return True

    def test_post(self):
        with patch.object(self.view, 'post_score', self.mock_post_score):
            self.view.kwargs['pk'] = self.quiz.id

            # setup the post data
            # two keys that indicate the original order of the markers
            # one key with the user's answer
            data = {}
            qmarkers = {}
            for idx, question in enumerate(self.quiz.question_set.all()):
                key = 'question-{}-markers'.format(question.pk)
                markers = []
                for m in question.random_markers():
                    markers.append(m.id)
                data[key] = json.dumps(markers)
                data[str(question.pk)] = idx
                qmarkers[question.pk] = markers

            self.view.request = RequestFactory().post('/', data)
            self.view.request.user = self.student

            response = self.view.post()
            self.assertEqual(response.status_code, 302)

            submission = self.quiz.quizsubmission_set.first()
            self.assertEqual(submission.user, self.student)
            self.assertEqual(submission.quiz, self.quiz)

            url = reverse('quiz-submission',
                          kwargs={'pk': self.quiz.id,
                                  'submission_id': submission.id})
            self.assertEqual(url, response.url)

            # check the response for the first question
            qr = submission.questionresponse_set.get(question=self.question1)
            self.assertEqual(qr.selected_position, 0)
            qr = submission.questionresponse_set.get(question=self.question2)
            self.assertEqual(qr.selected_position, 1)

            # check that the order was saved as expected for question 1
            qr = self.question1.questionresponse_set.get(submission=submission)
            for idx, pk in enumerate(qmarkers[self.question1.pk]):
                marker = Marker.objects.get(pk=pk)
                qrm = qr.questionresponsemarker_set.get(marker=marker)
                self.assertEqual(qrm.ordinal, idx)

            # check that the order was saved as expected for question 2
            qr = self.question2.questionresponse_set.get(submission=submission)
            for idx, pk in enumerate(qmarkers[self.question2.pk]):
                marker = Marker.objects.get(pk=pk)
                qrm = qr.questionresponsemarker_set.get(marker=marker)
                self.assertEqual(qrm.ordinal, idx)


class LTISpeedGraderViewTest(CourseTestMixin, TestCase):

    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)
        self.question1 = QuestionFactory(quiz=self.quiz)
        self.question2 = QuestionFactory(quiz=self.quiz)

        self.submission = QuizSubmissionFactory(
            quiz=self.quiz, user=self.student)

        self.view = LTISpeedGraderView()
        self.view.request = RequestFactory().get('/', {})
        self.view.request.user = self.student
        self.view.kwargs = {}

    def test_get_context_data_invalid_kwargs(self):
        # no submission specified
        with self.assertRaises(Http404):
            self.view.get_context_data()

    def test_get_context_data(self):
        self.view.kwargs['pk'] = self.submission.id

        ctx = self.view.get_context_data()
        self.assertFalse(ctx['is_faculty'])
        self.assertTrue(ctx['is_student'])
        self.assertEqual(ctx['quiz'], self.quiz)
        self.assertEqual(ctx['submission'], self.submission)
