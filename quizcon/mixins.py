from courseaffils.lib import in_course
from courseaffils.models import Course
from django.contrib.auth.mixins import UserPassesTestMixin
from quizcon.main.models import Quiz, Question, QuizSubmission


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


class UpdateQuestionPermissionMixin(UserPassesTestMixin):

    def test_func(self):
        try:
            question_pk = self.kwargs.get('pk')
            question = Question.objects.get(pk=question_pk)
        except Question.DoesNotExist:
            return False

        return question.quiz.course.is_true_faculty(self.request.user)


class AssignmentPermissionMixin(UserPassesTestMixin):

    def test_func(self):
        try:
            assignment_id = self.kwargs.get('assignment_id')

            assignment = Quiz.objects.get(pk=assignment_id)

            # course faculty can see the assignment & submission
            if assignment.quiz.course.is_true_faculty(self.request.user):
                return True

            # non-course students cannot see anything
            if not assignment.course.is_true_member(self.request.user):
                return False

            # course students can only see their own submissions
            submission_id = self.kwargs.get('submission_id', -1)
            submission = QuizSubmission.objects.get(id=int(submission_id))
            return submission.user == self.request.user

        except KeyError:
            # expecting an assignment id
            return False
        except Quiz.DoesNotExist:
            return False
        except QuizSubmission.DoesNotExist:
            # the submission may not exist
            return True


class SubmissionPermissionMixin(UserPassesTestMixin):

    def test_func(self):
        try:
            submission_id = self.request.GET.get('submission_id')
            submission = QuizSubmission.objects.get(pk=submission_id)

            # course faculty can see all submissions
            if submission.submitted.quiz.course.is_true_faculty(
                                                            self.request.user):
                return True

            # non-course students cannot see anything
            if not submission.submitted.quiz.course.is_true_member(
                                                            self.request.user):
                return False

            # course students can only see their own submissions
            return submission.user == self.request.user

        except KeyError:
            # exception a submission id
            return False
        except QuizSubmission.DoesNotExist:
            # exception a valid submission id
            return False
