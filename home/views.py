# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, redirect
from django.template import Context, RequestContext
from django.http import Http404, HttpResponse, FileResponse, JsonResponse
from django.db import connection
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from management.settings import UPLOAD_DIR
from management.settings import dic_univ, database_id, debug
from models import GeneratedCertificate
from .forms import UserForm, LoginForm
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import os
import subprocess
import commands
import sys
import pprint
import ast
import urllib
import csv
import datetime
import logging

reload(sys)
sys.setdefaultencoding('utf-8')

def get_file_ext(filename):
    filename_split = filename.split('.')
    file_ext_index = len(filename_split)
    file_ext = filename_split[file_ext_index-1] 
    return file_ext

@login_required
def multi_site(request):
    return render(request, 'multi_site/multi_site.html')

@csrf_exempt
def multi_site_db(request):
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        multi_site_list = []

        if request.GET['method'] == 'multi_site_list':
            cur = connection.cursor()
            query = """
                SELECT @rn := @rn - 1 rn,
                       site_id,
                       site_name,
                       site_code,
                       site_url,
                       username,
                       regist_date
                  FROM multisite a JOIN auth_user b on a.regist_id= b.id,
                       (SELECT @rn := count(*) + 1
                          FROM multisite) b
                 WHERE delete_yn = 'N'
              ORDER BY regist_date DESC;
			"""

            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            for multi in row:
                value_list = []
                value_list.append(multi[0])
                value_list.append(multi[1])
                value_list.append(multi[2])
                value_list.append(multi[3])
                value_list.append(multi[4])
                value_list.append(multi[5])
                value_list.append(multi[6])
                multi_site_list.append(value_list)

            data = json.dumps(list(multi_site_list), cls=DjangoJSONEncoder, ensure_ascii=False)
            print ('::::::::::::::::::::::::::::::::::')
            print data
        return HttpResponse(data, 'applications/json')
    return render(request, 'multi_site/multi_site.html')

@csrf_exempt
def add_multi_site(request, id):

    variables = RequestContext(request, {
        'id': id
    })
    return render_to_response('multi_site/modi_multi_site.html', variables)

def modi_multi_site(request, id):
    mod_multi = []
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            query = """
					SELECT site_name,
                           site_code,
                           site_url,
                           logo_img
					  FROM multisite
                     WHERE site_id =
			""" + id

            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            for p in row:
                mod_multi.append(p)
            print mod_multi
            data = json.dumps(list(mod_multi), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    variables = RequestContext(request, {
        'id': id
    })
    return render_to_response('multi_site/modi_multi_site.html', variables)

@csrf_exempt
def modi_multi_site_db(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        if request.POST.get('method') == 'add':
            site_name = request.POST.get('site_name')
            site_code = request.POST.get('site_code')
            site_url = request.POST.get('site_url')
            regist_id = request.POST.get('regist_id')
            logo_img = request.POST.get('logo_img')
            email_list = request.POST.get('email_list')
            email_list = email_list.split('+')
            email_list.pop()


            for item in email_list:
                cur = connection.cursor()
                query = '''SELECT id
                             FROM edxapp.auth_user
                            WHERE email = '{0}';
                        '''.format(item)
                cur.execute(query)
                row = cur.fetchall()
                cur.close()

                cur = connection.cursor()
                query = "select count(site_id) + 1 from multisite"
                cur.execute(query)
                cnt = cur.fetchall()
                cur.close()

                cur = connection.cursor()
                query = '''insert into edxapp.multisite_user(site_id, user_id, regist_id, modify_id)
                           VALUES ('{0}','{1}','{2}','{3}')
                        '''.format(str(cnt[0][0]), str(row[0][0]), regist_id, regist_id)
                cur.execute(query)
                cur.close()



            cur = connection.cursor()
            query = '''insert into edxapp.multisite(site_name, site_code, logo_img, site_url, regist_id, modify_id)
                       VALUES ('{0}','{1}','{2}','{3}','{4}', '{5}')
                    '''.format(site_name, site_code, logo_img, site_url, regist_id, regist_id)
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST['method'] == 'modi':
            site_name = request.POST.get('site_name')
            site_code = request.POST.get('site_code')
            site_url = request.POST.get('site_url')
            multi_no = request.POST.get('multi_no')
            regist_id = request.POST.get('regist_id')
            logo_img = request.POST.get('logo_img')

            cur = connection.cursor()
            query = '''
                    update edxapp.multisite
                    SET site_name = '{0}', site_code = '{1}', logo_img= '{2}', site_url = '{3}', modify_id = '{4}', modify_date = now()
                    WHERE site_id = '{5}'
                    '''.format(site_name, site_code, logo_img, site_url, regist_id, multi_no)
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'delete':
            multi_no = request.POST.get('multi_no')

            cur = connection.cursor()
            query = '''
                    update edxapp.multisite
                    SET delete_yn = 'Y'
                    WHERE site_id = '{0}'
                    '''.format(multi_no)
            cur.execute(query)
            cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

    return render(request, 'multi_site/modi_multi_site.html')

def manager_list(request):
    result = dict()
    id = request.GET.get('id')

    with connections['default'].cursor() as cur:

        query = '''
               SELECT au.email, up.name, au.username
                 FROM edxapp.auth_user AS au
                 JOIN edxapp.auth_userprofile as up
                   ON au.id = up.user_id
                 JOIN edxapp.multisite_user as mu
                   ON up.user_id = mu.user_id
                WHERE mu.site_id = '{0}' and mu.delete_yn = 'N'
        '''.format(id)
        print query

        cur.execute(query)
        columns = [i[0] for i in cur.description]
        rows = cur.fetchall()
        result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]

    result['data'] = result_list

    context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(context, 'applications/json')


def manager_db(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        if request.POST.get('method') == 'add':
            id = request.POST.get('id')
            input_email = request.POST.get('input_email')
            regist_id = request.POST.get('regist_id')


            cur = connection.cursor()
            query = '''SELECT id
                         FROM edxapp.auth_user
                        WHERE email = '{0}';
                    '''.format(input_email)
            cur.execute(query)
            row = cur.fetchall()
            cur.close()


            cur = connection.cursor()
            query = '''SELECT count(site_id)
                         FROM edxapp.multisite_user
                        WHERE user_id = '{0}' and site_id = '{1}' and delete_yn = 'Y' ;
                    '''.format(str(row[0][0]), id)
            cur.execute(query)
            cnt = cur.fetchall()
            cur.close()
            print cnt[0][0]
            if(cnt[0][0] == 1) :
                cur = connection.cursor()
                query = '''update edxapp.multisite_user
                              SET delete_yn = 'N'
                            WHERE site_id = '{0}' and user_id = '{1}';
                        '''.format(id, str(row[0][0]))
                cur.execute(query)
                cur.close()
            elif(cnt[0][0] == 0):
                cur = connection.cursor()
                query = '''insert into edxapp.multisite_user(site_id, user_id, regist_id, modify_id)
                           VALUES ('{0}','{1}','{2}','{3}')
                        '''.format(id, str(row[0][0]), regist_id, regist_id)
                cur.execute(query)
                cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST['method'] == 'temporary':
            input_email = request.POST.get('input_email')

            cur = connection.cursor()

            query = '''
                    SELECT au.email, up.name, au.username
                      FROM edxapp.auth_user AS au
                      JOIN edxapp.auth_userprofile as up
                        ON au.id = up.user_id
                     WHERE au.email = '{0}'
                    '''.format(input_email)
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            print row

            data = json.dumps(row, cls=DjangoJSONEncoder, ensure_ascii=False)

            return HttpResponse(data, 'applications/json')

        elif request.POST['method'] == 'verify':
            input_email = request.POST.get('input_email')

            cur = connection.cursor()

            query = '''
                    SELECT COUNT(id)
                    FROM edxapp.auth_user
                    WHERE email = '{0}';
                    '''.format(input_email)
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            print row[0][0]

            data = json.dumps(row[0][0], cls=DjangoJSONEncoder, ensure_ascii=False)

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'delete':
            site_id = request.POST.get('site_id')
            user_id = request.POST.get('user_id')
            regist_id = request.POST.get('regist_id')

            cur = connection.cursor()

            query = '''
                    SELECT id
                      FROM auth_user
                     WHERE auth_user.username = '{0}';
                    '''.format(user_id)
            cur.execute(query)
            new_id = cur.fetchall()
            cur.close()

            cur = connection.cursor()
            query = '''
                    update edxapp.multisite_user
                    SET delete_yn = 'Y', modify_id = '{0}', modify_date = now()
                    WHERE site_id = '{1}' and user_id = '{2}'
                    '''.format(regist_id, site_id, new_id[0][0])
            cur.execute(query)
            cur.close()


            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

    return render(request, 'multi_site/modi_multi_site.html')

@login_required
def popup_add(request):
    return render(request, 'popup/popup_add.html')

def popup_list(request):
    return render(request, 'popup/popup_list.html')

def modi_popup(request, id):
    mod_pop = []
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            query = """
					SELECT CASE
							  WHEN popup_type = 'H' THEN 'HTML'
							  WHEN popup_type = 'I' THEN 'Image'
						   END
					       popup_type,
					       CASE
							  WHEN link_type = '0' THEN '없음'
							  WHEN link_type = '1' THEN '전체링크'
							  WHEN link_type = '2' THEN '이미지맵'
						   END
						   link_type,
						   image_map,
						   title,
						   contents,
						   image_url,
						   link_url,
						   CASE
							  WHEN link_target = 'B' THEN 'blank'
							  WHEN link_target = 'S' THEN 'self'
						   END
						   link_target,
						   start_date,
						   start_time,
						   end_date,
						   end_time,
						   CASE
							  WHEN template = '0' THEN '없음'
							  WHEN template = '1' THEN '기본'
							  WHEN template = '2' THEN '중간템플릿'
						   END
						   template,
						   width,
						   height,
						   CASE
							  WHEN hidden_day = '0' THEN '그만보기'
							  WHEN hidden_day = '1' THEN '1일'
							  WHEN hidden_day = '7' THEN '7일'
						   END
						   hidden_day,
						   use_yn
					  FROM popup
					 WHERE popup_id = """ + id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            for p in row:
                mod_pop.append(p)
            cur = connection.cursor()
            query = """
                    select count(use_yn) from popup where use_yn = 'Y';
                    """
            cur.execute(query)
            print ('=====================================')
            print query
            row = cur.fetchall()
            cur.close()
            print row
            for p in row:
                mod_pop.append(p)

            print mod_pop
            data = json.dumps(list(mod_pop), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    variables = RequestContext(request, {
        'id': id
    })
    return render_to_response('popup/popup_modipopup.html', variables)

def create_popup(request):
    return render(request, 'popup/popup_modipopup.html')

@csrf_exempt
def popup_db(request):
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        popup_list = []

        if request.GET['method'] == 'popup_list':
            cur = connection.cursor()
            query = """
                SELECT popup_id,
                       CASE
                          WHEN popup_type = 'H' THEN 'HTML'
                          WHEN popup_type = 'I' THEN 'Image'
                       END
                       popup_type,
                       title,
                       regist_id,
                       start_date,
                       end_date,
                       CASE
                          WHEN link_type = '0' THEN '없음'
                          WHEN link_type = '1' THEN '전체링크'
                          WHEN link_type = '2' THEN '이미지맵'
                       END
                       link_type,
                       link_url,
                       CASE
                          WHEN use_yn = 'Y' THEN '사용함'
                          WHEN use_yn = 'N' THEN '사용안함'
                       END
                       use_yn
                  FROM popup
			"""
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            for pop in row:
                value_list = []
                value_list.append(pop[0])
                value_list.append(pop[1])
                value_list.append(pop[2])
                value_list.append(pop[3])
                value_list.append(pop[4])
                value_list.append(pop[5])
                value_list.append(pop[6])
                value_list.append(pop[7])
                value_list.append(pop[8])
                popup_list.append(value_list)

            data = json.dumps(list(popup_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')
    return render(request, 'popup/popup_add.html')

@csrf_exempt
def new_popup(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        if request.POST.get('method') == 'add':
            popup_type = request.POST.get('popup_type')
            link_type = request.POST.get('link_type')
            image_map = request.POST.get('image_map')
            title = request.POST.get('title')
            contents = request.POST.get('contents')
            image_url = request.POST.get('image_url')
            link_url = request.POST.get('link_url')
            link_target = request.POST.get('link_target')
            start_date = request.POST.get('start_date')
            start_time = request.POST.get('start_time')
            end_date = request.POST.get('end_date')
            end_time = request.POST.get('end_time')
            template = request.POST.get('template')
            width = request.POST.get('width')
            height = request.POST.get('height')
            hidden_day = request.POST.get('hidden_day')
            regist_id = request.POST.get('regist_id')
            use_yn = request.POST.get('use_yn')

            cur = connection.cursor()
            query = "insert into edxapp.popup(popup_type, link_type, image_map, title, contents, image_url, link_url, link_target, start_date, start_time, end_date, end_time, template, width, height, hidden_day, regist_id, modify_id, use_yn)"
            query += " VALUES ('" + popup_type + "', '" + link_type + "', '" + image_map + "', '" + title + "', '" + contents + "', '" + image_url + "', '" + link_url + "', '" + link_target + "', '" + start_date + "', '" + start_time + "', '" + end_date + "', '" + end_time + "', '" + template + "', '" + width + "', '" + height + "', '" + hidden_day + "', '" + regist_id + "', '" + regist_id + "', '" + use_yn + "') "
            cur.execute(query)
            cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')


        elif request.POST['method'] == 'modi':
            popup_type = request.POST.get('popup_type')
            link_type = request.POST.get('link_type')
            image_map = request.POST.get('image_map')
            title = request.POST.get('title')
            contents = request.POST.get('contents')
            image_url = request.POST.get('image_url')
            link_url = request.POST.get('link_url')
            link_target = request.POST.get('link_target')
            start_date = request.POST.get('start_date')
            start_time = request.POST.get('start_time')
            end_date = request.POST.get('end_date')
            end_time = request.POST.get('end_time')
            template = request.POST.get('template')
            width = request.POST.get('width')
            height = request.POST.get('height')
            hidden_day = request.POST.get('hidden_day')
            regist_id = request.POST.get('regist_id')
            pop_id = request.POST.get('pop_id')
            use_yn = request.POST.get('use_yn')

            cur = connection.cursor()
            query = "update edxapp.popup SET popup_type = '" + popup_type + "', link_type = '" + link_type + "', image_map = '" + image_map + "', title = '" + title + "', contents = '" + contents + "', image_url = '" + image_url + "', link_url = '" + link_url + "', link_target = '" + link_target + "', start_date = '" + start_date + "', start_time = '" + start_time + "', end_date = '" + end_date + "', end_time = '" + end_time + "', template = '" + template + "', width = '" + width + "', height = '" + height + "', hidden_day = '" + hidden_day + "', modify_id = '" + regist_id + "', use_yn = '" + use_yn + "', modify_date = now() WHERE popup_id =" +pop_id
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'delete':
            pop_id = request.POST.get('pop_id')

            cur = connection.cursor()
            query = "delete from popup where popup_id = " + pop_id
            cur.execute(query)
            cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

    return render(request, 'popup/popup_add.html')


@login_required
def stastic_index(request):
    return render(request, 'stastic/stastic_index.html')


def test(request):
    if request.is_ajax():
        data = {
            "data": [
                {
                    "name": "Tiger Nixon",
                    "position": "System Architect",
                    "salary": "$320,800",
                    "start_date": "2011/04/25",
                    "office": "Edinburgh",
                    "extn": "5421"
                },
                {
                    "name": "Garrett Winters",
                    "position": "Accountant",
                    "salary": "$170,750",
                    "start_date": "2011/07/25",
                    "office": "Tokyo",
                    "extn": "8422"
                },
                {
                    "name": "Ashton Cox",
                    "position": "Junior Technical Author",
                    "salary": "$86,000",
                    "start_date": "2009/01/12",
                    "office": "San Francisco",
                    "extn": "1562"
                },
                {
                    "name": "Cedric Kelly",
                    "position": "Senior Javascript Developer",
                    "salary": "$433,060",
                    "start_date": "2012/03/29",
                    "office": "Edinburgh",
                    "extn": "6224"
                },
                {
                    "name": "Airi Satou",
                    "position": "Accountant",
                    "salary": "$162,700",
                    "start_date": "2008/11/28",
                    "office": "Tokyo",
                    "extn": "5407"
                },
                {
                    "name": "Brielle Williamson",
                    "position": "Integration Specialist",
                    "salary": "$372,000",
                    "start_date": "2012/12/02",
                    "office": "New York",
                    "extn": "4804"
                },
                {
                    "name": "Herrod Chandler",
                    "position": "Sales Assistant",
                    "salary": "$137,500",
                    "start_date": "2012/08/06",
                    "office": "San Francisco",
                    "extn": "9608"
                },
                {
                    "name": "Rhona Davidson",
                    "position": "Integration Specialist",
                    "salary": "$327,900",
                    "start_date": "2010/10/14",
                    "office": "Tokyo",
                    "extn": "6200"
                },
                {
                    "name": "Colleen Hurst",
                    "position": "Javascript Developer",
                    "salary": "$205,500",
                    "start_date": "2009/09/15",
                    "office": "San Francisco",
                    "extn": "2360"
                },
                {
                    "name": "Sonya Frost",
                    "position": "Software Engineer",
                    "salary": "$103,600",
                    "start_date": "2008/12/13",
                    "office": "Edinburgh",
                    "extn": "1667"
                },
                {
                    "name": "Jena Gaines",
                    "position": "Office Manager",
                    "salary": "$90,560",
                    "start_date": "2008/12/19",
                    "office": "London",
                    "extn": "3814"
                },
                {
                    "name": "Quinn Flynn",
                    "position": "Support Lead",
                    "salary": "$342,000",
                    "start_date": "2013/03/03",
                    "office": "Edinburgh",
                    "extn": "9497"
                },
                {
                    "name": "Charde Marshall",
                    "position": "Regional Director",
                    "salary": "$470,600",
                    "start_date": "2008/10/16",
                    "office": "San Francisco",
                    "extn": "6741"
                },
                {
                    "name": "Haley Kennedy",
                    "position": "Senior Marketing Designer",
                    "salary": "$313,500",
                    "start_date": "2012/12/18",
                    "office": "London",
                    "extn": "3597"
                },
                {
                    "name": "Tatyana Fitzpatrick",
                    "position": "Regional Director",
                    "salary": "$385,750",
                    "start_date": "2010/03/17",
                    "office": "London",
                    "extn": "1965"
                },
                {
                    "name": "Michael Silva",
                    "position": "Marketing Designer",
                    "salary": "$198,500",
                    "start_date": "2012/11/27",
                    "office": "London",
                    "extn": "1581"
                },
                {
                    "name": "Paul Byrd",
                    "position": "Chief Financial Officer (CFO)",
                    "salary": "$725,000",
                    "start_date": "2010/06/09",
                    "office": "New York",
                    "extn": "3059"
                },
                {
                    "name": "Gloria Little",
                    "position": "Systems Administrator",
                    "salary": "$237,500",
                    "start_date": "2009/04/10",
                    "office": "New York",
                    "extn": "1721"
                },
                {
                    "name": "Bradley Greer",
                    "position": "Software Engineer",
                    "salary": "$132,000",
                    "start_date": "2012/10/13",
                    "office": "London",
                    "extn": "2558"
                },
                {
                    "name": "Dai Rios",
                    "position": "Personnel Lead",
                    "salary": "$217,500",
                    "start_date": "2012/09/26",
                    "office": "Edinburgh",
                    "extn": "2290"
                },
                {
                    "name": "Jenette Caldwell",
                    "position": "Development Lead",
                    "salary": "$345,000",
                    "start_date": "2011/09/03",
                    "office": "New York",
                    "extn": "1937"
                },
                {
                    "name": "Yuri Berry",
                    "position": "Chief Marketing Officer (CMO)",
                    "salary": "$675,000",
                    "start_date": "2009/06/25",
                    "office": "New York",
                    "extn": "6154"
                },
                {
                    "name": "Caesar Vance",
                    "position": "Pre-Sales Support",
                    "salary": "$106,450",
                    "start_date": "2011/12/12",
                    "office": "New York",
                    "extn": "8330"
                },
                {
                    "name": "Doris Wilder",
                    "position": "Sales Assistant",
                    "salary": "$85,600",
                    "start_date": "2010/09/20",
                    "office": "Sidney",
                    "extn": "3023"
                },
                {
                    "name": "Angelica Ramos",
                    "position": "Chief Executive Officer (CEO)",
                    "salary": "$1,200,000",
                    "start_date": "2009/10/09",
                    "office": "London",
                    "extn": "5797"
                },
                {
                    "name": "Gavin Joyce",
                    "position": "Developer",
                    "salary": "$92,575",
                    "start_date": "2010/12/22",
                    "office": "Edinburgh",
                    "extn": "8822"
                },
                {
                    "name": "Jennifer Chang",
                    "position": "Regional Director",
                    "salary": "$357,650",
                    "start_date": "2010/11/14",
                    "office": "Singapore",
                    "extn": "9239"
                },
                {
                    "name": "Brenden Wagner",
                    "position": "Software Engineer",
                    "salary": "$206,850",
                    "start_date": "2011/06/07",
                    "office": "San Francisco",
                    "extn": "1314"
                },
                {
                    "name": "Fiona Green",
                    "position": "Chief Operating Officer (COO)",
                    "salary": "$850,000",
                    "start_date": "2010/03/11",
                    "office": "San Francisco",
                    "extn": "2947"
                },
                {
                    "name": "Shou Itou",
                    "position": "Regional Marketing",
                    "salary": "$163,000",
                    "start_date": "2011/08/14",
                    "office": "Tokyo",
                    "extn": "8899"
                },
                {
                    "name": "Michelle House",
                    "position": "Integration Specialist",
                    "salary": "$95,400",
                    "start_date": "2011/06/02",
                    "office": "Sidney",
                    "extn": "2769"
                },
                {
                    "name": "Suki Burks",
                    "position": "Developer",
                    "salary": "$114,500",
                    "start_date": "2009/10/22",
                    "office": "London",
                    "extn": "6832"
                },
                {
                    "name": "Prescott Bartlett",
                    "position": "Technical Author",
                    "salary": "$145,000",
                    "start_date": "2011/05/07",
                    "office": "London",
                    "extn": "3606"
                },
                {
                    "name": "Gavin Cortez",
                    "position": "Team Leader",
                    "salary": "$235,500",
                    "start_date": "2008/10/26",
                    "office": "San Francisco",
                    "extn": "2860"
                },
                {
                    "name": "Martena Mccray",
                    "position": "Post-Sales support",
                    "salary": "$324,050",
                    "start_date": "2011/03/09",
                    "office": "Edinburgh",
                    "extn": "8240"
                },
                {
                    "name": "Unity Butler",
                    "position": "Marketing Designer",
                    "salary": "$85,675",
                    "start_date": "2009/12/09",
                    "office": "San Francisco",
                    "extn": "5384"
                },
                {
                    "name": "Howard Hatfield",
                    "position": "Office Manager",
                    "salary": "$164,500",
                    "start_date": "2008/12/16",
                    "office": "San Francisco",
                    "extn": "7031"
                },
                {
                    "name": "Hope Fuentes",
                    "position": "Secretary",
                    "salary": "$109,850",
                    "start_date": "2010/02/12",
                    "office": "San Francisco",
                    "extn": "6318"
                },
                {
                    "name": "Vivian Harrell",
                    "position": "Financial Controller",
                    "salary": "$452,500",
                    "start_date": "2009/02/14",
                    "office": "San Francisco",
                    "extn": "9422"
                },
                {
                    "name": "Timothy Mooney",
                    "position": "Office Manager",
                    "salary": "$136,200",
                    "start_date": "2008/12/11",
                    "office": "London",
                    "extn": "7580"
                },
                {
                    "name": "Jackson Bradshaw",
                    "position": "Director",
                    "salary": "$645,750",
                    "start_date": "2008/09/26",
                    "office": "New York",
                    "extn": "1042"
                },
                {
                    "name": "Olivia Liang",
                    "position": "Support Engineer",
                    "salary": "$234,500",
                    "start_date": "2011/02/03",
                    "office": "Singapore",
                    "extn": "2120"
                },
                {
                    "name": "Bruno Nash",
                    "position": "Software Engineer",
                    "salary": "$163,500",
                    "start_date": "2011/05/03",
                    "office": "London",
                    "extn": "6222"
                },
                {
                    "name": "Sakura Yamamoto",
                    "position": "Support Engineer",
                    "salary": "$139,575",
                    "start_date": "2009/08/19",
                    "office": "Tokyo",
                    "extn": "9383"
                },
                {
                    "name": "Thor Walton",
                    "position": "Developer",
                    "salary": "$98,540",
                    "start_date": "2013/08/11",
                    "office": "New York",
                    "extn": "8327"
                },
                {
                    "name": "Finn Camacho",
                    "position": "Support Engineer",
                    "salary": "$87,500",
                    "start_date": "2009/07/07",
                    "office": "San Francisco",
                    "extn": "2927"
                },
                {
                    "name": "Serge Baldwin",
                    "position": "Data Coordinator",
                    "salary": "$138,575",
                    "start_date": "2012/04/09",
                    "office": "Singapore",
                    "extn": "8352"
                },
                {
                    "name": "Zenaida Frank",
                    "position": "Software Engineer",
                    "salary": "$125,250",
                    "start_date": "2010/01/04",
                    "office": "New York",
                    "extn": "7439"
                },
                {
                    "name": "Zorita Serrano",
                    "position": "Software Engineer",
                    "salary": "$115,000",
                    "start_date": "2012/06/01",
                    "office": "San Francisco",
                    "extn": "4389"
                },
                {
                    "name": "Jennifer Acosta",
                    "position": "Junior Javascript Developer",
                    "salary": "$75,650",
                    "start_date": "2013/02/01",
                    "office": "Edinburgh",
                    "extn": "3431"
                },
                {
                    "name": "Cara Stevens",
                    "position": "Sales Assistant",
                    "salary": "$145,600",
                    "start_date": "2011/12/06",
                    "office": "New York",
                    "extn": "3990"
                },
                {
                    "name": "Hermione Butler",
                    "position": "Regional Director",
                    "salary": "$356,250",
                    "start_date": "2011/03/21",
                    "office": "London",
                    "extn": "1016"
                },
                {
                    "name": "Lael Greer",
                    "position": "Systems Administrator",
                    "salary": "$103,500",
                    "start_date": "2009/02/27",
                    "office": "London",
                    "extn": "6733"
                },
                {
                    "name": "Jonas Alexander",
                    "position": "Developer",
                    "salary": "$86,500",
                    "start_date": "2010/07/14",
                    "office": "San Francisco",
                    "extn": "8196"
                },
                {
                    "name": "Shad Decker",
                    "position": "Regional Director",
                    "salary": "$183,000",
                    "start_date": "2008/11/13",
                    "office": "Edinburgh",
                    "extn": "6373"
                },
                {
                    "name": "Michael Bruce",
                    "position": "Javascript Developer",
                    "salary": "$183,000",
                    "start_date": "2011/06/27",
                    "office": "Singapore",
                    "extn": "5384"
                },
                {
                    "name": "Donna Snider",
                    "position": "Customer Support",
                    "salary": "$112,000",
                    "start_date": "2011/01/25",
                    "office": "New York",
                    "extn": "4226"
                }
            ]
        }
        print json.dumps(data)

        return HttpResponse(json.dumps(data), 'applications/json')
    else:
        return render(request, 'test01.html')

def signin(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.authenticate_user()
        print user.is_staff
        if (user.is_staff == True):
            login(request, user)
            return render(request, 'stastic/stastic_index.html')
    return render(request, 'registration/login.html', {'form': form})

@login_required
def month_stastic(request):
    return render(request, 'stastic/month_stastic.html')


# state view
@login_required
def mana_state(request):
    return render(request, 'state/mana_state.html')

@login_required
def dev_state(request):
    return render(request, 'state/dev_state.html')


# certificate view
@login_required
def certificate(request):
    client = MongoClient(database_id, 27017)
    db = client.edxapp
    pb_list = []
    pb_dict = dict()

    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'org':
            data = json.dumps(dic_univ, cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'course':
            course_list = []
            org = request.GET['org']
            cur = connection.cursor()

            query = "select course_id from certificates_generatedcertificate where course_id like '%" + org + "%' group by course_id"
            cur.execute(query)
            course = cur.fetchall()
            cur.close()

            for c in course:
                value_list = []

                print "c[0]", c[0]
                course_id = c[0]

                cid = course_id.split('+')[1]
                run = course_id.split('+')[2]
                cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
                pb = cursor.get('versions').get('published-branch')

                cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},
                                                            {"blocks": {"$elemMatch": {"block_type": "course"}}})
                course_name = cursor.get('blocks')[0].get('fields').get('display_name')  # course_names
                value_list.append(str(pb))
                value_list.append(course_name)
                value_list.append(run)
                print value_list
                course_list.append(value_list)
            data = json.dumps(list(course_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'run':
            course_pb = request.GET['course']
            print 'course_pb', course_pb
            cursor = db.modulestore.active_versions.find({'versions.published-branch': ObjectId(course_pb)})

            for document in cursor:
                run = document.get('run')
                print 'run', run
            cursor.close()
            data = json.dumps(run, cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'certificate':
            course_pb = request.GET['course_id']
            run = request.GET['run']
            course = ''
            cursor = db.modulestore.active_versions.find({'versions.published-branch': ObjectId(course_pb)})
            for document in cursor:
                course = document.get('course')
            print 'course', course
            cursor.close()

            cur = connection.cursor()
            query = "SELECT DISTINCT course_id FROM certificates_generatedcertificate WHERE course_id LIKE '%" + course + "%' AND course_id LIKE '%" + run + "%'"
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            print 'row == ' + str(row)
            for r in row:
                certi = 'O'
                data = json.dumps(certi, cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'create_certi':
            org_name = request.GET['org_name']
            run = request.GET['run']
            for org, name in dic_univ.iteritems():
                if name == org_name:
                    org_id = org
            # print org_id
            cur = connection.cursor()
            query = "select course_id from certificates_generatedcertificate where course_id like '%" + org_id + "%' and course_id like '%" + run + "%' group by course_id"
            cur.execute(query)
            course = cur.fetchall()
            cur.close()

            for c in course:
                value_list = []
                print "c[0]", c[0]
                course_id = c[0]

                cid = course_id.split('+')[1]
                run = course_id.split('+')[2]
                print org_id, '/', cid, '/', run

                cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
                pb = cursor.get('versions').get('published-branch')

                cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},
                                                            {"blocks": {"$elemMatch": {"block_type": "course"}}})
                course_end = cursor.get('blocks')[0].get('fields').get('end')  # course_names
                end_date = datetime.datetime.strptime(str(course_end)[0:10], "%Y-%m-%d").date()
                today = datetime.date.today()

                if end_date > today:
                    data = json.dumps('Error')
                else:
                    print '-----ready make certificate !!-----'
                    subprocess.call('ssh vagrant@192.168.33.12 ./test.sh ' + org_id + ' ' + cid + ' ' + run + '',
                                    shell=True)
                    print '-----end create certificate !!-----'
                    data = json.dumps('Success')
        elif request.GET['method'] == 'uni_certi':
            cur = connection.cursor()
            query = """
				SELECT course_id,
					   date_format(min(created_date),'%Y-%m-%d') cdate,
					   sum(if(status = 'downloadable', 1, 0)) downcnt,
					   sum(if(status = 'notpassing', 1, 0)) notcnt,
					   count(*) cnt
				  FROM certificates_generatedcertificate
			"""
            if 'org_id' in request.GET:
                query += "WHERE course_id like '%" + request.GET['org_id'] + "%'"
            if 'run' in request.GET:
                query += " and course_id LIKE '%" + request.GET['run'] + "%'"
            query += "GROUP BY course_id ORDER BY created_date DESC"
            cur.execute(query)
            course_list = cur.fetchall()
            cur.close()
            course_orgs = {}
            course_end = {}
            course_name = {}

            certi_list = []
            for c, cdate, downcnt, notcnt, cnt in course_list:
                value_list = []
                # print c
                # cid = str(c[0])
                # cid = str(c)
                course_id = c
                cid = c.split('+')[1]
                run = c.split('+')[2]
                cer_per = (downcnt / cnt) * 100
                cer_percent = round(cer_per, 2)

                # db.modulestore.active_versions --------------------------------------
                cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
                pb = cursor.get('versions').get('published-branch')
                # course_orgs
                course_orgs[course_id] = cursor.get('org')

                # db.modulestore.structures --------------------------------------
                cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},
                                                            {"blocks": {"$elemMatch": {"block_type": "course"}}})

                course_name = cursor.get('blocks')[0].get('fields').get('display_name')  # course_names
                course_end = cursor.get('blocks')[0].get('fields').get('end')  # course_ends

                # print course_orgs[course_id],course_name, run, course_end, cdate, cnt, downcnt, notcnt, cer_percent
                end_date = datetime.datetime.strptime(str(course_end)[0:10], "%Y-%m-%d").date()

                value_list.append(dic_univ[course_orgs[course_id]])
                value_list.append(course_name)
                value_list.append(run)
                value_list.append(end_date)
                value_list.append(cdate)
                value_list.append(cnt)
                value_list.append(downcnt)
                value_list.append(notcnt)
                value_list.append(cer_percent)

                # print "value_list == ",value_list
                certi_list.append(value_list)
            # print "certi_list ==", certi_list
            data = json.dumps(list(certi_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    return render(request, 'certificate/certificate.html')

@login_required
def per_certificate(request):
    client = MongoClient(database_id, 27017)
    db = client.edxapp
    reload(sys)
    sys.setdefaultencoding('utf-8')
    alist = []
    if request.is_ajax():
        data = json.dumps('fail')
        if request.GET['method'] == 'per_certi':
            org_id = request.GET['org_id']
            run = request.GET['run']
            cur = connection.cursor()
            query = """
				SELECT course_id
				  FROM certificates_generatedcertificate
			"""
            if 'org_id' in request.GET:
                query += "WHERE course_id like '%" + org_id + "%'"
            if 'run' in request.GET:
                query += " and course_id LIKE '%" + run + "%'"
            query += "GROUP BY course_id"
            cur.execute(query)
            course_list = cur.fetchall()
            cur.close()

            for c in course_list:
                value_list = []
                course_id = c
                cid = c[0].split('+')[1]
                course = org_id + '+' + cid + '+' + run
                cur = connection.cursor()
                # print dic_univ[org_id], cid, run, course
                query = """
						select @RNUM := @RNUM + 1 AS NO, a.name, b.email,'""" + dic_univ[
                    org_id] + """' org, '""" + cid + """' course, '""" + run + """' run,
							   case when a.status = 'downloadable' then '생성완료'
									when a.status = 'notpassing' then '생성 전'
									when a.status = 'generated' then '생성오류' else '' end status
						  from ( SELECT @RNUM := 0 ) c, certificates_generatedcertificate a inner join auth_user b
							on (a.user_id = b.id)
						 where a.course_id like '%""" + str(course) + """%'
						 limit 2000
 				"""

                cur.execute(query)
                row = cur.fetchall()
                cur.close()
            # print str(row)

            data = json.dumps(list(row), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'email_search':
            course = ""
            user_list = []

            email = request.GET['email']
            cur = connection.cursor()
            query = """
					select course_id, email
					from certificates_generatedcertificate a inner join auth_user b
					on a.user_id = b.id
					where b.email like '%""" + email + """%'
			"""
            if 'org_id' in request.GET:
                query += "and a.course_id like '%" + request.GET['org_id'] + "%'"
            if 'run' in request.GET:
                query += " and a.course_id LIKE '%" + request.GET['run'] + "%'"
            cur.execute(query)
            course_list = cur.fetchall()
            cur.close()
            i = 1
            for c, email in course_list:
                value_list = []
                course_id = c
                org_start = c.find(':') + 1
                org_end = c.find('+', org_start)
                org = c[org_start:org_end]
                cid = c.split('+')[1]
                run = c.split('+')[2]

                cur = connection.cursor()
                # print dic_univ[org_id], cid, run, course
                query = """
						select a.name, b.email,'""" + dic_univ[org] + """' org, '""" + cid + """' course, '""" + run + """' run,
							   case when a.status = 'downloadable' then '생성완료'
									when a.status = 'notpassing' then '생성 전'
									when a.status = 'generated' then '생성오류' else '' end status
						  from ( SELECT @RNUM := 0 ) c, certificates_generatedcertificate a inner join auth_user b
							on (a.user_id = b.id)
						 where b.email like '%""" + email + """%'
 				"""

                cur.execute(query)
                row = cur.fetchone()
                cur.close()
                value_list.append(i)
                value_list.append(row[0])
                value_list.append(row[1])
                value_list.append(row[2])
                value_list.append(row[3])
                value_list.append(row[4])
                value_list.append(row[5])
                user_list.append(value_list)
                i += 1

            data = json.dumps(list(user_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(data, 'applications/json')

    return render(request, 'certificate/per_certificate.html')

@login_required
def uni_certificate(request):
    # cert = GeneratedCertificate.objects.get(course_id='course-v1:KoreaUnivK+ku_hum_001+2015_A02')
    cert = GeneratedCertificate.objects.filter(course_id='course-v1:KoreaUnivK+ku_hum_001+2015_A02').only('course_id')

    print '@@@ uni_certificate called @@@', len(cert)
    print 'sql s --------------------'
    print cert.query
    print 'sql e --------------------'

    context = dict()
    context['test'] = '1'

    return render(request, 'certificate/uni_certificate.html', context)


# community view
@login_required
def comm_notice(request):
    noti_list = []
    if request.is_ajax():
        aaData = {}
        if request.GET['method'] == 'notice_list':
            cur = connection.cursor()
            query = """
                SELECT board_id,
                       content,
                       subject,
                       SUBSTRING(reg_date, 1, 11),
                       CASE
                          WHEN use_yn = 'Y' THEN '보임'
                          WHEN use_yn = 'N' THEN '숨김'
                          ELSE ''
                       END
                          use_yn,
                       CASE WHEN odby = '0' THEN '' ELSE odby END odby,
                       CASE
                          WHEN head_title = 'noti_n' THEN '공지'
                          WHEN head_title = 'advert_n' THEN '공고'
                          WHEN head_title = 'guide_n' THEN '안내'
                          WHEN head_title = 'event_n' THEN '이벤트'
                          WHEN head_title = 'etc_n' THEN '기타'
                          ELSE ''
                       END
                          head_title,
                       use_yn
                  FROM tb_board
                 WHERE section = 'N' AND NOT use_yn = 'D'
			"""

            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                query += "and " + title + " like '%" + search + "%'"

            # query += " ORDER BY board_id"

            # print 'query', query

            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            index = 1
            for noti in row:
                value_list = []
                notice = noti
                # print notice
                value_list.append(notice[0])
                value_list.append(index)
                value_list.append(notice[6])
                value_list.append(notice[2])
                value_list.append(notice[1])
                value_list.append(notice[3])
                value_list.append(notice[4])
                value_list.append(notice[5])
                value_list.append(notice[7])
                noti_list.append(value_list)
                index += 1

            aaData = json.dumps(list(noti_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'notice_del':
            noti_id = request.GET['noti_id']
            use_yn = request.GET['use_yn']
            yn = ''
            if use_yn == 'Y':
                yn = 'N'
            else:
                yn = 'Y'
            # print 'use_yn == ',use_yn,' yn == ',yn
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + noti_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        elif request.GET['method'] == 'notice_delete':
            noti_id = request.GET['noti_id']
            use_yn = request.GET['use_yn']
            yn = 'D'

            # print 'use_yn == ',use_yn,' yn == ',yn
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + noti_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        return HttpResponse(aaData, 'applications/json')

    return render(request, 'community/comm_notice.html')

# ---------- 2017.10.23 ahn jin yong ---------- #
@csrf_exempt
def new_notice(request):
    if request.FILES:
        #init list
        file_name_list = []
        file_dir_list = []
        file_size_raw_list = []
        file_size_list = []
        file_ext_list = []
        file_list = request.FILES.getlist('file')
        file_list_cnt = len(request.FILES.getlist('file'))

        #make name, dir
        for item in file_list:
            file_name_list.append( str(item) )
            file_dir_list.append( UPLOAD_DIR+str(item) )

        #make ext
        for item in file_name_list:
            file_ext = get_file_ext(item)
            file_ext_list.append(file_ext)

        #crete file
        cnt = 0
        for item in file_list:
            fp = open(file_dir_list[cnt], 'wb')
            for chunk in item.chunks():
                fp.write(chunk)
            fp.close()
            cnt += 1

        #make raw_size
        for item in file_dir_list:
            file_size_raw_list.append( os.path.getsize(item) )

        #make size (KB)
        for item in file_size_raw_list:
            file_size_list.append( str(item / 1024) + "KB" ) #invert KB

        return JsonResponse({'name':file_name_list, 'size':file_size_list, 'len':file_list_cnt})

    elif request.method == 'POST':
        data = json.dumps({'status': "fail", 'msg': "오류가 발생했습니다"})
        if request.POST['method'] == 'add':

            # board var
            title = request.POST.get('nt_title')
            title = title.replace("'", "''")
            content = request.POST.get('nt_cont')
            content = content.replace("'", "''")
            head_title = request.POST.get('head_title')
            section = request.POST.get('notice')
            odby = request.POST.get('odby')
            upload_file = request.POST.get('uploadfile')

            # attach var
            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')

            # file 
            file_ext_list = []
            file_name_list = []
            file_size_list = []

            # make file name, size, ext
            upload_file = unicode(upload_file)
            upload_split = upload_file.split('+')
            for item in upload_split:
                index = item.find('   ')
                file_name_list.append( item[:index] )
                file_size_list.append( item[index+3:] )
            file_name_list.pop()
            file_size_list.pop()
            for item in file_name_list:
                file_ext_list.append( get_file_ext(item) )
            file_cnt = len(file_name_list)

            # ------ 공지사항 쓰기 query ------ #
            cur = connection.cursor()
            query = '''
                INSERT INTO edxapp.tb_board 
                            (subject, 
                             content, 
                             head_title, 
                             section,
                             odby) 
                VALUES      ('{0}', 
                             '{1}', 
                             '{2}', 
                             '{3}',
                             '{4}') 
            '''.format(title, content, head_title, section, odby)
            cur.execute(query)
            # ------ 공지사항 쓰기 query ------ #

            # ------ 공지사항 게시판 아이디 조회 query ------ #
            query2 = '''
                SELECT board_id 
                FROM   tb_board 
                WHERE  subject = '{0}' 
                       AND content = '{1}' 
            '''.format(title, content)
            cur.execute(query2)
            board_list = cur.fetchall()
            board_id = board_list[0][0]
            cur.close()
            # ------ 공지사항 게시판 아이디 조회 query ------ #

            # ------ 공지사항 파일첨부 query ------ #
            if upload_file != '':
                for i in range(0, file_cnt):
                    cur = connection.cursor()
                    query = '''
                    INSERT INTO edxapp.tb_board_attach 
                                (board_id, 
                                 attatch_file_name, 
                                 attatch_file_ext, 
                                 attatch_file_size) 
                     VALUES      ('{0}', 
                                  '{1}', 
                                  '{2}', 
                                  '{3}') 
                    '''.format(board_id, file_name_list[i], file_ext_list[i], file_size_list[i])
                    cur.execute(query)
                    cur.close()
            # ------ 공지사항 파일첨부 query ------ #
            data = json.dumps({'status': "success"})

        elif request.POST['method'] == 'modi':

            # board var
            title = request.POST.get('nt_title')
            title = title.replace("'", "''")
            content = request.POST.get('nt_cont')
            content = content.replace("'", "''")
            noti_id = request.POST.get('noti_id')
            odby = request.POST.get('odby')
            head_title = request.POST.get('head_title')
            upload_file = request.POST.get('uploadfile')

            # attach var
            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')

            # file 
            file_ext_list = []
            file_name_list = []
            file_size_list = []

            # make file name, size, ext
            upload_file = unicode(upload_file)
            upload_split = upload_file.split('+')
            for item in upload_split:
                index = item.find('   ')
                file_name_list.append( item[:index] )
                file_size_list.append( item[index+3:] )
            file_name_list.pop()
            file_size_list.pop()
            for item in file_name_list:
                file_ext_list.append( get_file_ext(item) )
            file_cnt = len(file_name_list)

            # ------ 공지사항 수정 query ------ #
            cur = connection.cursor()
            query = '''
                UPDATE edxapp.tb_board 
                SET    subject = '{0}', 
                       content = '{1}', 
                       head_title = '{2}', 
                       mod_date = Now(),
                       odby = {3}
                WHERE  board_id = '{4}' 
            '''.format(title, content, head_title, odby, noti_id)
            cur.execute(query)
            cur.close()
            # ------ 공지사항 수정 query ------ #

            # ------ 공지사항 파일첨부 query ------ #
            if upload_file != '':
                for i in range(0, file_cnt):
                    cur = connection.cursor()
                    query = '''
                    INSERT INTO edxapp.tb_board_attach 
                                (board_id, 
                                 attatch_file_name, 
                                 attatch_file_ext, 
                                 attatch_file_size) 
                     VALUES      ('{0}', 
                                  '{1}', 
                                  '{2}', 
                                  '{3}') 
                    '''.format(noti_id, file_name_list[i], file_ext_list[i], file_size_list[i])
                    cur.execute(query)
                    cur.close()
            # ------ 공지사항 파일첨부 query ------ #

            data = json.dumps({'status': "success"})
        return HttpResponse(data, 'applications/json')
    return render(request, 'community/comm_newnotice.html')
# ---------- 2017.10.23 ahn jin yong ---------- #

@csrf_exempt
def modi_notice(request, id, use_yn):
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            query = """
                SELECT subject,
                       content,
                       odby,
                       CASE
                          WHEN head_title = 'noti_n' THEN '공지'
                          WHEN head_title = 'advert_n' THEN '공고'
                          WHEN head_title = 'guide_n' THEN '안내'
                          WHEN head_title = 'event_n' THEN '이벤트'
                          WHEN head_title = 'etc_n' THEN '기타'
                          ELSE ''
                       END
                          head_title
                  FROM tb_board
                 WHERE section = 'N' AND board_id = %s
            """
            cur.execute(query, [id, ])
            row = cur.fetchall()
            cur.close()

            cur = connection.cursor()
            query = """
                SELECT attatch_id, attatch_file_name
                  FROM tb_board_attach
                 WHERE 1 = 1 AND del_yn = 'N' AND board_id = %s
            """
            cur.execute(query, [id, ])
            files = cur.fetchall()
            cur.close()

            mod_notice = []
            mod_notice.append(row[0][0])
            mod_notice.append(row[0][1])
            mod_notice.append(row[0][2])
            mod_notice.append(row[0][3])

            if files:
                mod_notice.append(files)
            data = json.dumps(list(mod_notice), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'file_download':
            pass # 'file_download with ajax is not working'

        return HttpResponse(data, 'applications/json')

    # ------ 공지사항 파일첨부 보여주기 query ------ #
    cur = connection.cursor()
    query = '''
        SELECT attatch_file_name, 
               attatch_file_ext, 
               attatch_file_size 
        FROM   edxapp.tb_board_attach 
        WHERE  board_id = '{0}'; 
    '''.format(id)
    cur.execute(query)
    file_list = cur.fetchall()
    cur.close()
    # ------ 공지사항 파일첨부 보여주기 query ------ #

    context = {
        'id': id,
        'use_yn': use_yn,
        'file_list':file_list
    } 

    return render_to_response('community/comm_modinotice.html', context)

@login_required
def test_index(request):
    return render(request, 'test_index.html')

@login_required
def file_download_test(request):
    print 'called  file_download_test'

    file_path = '/Users/redukyo/workspace/management/home/static/upload/create_table1.txt'
    # file_path = '/Users/redukyo/workspace/management/home/static/upload/test.jpg'

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    raise Http404

@login_required
def comm_k_news(request):
    knews_list = []
    if request.is_ajax():
        aaData = {}
        if request.GET['method'] == 'knews_list':
            cur = connection.cursor()
            query = """
                SELECT board_id,
                       content,
                       subject,
                       SUBSTRING(reg_date, 1, 11),
                       CASE
                          WHEN use_yn = 'Y' THEN '보임'
                          WHEN use_yn = 'N' THEN '숨김'
                          ELSE ''
                       END
                          use_yn,
                       CASE WHEN odby = '0' THEN '' ELSE odby END odby,
                       CASE
                          WHEN head_title = 'k_news_k' THEN 'K-MOOC소식'
                          WHEN head_title = 'report_k' THEN '보도자료'
                          WHEN head_title = 'u_news_k' THEN '대학뉴스'
                          WHEN head_title = 'support_k' THEN '서포터즈이야기'
                          WHEN head_title = 'n_new_k' THEN 'NILE소식'
                          WHEN head_title = 'etc_k' THEN '기타'
                          ELSE ''
                       END
                          head_title,
                       use_yn
                  FROM tb_board
                 WHERE section = 'K' AND NOT use_yn = 'D'
			"""

            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                query += "and " + title + " like '%" + search + "%'"
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            index = 1
            for news in row:
                value_list = []
                k_news = news
                # print 'news == ',news
                value_list.append(k_news[0])
                value_list.append(index)
                value_list.append(k_news[6])
                value_list.append(k_news[2])
                value_list.append(k_news[1])
                value_list.append(k_news[3])
                value_list.append(k_news[4])
                value_list.append(k_news[5])
                value_list.append(k_news[7])
                knews_list.append(value_list)
                index += 1

            aaData = json.dumps(list(knews_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'knews_del':
            noti_id = request.GET['noti_id']
            use_yn = request.GET['use_yn']
            yn = ''
            if use_yn == 'Y':
                yn = 'N'
            else:
                yn = 'Y'
            print 'use_yn == ', use_yn, ' yn == ', yn
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + noti_id
            print 'query == ', query
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        elif request.GET['method'] == 'knews_delete':
            noti_id = request.GET['noti_id']
            use_yn = request.GET['use_yn']
            yn = 'D'

            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + noti_id
            print 'query == ', query
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        return HttpResponse(aaData, 'applications/json')

    return render(request, 'community/comm_k_news.html')

# ---------- 2017.10.24 ahn jin yong ---------- #
@login_required
def new_knews(request):
    if request.FILES:
        #init list
        file_name_list = []
        file_dir_list = []
        file_size_raw_list = []
        file_size_list = []
        file_ext_list = []
        file_list = request.FILES.getlist('file')
        file_list_cnt = len(request.FILES.getlist('file'))

        #make name, dir
        for item in file_list:
            file_name_list.append( str(item) )
            file_dir_list.append( UPLOAD_DIR+str(item) )

        #make ext
        for item in file_name_list:
            file_ext = get_file_ext(item)
            file_ext_list.append(file_ext)

        #crete file
        cnt = 0
        for item in file_list:
            fp = open(file_dir_list[cnt], 'wb')
            for chunk in item.chunks():
                fp.write(chunk)
            fp.close()
            cnt += 1

        #make raw_size
        for item in file_dir_list:
            file_size_raw_list.append( os.path.getsize(item) )

        #make size (KB)
        for item in file_size_raw_list:
            file_size_list.append( str(item / 1024) + "KB" ) #invert KB

        return JsonResponse({'name':file_name_list, 'size':file_size_list, 'len':file_list_cnt})

    elif request.method == 'POST':
        data = json.dumps({'status': "fail", 'msg': "오류가 발생했습니다"})
        if request.POST['method'] == 'add':

            # board var
            title = request.POST.get('knews_title')
            title = title.replace("'", "''")
            content = request.POST.get('knews_content')
            content = content.replace("'", "''")
            head_title = request.POST.get('head_title')
            section = request.POST.get('k_news')
            odby = request.POST.get('odby')
            upload_file = request.POST.get('uploadfile')

            # attach var
            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')

            # file 
            file_ext_list = []
            file_name_list = []
            file_size_list = []

            # make file name, size, ext
            upload_file = unicode(upload_file)
            upload_split = upload_file.split('+')
            for item in upload_split:
                index = item.find('   ')
                file_name_list.append( item[:index] )
                file_size_list.append( item[index+3:] )
            file_name_list.pop()
            file_size_list.pop()
            for item in file_name_list:
                file_ext_list.append( get_file_ext(item) )
            file_cnt = len(file_name_list)

            # ------ K-MOOC 소식 쓰기 query ------ #
            cur = connection.cursor()
            query = '''
                INSERT INTO edxapp.tb_board 
                            (subject, 
                             content, 
                             head_title, 
                             section,
                             odby) 
                VALUES      ('{0}', 
                             '{1}', 
                             '{2}', 
                             '{3}',
                             '{4}') 
            '''.format(title, content, head_title, section, odby)
            cur.execute(query)
            # ------ K-MOOC 소식 쓰기 query ------ #

           # ------ K-MOOC 소식 아이디 조회 query ------ #
            query2 = '''
                SELECT board_id 
                FROM   tb_board 
                WHERE  subject = '{0}' 
                       AND content = '{1}' 
            '''.format(title, content)
            cur.execute(query2)
            board_list = cur.fetchall()
            board_id = board_list[0][0]
            cur.close()
           # ------ K-MOOC 소식 아이디 조회 query ------ #

            # ------ K-MOOC 소식 파일첨부 query ------ #
            if upload_file != '':
                for i in range(0, file_cnt):
                    cur = connection.cursor()
                    query = '''
                    INSERT INTO edxapp.tb_board_attach 
                                (board_id, 
                                 attatch_file_name, 
                                 attatch_file_ext, 
                                 attatch_file_size) 
                     VALUES      ('{0}', 
                                  '{1}', 
                                  '{2}', 
                                  '{3}') 
                    '''.format(board_id, file_name_list[i], file_ext_list[i], file_size_list[i])
                    cur.execute(query)
                    cur.close()
            # ------ K-MOOC 소식 파일첨부 query ------ #
            data = json.dumps({'status': "success"})

        elif request.POST['method'] == 'modi':

            # board var
            title = request.POST.get('k_news_title')
            title = title.replace("'", "''")
            content = request.POST.get('k_news_cont')
            content = content.replace("'", "''")
            noti_id = request.POST.get('k_news_id')
            odby = request.POST.get('odby')
            head_title = request.POST.get('head_title')
            upload_file = request.POST.get('uploadfile')
 
            # attach var
            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')

            # file 
            file_ext_list = []
            file_name_list = []
            file_size_list = []

            # make file name, size, ext
            upload_file = unicode(upload_file)
            upload_split = upload_file.split('+')
            for item in upload_split:
                index = item.find('   ')
                file_name_list.append( item[:index] )
                file_size_list.append( item[index+3:] )
            file_name_list.pop()
            file_size_list.pop()
            for item in file_name_list:
                file_ext_list.append( get_file_ext(item) )
            file_cnt = len(file_name_list)

            # ------ K-MOOC 소식 수정 query ------ #
            cur = connection.cursor()
            query = '''
                UPDATE edxapp.tb_board 
                SET    subject = '{0}', 
                       content = '{1}', 
                       head_title = '{2}', 
                       mod_date = Now(),
                       odby = {3}
                WHERE  board_id = '{4}' 
            '''.format(title, content, head_title, odby, noti_id)
            cur.execute(query)
            cur.close()
            # ------ K-MOOC 소식 수정 query ------ #

            # ------ K-MOOC 파일첨부 query ------ #
            if upload_file != '':
                for i in range(0, file_cnt):
                    cur = connection.cursor()
                    query = '''
                    INSERT INTO edxapp.tb_board_attach 
                                (board_id, 
                                 attatch_file_name, 
                                 attatch_file_ext, 
                                 attatch_file_size) 
                     VALUES      ('{0}', 
                                  '{1}', 
                                  '{2}', 
                                  '{3}') 
                    '''.format(str(noti_id), file_name_list[i], file_ext_list[i], file_size_list[i])
                    cur.execute(query)
                    cur.close()
            # ------ K-MOOC 파일첨부 query ------ #

            data = json.dumps({'status': "success"})
        return HttpResponse(data, 'applications/json')
    return render(request, 'community/comm_newknews.html')
# ---------- 2017.10.24 ahn jin yong ---------- #

@login_required
def modi_knews(request, id, use_yn):
    mod_knews = []
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            query = """
					SELECT subject,
						   content,
						   odby,
						   CASE
							  WHEN head_title = 'k_news_k' THEN 'K-MOOC소식'
							  WHEN head_title = 'report_k' THEN '보도자료'
							  WHEN head_title = 'u_news_k' THEN '대학뉴스'
							  WHEN head_title = 'support_k' THEN '서포터즈이야기'
							  WHEN head_title = 'n_new_k' THEN 'NILE소식'
							  WHEN head_title = 'etc_k' THEN '기타'
							  ELSE ''
						   END
							  head_title
					  FROM tb_board
					 WHERE section = 'K' and board_id = """ + id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()

            cur = connection.cursor()

            query = """
                SELECT attatch_id, attatch_file_name
                  FROM tb_board_attach
                 WHERE 1 = 1 AND del_yn = 'N' AND board_id = %s
            """
            cur.execute(query, [id, ])
            files = cur.fetchall()
            cur.close()
            mod_knews.append(row[0][0])
            mod_knews.append(row[0][1])
            mod_knews.append(row[0][2])
            mod_knews.append(row[0][3])
            if files:
                mod_knews.append(files)
            data = json.dumps(list(mod_knews), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'file_download':
            file_name = request.GET['file_name']
            data = json.dumps(UPLOAD_DIR + file_name, cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(data, 'applications/json')
    
    # ------ knews 파일첨부 보여주기 query ------ #
    cur = connection.cursor()
    query = '''
        SELECT attatch_file_name, 
               attatch_file_ext, 
               attatch_file_size 
        FROM   edxapp.tb_board_attach 
        WHERE  board_id = '{0}'; 
    '''.format(id)
    cur.execute(query)
    file_list = cur.fetchall()
    cur.close()
    # ------ knews 파일첨부 보여주기 query ------ #

    context = {
        'id': id,
        'use_yn': use_yn,
        'file_list':file_list
    } 

    return render_to_response('community/comm_modi_knews.html', context)

@login_required
def comm_faq(request):
    faq_list = []
    data = json.dumps({'status': "fail"})
    if request.is_ajax():
        if request.GET['method'] == 'faq_list':
            aaData = {}
            cur = connection.cursor()
            query = """
					SELECT board_id,
						   content,
						   subject,
						   SUBSTRING(reg_date, 1, 11),
						   CASE
							  WHEN use_yn = 'Y' THEN '보임'
							  WHEN use_yn = 'N' THEN '숨김'
							  ELSE ''
						   END
							  use_yn,
						   CASE
							  WHEN head_title = 'kmooc_f' THEN 'K-MOOC'
							  WHEN head_title = 'regist_f ' THEN '회원가입'
							  WHEN head_title = 'login_f ' THEN '로그인/계정'
							  WHEN head_title = 'enroll_f ' THEN '수강신청/취소'
							  WHEN head_title = 'course_f ' THEN '강좌수강'
							  WHEN head_title = 'certi_f  ' THEN '성적/이수증'
							  WHEN head_title = 'tech_f ' THEN '기술적문제'
							  WHEN head_title = 'mobile_f ' THEN '모바일앱'
							  ELSE ''
						   END
							  head_title,
						   use_yn
					  FROM tb_board
					 WHERE section = 'F' AND NOT use_yn = 'D'
			"""
            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                query += "and " + title + " like '%" + search + "%'"

            # query += " ORDER BY board_id"

            # print 'query', query

            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            index = 1
            for f in row:
                value_list = []
                faq = f
                # print faq
                value_list.append(faq[0])
                value_list.append(index)
                value_list.append(faq[5])
                value_list.append(faq[2])
                value_list.append(faq[1])
                value_list.append(faq[3])
                value_list.append(faq[4])
                value_list.append(faq[6])
                faq_list.append(value_list)
                index += 1
            # print 'faq_list == ',faq_list
            aaData = json.dumps(list(faq_list), cls=DjangoJSONEncoder, ensure_ascii=False)
            return HttpResponse(aaData, 'applications/json')

        elif request.GET['method'] == 'faq_del':
            faq_id = request.GET['faq_id']
            use_yn = request.GET['use_yn']
            yn = ''
            if use_yn == 'Y':
                yn = 'N'
            else:
                yn = 'Y'
            # print 'use_yn == ',use_yn,' yn == ',yn
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + faq_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
            return HttpResponse(aaData, 'applications/json')
        elif request.GET['method'] == 'faq_delete':
            faq_id = request.GET['faq_id']
            use_yn = request.GET['use_yn']
            yn = 'D'

            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + faq_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
            return HttpResponse(aaData, 'applications/json')

        # elif request.GET['method'] == 'total_page':
        # 	if 'search_con' in request.GET:
        # 		subject = request.GET['search_con']
        # 		search = request.GET['search_search']
        # 		cur = connection.cursor()
        # 		cur.execute('''
        # 		select ceil(count(board_id)/10) from tb_board where section="F" and '''+subject+''' like "%'''+search+'''%"
        # 		''')
        # 		row = cur.fetchall()
        # 		cur.close()
        # 	else:
        # 		cur =connection.cursor()
        # 		cur.execute('''
        # 		select ceil(count(board_id)/10) from tb_board where section="F"
        # 		''')
        # 		row =cur.fetchall()
        # 		cur.close()
        # 	data = json.dumps(list(row), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    return render(request, 'community/comm_faq.html')

@login_required
def new_faq(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        if request.POST.get('method') == 'add':
            head_title = request.POST.get('head_title')
            faq_question = request.POST.get('faq_question')
            faq_question = faq_question.replace("'", "''")
            faq_answer = request.POST.get('faq_answer')
            faq_answer = faq_answer.replace("'", "''")
            section = request.POST.get('section')

            print 'head_title == ', head_title, ' faq_question == ', faq_question, ' faq_answer == ', faq_answer, ' section == ', section
            cur = connection.cursor()
            query = "insert into edxapp.tb_board(subject, content, section, head_title)"
            query += " VALUES ('" + faq_question + "', '" + faq_answer + "', '" + section + "', '" + head_title + "') "
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

        if request.POST['method'] == 'modi':
            question = request.POST.get('faq_question')
            question = question.replace("'", "''")
            answer = request.POST.get('faq_answer')
            answer = answer.replace("'", "''")
            head_title = request.POST.get('head_title')
            faq_id = request.POST.get('faq_id')
            cur = connection.cursor()
            query = "update edxapp.tb_board set subject = '" + question + "', content = '" + answer + "', head_title = '" + head_title + "', mod_date = now() where board_id = '" + faq_id + "'"
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})
        return HttpResponse(data, 'applications/json')

    return render(request, 'community/comm_newfaq.html')

@login_required
def modi_faq(request, id, use_yn):
    mod_faq = []
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            query = """
					SELECT subject,
						   content,
						   CASE
							  WHEN head_title = 'kmooc_f' THEN 'K-MOOC'
							  WHEN head_title = 'regist_f ' THEN '회원가입'
							  WHEN head_title = 'login_f ' THEN '로그인/계정'
							  WHEN head_title = 'enroll_f ' THEN '수강신청/취소'
							  WHEN head_title = 'course_f ' THEN '강좌수강'
							  WHEN head_title = 'certi_f  ' THEN '성적/이수증'
							  WHEN head_title = 'tech_f ' THEN '기술적문제'
							  WHEN head_title = 'mobile_f ' THEN '모바일앱'
							  ELSE ''
						   END
							  head_title
					  FROM tb_board
					 WHERE board_id = """ + id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            print 'query', query
            for f in row:
                faq = f
                mod_faq.append(faq)
            data = json.dumps(list(mod_faq), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    variables = RequestContext(request, {
        'id': id,
        'use_yn': use_yn
    })

    return render_to_response('community/comm_modifaq.html', variables)

@login_required
def comm_faqrequest(request):
    if request.is_ajax():
        aaData = json.dumps({'status': "fail"})
        f_request_list = []
        if request.GET['method'] == 'faqrequest_list':
            cur = connection.cursor()
            query = """
					SELECT id,
						   head_title,
						   question,
						   student_email,
						   response_email,
						   SUBSTRING(reg_date, 1, 11)
					  FROM faq_request;
			"""
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            index = 1
            for fr in row:
                value_list = []
                faq_request = fr
                value_list.append(faq_request[0])
                value_list.append(index)
                value_list.append(faq_request[1])
                value_list.append(faq_request[2])
                value_list.append(faq_request[3])
                value_list.append(faq_request[4])
                value_list.append(faq_request[5])
                f_request_list.append(value_list)
                index += 1
            aaData = json.dumps(list(f_request_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(aaData, 'applications/json')
    return render_to_response('community/comm_faqrequest.html')

@login_required
def comm_reference_room(request):
    refer_list = []
    if request.is_ajax():
        aaData = {}
        if request.GET['method'] == 'refer_list':
            cur = connection.cursor()
            query = """
					SELECT board_id,
						   use_yn,
						   CASE
							  WHEN head_title = 'publi_r' THEN '홍보자료'
							  WHEN head_title = 'data_r' THEN '자료집'
							  WHEN head_title = 'repo_r' THEN '보고서'
							  WHEN head_title = 'etc_r' THEN '기타'
							  ELSE ''
						   END
							  head_title,
						   subject,
						   SUBSTRING(reg_date, 1, 11),
						   CASE
							  WHEN use_yn = 'Y' THEN '보임'
							  WHEN use_yn = 'N' THEN '숨김'
							  ELSE ''
						   END
							  use_yn,
						   CASE WHEN odby = '0' THEN '' ELSE odby END odby
					  FROM tb_board
					 WHERE section = 'R' AND NOT use_yn = 'D'
			"""
            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                query += "and " + title + " like '%" + search + "%'"

            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            index = 1
            for r in row:
                value_list = []
                refer = r
                value_list.append(refer[0])
                value_list.append(refer[1])
                value_list.append(index)
                value_list.append(refer[2])
                value_list.append(refer[3])
                value_list.append(refer[4])
                value_list.append(refer[5])
                refer_list.append(value_list)
                index += 1

            aaData = json.dumps(list(refer_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'refer_del':
            refer_id = request.GET['refer_id']
            use_yn = request.GET['use_yn']
            if use_yn == 'Y':
                yn = 'N'
            else:
                yn = 'Y'
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + refer_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        elif request.GET['method'] == 'refer_delete':
            refer_id = request.GET['refer_id']
            use_yn = request.GET['use_yn']
            yn = 'D'

            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + refer_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')

        return HttpResponse(aaData, 'applications/json')
    return render(request, 'community/comm_reference_room.html')

# ---------- 2017.10.24 ahn jin yong ---------- #
@login_required
def new_refer(request):
    if request.FILES:
        #init list
        file_name_list = []
        file_dir_list = []
        file_size_raw_list = []
        file_size_list = []
        file_ext_list = []
        file_list = request.FILES.getlist('file')
        file_list_cnt = len(request.FILES.getlist('file'))

        #make name, dir
        for item in file_list:
            file_name_list.append( str(item) )
            file_dir_list.append( UPLOAD_DIR+str(item) )

        #make ext
        for item in file_name_list:
            file_ext = get_file_ext(item)
            file_ext_list.append(file_ext)

        #crete file
        cnt = 0
        for item in file_list:
            fp = open(file_dir_list[cnt], 'wb')
            for chunk in item.chunks():
                fp.write(chunk)
            fp.close()
            cnt += 1

        #make raw_size
        for item in file_dir_list:
            file_size_raw_list.append( os.path.getsize(item) )

        #make size (KB)
        for item in file_size_raw_list:
            file_size_list.append( str(item / 1024) + "KB" ) #invert KB

        return JsonResponse({'name':file_name_list, 'size':file_size_list, 'len':file_list_cnt})

    elif request.method == 'POST':
        data = json.dumps({'status': "fail", 'msg': "오류가 발생했습니다"})
        if request.POST['method'] == 'add':

            # board var
            title = request.POST.get('refer_title')
            title = title.replace("'", "''")
            content = request.POST.get('refer_cont')
            content = content.replace("'", "''")
            head_title = request.POST.get('head_title')
            section = request.POST.get('refer')
            odby = request.POST.get('odby')
            upload_file = request.POST.get('uploadfile')

            # attach var
            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')

            # file 
            file_ext_list = []
            file_name_list = []
            file_size_list = []

            # make file name, size, ext
            upload_file = unicode(upload_file)
            upload_split = upload_file.split('+')
            for item in upload_split:
                index = item.find('   ')
                file_name_list.append( item[:index] )
                file_size_list.append( item[index+3:] )
            file_name_list.pop()
            file_size_list.pop()
            for item in file_name_list:
                file_ext_list.append( get_file_ext(item) )
            file_cnt = len(file_name_list)

            # ------ 자료실 쓰기 query ------ #
            cur = connection.cursor()
            query = '''
                INSERT INTO edxapp.tb_board 
                            (subject, 
                             content, 
                             head_title, 
                             section,
                             odby) 
                VALUES      ('{0}', 
                             '{1}', 
                             '{2}', 
                             '{3}',
                             '{4}') 
            '''.format(title, content, head_title, section, odby)
            cur.execute(query)
            # ------ 자료실 쓰기 query ------ #

            # ------ 자료실 게시판 아이디 조회 query ------ #
            query2 = '''
                SELECT board_id 
                FROM   tb_board 
                WHERE  subject = '{0}' 
                       AND content = '{1}' 
            '''.format(title, content)
            cur.execute(query2)
            board_list = cur.fetchall()
            board_id = board_list[0][0]
            cur.close()
            # ------ 자료실 게시판 아이디 조회 query ------ #

            # ------ 자료실 파일첨부 query ------ #
            if upload_file != '':
                for i in range(0, file_cnt):
                    cur = connection.cursor()
                    query = '''
                    INSERT INTO edxapp.tb_board_attach 
                                (board_id, 
                                 attatch_file_name, 
                                 attatch_file_ext, 
                                 attatch_file_size) 
                     VALUES      ('{0}', 
                                  '{1}', 
                                  '{2}', 
                                  '{3}') 
                    '''.format(board_id, file_name_list[i], file_ext_list[i], file_size_list[i])
                    cur.execute(query)
                    cur.close()
            # ------ 자료실 파일첨부 query ------ #
            data = json.dumps({'status': "success"})

        elif request.POST['method'] == 'modi':

            # board var
            title = request.POST.get('refer_title')
            title = title.replace("'", "''")
            content = request.POST.get('refer_cont')
            content = content.replace("'", "''")
            refer_id = request.POST.get('refer_id')
            odby = request.POST.get('odby')
            head_title = request.POST.get('head_title')
            upload_file = request.POST.get('uploadfile')

            # attach var
            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')

            # file 
            file_ext_list = []
            file_name_list = []
            file_size_list = []

            # make file name, size, ext
            upload_file = unicode(upload_file)
            upload_split = upload_file.split('+')
            for item in upload_split:
                index = item.find('   ')
                file_name_list.append( item[:index] )
                file_size_list.append( item[index+3:] )
            file_name_list.pop()
            file_size_list.pop()
            for item in file_name_list:
                file_ext_list.append( get_file_ext(item) )
            file_cnt = len(file_name_list)

            # ------ 자료실 수정 query ------ #
            cur = connection.cursor()
            query = '''
                UPDATE edxapp.tb_board 
                SET    subject = '{0}', 
                       content = '{1}', 
                       mod_date = Now(), 
                       head_title = '{2}',
                       odby = '{3}'
                WHERE  board_id = '{4}' 
            '''.format(title, content, head_title, odby, refer_id)
            cur.execute(query)
            cur.close()
            # ------ 자료실 수정 query ------ #
  
            # ------ 자료실 파일첨부 query ------ #
            if upload_file != '':
                for i in range(0, file_cnt):
                    cur = connection.cursor()
                    query = '''
                    INSERT INTO edxapp.tb_board_attach 
                                (board_id, 
                                 attatch_file_name, 
                                 attatch_file_ext, 
                                 attatch_file_size) 
                     VALUES      ('{0}', 
                                  '{1}', 
                                  '{2}', 
                                  '{3}') 
                    '''.format(str(refer_id), file_name_list[i], file_ext_list[i], file_size_list[i])
                    cur.execute(query)
                    cur.close()
            # ------ 자료실 파일첨부 query ------ #

            data = json.dumps({'status': "success"})
        return HttpResponse(data, 'applications/json')
    return render(request, 'community/comm_newrefer.html')
# ---------- 2017.10.24 ahn jin yong ---------- #

@login_required
def modi_refer(request, id, use_yn):
    mod_refer = []

    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            query = """
                SELECT subject,
                       content,
                       odby,
                       CASE
                          WHEN head_title = 'publi_r' THEN '홍보자료'
                          WHEN head_title = 'data_r' THEN '자료집'
                          WHEN head_title = 'repo_r' THEN '보고서'
                          WHEN head_title = 'etc_r' THEN '기타'
                          ELSE ''
                       END
                          head_title
                  FROM tb_board
                 WHERE section = 'R' AND board_id = """ + id

            cur.execute(query)
            row = cur.fetchall()
            cur.close()

            cur = connection.cursor()
            query = """
                SELECT attatch_id, attatch_file_name
                  FROM tb_board_attach
                 WHERE 1 = 1 AND del_yn = 'N' AND board_id = %s
            """
            cur.execute(query, [id, ])
            files = cur.fetchall()
            cur.close()

            mod_refer.append(row[0][0])
            mod_refer.append(row[0][1])
            mod_refer.append(row[0][2])
            mod_refer.append(row[0][3])
            if files:
                mod_refer.append(files)
            data = json.dumps(list(mod_refer), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'file_download':
            file_name = request.GET['file_name']
            data = json.dumps(UPLOAD_DIR + file_name, cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    # ------ 공지사항 파일첨부 보여주기 query ------ #
    cur = connection.cursor()
    query = '''
        SELECT attatch_file_name, 
               attatch_file_ext, 
               attatch_file_size 
        FROM   edxapp.tb_board_attach 
        WHERE  board_id = '{0}'; 
    '''.format(id)
    cur.execute(query)
    file_list = cur.fetchall()
    cur.close()
    # ------ 공지사항 파일첨부 보여주기 query ------ #

    context = {
        'id': id,
        'use_yn': use_yn,
        'file_list':file_list
    } 

    return render_to_response('community/comm_modirefer.html', context)


# RSA 설정 필요
# monitoring view
@login_required
def moni_storage(request):
    if request.is_ajax():
        if request.GET['method'] == 'storage_list':
            data_list = []
            a = commands.getoutput('df -h /video')
            a_list = [1, a.split()[7], a.split()[9], a.split()[10], a.split()[11]]
            data_list.append(a_list)
            aaData = json.dumps(list(data_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(aaData, 'applications/json')
    return render(request, 'monitoring/moni_storage.html')


@csrf_exempt
def summer_upload(request):
    if 'file' in request.FILES:
        file = request.FILES['file']
        filename = file._name
        fp = open('%s/%s' % (UPLOAD_DIR, filename), 'wb')

        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        return HttpResponse('/manage/home/static/upload/' + filename)
    return HttpResponse('fail')

@login_required
def history(request):
    if request.is_ajax():
        result = dict()
        columns, recordsTotal, result_list = history_rows(request)
        result['data'] = result_list
        result['recordsTotal'] = recordsTotal
        result['recordsFiltered'] = recordsTotal

        context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(context, 'applications/json')

    else:
        return render(request, 'history/history.html')

@login_required
def history_csv(request):
    filename = 'history_csv_%s.csv' % datetime.datetime.now().strftime('%y%m%d%H%M%S')
    columns, recordsTotal, result_list = history_rows(request)

    # csv 표시 순서 정렬을 위해 header 지정
    csv_headers = [
        'system',
        'username',
        'action_time',
        'content_type_id',
        'content_type_detail',
        'action_flag',
        'target_id',
        'search_string',
        'cnt',
        'ip',
    ]
    try:

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        csvwriter = csv.writer(
            response,
            dialect='excel',
            quotechar='"',
            quoting=csv.QUOTE_ALL)

        encoded_header = [unicode(s).encode('utf-8') for s in csv_headers]
        csvwriter.writerow(encoded_header)

        for result in result_list:
            # encoded_row = [unicode(value).encode('utf-8') for key, value in result.iteritems()]
            encoded_row = [result[c] if c in result else '' for c in csv_headers]

            csvwriter.writerow(encoded_row)

        try:
            contents = unicode(response.content, 'utf-8')
            response.content = contents.encode('utf-8-sig')
        except Exception as e:
            print e

        return response

    except Exception as e:
        print e

@login_required
def history_rows(request):
    if request.is_ajax():
        is_csv = False
    else:
        is_csv = True

    page_no = request.GET.get('page_no')
    page_length = request.GET.get('page_length')
    start_no = 0

    system = request.GET.get('system')
    operation = request.GET.get('operation')
    func = request.GET.get('func')
    func_detail = request.GET.get('func_detail')
    user_id = request.GET.get('user_id')
    target_id = request.GET.get('target_id')
    # search_string = urllib.quote('검색').encode('utf8')

    print 'param s ---------------------------'
    print page_no
    print page_length
    print system
    print operation
    print func
    print func_detail
    print user_id
    print target_id
    print 'param e ---------------------------'

    if page_length == '-1' or is_csv:
        page_length = '999999'
    else:
        start_no = int(page_no) * int(page_length)

    with connections['default'].cursor() as cur:
        query_arr = []
        query_arr.append("""
            SELECT SQL_CALC_FOUND_ROWS
                     b.content_type_id, b.id, date_format(if(b.content_type_id = '311', adddate(b.action_time, interval 9 hour), b.action_time), '%Y/%m/%d %H:%i:%s') action_time,
                     a.app_label,
                     b.user_id,
                     (select username from auth_user where id = b.user_id) username,
                     b.object_id, b.object_repr,
                     b.change_message,
                     b.action_flag
                FROM django_content_type a, django_admin_log b, auth_user c
               WHERE     a.id = b.content_type_id
                         and b.user_id = c.id
                     AND (a.app_label = 'auth' OR a.model = 'custom')
                     and b.id > 247
        """)

        if system:
            if system == 'a':
                query_arr.append(" and a.id = 3 ")
            elif system == 'k':
                query_arr.append(" and a.id not in (3, 311) ")
            elif system == 'i':
                query_arr.append(" and a.id = 311 ")

        if operation:
            print 'add query type 1'
            query_arr.append(" and b.action_flag = %s " % operation)

        if func:
            print 'add query type 2'
            query_arr.append(" and a.id = %s " % func)

        if func_detail:
            print 'add query type 3'
            query_arr.append(" and b.action_flag = %s " % func_detail)

        if user_id:
            print 'add query type 4'
            query_arr.append(" and (c.id = '{user_id}' or c.username like '%{user_id}%')".format(user_id=user_id))

        if target_id:
            print 'add query type 5'
            # 강좌 운영팀 관리
            if func in ['3', '295', '306']:
                query_arr.append(" and b.object_repr like '%%%s%%' " % target_id)
            elif func in ['291']:
                query_arr.append(
                    " and b.change_message like concat('%%',(select id from auth_user where username = '%s'),'%%') " % target_id)

        query_arr.append("""
            ORDER BY b.action_time DESC, b.id desc
               LIMIT {start_no}, {page_length}
        """.format(start_no=start_no, page_length=page_length))

        query = ''.join(query_arr)

        # print 'query:', query
        # print start_no, page_length

        cur.execute(query)
        rows = cur.fetchall()
        columns = [col[0] for col in cur.description]

        cur.execute('SELECT found_rows();')
        recordsTotal = cur.fetchone()[0]

        print 'recordsTotal:', recordsTotal

        result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]

        '''
        content_type_id 에 따른 기능 구분 추가
        [306]강좌 운영팀 관리 (운영팀 - staff, 교수자 - instructor, 베타 테스터 - beta)
        [295]강좌 운영팀 관리 (게시판 관리자 - Administrator, 토의 진행자 - Moderator, 게시판 조교 - Community TA)
        '''

        diff_query1 = '''
              SELECT id,
                     username,
                     first_name,
                     last_name,
                     email,
                     password,
                     is_staff,
                     is_active,
                     is_superuser
                FROM auth_user_trigger
               WHERE id = %s
                     AND created BETWEEN adddate(str_to_date(%s, '%%Y/%%m/%%d %%H:%%i:%%s'), INTERVAL -2 SECOND)
                                     AND adddate(str_to_date(%s, '%%Y/%%m/%%d %%H:%%i:%%s'), INTERVAL 2 SECOND)
            ORDER BY action;
        '''

        diff_query2 = '''
              SELECT id,
                     user_id,
                     name,
                     language,
                     location,
                     courseware,
                     gender,
                     mailing_address,
                     year_of_birth,
                     level_of_education,
                     goals,
                     allow_certificate,
                     country,
                     city,
                     bio,
                     profile_image_uploaded_at
                FROM auth_userprofile_trigger
               WHERE     user_id = %s
                     AND created BETWEEN adddate(str_to_date(%s, '%%Y/%%m/%%d %%H:%%i:%%s'), INTERVAL -2 SECOND)
                                     AND adddate(str_to_date(%s, '%%Y/%%m/%%d %%H:%%i:%%s'), INTERVAL 2 SECOND)
            ORDER BY action;
        '''

        def git_diff_dict(columns, rows):
            return_dict = dict()
            if columns is None or rows is None:
                pass

            elif not rows or len(rows) < 2:
                pass

            else:
                check_list = [dict(zip(columns, row)) for row in rows]

                for column in columns:
                    if column == 'password':
                        continue

                    if not str(check_list[0][column]).replace('None', '') == str(check_list[1][column]).replace('None',
                                                                                                                ''):
                        return_dict[auth_dict[column]] = '"%s" > "%s"' % (check_list[0][column], check_list[1][column])

            return return_dict

        def git_diff_password(columns, rows):
            password_dict = dict()
            if columns is None or rows is None:
                pass

            elif not rows or len(rows) < 2:
                pass

            else:
                check_list = [dict(zip(columns, row)) for row in rows]

                for column in columns:
                    if not check_list[0][column] == check_list[1][column]:
                        password_dict[auth_dict[column]] = '"%s" > "%s"' % (
                            check_list[0][column], check_list[1][column])

            return password_dict

        for result_dict in result_list:
            content_type_id = result_dict['content_type_id']
            action_flag = result_dict['action_flag']
            action_time = result_dict['action_time']
            change_message_dict = get_change_message_dict(result_dict['change_message'])

            print 'action_time:', type(action_time), action_time

            # 회원정보 수정의 경우 변경점을 찾아서 추가한다.
            diff_result = dict()
            diff_result_string = ''
            if content_type_id == '3' and action_flag == '2':
                check_id = result_dict['object_id']

                # 비밀번호를 변경하는 화면은 회원정보 수정과 별개로 구성되어있음
                # 비밀번호 변경의 경우와 아닌경우를 분기
                query_string_dict = change_message_dict['query']

                # print 'check diff ---------------------------------------------- s'
                # print diff_query1, [check_id, check_id, action_time, action_time]
                # print 'check diff ---------------------------------------------- e'

                if query_string_dict.has_key('password1') and query_string_dict.has_key('password2'):
                    print 'just password change !!'

                    cur.execute(diff_query1, [check_id, action_time, action_time])
                    columns1 = [col[0] for col in cur.description]
                    diff_rows1 = cur.fetchall()
                    diff_result.update(git_diff_password(columns1, diff_rows1))

                    for index, key in enumerate(diff_result.keys()):
                        diff_result_string += ('' if index == 0 else ', ') + key + " : " + diff_result[key]
                else:

                    cur.execute(diff_query1, [check_id, action_time, action_time])
                    columns1 = [col[0] for col in cur.description]
                    diff_rows1 = cur.fetchall()
                    diff_result.update(git_diff_dict(columns1, diff_rows1))

                    print 'action_time ===>', result_dict['action_time']

                    cur.execute(diff_query2, [check_id, action_time, action_time])
                    columns2 = [col[0] for col in cur.description]
                    diff_rows2 = cur.fetchall()
                    diff_result.update(git_diff_dict(columns2, diff_rows2))

                    for index, key in enumerate(diff_result.keys()):
                        # print 'index -------------->', index, key, index == 0
                        diff_result_string += ('' if index == 0 else ', ') + key + " : " + diff_result[key]

            object_repr_dict = get_object_repr_dict(result_dict['object_repr'])

            # 기능 구분에 따라 시스템 표시 구분
            result_dict['system'] = get_system_name(content_type_id)

            # 기능 구분별 상세구분 표시 내용 추가
            # 개인정보 수정의 경우 수정 내역을 표시
            if content_type_id in ['2', '3']:
                content_detail = diff_result_string
            else:
                content_detail = get_content_detail(content_type_id, object_repr_dict, change_message_dict)

            result_dict['content_type_detail'] = content_detail
            result_dict['search_string'] = get_searcy_string(content_type_id, change_message_dict)

            if content_type_id in ['293', '309']:
                beta_testers = object_repr_dict['identifiers']
                targets = beta_testers.replace('[', '').replace("u'", "").replace('\'', '')
            else:
                targets = get_target_id(content_type_id, object_repr_dict)

            result_dict['target_id'] = targets
            result_dict['content_type_id'] = content_type_dict[content_type_id]
            result_dict['action_flag'] = action_flag_dict[action_flag]
            result_dict['ip'] = change_message_dict['ip'] if 'ip' in change_message_dict else '-'
            result_dict['cnt'] = (change_message_dict['count'] if isinstance(change_message_dict['count'], int) else '-') if 'count' in change_message_dict and content_type_id not in ['303',
                                                                                                                                                                                        '304'] else '-'

    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(connection.queries)

    return columns, recordsTotal, result_list

@login_required
def get_content_detail(content_type_id, object_repr_dict, change_message_dict):
    if not content_type_id:
        return ''
    elif content_type_id == '3':
        # auth_user
        pass
    elif content_type_id == '308':
        change_message_dict
    elif content_type_id == '297':
        return object_repr_dict['filename']
    # elif content_type_id in ['293', '309']:
    #     beta_testers = object_repr_dict['identifiers']
    #     return beta_testers.replace('[', '').replace("u'", "").replace('\'', '')
    elif content_type_id in ['295', '306']:
        # role
        if 'rolename' in object_repr_dict:
            rolename_en = object_repr_dict['rolename']
        elif 'new_role' in object_repr_dict:
            rolename_en = object_repr_dict['new_role']

        if rolename_en == 'staff':
            rolename = '운영팀'
        elif rolename_en == 'instructor':
            rolename = '교수자'
        elif rolename_en == 'beta':
            rolename = '베타 테스터'
        elif rolename_en == 'Administrator':
            rolename = '게시판 관리자'
        elif rolename_en == 'Moderator':
            rolename = '토의 게시자'
        elif rolename_en == 'Community TA':
            rolename = '게시판 커뮤니티 조교'
        else:
            # print 'rolename_en:', rolename_en
            rolename = ''
        return rolename
    else:
        pass

    return ''

@login_required
def get_system_name(content_type_id):
    """
    시스템 표시 구분.
    content_type_id: 3 = django admin
    content_type_id: 311 = insight
    etc : kmooc

    :param content_type_id:
    :return:
    """
    if content_type_id in ['3', '291', '292']:
        system = 'admin'
    elif content_type_id in ['311', ]:
        system = 'insight'
    else:
        system = 'k-mooc'
    return system

@login_required
def get_change_message_dict(change_message):
    """
    request의 파라미터를 dict 형태로 변환후 문자열로 재변환하여 change_message 값으로 저장하고 있음.
    저장된 값을 사용하기 위해 다시 dict 형태로 변환처리

    request 의 값중 query 의 내용중에 역슬러쉬가 포함되는 경우가 있어서 문자열 > dict 변환중 오류가 발생하므로 query 내용 제거 작업 추가.

    :param change_message:
    :return:
    """
    try:
        change_message_dict = ast.literal_eval(change_message)
    except:
        try:
            temp_string = change_message[:change_message.find('query') - 1] + change_message[
                                                                              change_message.find('>') + 2:]
            change_message_dict = ast.literal_eval(temp_string)
        except Exception as e:
            change_message_dict = dict()
            print 'Exception:', e, change_message
    finally:
        return change_message_dict

@login_required
def get_object_repr_dict(object_repr):
    """
    object_repr 의 내용은 재정의된 문자열로 저장이되고 있으며,
    json 형식이 아니므로 split 을 이요하여 분리하여 dict 로 변환하여 사용함.

    :param object_repr:
    :return:
    """
    object_repr_temp = object_repr[object_repr.find('[') + 1:].replace(']', '')
    list1 = object_repr_temp.split(';')
    result = dict()
    for l1 in list1:
        list2 = l1.split(':')
        # print 'len(list2) = ', len(list2)
        if len(list2) == 1:
            result['student'] = list2[0]
        else:
            result[list2[0]] = list2[1]
    return result

@login_required
def get_searcy_string(content_type_id, change_message_dict):
    """
    django admin 에서 사용자 검색을 한경우 검색어를 추출.

    :param content_type_id:
    :param change_message_dict:
    :return:
    """
    if content_type_id == '292' and 'query' in change_message_dict:
        search_query = urllib.unquote(change_message_dict['query']).decode('utf8')
        search_query = search_query.split('=')[1] if search_query else ''
    else:
        search_query = ''
    return search_query

@login_required
def get_target_id(content_type_id, object_repr_dict):
    """
    개인정보 수정, 사용자를 지정하여 처리하는 액션의 경우 대상 아이디를 조회하여 리턴.

    :param content_type_id:
    :param object_repr_dict:
    :return:
    """
    # print 'object_repr_dict ==> ', object_repr_dict
    target_id = ''
    if content_type_id == '3':
        target_id = object_repr_dict['student']
    elif content_type_id in ['295', '306']:
        return object_repr_dict['user'] if 'user' in object_repr_dict else ''
    elif content_type_id in ['291', '308']:
        all_students = object_repr_dict['all_students'] if 'all_students' in object_repr_dict else 'False'
        if all_students == 'True':
            return 'All'
        else:
            return object_repr_dict['student'] if 'student' in object_repr_dict else ''

    return target_id


action_flag_dict = {
    '0': u'조회',
    '1': u'생성',
    '2': u'수정',
    '3': u'삭제',
}
content_type_dict = {
    '0': u'조회',
    '1': u'회원권한 수정',
    '2': u'회원그룹 수정',
    '3': u'회원정보 수정',
    '291': u'회원 정보 상세',
    '292': u'회원 정보 리스트',
    '293': u'등록관리 - 베타 테스터',
    '294': u'성적 보고서',
    '295': u'강좌 운영팀 관리 (게시판 관리자, 토의 진행자, 게시판 조교)',
    '296': u'ORA 데이터 보고 생성하기',
    '297': u'파일 다운로드',
    '298': u'익명 학습자 아이디 CSV 파일',
    '299': u'발급된 이수증 조회',
    '300': u'발급된 이수증 CSV 파일',
    '301': u'문제 답변 CSV 파일 다운로드',
    '302': u'학습자 진도 페이지',
    '303': u'등록된 학습자의 프로필 목록',
    '304': u'개인정보를 CSV 파일로 다운로드',
    '305': u'등록할 수 있는 학습자의 CSV 다운로드',
    '306': u'강좌 운영팀 관리 (운영팀, 교수자, 베타 테스터)',
    '307': u'문항 성적 보고서 생성',
    '308': u'문제 풀이 횟수 설정 초기화',
    '309': u'등록관리 - 일괄 등록',
    '311': u'강좌 데이터 조회',
}

auth_dict = {
    'username': u'아이디',
    'first_name': u'성',
    'last_name': u'이름',
    'email': u'이메일 주소',
    'password': u'비밀번호',
    'is_staff': u'스태프 권한',
    'is_active': u'활성',
    'is_superuser': u'최상위 사용자 권한',
    'last_login': u'마지막 로그인',
    'date_joined': u'등록일',
    'dormant_mail_cd': u'탈퇴 메일',
    'dormant_yn': u'탈퇴 여부',
    'dormant_dt': u'탈퇴일',
    'name': u'프로필 이름',
    'language': u'언어',
    'location': u'지역',
    'meta': u'메타정보',
    'courseware': u'courseware',
    'gender': u'성별',
    'mailing_address': u'mailing_address',
    'year_of_birth': u'출생 연도',
    'level_of_education': u'최종 학력',
    'goals': u'목표',
    'allow_certificate': u'이수증 생성 허용',
    'country': u'국가',
    'city': u'도시',
    'bio': u'자기소개',
    'profile_image_uploaded_at': u'프로필 이미지 업로드 일시',
}

# community view
def comm_mobile(request):
    if request.is_ajax():
        if request.GET['method'] == 'mobile_list':
            cur = connection.cursor()
            query = """
              SELECT board_id,
                     (@rn := @rn + 1)                   rn,
                     subject,
                     content,
                     SUBSTRING(reg_date, 1, 11),
                     if(use_yn = 'Y', '보임', '숨김') use_yn,
                     if(odby = '0', '', odby)           odby,
                     use_yn
                FROM tb_board a, (SELECT @rn := 0) b
               WHERE section = 'M' AND NOT use_yn = 'D'
            ORDER BY reg_date;
			"""

            cur.execute(query)
            rows = cur.fetchall()
            cur.close()

            print [list(row) for row in rows]

            aaData = json.dumps([list(row) for row in rows], cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'mobile_del':
            noti_id = request.GET['noti_id']
            use_yn = request.GET['use_yn']
            yn = ''
            if use_yn == 'Y':
                yn = 'N'
            else:
                yn = 'Y'
            # print 'use_yn == ',use_yn,' yn == ',yn
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + noti_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        elif request.GET['method'] == 'mobile_delete':
            noti_id = request.GET['noti_id']
            use_yn = request.GET['use_yn']
            yn = 'D'

            # print 'use_yn == ',use_yn,' yn == ',yn
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + noti_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        return HttpResponse(aaData, 'applications/json')

    return render(request, 'community/comm_mobile.html')


@csrf_exempt
def new_mobile(request):
    if 'file' in request.FILES:
        value_list = []
        file = request.FILES['file']
        filename = ''
        file_ext = ''
        file_size = ''
        print 'file:', file
        filename = file._name
        file_ext = get_file_ext(filename)

        fp = open('%s/%s' % (UPLOAD_DIR, filename), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        data = '성공'

        n = os.path.getsize(UPLOAD_DIR + filename)
        file_size = str(n / 1024) + "KB"  # 킬로바이트 단위로

        value_list.append(filename)
        value_list.append(file_ext)
        value_list.append(file_size)
        data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    elif request.method == 'POST':
        data = json.dumps({'status': "fail", 'msg': "오류가 발생했습니다"})
        if request.POST['method'] == 'add':

            title = request.POST.get('nt_title')
            title = title.replace("'", "''")
            content = request.POST.get('nt_cont')
            content = content.replace("'", "''")
            section = request.POST.get('mobile')
            head_title = request.POST.get('head_title')

            if not head_title:
                head_title = ''

            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')
            print file_name, '/', file_ext, '/', file_size

            cur = connection.cursor()
            query = "insert into edxapp.tb_board(subject, content, head_title, section)"
            query += " VALUES ('" + title + "', '" + content + "', '" + head_title + "', '" + section + "') "
            cur.execute(query)

            query2 = "select board_id from tb_board where subject ='" + title + "' and content='" + content + "'"
            cur.execute(query2)
            board_id = cur.fetchall()
            cur.close()
            # print board_id[0][0]
            if upload_file != '':
                cur = connection.cursor()
                query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
                        "VALUES ('" + str(board_id[0][0]) + "','" + str(file_name) + "','" + str(
                    file_ext) + "','" + str(file_size) + "')"
                cur.execute(query)
                cur.close()

            data = json.dumps({'status': "success"})

        elif request.POST['method'] == 'modi':
            title = request.POST.get('nt_title')
            title = title.replace("'", "''")
            content = request.POST.get('nt_cont')
            content = content.replace("'", "''")
            noti_id = request.POST.get('noti_id')
            odby = request.POST.get('odby')
            head_title = request.POST.get('head_title')
            if not head_title:
                head_title = ''

            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')

            cur = connection.cursor()
            # query = "update edxapp.tb_board set subject = '"+title+"', content = '"+content+"', odby = '"+odby+"' where board_id = '"+noti_id+"'"
            query = "update edxapp.tb_board set subject = '" + title + "', content = '" + content + "', head_title = '" + head_title + "', mod_date = now() where board_id = '" + noti_id + "'"
            cur.execute(query)
            cur.close()

            if upload_file != '':
                cur = connection.cursor()
                query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
                        "VALUES ('" + str(noti_id) + "','" + str(file_name) + "','" + str(file_ext) + "','" + str(
                    file_size) + "')"
                cur.execute(query)
                cur.close()
            data = json.dumps({'status': "success"})

        return HttpResponse(data, 'applications/json')

    return render(request, 'community/comm_newmobile.html')



@csrf_exempt
def modi_mobile(request, id, use_yn):
    mod_mobile = []

    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            # query = "SELECT subject, content, odby, head_title from tb_board WHERE section = 'N' and board_id = "+id
            query = """
                SELECT subject, content, odby
                  FROM tb_board
                 WHERE section = 'M' AND board_id = %s
            """
            cur.execute(query, [id])
            row = cur.fetchall()
            cur.close()

            cur = connection.cursor()

            query = """
                SELECT attatch_id, attatch_file_name
                  FROM tb_board_attach
                 WHERE del_yn = 'N' AND board_id = %s
            """
            cur.execute(query, [id])
            # print 'connection.queries check s'
            # print connection.queries
            # print 'connection.queries check e'

            files = cur.fetchall()
            cur.close()

            mod_mobile.append(row[0][0])
            mod_mobile.append(row[0][1])
            mod_mobile.append(row[0][2])

            if files:
                # mod_mobile.append([list(file) for file in files])
                mod_mobile.append(files)

            print 'mod_mobile == ', mod_mobile

            data = json.dumps(list(mod_mobile), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'file_download':
            pass

            print 'file_download with ajax is not working'

        return HttpResponse(data, 'applications/json')

    variables = RequestContext(request, {
        'id': id,
        'use_yn': use_yn
    })

    return render_to_response('community/comm_modimobile.html', variables)


# execute mysql query : alter table tb_board_attach modify del_yn varchar(1) default 'N';
def file_delete(request):
    # `attatch` 이딴 단어는 어디서 나온겁니까???

    attach_id = request.POST.get('attach_id')

    with connections['default'].cursor() as cur:
        query = """
            UPDATE tb_board_attach
               SET del_yn = 'Y'
             WHERE del_yn = 'N' and attatch_id = %s;
        """
        result = cur.execute(query, [attach_id])

        context = dict()

        context['result'] = result

        print context

    return HttpResponse(json.dumps(context), 'applications/json')


def file_download(request, file_name):
    print 'called  file_download_test'

    # 실제 있는 파일로 지정
    file_path = '%s/%s' % (UPLOAD_DIR, file_name)
    # file_path = '/Users/redukyo/workspace/management/home/static/upload/test.jpg'

    print 'file_path:', file_path

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    raise Http404
