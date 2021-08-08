from quizcon.main.middleware import WhoDidItMiddleware
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from django.urls.base import reverse
from quizcon.main.models import Quiz
from quizcon.main.tests.factories import UserFactory, QuizFactory


def get_response(request):
    # Make a change, any change
    quiz = Quiz.objects.first()
    quiz.title = 'Something Different'
    quiz.save()


class WhoDidItMiddlewareTest(TestCase):

    def test_whodidit(self):
        author = UserFactory()
        quiz = QuizFactory()
        self.assertEqual(quiz.created_by, None)
        self.assertEqual(quiz.modified_by, None)

        mw = WhoDidItMiddleware(get_response)

        url = reverse('quiz-detail', kwargs={'pk': quiz.pk})

        # get operations should leave the object unchanged
        request = RequestFactory().get(url)
        request.user = author
        mw.__call__(request)

        quiz.refresh_from_db()
        self.assertEqual(quiz.created_by, None)
        self.assertEqual(quiz.modified_by, None)

        # post operations should save the request.user
        request = RequestFactory().post(url)
        request.user = author
        mw.__call__(request)

        quiz.refresh_from_db()
        self.assertEqual(quiz.created_by, author)
        self.assertEqual(quiz.modified_by, author)
