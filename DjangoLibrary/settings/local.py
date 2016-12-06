from .base import *

# Turn on debugging
DEBUG = True

# Enable Django Debug toolbar and Django extensions locally
INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ('127.0.0.1',)
