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
import tracking_control.views as tracking_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(
        r'^accounts/login/',
        views.signin,
        name='login'
    ),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^logout/$', views.logout, {'next_page': '/'}, name='logout'),
    url(r'^logout_time/$', views.logout_time, name='logout_time'),
    url(r'^test_index/$', views.test_index),
    url(r'^file_download_test$', views.file_download_test),

    url(r'^admin/', admin.site.urls),
    # url(r'^excel_download/?$', statistics_excel),
    # url(r'^excel_select/$', excel_manage),
    url(r'^excel_download/(?P<date>.*?)$', statistics_excel),
    # url(r'^excel_download_week/(?P<date>.*?)$', statistics_excel_week),
    # url(r'^excel_download_month/(?P<date>.*?)$', statistics_excel_month),

    # url(r'^excel_download2/(?P<courseId>.*?)$', certificate_excel),
    # url(r'^notice/reg$', notice_reg),
    # url(r'^notice/list$', notice_list),
    # url(r'^notice/mod$', notice_mod),
    # url(r'^notice/del$', notice_del),

    # stastic url
    url(r'^$', views.stastic_index, name='stastic_index'),
    url(r'^test/$', views.test, name='test'),
    url(r'^month_stastic/', views.month_stastic, name='month_stastic'),
    # state url
    url(r'^mana_state/', views.mana_state, name='mana_state'),
    # url(r'^get_options/', views.get_options, name='mana_state'),
    url(r'^dev_state/', views.dev_state, name='dev_state'),
    # certificate url
    url(r'^certificate/', views.certificate, name='certificate'),
    url(r'^per_certificate/', views.per_certificate, name='per_certificate'),
    url(r'^uni_certificate/', views.uni_certificate, name='uni_certificate'),

    # ---------- board common ---------- #
    # notice
    url(r'^comm_notice/', views.comm_notice, name='comm_notice'),
    url(r'^new_notice/', views.new_notice, name='new_notice'),
    url(r'^modi_notice/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_notice, name='modi_notice'),

    # k_news
    url(r'^comm_k_news/', views.comm_k_news, name='comm_k_news'),
    url(r'^modi_knews/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_knews, name='modi_knews'),
    url(r'^summer_upload/', views.summer_upload, name='summer_upload'),
    url(r'^new_knews/', views.new_knews, name='new_knews'),  # -> new_notice (module)

    # reference_room
    url(r'^comm_reference_room/', views.comm_reference_room, name='comm_reference_room'),
    url(r'^modi_refer/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_refer, name='modi_refer'),
    url(r'^new_refer/', views.new_refer, name='new_refer'),  # -> new_notice (module)

    # common file upload module
    url(r'^file_upload/', views.file_upload, name='file_upload'),
    # ---------- board common ---------- #

    # ---------- multiple email ---------- #
    url(r'^multiple_email/', views.multiple_email, name='multiple_email'),
    url(r'^multiple_email_new/', views.multiple_email_new, name='multiple_email_new'),
    url(r'^django_mail/', views.django_mail, name='multiple_email_new'),
    # ---------- multiple email ---------- #

    # ---------- user enroll ---------- #
    url(r'^user_enroll/', views.user_enroll, name='user_enroll'),
    url(r'^download_bulkuser_example/', views.download_bulkuser_example, name='download_bulkuser_example'),
    # ---------- user enroll ---------- #

    # faq
    url(r'^comm_faq/', views.comm_faq, name='comm_faq'),
    url(r'^new_faq/', views.new_faq, name='new_faq'),
    url(r'^comm_faqrequest/', views.comm_faqrequest, name='comm_faqrequest'),
    url(r'^modi_faq/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_faq, name='modi_faq'),

    # mobile
    url(r'^comm_mobile/', views.comm_mobile, name='comm_mobile'),
    url(r'^new_mobile/', views.new_mobile, name='new_mobile'),
    url(r'^modi_mobile/(?P<id>.*?)/(?P<use_yn>.*?)/$', views.modi_mobile, name='modi_mobile'),

    # monitoring url
    url(r'^moni_storage/', views.moni_storage, name='moni_storage'),

    # monitoring url
    url(r'^history/', views.history, name='history'),
    url(r'^login_history/', views.login_history, name='login_history'),
    url(r'^csv/history/', views.history_csv, name='history'),

    url(r'^file_delete/', views.file_delete, name='file_delete'),
    url(r'^file_download/(?P<file_name>.*?)/$', views.file_download, name='file_download'),

    # popup url
    url(r'^popup_add/', views.popup_add, name='popup_add'),
    url(r'^create_popup/', views.create_popup, name='create_popup'),
    url(r'^popup_db/', views.popup_db, name='popup_db'),
    url(r'^new_popup/', views.new_popup, name='new_popup'),
    url(r'^modi_popup/(?P<id>.*?)/$', views.modi_popup, name='modi_popup'),
    url(r'^popupZone_add/$', views.popupZone_add, name='popupZone_add'),
    url(r'^modi_popupZone/(?P<id>.*?)/$', views.modi_popupZone, name='modi_popupZone'),
    url(r'^popupZone_db/', views.popupZone_db, name='popupZone_db'),
    url(r'^new_popupZone/', views.new_popupZone, name='new_popupZone'),

    # popup index url
    url(r'^popup_index0/(?P<id>.*?)/(?P<type>.*?)/$', views.popup_index0, name='popup_index0'),
    url(r'^popup_index1/(?P<id>.*?)/$', views.popup_index1, name='popup_index1'),
    url(r'^popup_index2/(?P<id>.*?)/$', views.popup_index2, name='popup_index2'),
    url(r'^popup_index3/(?P<id>.*?)/$', views.popup_index3, name='popup_index3'),

    url(r'^tracking_log/$', tracking_view.log_download, name='tracking_log'),
    url(r'^tracking_log/date/(?P<date>.*?)/$', tracking_view.logfile_download, name='tracking_log'),
    url(r'^tracking_log/down/(?P<file_name>.*?)/$', views.file_download, name='tracking_download'),
    # url(r'^filed/$', tracking_view.send_file)
    url(r'^tracking_log/logdata_add/', tracking_view.data_insert),
    url(r'^tracking_log/downlist/', tracking_view.log_board, name='log_board'),
    # multi_site url
    url(r'^multi_site/$', views.multi_site, name='multi_site'),
    url(r'^multi_site_db/$', views.multi_site_db, name='multi_site'),
    url(r'^add_multi_site/(?P<id>.*?)/$', views.add_multi_site, name='add_multi_site'),
    url(r'^modi_multi_site_db/$', views.modi_multi_site_db, name='modi_multi_site_db'),
    url(r'^modi_multi_site/(?P<id>.*?)/$', views.modi_multi_site, name='modi_multi_site'),
    url(r'^manager_list/$', views.manager_list, name='manager_list'),
    url(r'^manager_db/$', views.manager_db, name='manager_db'),
    url(r'^course_list/(?P<site_id>.*?)/(?P<org_name>.*?)/$', views.course_list, name='course_list'),
    url(r'^course_list_db/$', views.course_list_db, name='course_list_db'),
    url(r'^select_list_db/$', views.select_list_db, name='select_list_db'),
    url(r'^multisite_course/$', views.multisite_course, name='multisite_course'),
    url(r'^multisite_org/$', views.multisite_org, name='multisite_org'),

    # course_manage url
    url(r'^course_manage$', views.course_manage, name='course_manage'),
    url(r'^course_db_list/$', views.course_db_list, name='course_db_list'),
    url(r'^course_db/$', views.course_db, name='course_db'),

    url(r'^code_manage$', views.code_manage, name='code_manage'),
    url(r'^group_code/$', views.group_code, name='group_code'),
    url(r'^detail_code/$', views.detail_code, name='detail_code'),
    url(r'^group_code_db/$', views.group_code_db, name='group_code_db'),
    url(r'^detail_code_db/$', views.detail_code_db, name='detail_code_db'),

    url(r'^series_course/$', views.series_course, name='series_course'),
    url(r'^modi_series/(?P<id>.*?)/$', views.modi_series, name='modi_series'),
    url(r'^modi_series_course/$', views.modi_series_course, name='modi_series_course'),
    url(r'^series_list/$', views.series_list, name='series_list'),
    url(r'^all_course/$', views.all_course, name='all_course'),
    url(r'^series_course_list_view/(?P<id>.*?)/$', views.series_course_list_view, name='series_course_list_view'),
    url(r'^series_complete_list_view/(?P<id>.*?)/$', views.series_complete_list_view, name='series_complete_list_view'),
    url(r'^series_course_list_db/$', views.series_course_list_db, name='series_course_list_db'),
    url(r'^series_course_list/$', views.series_course_list, name='series_course_list'),
    # review_manage url
    url(r'^review_manage$', views.review_manage, name='review_manage'),
    url(r'^series_complete_db/$', views.series_complete_db, name='series_complete_db'),
    # login_history
    url(r'^login_history/$', views.login_history, name='login_history'),
    # history
    # url(r'^history_auth/', views.history_auth, name='history_auth'),
    # url(r'^history_inst/', views.history_inst, name='history_inst'),
    # url(r'^history_cert/', views.history_cert, name='history_cert'),
]
