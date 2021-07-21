import datetime
from random import randrange

from courseaffils.models import Course
from django.contrib.auth.models import User, Group
import factory
from quizcon.main.models import Quiz, Question, Marker, QuizSubmission, \
    QuestionResponse, QuestionResponseMarker


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence('user{}'.format)
    password = factory.PostGenerationMethodCall('set_password', 'test')
    email = 'foo@bar.com'


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
    name = factory.Sequence('group {}'.format)


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course
    title = factory.Sequence('course {}'.format)
    group = factory.SubFactory(GroupFactory)
    faculty_group = factory.SubFactory(GroupFactory)

    @factory.post_generation
    def course_info(obj, create, extracted, **kwargs):
        obj.info.term = randrange(1, 3)
        current_year = datetime.datetime.now().year
        obj.info.year = randrange(current_year, current_year + 5)
        obj.info.save()


class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz

    course = factory.SubFactory(CourseFactory)
    title = 'Lorem Ipsum'
    description = 'dolor sit amet'
    multiple_attempts = 2
    show_answers = False
    randomize = True
    scoring_scheme = 2


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    quiz = factory.SubFactory(QuizFactory)
    text = 'Lorem Ipsum'
    explanation = 'consectetur adipiscing elit'
    ordinality = -1

    @factory.post_generation
    def create_marker(obj, create, extracted, **kwargs):
        obj.marker_set.add(MarkerFactory(question=obj))
        obj.marker_set.add(MarkerFactory(question=obj))
        obj.marker_set.add(MarkerFactory(question=obj))


class MarkerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Marker

    question = factory.SubFactory(QuestionFactory)
    label = factory.Sequence(lambda n: "Marker%03d" % n)
    correct = False
    value = -1


class QuizSubmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuizSubmission

    @factory.post_generation
    def create_question_responses(obj, create, extracted, **kwargs):
        for question in obj.quiz.question_set.all():
            QuestionResponseFactory(submission=obj, question=question)


class QuestionResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuestionResponse

    selected_position = 0

    @factory.post_generation
    def create_marker_responses(obj, create, extracted, **kwargs):
        for idx, marker in enumerate(obj.question.random_markers()):
            QuestionResponseMarkerFactory(
                response=obj, marker=marker, ordinal=idx)


class QuestionResponseMarkerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuestionResponseMarker


class CourseTestMixin(object):
    def setup_course(self) -> None:
        # Users
        self.superuser: User = UserFactory.create(
            first_name='Super',
            last_name='User',
            email='superuser@example.com',
            is_superuser=True
        )
        self.student: User = UserFactory.create(
            first_name='Student',
            last_name='One',
            email='studentone@example.com'
        )
        self.faculty: User = UserFactory.create(
            first_name='Faculty',
            last_name='One',
            email='facultyone@example.com'
        )

        # Registrar Course
        self.course = CourseFactory.create()
        self.course.group.user_set.add(self.student)
        self.course.group.user_set.add(self.faculty)
        self.course.faculty_group.user_set.add(self.faculty)
