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

CAS_SERVER_URL = 'https://cas.columbia.edu/cas/'
CAS_VERSION = '3'
CAS_ADMIN_REDIRECT = False
CAS_MAP_AFFILIATIONS = True

# Translate CUIT's CAS user attributes to the Django user model.
# https://cuit.columbia.edu/content/cas-3-ticket-validation-response
CAS_APPLY_ATTRIBUTES_TO_USER = True
CAS_RENAME_ATTRIBUTES = {
    'givenName': 'first_name',
    'lastName': 'last_name',
    'mail': 'email',
}

INSTALLED_APPS.remove('djangowind') # noqa
INSTALLED_APPS += [  # noqa
    'bootstrap4',
    'infranil',
    'contactus',
    'django_extensions',
    'courseaffils',
    'lti_provider',
    'quizcon.main',
    'waffle',
    'django_cas_ng',
]

ALLOWED_HOSTS += ['127.0.0.1']  # noqa

MIDDLEWARE += [ # noqa
    'quizcon.main.middleware.WhoDidItMiddleware'
]

THUMBNAIL_SUBDIR = "thumbs"
LOGIN_REDIRECT_URL = "/"

ACCOUNT_ACTIVATION_DAYS = 7

CONTACT_US_EMAIL = 'ctl-quizcon@columbia.edu'
SERVER_EMAIL = 'automated@mail.ctl.columbia.edu'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'lti_provider.auth.LTIBackend',
    'django_cas_ng.backends.CASBackend',
]

TEMPLATES[0]['OPTIONS']['context_processors'].remove(  # noqa
    'djangowind.context.context_processor')

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
