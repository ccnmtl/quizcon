from django.test import TestCase
from django.urls.base import reverse
from quizcon.main.models import Quiz, Question
from quizcon.main.tests.factories import (
    CourseTestMixin, QuizFactory, QuestionFactory
)


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
                'randomize': True, 'scoring_scheme': 3})

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


class CreateQuestionView(CourseTestMixin, TestCase):

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
            {'text': 'Lorem Ipsum', 'description': 'dolor sit amet',
             'explanation': 'consectetur adipiscing elit', 'ordinality': -1,
             'quiz': self.quiz.pk})

        self.assertEqual(self.quiz.question_set.count(), 1)
        question = self.quiz.question_set.first()
        self.assertEqual(question.text, 'Lorem Ipsum')
        self.assertEqual(question.description, 'dolor sit amet')
        self.assertEqual(question.explanation, 'consectetur adipiscing elit')
        self.assertEqual(question.ordinality, -1)

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
                'description': 'Quiz updated.',
                'explanation': 'Ch-ch-changes', 'ordinality': 0})

        self.question.refresh_from_db()
        self.assertEqual(self.question.text, 'Alpha')
        self.assertEqual(self.question.description, 'Quiz updated.')
        self.assertEqual(self.question.explanation, 'Ch-ch-changes')
        self.assertEqual(self.question.ordinality, 0)


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
