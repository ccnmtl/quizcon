import datetime
from random import randrange

from courseaffils.models import Course
from django.contrib.auth.models import User, Group
import factory


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence('user{}'.format)
    password = factory.PostGenerationMethodCall('set_password', 'test')
    email = 'foo@bar.com'


class GroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = Group
    name = factory.Sequence('group {}'.format)


class RegistrarCourseFactory(factory.DjangoModelFactory):
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
            email='facultyone@example.com',
            is_staff=True
        )

        # Registrar Course
        self.registrar_course = RegistrarCourseFactory.create()
        self.registrar_course.group.user_set.add(self.student)
        self.registrar_course.group.user_set.add(self.faculty)
        self.registrar_course.faculty_group.user_set.add(self.faculty)
