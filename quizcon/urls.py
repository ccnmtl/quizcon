from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from django.views.static import serve
from django_cas_ng import views as cas_views
from quizcon.main import views

admin.autodiscover()

auth_urls = re_path(r'^accounts/', include('django.contrib.auth.urls'))

urlpatterns = [
    auth_urls,
    path('admin/', admin.site.urls),

    path('accounts/', include('django.contrib.auth.urls')),
    path('cas/login', cas_views.LoginView.as_view(),
         name='cas_ng_login'),
    path('cas/logout', cas_views.LogoutView.as_view(),
         name='cas_ng_logout'),

    path(r'lti/', include('lti_provider.urls')),
    path(r'course/lti/create/',
         views.LTICourseCreate.as_view(), name='lti-course-create'),
    re_path(r'^course/lti/(?P<context>\w[^/]*)/$',
            views.LTICourseSelector.as_view(), name='lti-course-select'),
    re_path('^$', views.DashboardView.as_view(),
            name='course-list-view'),
    re_path(r'^course/(?P<pk>\d+)/$', views.CourseDetailView.as_view(),
            name='course-detail-view'),
    path('_impersonate/', include('impersonate.urls')),
    path('stats/', TemplateView.as_view(template_name="stats.html")),
    path('smoketest/', include('smoketest.urls')),
    path('uploads/<str:path>', serve, {'document_root': settings.MEDIA_ROOT}),

    re_path(r'^quiz/(?P<pk>\d+)/update/$', views.UpdateQuizView.as_view(),
            name='update-quiz'),
    re_path(r'^quiz/(?P<pk>\d+)/delete/$', views.DeleteQuizView.as_view(),
            name='delete-quiz'),
    re_path(r'^quiz/(?P<pk>\d+)/clone/$', views.CloneQuizView.as_view(),
            name='clone-quiz'),
    re_path(r'^quiz/(?P<pk>\d+)/report/$', views.AnalyticsQuizView.as_view(),
            name='report-quiz'),
    re_path(r'^quiz/(?P<pk>\d+)/reorder/$',
            views.ReorderQuestionsView.as_view(),
            name='reorder-questions'),
    re_path(r'^quiz/(?P<pk>\d+)/question/create/$',
            views.CreateQuestionView.as_view(), name='create-question'),
    re_path(r'^quiz/(?P<pk>\d+)/', views.QuizDetailView.as_view(),
            name='quiz-detail'),

    re_path(r'^assignment/(?P<pk>\d+)/(?P<submission_id>\d+)/$',
            views.LTIAssignmentView.as_view(),
            name='quiz-submission'),
    re_path(r'^assignment/(?P<pk>\d+)/start/',
            views.AddTimeView.as_view(),
            name='submission-creation'),
    re_path(r'^assignment/(?P<pk>\d+)/',
            views.LTIAssignmentView.as_view(),
            name='quiz'),
    re_path(r'^assignment/grade/(?P<pk>\d+)/$',
            views.LTISpeedGraderView.as_view(),
            name='grade'),

    re_path(r'^course/(?P<pk>\d+)/quiz/create/$',
            views.CreateQuizView.as_view(),
            name='create-quiz'),
    re_path(r'^question/(?P<pk>\d+)/update/$',
            views.UpdateQuestionView.as_view(),
            name='update-question'),
    re_path(r'^question/(?P<pk>\d+)/delete/$',
            views.DeleteQuestionView.as_view(),
            name='delete-question'),

    re_path('^contact/', include('contactus.urls'))
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]
