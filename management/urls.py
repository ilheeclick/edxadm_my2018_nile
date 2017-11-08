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
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(
        r'^accounts/login/',
        views.signin,
        name='login'
    ),
    url(r'^logout/$', auth_views.logout, {'next_page': '/manage/'}, name='logout'),
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

    # ---------- board common ---------- #
    # notice
    url(r'^manage/comm_notice/', views.comm_notice, name='comm_notice'),
    url(r'^manage/new_notice/', views.new_notice, name='new_notice'),
    url(r'^manage/modi_notice/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_notice, name='modi_notice'),

    # k_news
    url(r'^manage/comm_k_news/', views.comm_k_news, name='comm_k_news'),
    url(r'^manage/modi_knews/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_knews, name='modi_knews'),
    url(r'^manage/summer_upload/', views.summer_upload, name='summer_upload'),
    url(r'^manage/new_knews/', views.new_knews, name='new_knews'), # -> new_notice (module)

    # reference_room
    url(r'^manage/comm_reference_room/', views.comm_reference_room, name='comm_reference_room'),
    url(r'^manage/modi_refer/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_refer, name='modi_refer'),
    url(r'^manage/new_refer/', views.new_refer, name='new_refer'), # -> new_notice (module)

    # common file upload module
    url(r'^manage/file_upload/', views.file_upload, name='file_upload'),
    # ---------- board common ---------- #

    # faq
    url(r'^manage/comm_faq/', views.comm_faq, name='comm_faq'),
    url(r'^manage/new_faq/', views.new_faq, name='new_faq'),
    url(r'^manage/comm_faqrequest/', views.comm_faqrequest, name='comm_faqrequest'),
    url(r'^manage/modi_faq/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_faq, name='modi_faq'),

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

    # popup url
    url(r'^manage/popup_add/', views.popup_add, name='popup_add'),
    url(r'^manage/create_popup/', views.create_popup, name='create_popup'),
    url(r'^manage/popup_db/', views.popup_db, name='popup_db'),
    url(r'^manage/new_popup/', views.new_popup, name='new_popup'),
    url(r'^manage/modi_popup/(?P<id>.*?)/$', views.modi_popup, name='modi_popup'),
    url(r'^manage/popup_list/', views.popup_list, name='popup_list'),

    # multi_site url
    url(r'^manage/multi_site/$', views.multi_site, name='multi_site'),
    url(r'^manage/multi_site_db/$', views.multi_site_db, name='multi_site'),
    url(r'^manage/add_multi_site/(?P<id>.*?)/$', views.add_multi_site, name='add_multi_site'),
    url(r'^manage/modi_multi_site_db/$', views.modi_multi_site_db, name='modi_multi_site_db'),
    url(r'^manage/modi_multi_site/(?P<id>.*?)/$', views.modi_multi_site, name='modi_multi_site'),
    url(r'^manage/manager_list/$', views.manager_list, name='manager_list'),
    url(r'^manage/manager_db/$', views.manager_db, name='manager_db'),
    url(r'^manage/course_list/(?P<site_id>.*?)/(?P<org_name>.*?)/$', views.course_list, name='course_list'),
    url(r'^manage/course_list_db/$', views.course_list_db, name='course_list_db'),
    url(r'^manage/select_list_db/$', views.select_list_db, name='select_list_db'),
    url(r'^manage/multisite_course/$', views.multisite_course, name='multisite_course'),
    url(r'^manage/multisite_org/$', views.multisite_org, name='multisite_org'),

    # course_manage url
    url(r'^manage/course_manage/$', views.course_manage, name='course_manage'),
    url(r'^manage/course_db_list/$', views.course_db_list, name='course_db_list'),
    url(r'^manage/course_db/$', views.course_db, name='course_db'),


    #history
    # url(r'^manage/history_auth/', views.history_auth, name='history_auth'),
    # url(r'^manage/history_inst/', views.history_inst, name='history_inst'),
    # url(r'^manage/history_cert/', views.history_cert, name='history_cert'),

]
