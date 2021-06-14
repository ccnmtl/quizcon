# from django.test import TestCase
# from django.urls.base import reverse
# from django.test.client import RequestFactory
# from quizcon.main.tests.factories import UserFactory
# from quizcon.main.middleware import WhoDidItMiddleware
# from quizcon.main.models import Quiz
#
#
# class WhoDidItMiddlewareTest(TestCase):
#     def setUp(self):
#         self.request = RequestFactory.post('/')
#         self.request.user = UserFactory()
#
#     def test_created_by(self):
#         middleware = WhoDidItMiddleware()
#         respone = self.middleware.process_request(self.request)
#         quiz = Quiz.objects.create()
