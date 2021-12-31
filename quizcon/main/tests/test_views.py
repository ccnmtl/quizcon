import json
from mock import patch

from django.http import Http404
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls.base import reverse
from quizcon.main.models import Quiz, Question, Marker
from quizcon.main.tests.factories import (
    CourseTestMixin, QuizFactory, QuestionFactory, QuizSubmissionFactory,
    UserFactory
)
from quizcon.main.views import LTIAssignmentView, LTISpeedGraderView
from quizcon.main.templatetags.quiz_tools import (
    submission_median, submission_mean, submission_mode,
    submission_standard_dev, submission_max_points, submission_min_points,
    total_right_answers, total_wrong_answers, total_idk_answers,
    percentage_choice
)


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
             'multiple_attempts': 1, 'show_answers': 1,
             'randomize': True, 'course': self.course.pk, 'scoring_scheme': 2})

        self.assertEqual(self.course.quiz_set.count(), 1)
        quiz = self.course.quiz_set.first()
        self.assertEqual(quiz.created_by, self.faculty)
        self.assertEqual(quiz.title, 'Lorem Ipsum')
        self.assertEqual(quiz.description, 'dolor sit amet')
        self.assertEqual(quiz.multiple_attempts, 1)
        self.assertEqual(quiz.show_answers, 1)
        self.assertTrue(quiz.randomize)
        self.assertEqual(quiz.scoring_scheme, 2)

        self.assertTrue('Lorem Ipsum quiz created'
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
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            url,
            {'title': 'Alpha',
             'description': 'Quiz updated.',
             'multiple_attempts': 3, 'show_answers': 2,
             'randomize': True, 'scoring_scheme': 0,
             'course': self.quiz.course.pk})

        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, 'Alpha')
        self.assertEqual(self.quiz.description, 'Quiz updated.')
        self.assertEqual(self.quiz.multiple_attempts, 3)
        self.assertTrue(self.quiz.randomize)
        self.assertEqual(self.quiz.show_answers, 2)
        self.assertEqual(self.quiz.scoring_scheme, 0)


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

        self.assertTrue('Congratulations! New question created!'
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

    def test_get_invalid_kwargs(self):
        # no course or assignment specified
        with self.assertRaises(Http404):
            self.view.get(self.view.request)

        # no assignment specified
        with self.assertRaises(Http404):
            self.view.get(self.view.request)

    def test_get(self):
        self.view.kwargs['pk'] = self.quiz.id

        response = self.view.get(self.view.request)
        self.assertFalse(response.context_data['is_faculty'])
        self.assertEqual(response.context_data['quiz'], self.quiz)
        self.assertEqual(response.context_data['submission'], None)

    def test_get_data_submitted(self):
        self.view.kwargs['pk'] = self.quiz.id

        # Create a submission
        submission = QuizSubmissionFactory(quiz=self.quiz, user=self.student)
        self.view.kwargs['submission_id'] = submission.id

        response = self.view.get(self.view.request)
        self.assertFalse(response.context_data['is_faculty'])
        self.assertEqual(response.context_data['quiz'], self.quiz)
        self.assertEqual(response.context_data['submission'], submission)

    # Check behavior if a student has two submissions; different quiz
    def test_get_data_submitted_twice(self):
        self.view.kwargs['pk'] = self.quiz.id
        self.quiz2 = QuizFactory(course=self.course)
        self.question1 = QuestionFactory(quiz=self.quiz2)
        self.question2 = QuestionFactory(quiz=self.quiz2)

        submission = QuizSubmissionFactory(quiz=self.quiz, user=self.student)
        QuizSubmissionFactory(quiz=self.quiz2, user=self.student)
        self.view.kwargs['submission_id'] = submission.id

        response = self.view.get(self.view.request)
        self.assertFalse(response.context_data['is_faculty'])
        self.assertEqual(response.context_data['quiz'], self.quiz)
        self.assertEqual(response.context_data['submission'], submission)

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


class AnalyticsQuizViewTest(CourseTestMixin, TestCase):

    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)
        self.question1 = QuestionFactory(quiz=self.quiz)
        self.submissions = []

    def test_mean_median_standdev_mode(self):
        # no submissions
        self.assertEqual(submission_median(self.submissions),
                         "Cannot calculate median.")
        self.assertEqual(submission_mean(self.submissions),
                         "Cannot calculate mean.")
        self.assertEqual(submission_standard_dev(self.submissions),
                         "Not enough data")
        self.assertEqual(submission_mode(self.submissions),
                         "No unique mode.")
        # one submission
        self.submission = QuizSubmissionFactory(
            quiz=self.quiz, user=self.student)
        self.submissions.append(self.submission)
        self.assertEqual(submission_standard_dev(self.submissions),
                         "Not enough data")

    def test_max_min(self):
        # no submissions
        self.assertEqual(submission_max_points(self.submissions),
                         None)
        self.assertEqual(submission_min_points(self.submissions),
                         None)
        # one submission
        self.submission = QuizSubmissionFactory(
            quiz=self.quiz, user=self.student)
        self.submissions.append(self.submission)
        qres = self.submission.questionresponse_set.first()
        correct_marker = qres.questionresponsemarker_set.get(
            marker__correct=True)

        correct_marker.ordinal = 0
        correct_marker.save()

        self.assertEqual(submission_max_points(self.submissions), 3)
        self.assertEqual(submission_min_points(self.submissions), 3)

        correct_marker.ordinal = 1
        correct_marker.save()

        self.assertEqual(submission_max_points(self.submissions), -5)
        self.assertEqual(submission_min_points(self.submissions), -5)

    def test_precentage_choice(self):
        self.question1 = QuestionFactory(quiz=self.quiz)
        self.question2 = QuestionFactory(quiz=self.quiz)
        user2 = UserFactory()
        user3 = UserFactory()
        self.submission1 = QuizSubmissionFactory(
                            quiz=self.quiz, user=self.student)
        self.submission2 = QuizSubmissionFactory(quiz=self.quiz, user=user2)
        self.submission3 = QuizSubmissionFactory(quiz=self.quiz, user=user3)
        questions = self.quiz.question_set.all()
        num_markers = range(13)
        for idx in enumerate(num_markers):
            for question in questions:
                test = percentage_choice(idx, question)
                import pdb; pdb.set_trace()

    # def test_normalize_percent(self):
    #     self.submission = QuizSubmissionFactory(
    #         quiz=self.quiz, user=self.student)
    #     self.submissions.append(self.submission)
    #     qres = self.submission.questionresponse_set.first()
    #     correct_marker = qres.questionresponsemarker_set.get(
    #         marker__correct=True)
    #
    #     correct_marker.ordinal = 0
    #     correct_marker.save()
    #
    #     self.assertEqual(normalize_percent(qres), 0)
    #
    #     qres.selected_position = 2
    #     qres.save()
    #
    #     self.assertEqual(normalize_percent(qres), 2)
    #
    #     correct_marker.ordinal = 2
    #     correct_marker.save()
    #
    #     self.assertEqual(normalize_percent(qres), 6)

    def test_total_answers(self):
        self.submission = QuizSubmissionFactory(
            quiz=self.quiz, user=self.student)
        self.submissions.append(self.submission)
        qres = self.submission.questionresponse_set.first()
        correct_marker = qres.questionresponsemarker_set.get(
            marker__correct=True)

        correct_marker.ordinal = 0
        correct_marker.save()

        self.assertEqual(total_right_answers(qres.question), 1)
        self.assertEqual(total_wrong_answers(qres.question), 0)
        self.assertEqual(total_idk_answers(qres.question), 0)

        qres.selected_position = 2
        qres.save()

        self.assertEqual(total_right_answers(qres.question), 0)
        self.assertEqual(total_wrong_answers(qres.question), 1)
        self.assertEqual(total_idk_answers(qres.question), 0)

        qres.selected_position = 12
        qres.save()

        self.assertEqual(total_right_answers(qres.question), 0)
        self.assertEqual(total_wrong_answers(qres.question), 0)
        self.assertEqual(total_idk_answers(qres.question), 1)
