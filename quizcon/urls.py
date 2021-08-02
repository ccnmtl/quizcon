from django.urls import include, path
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from django.views.static import serve
from quizcon.main import views

admin.autodiscover()

auth_urls = url(r'^accounts/', include('django.contrib.auth.urls'))
if hasattr(settings, 'CAS_BASE'):
    auth_urls = url(r'^accounts/', include('djangowind.urls'))

urlpatterns = [
    auth_urls,
    path('admin/', admin.site.urls),

    path('accounts/', include('django.contrib.auth.urls')),

    path(r'lti/', include('lti_provider.urls')),
    path(r'course/lti/create/',
         views.LTICourseCreate.as_view(), name='lti-course-create'),
    url(r'^course/lti/(?P<context>\w[^/]*)/$',
        views.LTICourseSelector.as_view(), name='lti-course-select'),
    url('^$', views.DashboardView.as_view(),
        name='course-list-view'),
    url(r'^course/(?P<pk>\d+)/$', views.CourseDetailView.as_view(),
        name='course-detail-view'),
    path('_impersonate/', include('impersonate.urls')),
    path('stats/', TemplateView.as_view(template_name="stats.html")),
    path('smoketest/', include('smoketest.urls')),
    path('infranil/', include('infranil.urls')),
    path('uploads/<str:path>', serve, {'document_root': settings.MEDIA_ROOT}),

    url(r'^quiz/(?P<pk>\d+)/update/$', views.UpdateQuizView.as_view(),
        name='update-quiz'),
    url(r'^quiz/(?P<pk>\d+)/delete/$', views.DeleteQuizView.as_view(),
        name='delete-quiz'),
    url(r'^quiz/(?P<pk>\d+)/clone/$', views.CloneQuizView.as_view(),
        name='clone-quiz'),
    url(r'^quiz/(?P<pk>\d+)/question/create/$',
        views.CreateQuestionView.as_view(), name='create-question'),
    url(r'^quiz/(?P<pk>\d+)/', views.QuizDetailView.as_view(),
        name='quiz-detail'),

    url(r'^assignment/(?P<pk>\d+)/(?P<submission_id>\d+)/$',
        views.LTIAssignmentView.as_view(),
        name='quiz-submission'),
    url(r'^assignment/(?P<pk>\d+)/',
        views.LTIAssignmentView.as_view(),
        name='quiz'),
    url(r'^assignment/grade/(?P<pk>\d+)/$',
        views.LTISpeedGraderView.as_view(),
        name='grade'),

    url(r'^course/(?P<pk>\d+)/quiz/create/$', views.CreateQuizView.as_view(),
        name='create-quiz'),
    url(r'^question/(?P<pk>\d+)/update/$', views.UpdateQuestionView.as_view(),
        name='update-question'),
    url(r'^question/(?P<pk>\d+)/delete/$', views.DeleteQuestionView.as_view(),
        name='delete-question')
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]
