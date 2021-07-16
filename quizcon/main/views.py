import re

from courseaffils.columbia import WindTemplate, CanvasTemplate
from courseaffils.models import Course
from courseaffils.views import get_courses_for_instructor
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin
)
from django.contrib.auth.models import Group
from django.http import (
    HttpResponseRedirect, HttpResponse
)
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView)
from lti_provider.mixins import LTIAuthMixin
from lti_provider.models import LTICourseContext
from quizcon.main.forms import QuizForm, QuestionForm
from quizcon.main.models import Quiz, Question, Marker
from quizcon.main.utils import send_template_email
from quizcon.mixins import (
    LoggedInCourseMixin, LoggedInFacultyMixin, UpdateQuizPermissionMixin,
    UpdateQuestionPermissionMixin)
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator


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


class DashboardView(LoginRequiredMixin, View):
    template_name = 'main/courses.html'
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs) -> HttpResponse:

        ctx = {
            'user': request.user,
            'courses': get_courses_for_instructor(
                self.request.user).order_by('title'),
            'page_type': 'dashboard'
        }
        return render(request, self.template_name, ctx)

    def get(self, request, *args, **kwargs) -> HttpResponse:
        ctx = {
            'user': request.user,
            'courses': get_courses_for_instructor(
                self.request.user).order_by('title'),
            'page_type': 'dashboard'
        }
        return render(request, self.template_name, ctx)


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
            '<strong>Success!</strong> ' +
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


@method_decorator(xframe_options_exempt, name='dispatch')
class LTIAssignmentView(LTIAuthMixin, LoginRequiredMixin, TemplateView):

    template_name = 'main/assignment.html'

    def get_context_data(self, **kwargs):
        return {
            'is_student': self.lti.lis_result_sourcedid(self.request),
            'course_title': self.lti.course_title(self.request),
            'number': 1,
            'assignment_id': kwargs.get('assignment_id')
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
            '<strong>{}</strong> quiz created.'.format(title),
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
            '<strong>{}</strong> quiz updated.'.format(title),
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
            '<strong>{}</strong> quiz deleted.'.format(
                self.object.title),
            extra_tags='safe'
        )

        return reverse('course-detail-view',
                       kwargs={'pk': self.object.course.pk})


class QuizDetailView(UpdateQuizPermissionMixin, DetailView):
    model = Quiz

    def get_context_data(self, **kwargs):
        return {
            'quiz': self.object
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

        text = form.cleaned_data['text']
        messages.add_message(
            self.request, messages.SUCCESS,
            '<strong>{}</strong> question created.'.format(text),
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

        text = form.cleaned_data['text']
        messages.add_message(
            self.request, messages.SUCCESS,
            '<strong>{}</strong> question updated.'.format(text),
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
            '<strong>{}</strong> question deleted.'.format(
                self.object.text),
            extra_tags='safe'
        )

        return reverse('update-quiz',
                       kwargs={'pk': self.object.quiz.pk})
