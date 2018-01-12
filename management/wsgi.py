"""
WSGI config for examproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys
import site

site.addsitedir('/home/ubuntu/project/venv/lib/python2.7/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'management.settings'

sys.path.insert(0, '/home/ubuntu/project/management/management')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

