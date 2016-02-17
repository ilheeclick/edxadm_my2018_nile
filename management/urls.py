"""management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from user_manage.views import user_manage, excel_manage
from user_manage.statistics import statistics_excel, certificate_excel, statistics_excel3

urlpatterns = [
    url(r'^manage/$', user_manage),
    # url(r'^excel_download/?$', statistics_excel),
    url(r'^manage/excel_select/$', excel_manage),
    url(r'^manage/excel_download/(?P<date>.*?)$', statistics_excel),
    url(r'^manage/excel_download3/(?P<date>.*?)$', statistics_excel3),
    url(r'^manage/excel_download2/(?P<courseId>.*?)$', certificate_excel),
    #url(r'^', user_manage),
    #url(r'^admin/', google_test),
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^manage/', include('user_manage.urls')),
]