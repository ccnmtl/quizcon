# Django settings for quizcon project.
import os.path
import sys
from ccnmtlsettings.shared import common
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
    'infranil',
    'django_extensions',
    'courseaffils',
    'lti_provider',
    'quizcon.main',
]

MIDDLEWARE += [ # noqa
    'quizcon.main.middleware.WhoDidItMiddleware'
]

THUMBNAIL_SUBDIR = "thumbs"
LOGIN_REDIRECT_URL = "/"

ACCOUNT_ACTIVATION_DAYS = 7

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'lti_provider.auth.LTIBackend',
    'djangowind.auth.SAMLAuthBackend'
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
    'navigation': True,
    'new_tab': True,
    'frame_width': 1024,
    'frame_height': 1024
}

COURSEAFFILS_COURSESTRING_MAPPER = CourseStringMapper

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
