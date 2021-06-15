from django.test import TestCase
from django.urls.base import reverse
from quizcon.main.tests.factories import CourseTestMixin, QuizFactory
from quizcon.main.models import Quiz


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
                'multiple_attempts': True, 'show_answers': False,
                'randomize': True})

        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, 'Alpha')
        self.assertEqual(self.quiz.description, 'Quiz updated.')
        self.assertTrue(self.quiz.multiple_attempts)
        self.assertTrue(self.quiz.randomize)
        self.assertFalse(self.quiz.show_answers)


class DeleteQuizTest(CourseTestMixin, TestCase):
    def setUp(self):
        self.setup_course()
        self.quiz = QuizFactory(course=self.course)

    def test_delete_quiz(self):
        url = reverse('delete-quiz', kwargs={'pk': self.quiz.pk})

        self.client.login(username=self.faculty.username, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url)
        self.assertRedirects(response, '/course/' + str(self.course.pk) + '/')
        with self.assertRaises(Quiz.DoesNotExist):
            Quiz.objects.get(id=self.quiz.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.course.quiz_set.count(), 0)
