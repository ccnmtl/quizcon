"""
Integrationserver: bring up a test server populated with fake data

This is meant to be used for two cases:
- Front-end integration testing: just point the testing framework at the
running test server.
- Local dev: It can be tedious to recreate models for local dev after
deleting a database.

This is largely copied from django.core.management.commands.testserver
It reimplements the testserver functionality except that it generates
test data dynamically using factories
"""

from quizcon.main.tests.factories import (UserFactory, CourseFactory,
                                          QuizFactory)
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


def reset_test_models():
    call_command('flush', verbosity=0, interactive=False)

    # Create some models
    UserFactory.create(
        username='superuser',
        first_name='Super',
        last_name='User',
        email='superuser@example.com',
        is_superuser=True,
        is_staff=True
    )

    faculty = UserFactory.create(
        username='faculty_one',
        first_name='Faculty',
        last_name='One',
        email='faculty_one@example.com'
    )

    student = UserFactory.create(
        username='student_one',
        first_name='Student',
        last_name='One',
        email='student_one@example.com'
    )
    course = CourseFactory.create()
    course.group.user_set.add(student)
    course.group.user_set.add(faculty)
    course.faculty_group.user_set.add(faculty)

    # add test quiz
    QuizFactory(course=course, title='A Bird Quiz')


class Command(BaseCommand):
    help = 'Runs a development server with data created by factories.'

    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', '--no-input', action='store_false',
            dest='interactive',
            help='Tells Django not to prompt the user for input.',
        )
        parser.add_argument(
            '--addrport', default='',
            help='Port number or ipaddr:port to run the server on.',
        )
        parser.add_argument(
            '--ipv6', '-6', action='store_true', dest='use_ipv6',
            help='Tells Django to use an IPv6 address.',
        )

    def handle(self, *fixture_labels, **options):
        verbosity = options['verbosity']

        # Create a test database.
        db_name = connection.creation.create_test_db(
            verbosity=verbosity, autoclobber=True, serialize=False)

        reset_test_models()

        shutdown_message = (
            '\nServer stopped.' +
            '\nNote that the test database, {}, '.format(db_name) +
            'has not been deleted. You can explore it on your own.'
        )

        # - Because we defer to 'runserver' there's no easy way to clean up the
        # test database. Therefore, we always autoclobber it
        # - Turn off auto-reloading because it causes this handle() method
        # to be called multiple times.
        # - Always use_threading, requests from the integration server need
        # to be handled concurrently
        call_command(
            'runserver',
            # Use the --insecure flag in order to serve static files here,
            # even though I have DEBUG=False for testing.
            # https://docs.djangoproject.com/en/3.0/ref/contrib/staticfiles/#runserver
            insecure=True,
            addrport=options['addrport'],
            shutdown_message=shutdown_message,
            use_reloader=False,
            use_ipv6=options['use_ipv6'],
            use_threading=True
        )
