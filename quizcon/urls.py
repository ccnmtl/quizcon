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

    path('_impersonate/', include('impersonate.urls')),
    path('stats/', TemplateView.as_view(template_name="stats.html")),
    path('smoketest/', include('smoketest.urls')),
    path('infranil/', include('infranil.urls')),
    path('uploads/<str:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]
