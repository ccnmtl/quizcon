from django.test import TestCase
from django.urls.base import reverse
from quizcon.main.tests.factories import (
    UserFactory, CourseTestMixin, RegistrarCourseFactory
)
# from lti_provider.tests.factories import LTICourseContextFactory
# from quizcon.main.views import CreateQuizView, UpdateQuizView, DeleteQuizView


class BasicTest(TestCase):
    def test_root(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 200)

    def test_smoketest(self):
        response = self.client.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'PASS')


class CreateQuizTest(CourseTestMixin, TestCase):
    def setUp(self):
        self.course = RegistrarCourseFactory()

    def test_create_quiz_student(self):
        url = reverse('create-quiz', kwargs={'pk': self.course.pk})

        student = UserFactory()
        self.client.login(username=student.username, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_create_flow(self):
        self.setup_course()
        url = reverse('create-quiz', kwargs={'pk': self.course.pk})

        self.client.login(username=self.faculty.username, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            url,
            {'title': 'Lorem Ipsum', 'description': 'dolor sit amet',
             'multiple_attempts': True, 'show_answers': False,
             'randomize': True, 'course': self.course.pk})

        self.assertEqual(self.course.quiz_set.count(), 1)
        quiz = self.course.quiz_set.first()
        self.assertEqual(quiz.created_by, self.faculty)
        self.assertEqual(quiz.title, 'Lorem Ipsum')
        self.assertEqual(quiz.description, 'dolor sit amet')
        self.assertTrue(quiz.multiple_attempts)
        self.assertFalse(quiz.show_answers)
        self.assertTrue(quiz.randomize)

        self.assertTrue('<strong>Lorem Ipsum</strong> quiz created'
                        in response.cookies['messages'].value)
