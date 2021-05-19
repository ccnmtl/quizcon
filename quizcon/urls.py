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
    path('', views.IndexView.as_view()),
    path('admin/', admin.site.urls),

    path('accounts/', include('django.contrib.auth.urls')),

    path(r'lti/', include('lti_provider.urls')),
    path(r'course/lti/create/',
         views.LTICourseCreate.as_view(), name='lti-course-create'),
    url(r'^course/lti/(?P<context>\w[^/]*)/$',
        views.LTICourseSelector.as_view(), name='lti-course-select'),
    url(r'^course/(?P<pk>\d+)/$', views.CourseDetailView.as_view(),
        name='course-detail-view'),
    path('_impersonate/', include('impersonate.urls')),
    path('stats/', TemplateView.as_view(template_name="stats.html")),
    path('smoketest/', include('smoketest.urls')),
    path('infranil/', include('infranil.urls')),
    path('uploads/<str:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^quiz/(?P<assignment_id>\d+)/', views.LTIAssignment1View.as_view(),
        name='quiz'),
    url(r'^assignment/success', TemplateView.as_view(
        template_name='main/assignment_success.html'),
        name='assignment-success')
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]
