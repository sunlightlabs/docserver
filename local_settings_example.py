import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    #('Name', 'email address'),
)

MANAGERS = ADMINS

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

DATABASE_ENGINE = ''
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = 'America/Chicago'

MEDIA_ROOT = ''

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "%s/templates" % PROJECT_ROOT,
)

DATA_ROOT = ''