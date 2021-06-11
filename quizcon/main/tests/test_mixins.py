from django.test.client import RequestFactory
from django.test.testcases import TestCase
from quizcon.main.tests.factories import (
    CourseTestMixin, UserFactory, QuizFactory, CourseFactory)
from quizcon.mixins import LoggedInFacultyMixin, LoggedInCourseMixin, \
    LoggedInSuperuserMixin, UpdateQuizPermissionMixin


class LoggedInCourseMixinTest(CourseTestMixin, TestCase):

    def test_permissions(self):
        self.setup_course()

        mixin = LoggedInCourseMixin()
        mixin.request = RequestFactory().get('/')

        # test exception path - course does not exist - returns False
        mixin.kwargs = {'pk': 42}
        self.assertFalse(mixin.test_func())

        # test success path - user is faculty return True
        mixin.kwargs = {'pk': self.course.pk}
        mixin.request.user = self.faculty
        self.assertTrue(mixin.test_func())

        # test failure path - user is not faculty returns False
        mixin.request.user = self.student
        self.assertTrue(mixin.test_func())


class LoggedInFacultyMixinTest(CourseTestMixin, TestCase):

    def test_permissions(self):
        self.setup_course()

        mixin = LoggedInFacultyMixin()
        mixin.request = RequestFactory().get('/')

        # test exception path - course does not exist - returns False
        mixin.kwargs = {'pk': 42}
        self.assertFalse(mixin.test_func())

        # test success path - user is faculty return True
        mixin.kwargs = {'pk': self.course.pk}
        mixin.request.user = self.faculty
        self.assertTrue(mixin.test_func())

        # test failure path - user is not faculty returns False
        mixin.request.user = self.student
        self.assertFalse(mixin.test_func())


class LoggedInSuperUserMixinTest(CourseTestMixin, TestCase):

    def test_permissions(self):
        self.setup_course()
        su = UserFactory(is_staff=True, is_superuser=True)

        mixin = LoggedInSuperuserMixin()
        mixin.request = RequestFactory().get('/')

        # test failure path - user is faculty returns False
        mixin.request.user = self.faculty
        self.assertFalse(mixin.test_func())

        # test failure path - user is student returns False
        mixin.request.user = self.student
        self.assertFalse(mixin.test_func())

        # test success path - superuser returns True
        mixin.request.user = su
        self.assertTrue(mixin.test_func())


class UpdateQuizPermissionUpdateTest(CourseTestMixin, TestCase):

    def test_permissions(self):
        self.setup_course()

        alt_course = CourseFactory.create()
        alt_student = UserFactory()
        alt_faculty = UserFactory()
        alt_course.group.user_set.add(alt_student)
        alt_course.group.user_set.add(alt_faculty)
        alt_course.faculty_group.user_set.add(alt_faculty)

        quiz = QuizFactory(course=self.course)

        mixin = UpdateQuizPermissionMixin()
        mixin.request = RequestFactory().get('/')

        # failure - quiz does not exist
        mixin.kwargs = {'pk': 42}
        self.assertFalse(mixin.test_func())

        # success - faculty in our course can edit & delete
        mixin.kwargs = {'pk': quiz.pk}
        mixin.request.user = self.faculty
        self.assertTrue(mixin.test_func())

        # failure - student in our course cannot edit or delete
        mixin.request.user = self.student
        self.assertFalse(mixin.test_func())

        # failure - faculty from another course cannot edit or delete
        mixin.request.user = alt_faculty
        self.assertFalse(mixin.test_func())

        # failure - student from another course cannot edit or delete
        mixin.request.user = alt_student
        self.assertFalse(mixin.test_func())

        # failure - superusers can't randomly edit or delete either
        mixin.request.user = UserFactory(is_staff=True, is_superuser=True)
        self.assertFalse(mixin.test_func())
