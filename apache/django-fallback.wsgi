import os, sys
sys.path.append('/var/www/django/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'docserver.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
