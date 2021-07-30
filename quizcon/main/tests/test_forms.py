from django.test import TestCase
from quizcon.main.forms import QuestionForm
from quizcon.main.tests.factories import QuestionFactory


class QuestionFormTest(TestCase):
    def test_init(self):
        form = QuestionForm([], {})
        self.assertEqual(form.initial, {})

        question = QuestionFactory()
        form = QuestionForm([], {'instance': question})
        self.assertEqual(form.initial, {})
