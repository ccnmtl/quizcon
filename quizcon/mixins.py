from courseaffils.lib import in_course
from courseaffils.models import Course
from django.contrib.auth.mixins import UserPassesTestMixin
from quizcon.main.models import Quiz


class LoggedInCourseMixin(UserPassesTestMixin):
    """Mixin for class-based views that handle courseaffils Course

    Returns True if a user is a member/student of a given course.

    Note that this mixin can not be stacked with other
    mixins that implement test_func
    https://docs.djangoproject.com/en/2.2/topics/auth/default/#django.contrib.auth.mixins.UserPassesTestMixin
    """
    def test_func(self):
        # Because this is a mixin in a class-based view, its not neccessary to
        # to raise a 404 response here, hence this pattern.
        try:
            course_pk = self.kwargs.get('pk')
            course = Course.objects.get(pk=course_pk)
        except Course.DoesNotExist:
            return False

        return (
            in_course(self.request.user.username, course) or
            course.is_true_faculty(self.request.user)
        )


class LoggedInFacultyMixin(UserPassesTestMixin):
    """Mixin for class-based views that handle courseaffils Course

    Returns True if a user is an instructor of a given course.

    Note that this mixin can not be stacked with other
    mixins that implement test_func
    https://docs.djangoproject.com/en/2.2/topics/auth/default/#django.contrib.auth.mixins.UserPassesTestMixin
    """
    def test_func(self):
        try:
            course_pk = self.kwargs.get('pk')
            course = Course.objects.get(pk=course_pk)
        except Course.DoesNotExist:
            return False

        return course.is_true_faculty(self.request.user)


class LoggedInSuperuserMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser


class UpdateQuizPermissionMixin(UserPassesTestMixin):

    def test_func(self):
        try:
            quiz_pk = self.kwargs.get('pk')
            quiz = Quiz.objects.get(pk=quiz_pk)
        except Quiz.DoesNotExist:
            return False

        return quiz.course.is_true_faculty(self.request.user)
