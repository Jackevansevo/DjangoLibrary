from django.core.exceptions import ImproperlyConfigured
from django.utils.timezone import timedelta
from configparser import ConfigParser


import os

# Load settings.ini file configuration
config = ConfigParser(allow_no_value=True)
config.read('settings.ini')


def get_env_variable(var_name):
    """Get the environment variable or return exception"""
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the {} environment variable".format(var_name)
        raise ImproperlyConfigured(error_msg)


#
# -- Settings.ini file configuration --
#

# Default loan periods
default = config['DEFAULT']
LOAN_DURATION = timedelta(days=default.getint('LOAN_DURATION', 7))
RENEW_DURATION = timedelta(days=default.getint('RENEW_DURATION', 2))
RENEW_WINDOW = timedelta(days=default.getint('RENEW_WINDOW', 2))


#
# -- Environment variable configuration --
#

# Default email sender
email_settings = config['EMAIL']
EMAIL_SENDER = email_settings.get('EMAIL_SENDER', '')
EMAIL_HOST = email_settings.get('EMAIL_HOST', '')
EMAIL_PORT = email_settings.getint('EMAIL_PORT', 25)
EMAIL_HOST_USER = email_settings.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = email_settings.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = email_settings.getboolean('EMAIL_USE_TLS', False)
EMAIL_USE_SSL = email_settings.getboolean('EMAIL_USE_SSL', False)


# Google Books API key
GOOGLE_BOOKS_API_KEY = get_env_variable('GOOGLE_BOOKS_API_KEY')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('SECRET_KEY')


#
# -- Django specific configuration --
#


# Site specific settings
AUTH_USER_MODEL = "books.Customer"
LOGIN_URL = 'books:login'
LOGOUT_REDIRECT_URL = 'books:book-list'


# https://docs.djangoproject.com/en/1.10/ref/settings/#internal-ips
INTERNAL_IPS = ('127.0.0.1',)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'books.apps.BooksConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.humanize',
    'widget_tweaks'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DjangoLibrary.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'DjangoLibrary.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djangolibrary',
        'USER': 'librarian',
        'PASSWORD': 'library',
        'HOST': 'localhost',
        'PORT': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Caching
# https://docs.djangoproject.com/en/1.10/topics/cache/
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}


# Password hashers
# https://docs.djangoproject.com/en/1.10/topics/auth/passwords/#how-django-stores-passwords
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
