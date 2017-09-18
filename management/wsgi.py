"""
WSGI config for management project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys
import site

site.addsitedir('/home/project/venv_manage/lib/python2.7/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'management.settings'

sys.path.insert(0, '/home/project/management/management')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
