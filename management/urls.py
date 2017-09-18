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
# from home.statistics import statistics_excel, statistics_excel_week, statistics_excel_month

from home.statistics import statistics_excel
from home import views


urlpatterns = [
    url(r'^manage/test_index/$', views.test_index),
    url(r'^manage/file_download_test$', views.file_download_test),

    url(r'^manage/admin/', admin.site.urls),
    # url(r'^excel_download/?$', statistics_excel),
    # url(r'^manage/excel_select/$', excel_manage),
    url(r'^manage/excel_download/(?P<date>.*?)$', statistics_excel),
    # url(r'^manage/excel_download_week/(?P<date>.*?)$', statistics_excel_week),
    # url(r'^manage/excel_download_month/(?P<date>.*?)$', statistics_excel_month),

    # url(r'^manage/excel_download2/(?P<courseId>.*?)$', certificate_excel),
    # url(r'^manage/notice/reg$', notice_reg),
    # url(r'^manage/notice/list$', notice_list),
    # url(r'^manage/notice/mod$', notice_mod),
    # url(r'^manage/notice/del$', notice_del),

    # stastic url
    url(r'^manage/$', views.stastic_index, name='stastic_index'),
    url(r'^manage/test/$', views.test, name='test'),
    url(r'^manage/month_stastic/', views.month_stastic, name='month_stastic'),
    # state url
    url(r'^manage/mana_state/', views.mana_state, name='mana_state'),
    # url(r'^manage/get_options/', views.get_options, name='mana_state'),
    url(r'^manage/dev_state/', views.dev_state, name='dev_state'),
    # certificate url
    url(r'^manage/certificate/', views.certificate, name='certificate'),
    url(r'^manage/per_certificate/', views.per_certificate, name='per_certificate'),
    url(r'^manage/uni_certificate/', views.uni_certificate, name='uni_certificate'),
    # community url
    # notice
    url(r'^manage/comm_notice/', views.comm_notice, name='comm_notice'),
    url(r'^manage/new_notice/', views.new_notice, name='new_notice'),
    url(r'^manage/modi_notice/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_notice, name='modi_notice'),
    # k_news
    url(r'^manage/comm_k_news/', views.comm_k_news, name='comm_k_news'),
    url(r'^manage/new_knews/', views.new_knews, name='new_knews'),
    url(r'^manage/modi_knews/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_knews, name='modi_knews'),
    url(r'^manage/summer_upload/', views.summer_upload, name='summer_upload'),
    # faq
    url(r'^manage/comm_faq/', views.comm_faq, name='comm_faq'),
    url(r'^manage/new_faq/', views.new_faq, name='new_faq'),
    url(r'^manage/comm_faqrequest/', views.comm_faqrequest, name='comm_faqrequest'),
    url(r'^manage/modi_faq/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_faq, name='modi_faq'),
    # reference_room
    url(r'^manage/comm_reference_room/', views.comm_reference_room, name='comm_reference_room'),
    url(r'^manage/new_refer/', views.new_refer, name='new_refer'),
    url(r'^manage/modi_refer/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_refer, name='modi_refer'),

    # mobile
    url(r'^manage/comm_mobile/', views.comm_mobile, name='comm_mobile'),
    url(r'^manage/new_mobile/', views.new_mobile, name='new_mobile'),
    url(r'^manage/modi_mobile/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_mobile, name='modi_mobile'),

    # monitoring url
    url(r'^manage/moni_storage/', views.moni_storage, name='moni_storage'),

    # monitoring url
    url(r'^manage/history/', views.history, name='history'),
    url(r'^manage/csv/history/', views.history_csv, name='history'),

    url(r'^manage/file_delete/', views.file_delete, name='file_delete'),
    url(r'^manage/file_download/(?P<file_name>.*?)/$', views.file_download, name='file_download'),

    #history
    # url(r'^manage/history_auth/', views.history_auth, name='history_auth'),
    # url(r'^manage/history_inst/', views.history_inst, name='history_inst'),
    # url(r'^manage/history_cert/', views.history_cert, name='history_cert'),

]
