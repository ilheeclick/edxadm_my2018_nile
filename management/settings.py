# -*- coding: utf-8 -*-
"""
Django settings for management project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u0-$j2v%)u-w52*spjq7)i@8rv*=!el9ua+@j9j-i_h_$u-bmb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user_manage',
    'home',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates1')],
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

WSGI_APPLICATION = 'management.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'edxapp',
        'USER': 'edxapp001',
        'PASSWORD' : 'password',
        # 'HOST': '192.168.33.13',
        'HOST': '192.168.33.13',
        'PORT': '3306',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/home/static/'

STATICFILES_DIRS = (
     ("css", os.path.join(BASE_DIR, 'static1/css')),
     ("image", os.path.join(BASE_DIR, 'static1/image')),
     ("js", os.path.join(BASE_DIR, 'static1/js')),
     ("font", os.path.join(BASE_DIR, 'static1/font')),
     ("excel", os.path.join(BASE_DIR, 'home/static/excel')),
      # Put strings here, like "/home/html/static" or "C:/www/django/static".
      # Always use forward slashes, even on Windows.
      # Don't forget to use absolute paths, not relative paths.
)

# ============================================================================================================
# global variables ===========================================================================================
# ============================================================================================================
database_id = '192.168.33.13'

# EXCEL_PATH = '/home/project/management/static/excel/'
EXCEL_PATH = '/home/vagrant/management/management/home/static/excel/'
# EXCEL_PATH = '/home/vagrant/management/management/static/excel/'
UPLOAD_DIR = '/home/vagrant/management/management/'


debug = True

dic_univ = {
        'KHUk':u'경희대학교',
        'KoreaUnivK':u'고려대학교',
        'PNUk':u'부산대학교',
        'SNUk':u'서울대학교',
        'SKKUk':u'성균관대학교',
        'YSUk':u'연세대학교',
        'EwhaK':u'이화여자대학교',
        'POSTECHk':u'포항공과대학교',
        'KAISTk':u'한국과학기술원',
        'HYUk':u'한양대학교',
        'KYUNGNAMUNIVk':u'경남대학교',
        'DGUk':u'대구대학교',
        'SMUCk':u'상명대학교(천안)',
        'SSUk':u'성신여자대학교',
        'SejonguniversityK':u'세종대학교',
        'SookmyungK':u'숙명여자대학교',
        'YeungnamUnivK':u'영남대학교',
        'UOUk':u'울산대학교',
        'INHAuniversityK':u'인하대학교',
        'CBNUk':u'전북대학교',
        'GachonUnivK':u'가천대학교',
        'KonYangK':u'건양대학교',
        'DonggukK':u'동국대학교',
        'DSUk':u'동신대학교',
        'MokwonK':u'목원대학교',
        'SMUk':u'상명대학교(서울)',
        'UOSk':u'서울시립대',
        'CAUk':u'중앙대학교',
        'CNUk':u'충남대학교',
        'HGUk':u'한동대학교',
        'HallymK':u'한림대학교',
        'KONGJUk':u'공주대학교',
        'KUMOHk':u'금오공과대학교',
        'DKUK':u'단국대학교',
        'BUFSk':u'부산외국어대학교',
        'SYUk':u'삼육대학교',
        'KNUk':u'경북대학교',
        'CUKk':u'가톨릭대학교',
        'JEJUk':u'제주대학교',
        'SKP.KAISTk':u'서울대, 한국과학기술원, 포항공대',
        'SKP.SNUk':u'서울대, 한국과학기술원, 포항공대',
        'SKP.POSTECHk':u'서울대, 한국과학기술원, 포항공대'

    }
