# Django settings for quizcon project.
import os.path
import sys
from ctlsettings.shared import common
from courseaffils.columbia import CourseStringMapper

project = 'quizcon'
base = os.path.dirname(__file__)

locals().update(common(project=project, base=base))

PROJECT_APPS = [
    'quizcon.main',
]

USE_TZ = True

INSTALLED_APPS += [  # noqa
    'bootstrap4',
    'contactus',
    'django_extensions',
    'courseaffils',
    'lti_provider',
    'quizcon.main',
]

ALLOWED_HOSTS += ['127.0.0.1']  # noqa

MIDDLEWARE += [ # noqa
    'quizcon.main.middleware.WhoDidItMiddleware'
]

THUMBNAIL_SUBDIR = "thumbs"
LOGIN_REDIRECT_URL = "/"

ACCOUNT_ACTIVATION_DAYS = 7

CONTACT_US_EMAIL = 'ctl-dev@columbia.edu'
SERVER_EMAIL = 'automated@mail.ctl.columbia.edu'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'lti_provider.auth.LTIBackend',
    'django_cas_ng.backends.CASBackend',
]

LTI_TOOL_CONFIGURATION = {
    'title': 'Quizzing With Confidence',
    'description': 'Weighted Multiple Choice Questions',
    'launch_url': 'lti/',
    'embed_url': '',
    'embed_icon_url': '',
    'embed_tool_id': '',
    'landing_url': '{}://{}/course/lti/{}/',
    'course_aware': True,
    'course_navigation': True,
    'new_tab': True,
    'frame_width': 1024,
    'frame_height': 1024,
    'allow_ta_access': True
}

COURSEAFFILS_COURSESTRING_MAPPER = CourseStringMapper
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

if 'integrationserver' in sys.argv:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'HOST': '',
            'PORT': '',
            'USER': '',
            'PASSWORD': '',
            'ATOMIC_REQUESTS': True,
        }
    }

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
