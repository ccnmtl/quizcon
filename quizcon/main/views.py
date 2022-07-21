import json
import re
import time
from datetime import date

from courseaffils.columbia import WindTemplate, CanvasTemplate
from courseaffils.models import Course
from courseaffils.views import get_courses_for_user
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin
)
from django.contrib.auth.models import Group
from django.http import (
    HttpResponseRedirect, HttpResponse
)
from django.shortcuts import get_object_or_404
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView)
from lti_provider.mixins import LTIAuthMixin
from lti_provider.models import LTICourseContext
from pylti.common import LTIPostMessageException, post_message
from quizcon.main.forms import QuizForm, QuestionForm
from quizcon.main.models import (
    Quiz, Question, Marker, QuizSubmission,
    QuestionResponse, QuestionResponseMarker)
from quizcon.main.utils import send_template_email
from quizcon.mixins import (
    LoggedInCourseMixin, LoggedInFacultyMixin, UpdateQuizPermissionMixin,
    UpdateQuestionPermissionMixin)


class IndexView(TemplateView):
    template_name = "main/index.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return super(IndexView, self).dispatch(request, *args, *kwargs)

        qs = Course.objects.filter(group__user=request.user)
        if qs.count() == 1:
            course_url = reverse('course-detail-view', args=[qs.first().id])
            return HttpResponseRedirect(course_url)
        else:
            return HttpResponseRedirect(reverse('course-list-view'))


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'main/courses.html'
    http_method_names = ['get', 'post']

    def get_context_data(self, **kwargs):
        return {
            'user': self.request.user,
            'courses': get_courses_for_user(
                self.request.user).order_by('title'),
            'page_type': 'dashboard'
        }


class LTICourseCreate(LoginRequiredMixin, View):

    def notify_staff(self, course):
        data = {
            'course': course,
            'user': self.request.user
        }
        send_template_email(
            'Quizzing with Confidence Course Connected',
            'main/notify_lti_course_connect.txt',
            data, settings.SERVER_EMAIL)

    def thank_faculty(self, course):
        user = self.request.user
        send_template_email(
            'Quizzing with Confidence Course Connected',
            'main/lti_course_connect.txt',
            {'course': course},
            user.email if user.email else user.username + '@columbia.edu')

    def groups_from_context(self, course_context):
        group, created = Group.objects.get_or_create(name=course_context)
        faculty_group, created = Group.objects.get_or_create(
            name='{}_faculty'.format(course_context))
        return (group, faculty_group)

    def groups_from_sis_course_id(self, attrs):
        user = self.request.user
        st_affil = WindTemplate.to_string(attrs)
        group, created = Group.objects.get_or_create(name=st_affil)
        user.groups.add(group)

        attrs['member'] = 'fc'
        fc_affil = WindTemplate.to_string(attrs)
        faculty_group, created = Group.objects.get_or_create(name=fc_affil)
        user.groups.add(faculty_group)
        return (group, faculty_group)

    def add_yt_to_course(self, sis_course_id, course):
        """
        Sets the year and term attributes on a course if
        they can be determined from a sis_course_id
        """

        # CanvasTemplate matches a CU course string
        cu_course = CanvasTemplate.to_dict(sis_course_id)
        # TC courses use a different format
        tc_course = re.match(
            (r'(?P<year>\d{4})(?P<term>\d{2})'), sis_course_id)

        if cu_course:
            course.info.term = cu_course['term']
            course.info.year = cu_course['year']
            course.info.save()
        elif tc_course:
            course.info.term = tc_course['term']
            course.info.year = tc_course['year']
            course.info.save()

    def post(self, *args, **kwargs):
        user = self.request.user
        course_context = self.request.POST.get('lms_course')
        title = self.request.POST.get('lms_course_title')
        sis_course_id = '' if self.request.POST['sis_course_id'] == 'None' \
            else self.request.POST['sis_course_id']

        # This view needs to take four steps to create a course
        # 1. Create groups for students and faculty, named after the course
        # 2. Create the course
        # 3. Set the year and term, if applicable
        # 4. Create the course context

        # 1. Create groups
        cu_course = CanvasTemplate.to_dict(sis_course_id)
        if cu_course:
            (group, faculty_group) = self.groups_from_sis_course_id(cu_course)
        else:
            (group, faculty_group) = self.groups_from_context(course_context)

        user.groups.add(group)
        user.groups.add(faculty_group)

        # 2. Create the course
        course, created = Course.objects.get_or_create(
            group=group, faculty_group=faculty_group,
            defaults={'title': title})

        # 3. Set the term and year of the course
        if sis_course_id:
            self.add_yt_to_course(sis_course_id, course)

        # 4. Create the course context
        (ctx, created) = LTICourseContext.objects.get_or_create(
            group=group, faculty_group=faculty_group,
            lms_course_context=course_context)

        messages.add_message(
            self.request, messages.INFO,
            'Success! ' +
            '{} is connected to Quizzing with Confidence.'.format(title))

        self.notify_staff(course)
        self.thank_faculty(course)

        return HttpResponseRedirect(reverse('lti-landing-page'))


class LTICourseSelector(LoginRequiredMixin, View):

    def get(self, request, context):
        try:
            messages.add_message(
                request, messages.INFO,
                'Reminder: please log out of Quizzing with Confidence '
                'after you log out of Courseworks.')

            ctx = LTICourseContext.objects.get(lms_course_context=context)
            url = u'/course/{}/'.format(ctx.group.course.id)
        except LTICourseContext.DoesNotExist:
            url = '/'

        return HttpResponseRedirect(url)


class CourseDetailView(LoggedInCourseMixin, DetailView):
    model = Course

    def get_context_data(self, **kwargs):
        is_faculty = self.object.is_true_faculty(self.request.user)

        return {
            'course': self.object,
            'is_faculty': is_faculty,
        }


class AddTimeView(LTIAuthMixin, View):
    http_method_names = ['get']

    def get(self, *args, **kwargs):
        assignment_id = self.kwargs.get('pk', None)
        quiz = get_object_or_404(Quiz, pk=assignment_id)
        QuizSubmission.objects.create(
                    quiz=quiz, user=self.request.user, time=time.time())

        return HttpResponseRedirect(reverse('quiz',
                                    kwargs={'pk': assignment_id}))


@method_decorator(xframe_options_exempt, name='dispatch')
class LTIAssignmentView(LTIAuthMixin, TemplateView):

    template_name = 'main/lti_assignment.html'
    http_method_names = ['get', 'post']

    def get(self, *args, **kwargs):
        assignment_id = self.kwargs.get('pk', None)
        quiz = get_object_or_404(Quiz, pk=assignment_id)
        submission_id = self.kwargs.get('submission_id', -1)
        submission = QuizSubmission.objects.filter(
            user=self.request.user, quiz=quiz).order_by('-modified_at').first()

        if submission_id == -1 and submission:
            if submission.submitted:
                data = {'pk': self.kwargs.get('pk'),
                        'submission_id': submission.id}

                url = reverse('quiz-submission', kwargs=data)

                return HttpResponseRedirect(url)

        return super(LTIAssignmentView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        assignment_id = self.kwargs.get('pk')
        quiz = get_object_or_404(Quiz, pk=assignment_id)
        today = date.today()
        submission = QuizSubmission.objects.filter(
            user=self.request.user, quiz=quiz).order_by('-modified_at').first()
        remaining = None

        if submission and submission.time:
            difference = time.time() - submission.time
            time_remaining = (quiz.time * 60) - difference
            if time_remaining <= 0:
                remaining = 0
            else:
                remaining = time_remaining

        is_faculty = quiz.course.is_true_faculty(self.request.user)
        is_student = (quiz.course.is_true_member(self.request.user) and
                      not is_faculty)

        return {
            'is_student': is_student,
            'is_faculty': is_faculty,
            'quiz': quiz,
            'num_markers': range(13),
            'submission': submission,
            'today': today,
            'remaining': remaining
        }

    def get_launch_url(self, submission):
        url = '/lti/?assignment=grade&pk={}'.format(submission.id)
        return self.request.build_absolute_uri(url)

    def message_identifier(self):
        return '{:.0f}'.format(time.time())

    def post_score(self, submission):
        """
        Post grade to LTI consumer using XML

        :param: score: 0 <= score <= 1. (Score MUST be between 0 and 1)
        :return: True if post successful and score valid
        :exception: LTIPostMessageException if call failed
        """
        score = submission.user_score()
        launch_url = self.get_launch_url(submission)
        print(launch_url)

        xml = self.lti.generate_request_xml(
            self.message_identifier(), 'replaceResult',
            self.lti.lis_result_sourcedid(self.request), score, launch_url)

        if post_message(self.lti.consumers(),
                        self.lti.oauth_consumer_key(self.request),
                        self.lti.lis_outcome_service_url(self.request), xml):
            return True
        else:
            msg = ('An error occurred while saving your score. '
                   'Please try again.')
            messages.add_message(self.request, messages.ERROR, msg)

            # Something went wrong, display an error.
            # Is 500 the right thing to do here?
            raise LTIPostMessageException('Post grade failed')

    def post(self, *args, **kwargs):
        assignment_id = self.kwargs.get('pk')
        quiz = get_object_or_404(Quiz, pk=assignment_id)

        # If a quiz is not timed, create Submission object here
        sub, created = QuizSubmission.objects.get_or_create(
            user=self.request.user, quiz=quiz)
        submission = QuizSubmission.objects.filter(pk=sub.id).first()

        for question in quiz.question_set.all():
            selected_position = None
            if self.request.POST.get(str(question.pk)):
                selected_position = self.request.POST.get(str(question.pk))
            else:
                selected_position = 12

            # import pdb; pdb.set_trace()
            response = QuestionResponse.objects.create(
                question=question, submission=submission,
                selected_position=selected_position)
            key = 'question-{}-markers'.format(question.pk)
            markers = json.loads(self.request.POST.get(key))
            for idx, marker_id in enumerate(markers):
                marker = get_object_or_404(Marker, pk=marker_id)
                QuestionResponseMarker.objects.create(
                    response=response, marker=marker, ordinal=idx)

        self.post_score(submission)

        data = {'pk': self.kwargs.get('pk'), 'submission_id': submission.id}
        url = reverse('quiz-submission', kwargs=data)
        return HttpResponseRedirect(url)


@method_decorator(xframe_options_exempt, name='dispatch')
class LTISpeedGraderView(LTIAuthMixin, TemplateView):
    template_name = 'main/lti_speedgrader.html'

    def get_context_data(self, **kwargs):
        submission_id = self.kwargs.get('pk')
        submission = get_object_or_404(QuizSubmission, pk=submission_id)

        is_faculty = submission.quiz.course.is_true_faculty(self.request.user)
        is_student = (
            submission.quiz.course.is_true_member(self.request.user) and
            not is_faculty)

        return {
            'is_student': is_student,
            'is_faculty': is_faculty,
            'num_markers': range(13),
            'quiz': submission.quiz,
            'submission': submission
        }


class CreateQuizView(LoggedInFacultyMixin, CreateView):
    model = Quiz
    form_class = QuizForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        ctx['course'] = get_object_or_404(Course, pk=pk)
        return ctx

    def get_success_url(self):
        return reverse('course-detail-view',
                       kwargs={'pk': self.kwargs.get('pk')})

    def form_valid(self, form):
        result = CreateView.form_valid(self, form)

        title = form.cleaned_data['title']
        messages.add_message(
            self.request, messages.SUCCESS,
            '{} quiz created.'.format(title),
            extra_tags='safe'
        )

        return result


class UpdateQuizView(UpdateQuizPermissionMixin, UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = "main/quiz_form_edit.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['course'] = self.object.course
        return ctx

    def get_success_url(self):
        return reverse('course-detail-view',
                       kwargs={'pk': self.object.course.pk})

    def form_valid(self, form):
        result = UpdateView.form_valid(self, form)

        title = form.cleaned_data['title']
        messages.add_message(
            self.request, messages.SUCCESS,
            '{} quiz updated.'.format(title),
            extra_tags='safe'
        )

        return result


class DeleteQuizView(UpdateQuizPermissionMixin, DeleteView):
    model = Quiz
    http_method_names = ['post']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['course'] = self.object.course
        return ctx

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS,
            '{} quiz deleted.'.format(
                self.object.title),
            extra_tags='safe'
        )

        return reverse('course-detail-view',
                       kwargs={'pk': self.object.course.pk})


class QuizDetailView(UpdateQuizPermissionMixin, DetailView):
    model = Quiz

    def get_context_data(self, **kwargs):

        return {
            'quiz': self.object,
            'num_markers': range(13)
        }


class CreateQuestionView(UpdateQuizPermissionMixin, CreateView):
    model = Question
    form_class = QuestionForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        ctx['quiz'] = get_object_or_404(Quiz, pk=pk)
        return ctx

    def get_success_url(self):
        return reverse('update-quiz',
                       kwargs={'pk': self.kwargs.get('pk')})

    def form_valid(self, form):
        result = CreateView.form_valid(self, form)

        Marker.objects.create(question=form.instance,
                              label=form.cleaned_data['answer_label_1'],
                              correct=form.cleaned_data['correct'] == 1,
                              value=1)
        Marker.objects.create(question=form.instance,
                              label=form.cleaned_data['answer_label_2'],
                              correct=form.cleaned_data['correct'] == 2,
                              value=1)
        Marker.objects.create(question=form.instance,
                              label=form.cleaned_data['answer_label_3'],
                              correct=form.cleaned_data['correct'] == 3,
                              value=1)

        messages.add_message(
            self.request, messages.SUCCESS,
            'Congratulations! New question created!',
            extra_tags='safe'
        )

        return result


class UpdateQuestionView(UpdateQuestionPermissionMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = "main/question_form_edit.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['course'] = self.object.quiz.course
        return ctx

    def get_success_url(self):
        return reverse('update-quiz',
                       kwargs={'pk': self.object.quiz.pk})

    def form_valid(self, form):
        result = UpdateView.form_valid(self, form)

        for idx, marker in enumerate(self.object.marker_set.all()):
            marker.correct = form.cleaned_data['correct'] == (idx + 1)
            marker.label = form.cleaned_data['answer_label_' + str(idx + 1)]
            marker.save()

        messages.add_message(
            self.request, messages.SUCCESS,
            'Question updated.',
            extra_tags='safe'
        )

        return result


class DeleteQuestionView(UpdateQuestionPermissionMixin, DeleteView):
    model = Question
    http_method_names = ['post']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['course'] = self.object.quiz.course
        return ctx

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS,
            'Question deleted.',
            extra_tags='safe'
        )

        return reverse('update-quiz',
                       kwargs={'pk': self.object.quiz.pk})


class CloneQuizView(UpdateQuizPermissionMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, pk=self.kwargs.get('pk'))
        cloned_quiz = quiz.clone()
        messages.add_message(
            self.request, messages.SUCCESS,
            '{} quiz created.'.format(cloned_quiz.title),
            extra_tags='safe'
        )

        return HttpResponseRedirect(reverse('update-quiz',
                                    kwargs={'pk': cloned_quiz.pk}))


class AnalyticsQuizView(UpdateQuizPermissionMixin, TemplateView):
    template_name = "main/quiz_report.html"

    def get_context_data(self, **kwargs):
        quiz_id = self.kwargs.get('pk')
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        submissions = []
        count = quiz.quizsubmission_set.count()
        for sub in quiz.quizsubmission_set.all():
            submissions.append(sub)

        return {
            'quiz': quiz,
            'submissions': submissions,
            'total_submissions': count,
            'num_markers': range(13)
        }


class ReorderQuestionsView(UpdateQuizPermissionMixin, View):
    def post(self, request, *args, **kwargs):
        order_json = json.loads(request.body.decode('utf-8'))
        for idx, id in enumerate(order_json['ids']):
            q = Question.objects.get(id=id)
            q.ordinality = idx
            q.save()
        return HttpResponse("Ok")
