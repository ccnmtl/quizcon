# flake8: noqa
from quizcon.settings_shared import *

try:
    from quizcon.local_settings import *
except ImportError:
    pass
