from django.core import mail
from django.test.testcases import TestCase

from quizcon.main.tests.factories import UserFactory
from quizcon.main.utils import send_template_email


class UtilTest(TestCase):

    def test_send_template_email(self):
        user = UserFactory()
        with self.settings(SERVER_EMAIL='quizcon@example.com'):
            send_template_email('foo', 'main/notify_lti_course_connect.txt',
                                {'user': user}, 'abc123@columbia.edu')
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, 'foo')
            self.assertEquals(mail.outbox[0].from_email,
                              'quizcon@example.com')
            self.assertTrue(mail.outbox[0].to, ['abc123@columbia.edu'])
