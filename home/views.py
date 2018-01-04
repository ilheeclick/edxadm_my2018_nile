# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, redirect
from django.template import Context, RequestContext
from django.http import Http404, HttpResponse, FileResponse, JsonResponse
from django.db import connection
from management.settings import UPLOAD_DIR, STATIC_URL
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.db import connections
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from management.settings import UPLOAD_DIR, EXCEL_PATH
from management.settings import dic_univ, database_id, debug
from management.settings import REAL_WEB1_HOST, REAL_WEB1_ID, REAL_WEB1_PW
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
from django.views.generic import View
from .forms import UserForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from tracking_control.views import oldLog_remove
import uuid

reload(sys)
sys.setdefaultencoding('utf-8')


def get_file_ext(filename):
    filename_split = filename.split('.')
    file_ext_index = len(filename_split)
    file_ext = filename_split[file_ext_index - 1]
    return file_ext

def common_read_csv(file_name):
    user_list = []
    f = open(UPLOAD_DIR + file_name, 'r')
    reader = csv.reader(f, dialect=csv.excel_tab)
    for row in reader:
        for r in row:
            print r.decode('euckr').encode('utf-8')
            user_list.append( r.decode('euckr').encode('utf-8') )
    f.close()
    return user_list

def common_single_file_upload(file_object, gubun, user_id, return_data=None):
    file_name = str(file_object).strip()
    file_name_enc = str(uuid.uuid4()).replace('-', '')
    file_ext = get_file_ext(file_name).strip()
    file_byte_size = file_object.size
    file_size = str(file_byte_size / 1024) + "KB"
    file_dir = UPLOAD_DIR + file_name_enc + '.' + file_ext

    file_path = UPLOAD_DIR
    if file_path[len(file_path) - 1] == '/':
        file_path = file_path[0:(len(file_path) - 1)]
    fp = open(file_dir, 'wb')
    for chunk in file_object.chunks():
        fp.write(chunk)
    fp.close()

    # DEBUG
    print "@@@@@@@@@@@@@@@@@@@@@"
    print file_name
    print file_name_enc
    print file_ext
    print file_size
    print file_dir
    print UPLOAD_DIR
    print file_path
    print "@@@@@@@@@@@@@@@@@@@@@"

    with connections['default'].cursor() as cur:
        query = '''
        INSERT INTO edxapp.tb_board_attach
                    (attatch_file_name,
                     attatch_file_ext,
                     attatch_file_size,
                     attach_file_path,
                     attach_org_name,
                     attach_gubun,
                     regist_id)
        VALUES      ('{0}',
                     '{1}',
                     '{2}',
                     '{3}',
                     '{4}',
                     '{5}',
                      {6})
        '''.format(file_name_enc, file_ext, file_size, file_path, file_name, gubun, user_id)
        cur.execute(query)

    if return_data == 'Y':
        with connections['default'].cursor() as cur:
            query = '''
                SELECT max(attatch_id)
                  FROM tb_board_attach
                 WHERE attach_gubun = '{0}'
            '''.format(gubun)
            cur.execute(query)
            rows = cur.fetchall()
            last_index = str(rows[0][0])

        context = {}
        context['filename'] = file_name_enc + '.' + file_ext
        context['lastindex'] = last_index

        return context


# ---------- common module ---------- #
@login_required
def modi_series(request, id):
    mod_multi = []
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi_list':

            cur = connection.cursor()
            query = """
					SELECT series_id, series_name, note, use_yn
                      FROM series
                     WHERE series_seq = '{0}';
			""".format(id)
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
    return render_to_response('series_course/modi_series_course.html', variables)


@login_required
def series_course_list(request):
    result = dict()

    with connections['default'].cursor() as cur:
        series_id = request.GET.get('series_id')

        query = '''
                    SELECT replace(@rn := @rn - 1, .0, '') rn,
                           org,
                           display_number_with_default,
                           course_name
                      FROM series_course,
                           (SELECT @rn := count(*) + 1
                              FROM series_course
                             WHERE series_seq = '{0}' AND delete_yn = 'N') rn
                     WHERE series_seq = '{1}' AND delete_yn = 'N';
                '''.format(series_id, series_id)

        cur.execute(query)
        columns = [i[0] for i in cur.description]
        rows = cur.fetchall()
        result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]

    result['data'] = result_list
    context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(context, 'applications/json')


@login_required
def series_course_list_db(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        if request.POST.get('method') == 'add':
            user_id = request.POST.get('user_id')
            series_id = request.POST.get('series_id')
            course_list = request.POST.get('course_list')
            course_list = course_list.split('$')
            course_list.pop()

            for item in course_list:
                cur = connection.cursor()
                query = '''
                    SELECT org, display_number_with_default, display_name
                      FROM course_overviews_courseoverview
                     WHERE id = '{0}'
                        '''.format(item)
                cur.execute(query)
                series_index = cur.fetchall()
                cur.close()

                cur = connection.cursor()
                query = '''
                    SELECT count(*)
                      FROM series_course
                     WHERE     series_seq = '{0}'
                           AND org = '{1}'
                           AND display_number_with_default = '{2}'
                        '''.format(series_id, series_index[0][0], series_index[0][1])
                cur.execute(query)
                add_check = cur.fetchall()
                cur.close()

                if (add_check[0][0] == 0):
                    cur = connection.cursor()
                    query = '''
                      INSERT INTO series_course(series_seq,
                                  org,
                                  display_number_with_default,
                                  course_name,
                                  regist_id,
                                  modify_id)
                         VALUES ('{0}',
                                 '{1}',
                                 '{2}',
                                 '{3}',
                                 '{4}',
                                 '{5}');
                            '''.format(series_id, series_index[0][0], series_index[0][1], series_index[0][2], user_id,
                                       user_id)

                    cur.execute(query)
                    cur.close()

                else:
                    cur = connection.cursor()
                    query = '''
                        SELECT count(*)
                          FROM series_course
                         WHERE     series_seq = '{0}'
                               AND org = '{1}'
                               AND display_number_with_default = '{2}'
                               AND delete_yn = 'Y';
                            '''.format(series_id, series_index[0][0], series_index[0][1])
                    cur.execute(query)
                    update_check = cur.fetchall()
                    cur.close()

                    if (update_check[0][0] == 1):
                        cur = connection.cursor()
                        query = '''
                                UPDATE edxapp.series_course
                                   SET delete_yn = 'N', modify_id = '{0}', modify_date = now()
                                 WHERE     series_seq = '{1}'
                                       AND org = '{2}'
                                       AND display_number_with_default = '{3}'
                                       AND delete_yn ='Y';
                                '''.format(user_id, series_id, series_index[0][0], series_index[0][1])
                        cur.execute(query)
                        cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')


        elif request.POST.get('method') == 'delete':
            user_id = request.POST.get('user_id')
            series_id = request.POST.get('series_id')

            org_code = request.POST.get('org_code')
            org_code = org_code.split('$')
            org_code.pop()

            course_code = request.POST.get('course_code')
            course_code = course_code.split('$')
            course_code.pop()

            for i in xrange(0, len(course_code)):
                cur = connection.cursor()
                query = '''
                        UPDATE edxapp.series_course
                           SET delete_yn = 'Y', modify_id = '{0}', modify_date = now()
                         WHERE     series_seq = '{1}'
                               AND org = '{2}'
                               AND display_number_with_default = '{3}';
                        '''.format(user_id, series_id, org_code[i], course_code[i])
                cur.execute(query)
                cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')


        elif request.POST.get('method') == 'update':
            user_id = request.POST.get('user_id')
            series_id = request.POST.get('series_id')
            org_code = request.POST.get('org_code')
            org_code = org_code.split('$')
            org_code.pop()
            course_code = request.POST.get('course_code')
            course_code = course_code.split('$')
            course_code.pop()
            course_name = request.POST.get('course_name')
            course_name = course_name.split('$')
            course_name.pop()

            for i in xrange(0, len(course_code)):
                cur = connection.cursor()
                query = '''
                        UPDATE edxapp.series_course
                           SET course_name = '{0}', modify_id = '{1}', modify_date = now()
                         WHERE     series_seq = '{2}'
                               AND org = '{3}'
                               AND display_number_with_default = '{4}';
                        '''.format(course_name[i], user_id, series_id, org_code[i], course_code[i])
                cur.execute(query)
                cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

    return render(request, 'series_course/series_course_list.html')


@login_required
def series_course_list_view(request, id):
    variables = RequestContext(request, {
        'id': id
    })
    return render_to_response('series_course/series_course_list.html', variables)

@login_required
def series_complete_list_view(request, id):
    variables = RequestContext(request, {
        'id': id
    })
    return render_to_response('series_course/series_complete_list.html', variables)


@login_required
def all_course(request):
    result = dict()

    with connections['default'].cursor() as cur:
        org = request.GET.get('org')
        series_id = request.GET.get('series_id')
        if (org == 'None'):
            org = '%%'

        query = '''
            SELECT org, display_number_with_default
              FROM series_course
             WHERE series_seq = '{0}' AND delete_yn = 'N';
            '''.format(series_id)
        cur.execute(query)
        select = cur.fetchall()
        Test = ""

        if (str(select) == "()"):
            Test = "('','')"
        else:
            for i in xrange(0, len(select)):
                if (i < len(select) - 1):
                    Test += "('" + select[i][0] + "','" + select[i][1] + "'), "
                elif (i == len(select) - 1):
                    Test += "('" + select[i][0] + "','" + select[i][1] + "')"

        query = '''
            SELECT replace(@rn := @rn - 1, .0, '') rn,
                   id,
                   IFNULL(cd.detail_name, coc.org) detail_name,
                   display_name,
                   display_number_with_default     course
              FROM course_overviews_courseoverview coc
                   LEFT OUTER JOIN code_detail cd ON coc.org = cd.detail_code,
                   (SELECT @rn := count(*) + 1
                      FROM course_overviews_courseoverview
                     WHERE     (org, display_number_with_default) NOT IN ({0})
                           AND org LIKE '{1}') b
             WHERE (org, display_number_with_default) NOT IN ({2}) AND org LIKE '{3}';
              '''.format(Test, org, Test, org)
        cur.execute(query)
        columns = [i[0] for i in cur.description]
        rows = cur.fetchall()
        result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]

    result['data'] = result_list

    context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(context, 'applications/json')


@login_required
def series_list(request):
    result = dict()

    with connections['default'].cursor() as cur:
        query = '''
              SELECT replace(@rn := @rn - 1, .0, '') rn,
                     series.series_seq,
                     series.series_id,
                     series.series_name,
                     count(series_course.series_seq) cnt
                FROM series
                     LEFT JOIN series_course
                        ON     series.series_seq = series_course.series_seq
                           AND series_course.delete_yn = 'N',
                     (SELECT @rn := count(*) + 1
                        FROM series
                       WHERE series.delete_yn = 'N') a
               WHERE series.delete_yn = 'N'
            GROUP BY series_name, series_course.series_seq
            ORDER BY series.regist_date DESC;
        '''
        cur.execute(query)
        columns = [i[0] for i in cur.description]
        rows = cur.fetchall()

        video_list = list()
        learning_list = list()
        columns += ['video_time']
        columns += ['learning_time']

        new_rows = []

        for i in xrange(0, len(rows)):
            query = '''
                SELECT effort
                  FROM (SELECT org,
                               display_number_with_default,
                               id,
                               effort,
                               (SELECT Count(*)
                                  FROM edxapp.course_overviews_courseoverview b
                                 WHERE     a.org = b.org
                                       AND a.display_number_with_default =
                                              b.display_number_with_default
                                       AND a.start >= b.start
                                       AND a.created >= b.created)
                                  AS rank
                          FROM edxapp.course_overviews_courseoverview a) ab
                 WHERE     rank = 1
                       AND (org, display_number_with_default) IN
                              (SELECT org, display_number_with_default
                                 FROM series_course
                                WHERE series_seq = {0} AND delete_yn = 'N');
            '''.format(rows[i][1])
            print query
            cur.execute(query)
            effort = cur.fetchall()

            video_time = 0
            learning_time = 0
            for e in effort:
                if e[0] != None:
                    series_time = e[0].replace('@', '+').replace('#', '+')
                    series_time_index = series_time.split('+')
                    time_flag = series_time.replace(':','+')
                    time_flag_index = time_flag.split('+')

                if (len(series_time_index) == 3 and '' not in time_flag_index):
                    all_learning_hour = series_time_index[0].split(':')
                    learning_hour = int(all_learning_hour[0]) * 60 * int(series_time_index[1])
                    learning_minut = int(all_learning_hour[1]) * int(series_time_index[1])
                    learning_time += (learning_hour + learning_minut)

                    all_video_hour = series_time_index[2].split(':')
                    video_hour = int(all_video_hour[0]) * 60 * int(series_time_index[1])
                    video_minut = int(all_video_hour[1]) * int(series_time_index[1])
                    video_time += (video_hour + video_minut)
                else:
                    learning_time += 0
                    video_time += 0

            if (len(str(video_time % 60)) == 1 and len(str(learning_time % 60)) != 1):
                video_list.append(str(video_time // 60) + ':0' + str(video_time % 60))
                learning_list.append(str(learning_time // 60) + ':' + str(learning_time % 60))

            elif (len(str(video_time % 60)) != 1 and len(str(learning_time % 60)) == 1):
                video_list.append(str(video_time // 60) + ':' + str(video_time % 60))
                learning_list.append(str(learning_time // 60) + ':0' + str(learning_time % 60))

            elif (len(str(video_time % 60)) == 1 and len(str(learning_time % 60)) == 1):
                video_list.append(str(video_time // 60) + ':0' + str(video_time % 60))
                learning_list.append(str(learning_time // 60) + ':0' + str(learning_time % 60))

            else:
                video_list.append(str(video_time // 60) + ':' + str(video_time % 60))
                learning_list.append(str(learning_time // 60) + ':' + str(learning_time % 60))

            new_rows.append(rows[i] + (video_list[i],) + (learning_list[i],))

        result_list = [dict(zip(columns, (str(col) for col in row))) for row in new_rows]

    result['data'] = result_list

    context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(context, 'applications/json')


@csrf_exempt
@login_required
def modi_series_course(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})

        try:
            upload_file = request.FILES['uploadfile']
            uploadfile_user_id = request.POST.get('uploadfile_user_id')
        except BaseException:
            upload_file = None
            uploadfile_user_id = None

        if upload_file:
            uploadfile = request.FILES['uploadfile']
            common_single_file_upload(uploadfile, 'series', str(uploadfile_user_id))

            return render(request, 'series_course/modi_series_course.html')

        if request.POST.get('method') == 'add':
            series_id = request.POST.get('series_id')
            series_name = request.POST.get('series_name')
            note = request.POST.get('note')
            user_id = request.POST.get('user_id')
            use_yn = request.POST.get('use_yn')

            cur = connection.cursor()
            query = '''select max(attatch_id)+1 from tb_board_attach
                    '''
            cur.execute(query)
            attatch_id = cur.fetchall()
            cur.close()

            cur = connection.cursor()
            query = '''
                    INSERT INTO edxapp.series(series_id,
                                              series_name,
                                              note,
                                              regist_id,
                                              modify_id,
                                              use_yn,
                                              sumnail_file_id)
                         VALUES ('{0}',
                                 '{1}',
                                 '{2}',
                                 '{3}',
                                 '{4}',
                                 '{5}',
                                 '{6}');
                    '''.format(series_id, series_name, note, user_id, user_id, use_yn, attatch_id[0][0])
            cur.execute(query)
            cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'modi':
            series_id = request.POST.get('series_id')
            series_name = request.POST.get('series_name')
            note = request.POST.get('note')
            user_id = request.POST.get('user_id')
            use_yn = request.POST.get('use_yn')
            series_seq = request.POST.get('series_seq')
            file_flag = request.POST.get('file_flag')
            update_flag = request.POST.get('update_flag')
            sumnail_file_id = None

            if (update_flag == '1' and file_flag != '1'):
                cur = connection.cursor()
                query = '''
                            SELECT sumnail_file_id
                              FROM series
                             WHERE series_seq = '{0}';
                            '''.format(series_seq)
                cur.execute(query)
                attatch_id = cur.fetchall()
                sumnail_file_id = attatch_id[0][0]
                cur.close()
            elif (file_flag == '1'):
                cur = connection.cursor()
                query = '''select max(attatch_id)+1 from tb_board_attach
                        '''
                cur.execute(query)
                attatch_id = cur.fetchall()
                sumnail_file_id = attatch_id[0][0]
                cur.close()

            cur = connection.cursor()
            query = '''
                    UPDATE series
                       SET series_id = '{0}',
                           series_name = '{1}',
                           note = '{2}',
                           modify_id = '{3}',
                           use_yn = '{4}',
                           sumnail_file_id = '{5}',
                           modify_date = now()
                     WHERE series_seq = '{6}';
                    '''.format(series_id, series_name, note, user_id, use_yn, sumnail_file_id, series_seq)
            cur.execute(query)
            cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'delete':
            series_seq = request.POST.get('series_seq')

            cur = connection.cursor()
            query = '''
                    UPDATE series
                       SET delete_yn = 'Y'
                     WHERE series_seq = '{0}';
                    '''.format(series_seq)
            cur.execute(query)
            cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'check':
            series_seq = request.POST.get('series_seq')

            cur = connection.cursor()
            query = '''
                    SELECT count(sumnail_file_id)
                      FROM series
                     WHERE series_seq = '{0}';
                    '''.format(series_seq)
            cur.execute(query)
            check_file = cur.fetchall()
            cur.close()

            data = check_file[0][0]

            return HttpResponse(data, 'applications/json')

    return render(request, 'series_course/modi_series_course.html')


@login_required
def series_course(request):
    return render(request, 'series_course/series_course.html')


@login_required
def detail_code_db(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        if request.POST.get('method') == 'add_row_save':
            group_code = request.POST.get('group_code')
            detail_code = request.POST.get('detail_code')
            detail_name = request.POST.get('detail_name')
            detail_Ename = request.POST.get('detail_Ename')
            detail_desc = request.POST.get('detail_desc')
            order_no = request.POST.get('order_no')
            use_yn = request.POST.get('use_yn')
            user_id = request.POST.get('user_id')

            cur = connection.cursor()
            query = '''insert into edxapp.code_detail(group_code, detail_code, detail_name, detail_Ename, detail_desc, order_no, use_yn, regist_id)
                       VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')
                    '''.format(group_code, detail_code, detail_name, detail_Ename, detail_desc, order_no, use_yn,
                               user_id)
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'del':
            group_code = request.POST.get('group_code')
            detail_code_list = request.POST.get('detail_code_list')
            user_id = request.POST.get('user_id')

            detail_code_split = detail_code_list.split("+")
            detail_code_split.pop()

            for detail_code in detail_code_split:
                cur = connection.cursor()
                query = '''
                        UPDATE code_detail
                           SET delete_yn = 'Y', modify_id = '{0}', modify_date = now()
                         WHERE group_code = '{1}' AND detail_code = '{2}';
                        '''.format(user_id, group_code, detail_code)
                cur.execute(query)
                cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'update':
            detail_code = request.POST.get('detail_code')
            detail_name = request.POST.get('detail_name')
            detail_Ename = request.POST.get('detail_Ename')
            detail_desc = request.POST.get('detail_desc')
            order_no = request.POST.get('order_no')
            use_yn = request.POST.get('use_yn')
            group_code_prev = request.POST.get('group_code_prev')
            detail_code_prev = request.POST.get('detail_code_prev')
            user_id = request.POST.get('user_id')

            cur = connection.cursor()
            query = '''
                    UPDATE code_detail
                       SET detail_code = '{0}',
                           detail_name = '{1}',
                           detail_Ename = '{2}',
                           detail_desc = '{3}',
                           order_no = '{4}',
                           use_yn = '{5}',
                           modify_id = '{6}',
                           modify_date = now()
                     WHERE group_code = '{7}' AND detail_code = '{8}';
                    '''.format(detail_code, detail_name, detail_Ename, detail_desc, order_no, use_yn, user_id,
                               group_code_prev, detail_code_prev)
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')


@login_required
def group_code_db(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        if request.POST.get('method') == 'add_row_save':
            group_code = request.POST.get('group_code')
            group_name = request.POST.get('group_name')
            group_desc = request.POST.get('group_desc')
            use_yn = request.POST.get('use_yn')
            user_id = request.POST.get('user_id')

            cur = connection.cursor()
            query = '''insert into edxapp.code_group(group_code, group_name, group_desc, use_yn, regist_id)
                       VALUES ('{0}','{1}','{2}','{3}','{4}')
                    '''.format(group_code, group_name, group_desc, use_yn, user_id)
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'del':
            group_code_list = request.POST.get('group_code_list')
            user_id = request.POST.get('user_id')
            group_code_split = group_code_list.split("+")
            group_code_split.pop()

            for group_code in group_code_split:
                cur = connection.cursor()
                query = '''
                        UPDATE code_group
                           SET delete_yn = 'Y', modify_id ='{0}', modify_date = now()
                         WHERE group_code = '{1}';
                        '''.format(user_id, group_code)
                cur.execute(query)
                cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'update':
            group_name = request.POST.get('group_name')
            group_desc = request.POST.get('group_desc')
            use_yn = request.POST.get('use_yn')
            user_id = request.POST.get('user_id')
            group_code_prev = request.POST.get('group_code_prev')

            cur = connection.cursor()
            query = '''
                    UPDATE code_group
                       SET group_name ='{0}', group_desc = '{1}', use_yn = '{2}', modify_id = '{3}', modify_date = now()
                     WHERE group_code = '{4}';
                    '''.format(group_name, group_desc, use_yn, user_id, group_code_prev)
            print query
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')


@csrf_exempt
@login_required
def detail_code(request):
    result = dict()
    group_code = request.GET.get('group_code')

    if (group_code == None):
        group_code = '%'

    with connections['default'].cursor() as cur:
        query = '''
              SELECT group_code,
                     detail_code,
                     detail_name,
                     detail_Ename,
                     detail_desc,
                     order_no,
                     use_yn,
                     regist_date
                FROM code_detail
               WHERE delete_yn = 'N' AND group_code LIKE '{0}'
            ORDER BY regist_date;
        '''.format(group_code)

        cur.execute(query)
        columns = [i[0] for i in cur.description]
        rows = cur.fetchall()
        result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]

    result['data'] = result_list

    context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(context, 'applications/json')


@csrf_exempt
@login_required
def group_code(request):
    result = dict()

    with connections['default'].cursor() as cur:
        query = '''
            SELECT group_code,
                   group_name,
                   group_desc,
                   use_yn,
                   regist_date
              FROM code_group
             WHERE delete_yn = 'N'
             ORDER BY regist_date;
        '''

        cur.execute(query)
        columns = [i[0] for i in cur.description]
        rows = cur.fetchall()
        result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]

    result['data'] = result_list

    context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(context, 'applications/json')


@login_required
def code_manage(request):
    return render(request, 'code_manage/code_manage.html')


@csrf_exempt
@login_required
def course_db(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        if request.POST.get('method') == 'add':
            user_id = request.POST.get('user_id')
            course_id = request.POST.get('course_id')
            course_id = course_id.split('$')
            course_id.pop()
            choice1_list = request.POST.get('choice1_list')
            choice1_list = choice1_list.split('$')
            choice1_list.pop()
            choice2_list = request.POST.get('choice2_list')
            choice2_list = choice2_list.split('$')
            choice2_list.pop()

            for idx in range(len(course_id)):
                cur = connection.cursor()
                query = '''
                            SELECT count(course_id)
                              FROM course_overview_addinfo
                             WHERE course_id = '{0}';
                        '''.format(course_id[idx])
                cur.execute(query)
                cnt = cur.fetchall()
                cur.close()

                if (cnt[0][0] == 0):
                    cur = connection.cursor()
                    query = '''
                               insert into edxapp.course_overview_addinfo(course_id, create_type, create_year, regist_id, modify_id)
                               VALUES ('{0}','{1}','{2}','{3}','{4}')
                            '''.format(course_id[idx], choice1_list[idx], choice2_list[idx], user_id, user_id)
                    cur.execute(query)
                    cur.close()
                elif (cnt[0][0] == 1):
                    cur = connection.cursor()
                    query = '''
                               UPDATE edxapp.course_overview_addinfo
                               SET delete_yn = 'N', create_type ='{0}', create_year='{1}', modify_id='{2}'
                               WHERE course_id = '{3}';
                            '''.format(choice1_list[idx], choice2_list[idx], user_id, course_id[idx])
                    cur.execute(query)
                    cur.close()

            data = json.dumps({'status': "success"})
            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'del':
            user_id = request.POST.get('user_id')
            course_id = request.POST.get('course_id')
            course_id = course_id.split('$')
            course_id.pop()

            for idx in range(len(course_id)):
                cur = connection.cursor()
                query = '''
                            UPDATE edxapp.course_overview_addinfo
                               SET delete_yn = 'Y'
                             WHERE course_id = '{0}';
                        '''.format(course_id[idx])
                cur.execute(query)
                cur.close()

            data = json.dumps({'status': "success"})
            return HttpResponse(data, 'applications/json')


@login_required
def course_db_list(request):
    client = MongoClient(database_id, 27017)
    db = client.edxapp
    result = dict()

    method = request.GET['method']
    start = request.GET['start']
    end = request.GET['end']
    course_name = request.GET['course_name']
    choice = request.GET['choice']
    if (course_name == ''):
        course_name = '%'

    if request.GET['method'] == 'course_list':
        with connections['default'].cursor() as cur:
            course_list = []
            if (choice == ''):
                query = '''
                        SELECT @rn := @rn - 1 rn, a.*
                          FROM (  SELECT CASE
                                        WHEN d.delete_yn = 'N' THEN d.create_type
                                        WHEN d.delete_yn = 'Y' THEN ''
                                     END
                                        create_type,
                                     CASE
                                        WHEN d.delete_yn = 'N' THEN d.create_year
                                        WHEN d.delete_yn = 'Y' THEN ''
                                     END
                                        create_year,
                                         d.course_no,
                                         e.detail_name,
                                         a.display_name,
                                         a.id,
                                         a.created,
                                         a.enrollment_start,
                                         a.enrollment_end,
                                         a.end,
                                         c.cert_date,
                                         d.teacher_name,
                                         a.effort,
                                         CASE
                                            WHEN c.cert_date IS NOT NULL
                                            THEN
                                               '이수증발급'
                                            WHEN start > end AND enrollment_start < enrollment_end
                                            THEN
                                               '미정'
                                            WHEN end < now()
                                            THEN
                                               '종료'
                                            WHEN start < now() AND now() < end
                                            THEN
                                               '운영중'
                                            WHEN now() < start
                                            THEN
                                               '개강예정'
                                            ELSE
                                               '미정'
                                         END
                                            AS condi
                                    FROM course_overviews_courseoverview a
                                         LEFT OUTER JOIN student_courseaccessrole b
                                            ON a.id = b.course_id AND b.role = 'instructor'
                                         LEFT OUTER JOIN course_overview_addinfo d
                                            ON a.id = d.course_id
                                         LEFT OUTER JOIN (  SELECT course_id, min(created_date) cert_date
                                                              FROM certificates_generatedcertificate
                                                          GROUP BY course_id) c
                                            ON a.id = c.course_id
                                         LEFT OUTER JOIN code_detail e ON e.detail_code = a.org
                                   WHERE     start >=
                                                DATE_FORMAT(DATE_ADD(now(), INTERVAL -6 MONTH),
                                                            '%Y-%m-%d')
                                         AND end <=
                                                DATE_FORMAT(DATE_ADD(now(), INTERVAL 6 MONTH),
                                                            '%Y-%m-%d')
                                         AND display_name like '%{0}%'
                                GROUP BY a.id) a,
                               (SELECT @rn := count(*) + 1
                                  FROM course_overviews_courseoverview
                                 WHERE     start >=
                                              DATE_FORMAT(DATE_ADD(now(), INTERVAL -6 MONTH),
                                                          '%Y-%m-%d')
                                       AND end <=
                                              DATE_FORMAT(DATE_ADD(now(), INTERVAL 6 MONTH),
                                                          '%Y-%m-%d')
                                       AND display_name like '%{1}%') b;
                '''.format(course_name, course_name)
            elif (choice == '1'):
                query = '''
                        SELECT @rn := @rn - 1 rn, a.*
                          FROM (  SELECT CASE
                                        WHEN d.delete_yn = 'N' THEN d.create_type
                                        WHEN d.delete_yn = 'Y' THEN ''
                                     END
                                        create_type,
                                     CASE
                                        WHEN d.delete_yn = 'N' THEN d.create_year
                                        WHEN d.delete_yn = 'Y' THEN ''
                                     END
                                        create_year,
                                         d.course_no,
                                         e.detail_name,
                                         a.display_name,
                                         a.id,
                                         a.created,
                                         a.enrollment_start,
                                         a.enrollment_end,
                                         a.end,
                                         c.cert_date,
                                         d.teacher_name,
                                         a.effort,
                                         CASE
                                            WHEN c.cert_date IS NOT NULL
                                            THEN
                                               '이수증발급'
                                            WHEN start > end AND enrollment_start < enrollment_end
                                            THEN
                                               '미정'
                                            WHEN end < now()
                                            THEN
                                               '종료'
                                            WHEN start < now() AND now() < end
                                            THEN
                                               '운영중'
                                            WHEN now() < start
                                            THEN
                                               '개강예정'
                                            ELSE
                                               '미정'
                                         END
                                            AS condi
                                    FROM course_overviews_courseoverview a
                                         LEFT OUTER JOIN student_courseaccessrole b
                                            ON a.id = b.course_id AND b.role = 'instructor'
                                         LEFT OUTER JOIN course_overview_addinfo d
                                            ON a.id = d.course_id
                                         LEFT OUTER JOIN (  SELECT course_id, min(created_date) cert_date
                                                              FROM certificates_generatedcertificate
                                                          GROUP BY course_id) c
                                            ON a.id = c.course_id
                                         LEFT OUTER JOIN code_detail e ON e.detail_code = a.org
                                   WHERE enrollment_start >= '{0}' AND enrollment_end <= '{1}' AND display_name like '%{4}%'
                                GROUP BY a.id) a,
                               (SELECT @rn := count(*) + 1
                                  FROM course_overviews_courseoverview
                                 WHERE enrollment_start >= '{2}' AND enrollment_end <= '{3}' AND display_name like '%{5}%') b;
                        '''.format(start, end, start, end, course_name, course_name)

            elif (choice == '2'):
                query = '''
                        SELECT @rn := @rn - 1 rn, a.*
                          FROM (  SELECT CASE
                                        WHEN d.delete_yn = 'N' THEN d.create_type
                                        WHEN d.delete_yn = 'Y' THEN ''
                                     END
                                        create_type,
                                     CASE
                                        WHEN d.delete_yn = 'N' THEN d.create_year
                                        WHEN d.delete_yn = 'Y' THEN ''
                                     END
                                        create_year,
                                         d.course_no,
                                         e.detail_name,
                                         a.display_name,
                                         a.id,
                                         a.created,
                                         a.enrollment_start,
                                         a.enrollment_end,
                                         a.end,
                                         c.cert_date,
                                         d.teacher_name,
                                         a.effort,
                                         CASE
                                            WHEN c.cert_date IS NOT NULL
                                            THEN
                                               '이수증발급'
                                            WHEN start > end AND enrollment_start < enrollment_end
                                            THEN
                                               '미정'
                                            WHEN end < now()
                                            THEN
                                               '종료'
                                            WHEN start < now() AND now() < end
                                            THEN
                                               '운영중'
                                            WHEN now() < start
                                            THEN
                                               '개강예정'
                                            ELSE
                                               '미정'
                                         END
                                            AS condi
                                    FROM course_overviews_courseoverview a
                                         LEFT OUTER JOIN student_courseaccessrole b
                                            ON a.id = b.course_id AND b.role = 'instructor'
                                         LEFT OUTER JOIN course_overview_addinfo d
                                            ON a.id = d.course_id
                                         LEFT OUTER JOIN (  SELECT course_id, min(created_date) cert_date
                                                              FROM certificates_generatedcertificate
                                                          GROUP BY course_id) c
                                            ON a.id = c.course_id
                                         LEFT OUTER JOIN code_detail e ON e.detail_code = a.org
                                   WHERE start >= '{0}' AND end <= '{1}' AND display_name like '%{4}%'
                                GROUP BY a.id) a,
                               (SELECT @rn := count(*) + 1
                                  FROM course_overviews_courseoverview
                                 WHERE start >= '{2}' AND end <= '{3}' AND display_name like '%{5}%') b;
                        '''.format(start, end, start, end, course_name, course_name)
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            for multi in row:
                value_list = []
                value_list.append(None)
                value_list.append(multi[0])
                value_list.append(multi[6])
                value_list.append(None)
                value_list.append(None)
                value_list.append(multi[1])
                value_list.append(multi[2])
                value_list.append(multi[4])
                multi_num = multi[6].split('+')
                multi_org = multi_num[0].split(':')

                cursor = db.modulestore.active_versions.find_one({'org': multi_org[1], 'course': multi_num[1], 'run': multi_num[2]})
                pb = cursor.get('versions').get('published-branch')
                cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)})
                blocks = cursor.get('blocks')

                for block in blocks:
                    block_type = block.get('block_type')

                    if block_type == 'course':
                        classfy = block.get('fields').get('classfy')
                        middle_classfy = block.get('fields').get('middle_classfy')

                        if not classfy:
                            classfy = ''
                        elif not middle_classfy:
                            middle_classfy = ''

                cur = connection.cursor()
                query = '''
                        SELECT detail_name
                          FROM code_detail
                         WHERE detail_code = '{0}';
                        '''.format(classfy)
                cur.execute(query)
                clsf_h = cur.fetchall()
                cur.close()

                cur = connection.cursor()

                query = '''
                        SELECT detail_name
                          FROM code_detail
                         WHERE detail_code = '{0}';
                        '''.format(middle_classfy)
                cur.execute(query)
                m_clsf_h = cur.fetchall()
                cur.close()
                print 'query======='
                print query
                print 'course_manage==================='
                print clsf_h
                print m_clsf_h
                print len(clsf_h)
                print len(m_clsf_h)
                if (len(clsf_h) == 0):
                    value_list.append("")
                elif (len(m_clsf_h) == 0):
                    value_list.append("")

                else :
                    value_list.append(clsf_h[0][0])
                    value_list.append(m_clsf_h[0][0])
                    value_list.append(multi[5])
                    value_list.append(multi_org[1])
                    value_list.append(multi_num[1])
                    value_list.append(multi_num[2])
                    value_list.append(multi[14])
                    value_list.append(multi[7])
                    value_list.append(multi[8])
                    value_list.append(multi[9])
                    value_list.append(multi[10])
                    value_list.append(multi[11])
                    value_list.append(multi[12])
                    if multi[13] != None:
                        multi_time = multi[13].replace('@', '+').replace('#', '+')
                    multi_time_num = multi_time.split('+')
                    if (len(multi_time_num) == 3):
                        value_list.append(multi_time_num[2])
                        value_list.append(multi_time_num[0])
                        value_list.append(multi_time_num[1])
                        all_hour = multi_time_num[0].split(':')
                        hour = int(all_hour[0]) * 60 * int(multi_time_num[1])
                        minut = int(all_hour[1]) * int(multi_time_num[1])
                        time = hour + minut
                        value_list.append(str(time // 60) + ':' + str(time % 60))
                    else:
                        value_list.append(None)
                        value_list.append(None)
                        value_list.append(None)
                        value_list.append(None)
                    value_list.append(None)

                    course_list.append(value_list)

            data = json.dumps(list(course_list), cls=DjangoJSONEncoder, ensure_ascii=False)
            return HttpResponse(data, 'applications/json')

        result['data'] = result_list

    context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(context, 'applications/json')


@login_required
def user_enroll(request):

    if request.is_ajax():
        # 조건 검색 요청 시
        if request.GET.get('startDt') and request.GET.get('endDt'):
            startDt = request.GET.get('startDt')
            endDt = request.GET.get('endDt')
            with connections['default'].cursor() as cur:
                query = '''
                    SELECT a.seq,
                           a.req_org,
                           a.reg_why,
                           b.username AS regist_id,
                           a.regist_date,
                           concat('성공 : ', a.pass_cnt, ' / 실패 : ', a.fail_cnt) AS result
                      FROM user_bulk_reg AS a JOIN auth_user AS b ON a.regist_id = b.id
                     WHERE regist_date > date('{}') AND regist_date < DATE_ADD(date('{}'), INTERVAL 1 DAY) ;
                '''.format(startDt, endDt)
                cur.execute(query)
                rows = cur.fetchall()
                columns = [col[0] for col in cur.description]
                result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]
            result = dict()
            result['data'] = result_list
            context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
            return HttpResponse(context, 'applications/json')

        # 등록 요청 시
        if request.POST.get('user_org') and request.POST.get('user_why'):
            user_org = request.POST.get('user_org')
            user_why = request.POST.get('user_why')
            regist_id = request.POST.get('user_id')
            user_file = request.FILES['user_file']

            user_list = []
            error_cnt = 0
            success_cnt = 0

            file_context = common_single_file_upload(user_file, 'UE', str(regist_id), 'Y')

            file_name = file_context['filename']
            last_index = file_context['lastindex']

            user_list = common_read_csv(file_name)

            # csv파일의 첫번재 행 제외 한 나머지
            for i in range(1, len(user_list)):
                tmp = str(user_list[i])
                tmp = tmp.replace("['","")
                tmp = tmp.replace("']","")
                tmp = tmp.split(',')

                # tmp의 길이가 9라면 모든 요소가 들어가 있는 것입니다 (누락없음)
                if len(tmp) == 9:
                    user_id = tmp[0]
                    user_pw = tmp[1]
                    user_email = tmp[2]
                    user_name = tmp[3]
                    user_gender = tmp[4]
                    user_year = tmp[5]
                    user_grade = tmp[6]
                    user_gender_code = tmp[7]
                    user_grade_code = tmp[8]

                    print "----------------------------> user s"
                    print "user_id = ", user_id
                    print "user_pw = ", user_pw
                    print "user_email = ", user_email
                    print "user_name = ", user_name
                    print "user_gender = ", user_gender
                    print "user_year = ", user_year
                    print "user_grade = ", user_grade
                    print "user_gender_code = ", user_gender_code
                    print "user_grade_code = ", user_grade_code
                    print "----------------------------> user e"

                    try:
                        # 회원 등록
                        cmd = 'sshpass -p{2} ssh -o StrictHostKeyChecking=no {1}@{0} /edx/app/edxapp/edx-platform/add_user.sh {3} {4}'.format(
                            REAL_WEB1_HOST,
                            REAL_WEB1_ID,
                            REAL_WEB1_PW,
                            user_email,
                            user_pw
                        )
                        result = os.system(cmd)

                        # 등록된 회원 정보 변경(업데이트)
                        with connections['default'].cursor() as cur:
                            query = '''
                                UPDATE auth_user AS a
                                       JOIN auth_userprofile AS b
                                         ON a.id = b.user_id
                                SET    a.username = '{1}',
                                       b.NAME = '{2}',
                                       b.gender = '{3}',
                                       b.year_of_birth = '{4}',
                                       level_of_education = '{5}'
                                WHERE  a.email = '{0}'
                            '''.format(user_email, user_id, user_name, user_gender_code, user_year, user_grade_code)
                            cur.execute(query)
                            print query

                        success_cnt += 1

                        # 등록 세부정보 디비에 삽입
                        with connections['default'].cursor() as cur:
                            query = '''
                                INSERT INTO user_bulk_reg_detail(user_bulk_reg_seq,
                                                                 req_id,
                                                                 email,
                                                                 name,
                                                                 year_of_birth,
                                                                 gender,
                                                                 education,
                                                                 result_cd,
                                                                 regist_id)
                                     VALUES (null,
                                             '{0}',
                                             '{1}',
                                             '{2}',
                                             '{3}',
                                             '{4}',
                                             '{5}',
                                             '00',
                                             '{6}')
                            '''.format(user_id, user_email, user_name, user_year, user_gender_code, user_grade_code, regist_id)
                            print query
                            cur.execute(query)

                    except BaseException:
                        error_cnt += 1

            print "-------------------> result s"
            print "success_cnt = ", success_cnt
            print "error_cnt = ", error_cnt
            print "-------------------> result e"

            # 등록 정보 디비에 삽입
            with connections['default'].cursor() as cur:
                query = '''
                    INSERT INTO user_bulk_reg(req_org,
                                              reg_why,
                                              pass_cnt,
                                              fail_cnt,
                                              attatch_id,
                                              regist_id)
                         VALUES ('{0}',
                                 '{1}',
                                 {2},
                                 {3},
                                 {4},
                                 {5})
                '''.format(user_org, user_why, success_cnt, error_cnt, last_index, regist_id)
                cur.execute(query)
                print query

            # 등록 세부정보 관계 테이블 동기
            with connections['default'].cursor() as cur:
                query = '''
                    UPDATE user_bulk_reg_detail
                       SET user_bulk_reg_seq = '{0}'
                     WHERE user_bulk_reg_seq IS NULL;
                '''.format(last_index)
                print query
                cur.execute(query)

            return JsonResponse({'a':'b'})

    return render(request, 'user_enroll/user_enroll.html')

def download_bulkuser_example(request):
    fsock = open(EXCEL_PATH + 'bulk_user/user_enroll.csv', 'r')
    response = HttpResponse(fsock)
    response['Content-Disposition'] = "attachment; filename=회원일괄등록요청.csv"
    return response

@login_required
def multi_site(request):
    return render(request, 'multi_site/multi_site.html')


@login_required
def course_manage(request):
    return render(request, 'course_manage/course_manage.html')


@login_required
def course_list(request, site_id, org_name):
    variables = RequestContext(request, {
        'site_id': site_id,
        'org_name': org_name
    })
    return render_to_response('multi_site/course_list.html', variables)


@login_required
def multisite_org(request):
    org_list = []

    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'org':
            cur = connection.cursor()

            query = """
                      SELECT detail_code, detail_name
                        FROM code_detail
                       WHERE group_code = '003' AND use_yn = 'Y' AND delete_yn = 'N'
                    ORDER BY detail_name;
                    """
            cur.execute(query)
            org = cur.fetchall()
            cur.close()

            data = json.dumps(list(org), cls=DjangoJSONEncoder, ensure_ascii=False)

    return HttpResponse(data, 'applications/json')


@login_required
def course_list_db(request):
    result = dict()

    with connections['default'].cursor() as cur:
        org = request.GET.get('org')
        site_id = request.GET.get('site_id')
        print org
        if (org == 'None'):
            org = '%'

        query = '''
            SELECT co.id
              FROM course_overviews_courseoverview co
                   JOIN multisite_course mc ON co.id = mc.course_id
                   LEFT OUTER JOIN code_detail cd ON co.org = cd.detail_code
             WHERE mc.site_id = '{0}';
            '''.format(site_id)
        cur.execute(query)
        select = cur.fetchall()
        select_course = ""

        for index in select:
            select_course += (index[0]) + "','"

        query = '''
            SELECT replace(@rn := @rn - 1, .0, '')        rn,
                   id,
                   display_name,
                   IFNULL(cd.detail_name, coc.org)        detail_name,
                   date_format(`start`, '%Y/%m/%d %H:%i') start,
                   date_format(`end`, '%Y/%m/%d %H:%i')   end,
                   org,
                   display_number_with_default            course,
                   substring_index(id, '+', -1)           run
              FROM course_overviews_courseoverview coc
                   LEFT OUTER JOIN code_detail cd ON coc.org = cd.detail_code,
                   (  SELECT @rn := count(*) + 1
                        FROM course_overviews_courseoverview
                       WHERE id NOT IN
                                ('{0}')
                    ORDER BY start DESC) b
             WHERE     org LIKE '{1}'
                   AND id NOT IN
                          ('{2}');
        '''.format(select_course, org, select_course)

        print ('+++++++++++++++++++++++++++++')
        print (query)

        cur.execute(query)
        columns = [i[0] for i in cur.description]
        rows = cur.fetchall()
        result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]

    result['data'] = result_list

    context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(context, 'applications/json')


@csrf_exempt
@login_required
def multisite_course(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        if request.POST.get('method') == 'add':
            site_id = request.POST.get('site_id')
            user_id = request.POST.get('user_id')
            course_list = request.POST.get('course_list')
            course_list = course_list.split('$')
            course_list.pop()

            for item in course_list:
                cur = connection.cursor()
                query = '''insert into edxapp.multisite_course(site_id, course_id, regist_id)
                           VALUES ('{0}','{1}','{2}')
                        '''.format(site_id, item, user_id)
                cur.execute(query)
                cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'input_add':
            site_id = request.POST.get('site_id')
            user_id = request.POST.get('user_id')
            course_list = request.POST.get('course_list')
            course_list = course_list.split()

            for item in course_list:
                cur = connection.cursor()
                query = '''
                        SELECT count(id)
                          FROM course_overviews_courseoverview
                         WHERE id = '{0}';
                        '''.format(item)
                cur.execute(query)
                count = cur.fetchall()
                cur.close()

                if (count[0][0] == 1):
                    cur = connection.cursor()
                    query = '''insert into edxapp.multisite_course(site_id, course_id, regist_id)
                               VALUES ('{0}','{1}','{2}')
                            '''.format(site_id, item, user_id)
                    cur.execute(query)
                    cur.close()
                    data = json.dumps({'status': "success"})
                else:
                    data = json.dumps({'status': "fail"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'delete':
            site_id = request.POST.get('site_id')
            course_list = request.POST.get('course_list')
            course_list = course_list.split('$')
            course_list.pop()

            for item in course_list:
                cur = connection.cursor()
                query = '''
                        delete from edxapp.multisite_course where site_id='{0}' and course_id = '{1}'
                        '''.format(site_id, item)
                cur.execute(query)
                cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

    return render(request, 'multi_site/modi_multi_site.html')


@login_required
def select_list_db(request):
    site_id = request.GET.get('site_id')
    org = request.GET.get('org')
    print org
    if (org == 'None'):
        org = '%'
    print org
    result = dict()

    with connections['default'].cursor() as cur:
        query = '''
            SELECT replace(@rn := @rn - 1, .0, '')        rn,
                   co.id,
                   cd.detail_name,
                   co.display_name,
                   date_format(`start`, '%Y/%m/%d %H:%i') start,
                   date_format(`end`, '%Y/%m/%d %H:%i')   end,
                   org,
                   display_number_with_default            course,
                   substring_index(id, '+', -1)           run
              FROM course_overviews_courseoverview co
                   JOIN multisite_course mc ON co.id = mc.course_id
                   LEFT OUTER JOIN code_detail cd ON co.org = cd.detail_code,
                   (SELECT @rn := count(*) + 1
                      FROM multisite_course
                     WHERE site_id = '{0}') b
             WHERE mc.site_id = '{1}' AND co.org LIKE '{2}';
        '''.format(site_id, site_id, org)
        cur.execute(query)
        columns = [i[0] for i in cur.description]
        rows = cur.fetchall()
        result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]

    result['data'] = result_list

    context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(context, 'applications/json')


@csrf_exempt
@login_required
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
                          FROM multisite where delete_yn = 'N') b
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
                value_list.append('<a href="/manage/course_list/' + str(multi[1]) + '/' + str(
                    multi[2]) + '"><input type="button" value="관  리" class="btn btn-default"></a>')
                multi_site_list.append(value_list)

            data = json.dumps(list(multi_site_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')
    return render(request, 'multi_site/multi_site.html')


@csrf_exempt
@login_required
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
                           site_url
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
@login_required
def modi_multi_site_db(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})


        if request.POST.get('method') == 'add':
            site_name = request.POST.get('site_name')
            site_code = request.POST.get('site_code')
            site_url = request.POST.get('site_url')
            regist_id = request.POST.get('regist_id')
            email_list = request.POST.get('email_list')
            email_list = email_list.split('+')
            email_list.pop()

            cur = connection.cursor()
            query = '''insert into edxapp.multisite(site_name, site_code, site_url, regist_id, modify_id)
                       VALUES ('{0}','{1}','{2}','{3}','{4}')
                    '''.format(site_name, site_code, site_url, regist_id, regist_id)
            cur.execute(query)
            cur.close()

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
                query = "select count(site_id) from multisite"
                cur.execute(query)
                cnt = cur.fetchall()
                cur.close()

                cur = connection.cursor()
                query = '''insert into edxapp.multisite_user(site_id, user_id, regist_id, modify_id, delete_yn)
                           VALUES ('{0}','{1}','{2}','{3}', 'N')
                        '''.format(str(cnt[0][0]), str(row[0][0]), regist_id, regist_id)
                cur.execute(query)
                cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'modi':
            site_name = request.POST.get('site_name')
            site_code = request.POST.get('site_code')
            site_url = request.POST.get('site_url')
            multi_no = request.POST.get('multi_no')
            regist_id = request.POST.get('regist_id')

            cur = connection.cursor()
            query = '''
                    update edxapp.multisite
                    SET site_name = '{0}', site_code = '{1}', site_url = '{2}', modify_id = '{3}', modify_date = now()
                    WHERE site_id = '{4}'
                    '''.format(site_name, site_code, site_url, regist_id, multi_no)
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

        elif request.POST.get('method') == 'check':
            multi_no = request.POST.get('multi_no')

            cur = connection.cursor()
            query = '''
                    SELECT count(logo_img)
                      FROM multisite
                     WHERE site_id = '{0}';
                    '''.format(multi_no)
            cur.execute(query)
            attatch_id = cur.fetchall()
            logo_file = attatch_id[0][0]
            cur.close()

            data = logo_file

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

        print 'Test === list ====='
        print query

        cur.execute(query)
        columns = [i[0] for i in cur.description]
        rows = cur.fetchall()

        print rows
        result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]

    result['data'] = result_list

    context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
    return HttpResponse(context, 'applications/json')


@login_required
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
            if (cnt[0][0] == 1):
                cur = connection.cursor()
                query = '''update edxapp.multisite_user
                              SET delete_yn = 'N'
                            WHERE site_id = '{0}' and user_id = '{1}';
                        '''.format(id, str(row[0][0]))
                cur.execute(query)
                cur.close()
            elif (cnt[0][0] == 0):
                cur = connection.cursor()
                query = '''insert into edxapp.multisite_user(site_id, user_id, regist_id, modify_id, delete_yn)
                           VALUES ('{0}','{1}','{2}','{3}', 'N')
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
                      FROM auth_user AS au
                      JOIN auth_userprofile as up
                        ON au.id = up.user_id
                     WHERE au.email = '{0}'
                    '''.format(input_email)
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            print query
            print 'temporary ----------------------'
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


@login_required
def popupZone_add(request):
    return render(request, 'popup/popupZone_add.html')


@csrf_exempt
@login_required
def popupZone_db(request):
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        popupZone_list = []

        if request.GET['method'] == 'popupZone_list':
            start = request.GET.get('start')
            end = request.GET.get('end')
            title = request.GET.get('title')
            cur = connection.cursor()
            start = start.replace("-", "")
            end = end.replace("-", "")
            if (end == ''):
                end = 99999999

            query = """
                      SELECT @rn := @rn - 1 rn,
                             seq,
                             title,
                             username,
                             CONCAT(SUBSTRING((start_date), 1, 4),
                                    "-",
                                    SUBSTRING((start_date), 5, 2),
                                    "-",
                                    SUBSTRING((start_date), 7, 2))
                                start_date,
                             CONCAT(SUBSTRING((end_date), 1, 4),
                                    "-",
                                    SUBSTRING((end_date), 5, 2),
                                    "-",
                                    SUBSTRING((end_date), 7, 2))
                                end_date,
                             CASE
                                WHEN link_target = '_blank' THEN '새창열기'
                                WHEN link_target = '_self' THEN '현재창열기'
                             END
                                link_target,
                             link_url
                        FROM popupzone pz
                             JOIN auth_user au ON au.id = pz.regist_id,
                             (SELECT @rn := count(*) + 1
                                FROM popupzone
                               WHERE     title LIKE '%{0}%'
                                     AND '{1}' <= BINARY (start_date)
                                     AND BINARY (end_date) <= '{2}') x
                       WHERE     title LIKE '%{3}%'
                             AND '{4}' <= BINARY (start_date)
                             AND BINARY (end_date) <= '{5}'
                    ORDER BY regist_date DESC;
			""".format(title, start, end, title, start, end)
            print query
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
                popupZone_list.append(value_list)

            data = json.dumps(list(popupZone_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')
    return render(request, 'popup/popupZone_add.html')


@login_required
def modi_popupZone(request, id):
    mod_popZone = []
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            query = """
					SELECT title,
                           image_file,
                           link_url,
                           link_target,
                           CONCAT(SUBSTRING((start_date), 1, 4),
                                  "-",
                                  SUBSTRING((start_date), 5, 2),
                                  "-",
                                  SUBSTRING((start_date), 7, 2))
                              start_date,
                           CONCAT(SUBSTRING((start_time), 1, 2),
                                  ":",
                                  SUBSTRING((start_time), 3, 4))
                              start_time,
                           CONCAT(SUBSTRING((end_date), 1, 4),
                                  "-",
                                  SUBSTRING((end_date), 5, 2),
                                  "-",
                                  SUBSTRING((end_date), 7, 2))
                              end_date,
                           CONCAT(SUBSTRING((end_time), 1, 2), ":", SUBSTRING((end_time), 3, 4))
                              end_time
                      FROM popupzone
             WHERE seq = """ + id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            for p in row:
                mod_popZone.append(p)
            data = json.dumps(list(mod_popZone), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    variables = RequestContext(request, {
        'id': id
    })
    return render_to_response('popup/popupZone_modi.html', variables)


@csrf_exempt
@login_required
def new_popupZone(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        file_flag = request.POST.get('file_flag')
        update_flag = request.POST.get('update_flag')
        try:
            upload_file = request.FILES['uploadfile']
            uploadfile_user_id = request.POST.get('uploadfile_user_id')
        except BaseException:
            upload_file = None
            uploadfile_user_id = None

        if upload_file:
            uploadfile = request.FILES['uploadfile']

            common_single_file_upload(uploadfile, 'popupzone', str(uploadfile_user_id))

            return render(request, 'popup/popup_add.html')

        if request.POST.get('method') == 'add':
            title = request.POST.get('title')
            link_url = request.POST.get('link_url')
            link_target = request.POST.get('link_target')
            start_date = request.POST.get('start_date')
            start_time = request.POST.get('start_time')
            end_date = request.POST.get('end_date')
            end_time = request.POST.get('end_time')
            regist_id = request.POST.get('regist_id')

            image_file = 0;
            if (file_flag == '1'):
                cur = connection.cursor()
                query = '''select max(attatch_id) + 1 from tb_board_attach
                        '''
                cur.execute(query)
                attatch_id = cur.fetchall()
                image_file = attatch_id[0][0]
                cur.close()

            cur = connection.cursor()
            query = """
                INSERT INTO edxapp.popupzone(title,
                         image_file,
                         link_url,
                         link_target,
                         start_date,
                         start_time,
                         end_date,
                         end_time,
                         regist_id,
                         modify_id)
                 VALUES ('{0}',
                         '{1}',
                         '{2}',
                         '{3}',
                         '{4}',
                         '{5}',
                         '{6}',
                         '{7}',
                         '{8}',
                         '{9}');
            """.format(title, image_file, link_url, link_target, start_date,
                       start_time, end_date, end_time, regist_id, regist_id)
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})
            return HttpResponse(data, 'applications/json')

        elif request.POST['method'] == 'modi':
            title = request.POST.get('title')
            link_url = request.POST.get('link_url')
            link_target = request.POST.get('link_target')
            start_date = request.POST.get('start_date')
            start_time = request.POST.get('start_time')
            end_date = request.POST.get('end_date')
            end_time = request.POST.get('end_time')
            regist_id = request.POST.get('regist_id')
            seq = request.POST.get('seq')

            if (file_flag != '1'):
                cur = connection.cursor()
                query = '''
                            SELECT image_file
                              FROM popupzone
                             WHERE seq = '{0}';
                            '''.format(seq)
                cur.execute(query)
                attatch_id = cur.fetchall()
                image_file = attatch_id[0][0]
                cur.close()
            elif (file_flag == '1'):
                cur = connection.cursor()
                query = '''select max(attatch_id) + 1 from tb_board_attach
                        '''
                cur.execute(query)
                attatch_id = cur.fetchall()
                image_file = attatch_id[0][0]
                cur.close()

            cur = connection.cursor()
            query = """
                    UPDATE edxapp.popupzone
                       SET title = '{0}',
                           image_file = '{1}',
                           link_url = '{2}',
                           link_target = '{3}',
                           start_date = '{4}',
                           start_time = '{5}',
                           end_date = '{6}',
                           end_time = '{7}',
                           modify_id = '{8}',
                           modify_date = now()
                     WHERE seq = '{9}';
            """.format(title, image_file, link_url, link_target,
                       start_date, start_time, end_date, end_time, regist_id, seq)
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST['method'] == 'del':
            seq = request.POST.get('seq')
            cur = connection.cursor()
            query = """
                    DELETE FROM popupzone
                          WHERE seq = '{0}';
            """.format(seq)
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

    return render(request, 'popup/popupZone_add.html')


@login_required
def popup_index0(request, id, type):
    cur = connection.cursor()
    if (type == "text"):
        query = """
            SELECT title,
                   contents,
                   link_url,
                   link_target,
                   CASE
                      WHEN hidden_day = '1' THEN '1일간 열지 않음'
                      WHEN hidden_day = '7' THEN '7일간 열지 않음'
                      WHEN hidden_day = '0' THEN '다시 열지 않음'
                   END
                   hidden_day,
                   popup_type,
                   width-2,
                   height-53
              FROM popup
             WHERE popup_id = {0};
            """.format(id)
        cur.execute(query)
        row = cur.fetchall()
        cur.close()
        pop_list = []
        for p in row:
            pop_list.append(list(p))
        context = {'pop_list': pop_list}

        return render_to_response('popup/popup_index/indexH.html', context)

    elif (type == "image"):
        query = """
            SELECT title,
                   contents,
                   link_url,
                   link_target,
                   CASE
                      WHEN hidden_day = '1' THEN '1일간 열지 않음'
                      WHEN hidden_day = '7' THEN '7일간 열지 않음'
                      WHEN hidden_day = '0' THEN '다시 열지 않음'
                   END
                   hidden_day,
                   popup_type,
                   attatch_file_name,
                   width,
                   height,
                   image_map
              FROM popup
              JOIN tb_board_attach ON tb_board_attach.attatch_id = popup.image_file
             WHERE popup_id = {0};
            """.format(id)
        cur.execute(query)
        row = cur.fetchall()
        cur.close()
        pop_list = []

        for p in row:
            image_map = p[9]
            im_arr = image_map.split('/')
            pop_list.append(list(p + (im_arr,)))

        print pop_list
        context = {'pop_list': pop_list}

        return render_to_response('popup/popup_index/indexI.html', context)


@login_required
def popup_index1(request, id):
    cur = connection.cursor()
    query = """
        SELECT title,
               contents,
               link_url,
               link_target,
               CASE
                  WHEN hidden_day = '1' THEN '1일간 열지 않음'
                  WHEN hidden_day = '7' THEN '7일간 열지 않음'
                  WHEN hidden_day = '0' THEN '다시 열지 않음'
               END
               hidden_day,
               width,
               height-118
          FROM popup
         WHERE popup_id = {0};
        """.format(id)

    print query
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    pop_list = []
    for p in row:
        pop_list.append(list(p))
    context = {'pop_list': pop_list}

    return render_to_response('popup/popup_index/index1.html', context)


@login_required
def popup_index2(request, id):
    cur = connection.cursor()
    query = """
        SELECT title,
               contents,
               link_url,
               link_target,
               CASE
                  WHEN hidden_day = '1' THEN '1일간 열지 않음'
                  WHEN hidden_day = '7' THEN '7일간 열지 않음'
                  WHEN hidden_day = '0' THEN '다시 열지 않음'
               END
               hidden_day,
               width,
               height-153
          FROM popup
         WHERE popup_id = {0};
        """.format(id)

    print query
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    pop_list = []
    for p in row:
        pop_list.append(list(p))
    context = {'pop_list': pop_list}

    return render_to_response('popup/popup_index/index2.html', context)


@login_required
def popup_index3(request, id):
    cur = connection.cursor()
    query = """
        SELECT title,
               contents,
               link_url,
               link_target,
               CASE
                  WHEN hidden_day = '1' THEN '1일간 열지 않음'
                  WHEN hidden_day = '7' THEN '7일간 열지 않음'
                  WHEN hidden_day = '0' THEN '다시 열지 않음'
               END
               hidden_day,
               width,
               height-156
          FROM popup
         WHERE popup_id = {0};
        """.format(id)

    print query
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    pop_list = []
    for p in row:
        pop_list.append(list(p))
    context = {'pop_list': pop_list}

    return render_to_response('popup/popup_index/index3.html', context)


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
                   image_file,
                   link_url,
                   CASE
                      WHEN link_target = 'B' THEN 'blank'
                      WHEN link_target = 'S' THEN 'self'
                   END
                      link_target,
                   CONCAT(SUBSTRING((start_date), 1, 4),
                          "-",
                          SUBSTRING((start_date), 5, 2),
                          "-",
                          SUBSTRING((start_date), 7, 2))
                      start_date,
                   CONCAT(SUBSTRING((start_time), 1, 2),
                          ":",
                          SUBSTRING((start_time), 3, 4))
                      start_time,
                   CONCAT(SUBSTRING((end_date), 1, 4),
                          "-",
                          SUBSTRING((end_date), 5, 2),
                          "-",
                          SUBSTRING((end_date), 7, 2))
                      end_date,
                   CONCAT(SUBSTRING((end_time), 1, 2), ":", SUBSTRING((end_time), 3, 4))
                      end_time,
                   CASE
                      WHEN template = '0' THEN '없음'
                      WHEN template = '1' THEN 'type1'
                      WHEN template = '2' THEN 'type2'
                      WHEN template = '3' THEN 'type3'
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
                    SELECT count(*)
                      FROM popup
                     WHERE     now() BETWEEN str_to_date(concat(start_date, start_time),
                                                         '%Y%m%d%H%i')
                                         AND str_to_date(concat(end_date, end_time),
                                                         '%Y%m%d%H%i')
                           AND use_yn = 'Y';
                    """
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            for p in row:
                mod_pop.append(p)

            data = json.dumps(list(mod_pop), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    variables = RequestContext(request, {
        'id': id
    })
    return render_to_response('popup/popup_modipopup.html', variables)


def create_popup(request):
    return render(request, 'popup/popup_modipopup.html')


@csrf_exempt
@login_required
def popup_db(request):
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        popup_list = []

        if request.GET['method'] == 'popup_list':
            cur = connection.cursor()
            query = """
                   SELECT @rn := @rn - 1 rn,
                         popup_id,
                         CASE
                            WHEN popup_type = 'H' THEN 'HTML'
                            WHEN popup_type = 'I' THEN 'Image'
                         END
                            popup_type,
                         title,
                         username,
                         CONCAT(SUBSTRING((start_date), 1, 4),
                          "-",
                          SUBSTRING((start_date), 5, 2),
                          "-",
                          SUBSTRING((start_date), 7, 2))
                         start_date,
                         CONCAT(SUBSTRING((end_date), 1, 4),
                          "-",
                          SUBSTRING((end_date), 5, 2),
                          "-",
                          SUBSTRING((end_date), 7, 2))
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
                    FROM popup pu
                         JOIN auth_user au ON au.id = pu.regist_id,
                         (SELECT @rn := count(*) + 1
                            FROM popup WHERE delete_yn = 'N') x
                            WHERE pu.delete_yn = 'N'
                ORDER BY regist_date DESC;
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
                value_list.append(pop[9])
                popup_list.append(value_list)

            data = json.dumps(list(popup_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')
    return render(request, 'popup/popup_add.html')


@csrf_exempt
@login_required
def new_popup(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        file_flag = request.POST.get('file_flag')
        update_flag = request.POST.get('update_flag')
        try:
            upload_file = request.FILES['uploadfile']
            uploadfile_user_id = request.POST.get('uploadfile_user_id')
        except BaseException:
            upload_file = None
            uploadfile_user_id = None

        if upload_file:
            uploadfile = request.FILES['uploadfile']

            common_single_file_upload(uploadfile, 'popup', str(uploadfile_user_id))

            return render(request, 'popup/popup_add.html')

        if request.POST.get('method') == 'add':
            popup_type = request.POST.get('popup_type')
            link_type = request.POST.get('link_type')
            image_map = request.POST.get('image_map').rstrip('/')
            title = request.POST.get('title')
            contents = request.POST.get('contents')
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
            image_file = 0;

            if (file_flag == '1'):
                cur = connection.cursor()
                query = '''select max(attatch_id) from tb_board_attach
                        '''
                cur.execute(query)
                attatch_id = cur.fetchall()
                image_file = attatch_id[0][0]
                cur.close()

            cur = connection.cursor()
            query = """
                INSERT INTO edxapp.popup(popup_type,
                         link_type,
                         image_map,
                         title,
                         contents,
                         image_file,
                         link_url,
                         link_target,
                         start_date,
                         start_time,
                         end_date,
                         end_time,
                         template,
                         width,
                         height,
                         hidden_day,
                         regist_id,
                         modify_id,
                         use_yn)
                 VALUES ('{0}',
                         '{1}',
                         '{2}',
                         '{3}',
                         '{4}',
                         '{5}',
                         '{6}',
                         '{7}',
                         '{8}',
                         '{9}',
                         '{10}',
                         '{11}',
                         '{12}',
                         '{13}',
                         '{14}',
                         '{15}',
                         '{16}',
                         '{17}',
                         '{18}');
            """.format(popup_type, link_type, image_map, title, contents, image_file, link_url, link_target, start_date,
                       start_time, end_date, end_time, template, width, height, hidden_day, regist_id, regist_id,
                       use_yn)
            cur.execute(query)
            cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')


        elif request.POST['method'] == 'modi':
            popup_type = request.POST.get('popup_type')
            link_type = request.POST.get('link_type')
            image_map = request.POST.get('image_map').rstrip('/')
            title = request.POST.get('title')
            contents = request.POST.get('contents')
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
            image_file = 0;

            if (update_flag == '1' and file_flag != '1'):
                cur = connection.cursor()
                query = '''
                            SELECT image_file
                              FROM popup
                             WHERE popup_id = '{0}';
                            '''.format(pop_id)
                cur.execute(query)
                attatch_id = cur.fetchall()
                image_file = attatch_id[0][0]
                cur.close()
            elif (file_flag == '1'):
                cur = connection.cursor()
                query = '''select max(attatch_id) from tb_board_attach
                        '''
                cur.execute(query)
                attatch_id = cur.fetchall()
                image_file = attatch_id[0][0]
                cur.close()

            cur = connection.cursor()
            query = """
                    UPDATE edxapp.popup
                       SET popup_type = '{0}',
                           link_type = '{1}',
                           image_map = '{2}',
                           title = '{3}',
                           contents = '{4}',
                           image_file = '{5}',
                           link_url = '{6}',
                           link_target = '{7}',
                           start_date = '{8}',
                           start_time = '{9}',
                           end_date = '{10}',
                           end_time = '{11}',
                           template = '{12}',
                           width = '{13}',
                           height = '{14}',
                           hidden_day = '{15}',
                           modify_id = '{16}',
                           use_yn = '{17}',
                           modify_date = now()
                     WHERE popup_id = '{18}';
            """.format(popup_type, link_type, image_map, title, contents, image_file, link_url, link_target,
                       start_date, start_time, end_date, end_time, template, width, height, hidden_day, regist_id,
                       use_yn, pop_id)
            print (query)
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'copy':
            pop_id = request.POST.get('pop_id')

            cur = connection.cursor()
            query = """
                  INSERT INTO popup(popup_type,
                              link_type,
                              image_map,
                              title,
                              contents,
                              image_file,
                              link_url,
                              link_target,
                              start_date,
                              start_time,
                              end_date,
                              end_time,
                              template,
                              width,
                              height,
                              hidden_day,
                              regist_id,
                              modify_id)
               SELECT popup_type,
                      link_type,
                      image_map,
                      title,
                      contents,
                      image_file,
                      link_url,
                      link_target,
                      end_date,
                      start_time,
                      end_date,
                      end_time,
                      template,
                      width,
                      height,
                      hidden_day,
                      regist_id,
                      modify_id
                 FROM popup
                WHERE popup_id = '{0}';
                    """.format(pop_id)

            cur.execute(query)
            cur.close()

            cur = connection.cursor()
            query = "SELECT max(popup_id) FROM popup;"
            cur.execute(query)
            maxN = cur.fetchall()
            cur.close()

            data = maxN[0][0]

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'delete':
            pop_id = request.POST.get('pop_id')

            cur = connection.cursor()
            query = "update edxapp.popup set use_yn = 'N', delete_yn = 'Y' where popup_id = " + pop_id
            cur.execute(query)
            cur.close()

            data = json.dumps({'status': "success"})

            return HttpResponse(data, 'applications/json')

        elif request.POST.get('method') == 'check':
            pop_id = request.POST.get('pop_id')

            cur = connection.cursor()
            query = """
                    SELECT count(image_file)
                      FROM popup
                     WHERE popup_id = '{0}';
                    """.format(pop_id)
            cur.execute(query)
            flag = cur.fetchall()
            cur.close()

            data = flag[0][0];

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


# ---------- 2017.11.03 ahn jin yong ---------- #
@csrf_exempt
def file_upload(request):
    if request.FILES:
        file_object_list = request.FILES.getlist('file')
        file_object = file_object_list[0]
        # 파일객체 고정 userid
        common_single_file_upload(file_object, 'multisite', '1')

        return JsonResponse({'hello': 'world'})


# ---------- 2017.11.03 ahn jin yong ---------- #

# ---------- 2017.10.23 ahn jin yong ---------- #
@csrf_exempt
def new_notice(request):
    # ---------- 공통 file upload(공지사항, K-MOOC소식, 자료실) ---------- #
    if request.FILES:
        # init list
        file_name_list = []
        file_dir_list = []
        file_size_raw_list = []
        file_size_list = []
        file_ext_list = []
        file_list = request.FILES.getlist('file')
        file_list_cnt = len(request.FILES.getlist('file'))

        # make name, dir
        for item in file_list:
            file_name_list.append(str(item))
            file_dir_list.append(UPLOAD_DIR + str(item))

        # make ext
        for item in file_name_list:
            file_ext = get_file_ext(item)
            file_ext_list.append(file_ext)

        # crete file
        cnt = 0
        for item in file_list:
            fp = open(file_dir_list[cnt], 'wb')
            for chunk in item.chunks():
                fp.write(chunk)
            fp.close()
            cnt += 1

        # make raw_size
        for item in file_dir_list:
            file_size_raw_list.append(os.path.getsize(item))

        # make size (KB)
        for item in file_size_raw_list:
            file_size_list.append(str(item / 1024) + "KB")  # invert KB

        return JsonResponse({'name': file_name_list, 'size': file_size_list, 'len': file_list_cnt})
    # ---------- 공통 file upload(공지사항, K-MOOC소식, 자료실) ---------- #

    elif request.method == 'POST':
        data = json.dumps({'status': "fail", 'msg': "오류가 발생했습니다"})
        # ---------- 공통 글 쓰기(공지사항, K-MOOC소식, 자료실) ---------- #
        if request.POST['method'] == 'add':

            # board var
            title = request.POST.get('title')
            title = title.replace("'", "''")
            content = request.POST.get('content')
            content = content.replace("'", "''")
            head_title = request.POST.get('head_title')
            section = request.POST.get('section')
            odby = request.POST.get('odby')
            upload_file = request.POST.get('uploadfile')

            # file 
            file_ext_list = []
            file_name_list = []
            file_size_list = []

            # make file name, size, ext
            upload_file = unicode(upload_file)
            upload_split = upload_file.split('+')
            for item in upload_split:
                index = item.find('   ')
                file_name_list.append(item[:index])
                file_size_list.append(item[index + 3:])
            file_name_list.pop()
            file_size_list.pop()
            for item in file_name_list:
                file_ext_list.append(get_file_ext(item))
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
            query3 = '''
                SELECT LAST_INSERT_ID()
            '''
            cur.execute(query3)
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
        # ---------- 공통 글 쓰기(공지사항, K-MOOC소식, 자료실) ---------- #

        # ---------- 공통 글 편집(공지사항, K-MOOC소식, 자료실) ---------- #
        elif request.POST['method'] == 'modi':

            # board var
            title = request.POST.get('title')
            title = title.replace("'", "''")
            content = request.POST.get('content')
            content = content.replace("'", "''")
            noti_id = request.POST.get('board_id')
            odby = request.POST.get('odby')
            head_title = request.POST.get('head_title')
            upload_file = request.POST.get('uploadfile')
            delete_list = request.POST.get('delete_list')

            # make delete list
            delete_list = delete_list.split('+')
            delete_list.pop()

            # ------ file delete query ------ #
            for item in delete_list:
                cur = connection.cursor()
                query = '''
                    UPDATE edxapp.tb_board_attach 
                    SET    del_yn = 'Y' 
                    WHERE  attatch_id = '{0}'; 
                '''.format(item)
                cur.execute(query)
                cur.close()
            # ------ file delete query ------ #

            # file 
            file_ext_list = []
            file_name_list = []
            file_size_list = []

            # make file name, size, ext
            upload_file = unicode(upload_file)
            upload_split = upload_file.split('+')
            for item in upload_split:
                index = item.find('   ')
                file_name_list.append(item[:index])
                file_size_list.append(item[index + 3:])
            file_name_list.pop()
            file_size_list.pop()
            for item in file_name_list:
                file_ext_list.append(get_file_ext(item))
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
        # ---------- 공통 글 편집(공지사항, K-MOOC소식, 자료실) ---------- #
    return render(request, 'community/comm_newnotice.html')


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
            pass  # 'file_download with ajax is not working'

        return HttpResponse(data, 'applications/json')

    # ------ 공지사항 파일첨부 보여주기 query ------ #
    cur = connection.cursor()
    query = '''
        SELECT attatch_file_name, 
               attatch_file_ext, 
               attatch_file_size,
               attatch_id
        FROM   edxapp.tb_board_attach 
        WHERE  board_id = '{0}' 
               AND del_yn = 'N'
    '''.format(id)
    cur.execute(query)
    file_list = cur.fetchall()
    cur.close()
    # ------ 공지사항 파일첨부 보여주기 query ------ #

    context = {
        'id': id,
        'use_yn': use_yn,
        'file_list': file_list
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
        pass  # 모듈화 new_notice OK
    elif request.method == 'POST':
        if request.POST['method'] == 'add':
            pass  # 모듈화 new_notice OK
        elif request.POST['method'] == 'modi':
            pass  # 모듈화 new_notice OK
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
               attatch_file_size,
               attatch_id
        FROM   edxapp.tb_board_attach 
        WHERE  board_id = '{0}'
               AND del_yn = 'N'
    '''.format(id)
    cur.execute(query)
    file_list = cur.fetchall()
    cur.close()
    # ------ knews 파일첨부 보여주기 query ------ #

    context = {
        'id': id,
        'use_yn': use_yn,
        'file_list': file_list
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
        pass  # 모듈화 new_notice OK
    elif request.method == 'POST':
        if request.POST['method'] == 'add':
            pass  # 모듈화 new_notice OK
        elif request.POST['method'] == 'modi':
            pass  # 모듈화 new_notice OK
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
               attatch_file_size,
               attatch_id
        FROM   edxapp.tb_board_attach 
        WHERE  board_id = '{0}'
               AND del_yn = 'N'
    '''.format(id)
    cur.execute(query)
    file_list = cur.fetchall()
    cur.close()
    # ------ 공지사항 파일첨부 보여주기 query ------ #

    context = {
        'id': id,
        'use_yn': use_yn,
        'file_list': file_list
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
def login_history(request):
    if request.is_ajax():
        result = dict()
        columns, recordsTotal, result_list = history_rows(request)
        result['data'] = result_list
        result['recordsTotal'] = recordsTotal
        result['recordsFiltered'] = recordsTotal

        context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(context, 'applications/json')

    else:
        return render(request, 'history/login_history.html')


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
            query_arr.append(" and b.action_flag = %s " % operation)

        if func:
            query_arr.append(" and a.id = %s " % func)

        if func_detail:
            query_arr.append(" and b.action_flag = %s " % func_detail)

        if user_id:
            query_arr.append(" and (c.id = '{user_id}' or c.username like '%{user_id}%')".format(user_id=user_id))

        if target_id:
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
                query_string_dict = change_message_dict['query'] if change_message_dict.has_key('query') else dict()

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
            result_dict['cnt'] = (change_message_dict['count'] if isinstance(change_message_dict['count'],
                                                                             int) else '-') if 'count' in change_message_dict and content_type_id not in [
                '303',
                '304'] else '-'

    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(connection.queries)

    return columns, recordsTotal, result_list


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
    file_path = '%s%s' % (STATIC_URL, file_name)
    # file_path = '/Users/kotech/workspace/scpTest/tracking_log.zip'
    print 'file_path:', file_path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            if file_name == 'tracking_log.zip':
                response = HttpResponse(fh.read(), content_type="application/x-zip-compressed")
            else:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)

            oldLog_remove(file_path, 3)

            return response
    raise Http404


# ---------- 2017.12.04 ahn jin yong ---------- #
def review_manage(request):

    if request.is_ajax():

        if request.GET.get('del_list'):
            del_list = request.GET.get('del_list')
            del_list = del_list.split('+')
            del_list.pop()

            with connections['default'].cursor() as cur:
                for item in del_list:
                    query = '''
                        delete from edxapp.course_review
                        where id = {0};
                    '''.format(item)
                    cur.execute(query)
            return JsonResponse({'return':'success'})

        startDt = request.GET.get('startDt')
        endDt = request.GET.get('endDt')
        startDt = startDt.replace('/', '-')
        endDt = endDt.replace('/', '-')
        name_search = request.GET.get('name_search')
        org_search = request.GET.get('org_search')
        code_search = request.GET.get('code_search')

        if name_search=='' and org_search=='' and code_search=='':
            mode = 'all'
        elif name_search!='' and org_search=='' and code_search=='':
            mode = 'name'
        elif name_search=='' and org_search!='' and code_search=='':
            mode = 'org'
        elif name_search=='' and org_search=='' and code_search!='':
            mode = 'code'
        elif name_search!='' and org_search!='' and code_search=='':
            mode = 'name_org'
        elif name_search!='' and org_search=='' and code_search!='':
            mode = 'name_code'
        elif name_search=='' and org_search!='' and code_search!='':
            mode = 'org_code'
        elif name_search!='' and org_search!='' and code_search!='':
            mode = 'name_org_code'

        print 'mode = ',mode

        with connections['default'].cursor() as cur:
            query = '''
                SELECT cr.id,
                       cd.detail_name,
                       coc.display_name,
                       cr.content,
                       cr.point,
                       Sum(CASE
                             WHEN good_bad = 'g' THEN 1
                             ELSE 0
                           END) AS good,
                       Sum(CASE
                             WHEN good_bad = 'b' THEN 1
                             ELSE 0
                           END) AS bad,
                       au.username,
                       Date_format(cr.reg_time, '%Y/%m/%d %h:%m') reg_time
                FROM   edxapp.course_review AS cr
                       LEFT JOIN edxapp.auth_user AS au
                              ON au.id = cr.user_id
                       LEFT JOIN edxapp.course_review_user AS cru
                              ON cru.review_id = cr.id
                       LEFT JOIN edxapp.course_overviews_courseoverview AS coc
                              ON cr.course_id = coc.id
                       LEFT JOIN edxapp.code_detail AS cd
                              ON coc.org = cd.detail_code
                WHERE cr.reg_time < '{0}' AND cr.reg_time > '{1}'
                -- mode
                GROUP  BY cr.id,
                          cd.detail_name,
                          coc.display_name,
                          cr.content,
                          cr.point,
                          au.username,
                          cr.reg_time
                ORDER  BY id
            '''.format(endDt, startDt)

            if mode == 'name':
                restr = "AND cr.content like '%{0}%'".format(name_search)
                query = query.replace("-- mode", restr)

            elif mode == 'org':
                restr = "AND cd.detail_name like '%{0}%'".format(org_search)
                query = query.replace("-- mode", restr)

            elif mode == 'code':
                restr = "AND coc.id like 'course-v1:%+{0}+%'".format(code_search)
                query = query.replace("-- mode", restr)

            elif mode == 'name_org':
                restr = "AND cr.content like '%{0}%' AND cd.detail_name like '%{1}%'".format(name_search, org_search)
                query = query.replace("-- mode", restr)

            elif mode == 'name_code':
                restr = "AND cr.content like '%{0}%' AND coc.id like 'course-v1:%+{1}+%'".format(name_search, code_search)
                query = query.replace("-- mode", restr)

            elif mode == 'org_code':
                restr = "AND cd.detail_name like '%{0}%' AND coc.id like 'course-v1:%+{1}+%'".format(org_search, code_search)
                query = query.replace("-- mode", restr)

            elif mode == 'name_org_code':
                restr = "AND cr.content like '%{0}%' AND cd.detail_name like '%{1}%' AND coc.id like 'course-v1:%+{2}+%'".format(name_search, org_search, code_search)
                query = query.replace("-- mode", restr)

            print "------------------>"
            print query
            print "------------------>"

            cur.execute(query)
            rows = cur.fetchall()
            columns = [col[0] for col in cur.description]
            result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]
        result = dict()
        result['data'] = result_list
        context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(context, 'applications/json')

    return render(request, 'review_manage/review_manage.html')
# ---------- 2017.12.04 ahn jin yong ---------- #

# ---------- 2017.11.03 ahn jin yong ---------- #
@login_required
def multiple_email(request):
    if request.is_ajax():

        # what is mode?
        search_mod = request.GET.get('search_mod')

        # search name
        if search_mod == '2':
            name_search = request.GET.get('name_search')
            with connections['default'].cursor() as cur:
                query = '''
                    SELECT mail_id,
                           CASE
                                  WHEN target1 = '1'
                                  AND    target2 = '0'
                                  AND    target3 = '0' THEN '수강신청경험자'
                                  WHEN target1 = '0'
                                  AND    target2 = '1'
                                  AND    target3 = '0' THEN '교수자 권한'
                                  WHEN target1 = '0'
                                  AND    target2 = '0'
                                  AND    target3 = '1' THEN '운영자 권한'
                                  WHEN target1 = '1'
                                  AND    target2 = '1'
                                  AND    target3 = '0' THEN '수강신청경험자, 교수자권한'
                                  WHEN target1 = '1'
                                  AND    target2 = '0'
                                  AND    target3 = '1' THEN '수강신청경험자한, 운영자권한'
                                  WHEN target1 = '0'
                                  AND    target2 = '1'
                                  AND    target3 = '1' THEN '교수자권한, 운영자 권한'
                                  WHEN target1 = '1'
                                  AND    target2 = '1'
                                  AND    target3 = '1' THEN '수강신청경험자, 교수자권한, 운영자권한'
                           end gubn,
                           au.username,
                           title,
                           Date_format(regist_date, '%Y/%m/%d %h:%m') regist_date,
                           send_count,
                           success_count
                    FROM   edxapp.group_email AS ge
                    JOIN   edxapp.auth_user   AS au
                    ON     ge.regist_id = au.id
                    WHERE   title like '%{0}%'
                '''.format(name_search)
                query = query.replace('\xe2\x80\xa8', '')  # query bugfix
                cur.execute(query)
                rows = cur.fetchall()
                columns = [col[0] for col in cur.description]
                result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]
            result = dict()
            result['data'] = result_list
            context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
            return HttpResponse(context, 'applications/json')

        # search date
        if search_mod == '1':
            startDt = request.GET.get('startDt')
            endDt = request.GET.get('endDt')
            startDt = startDt.replace('/', '-')
            endDt = endDt.replace('/', '-')
            with connections['default'].cursor() as cur:
                query = '''
                    SELECT mail_id,
                           CASE
                                  WHEN target1 = '1'
                                  AND    target2 = '0'
                                  AND    target3 = '0' THEN '수강신청경험자'
                                  WHEN target1 = '0'
                                  AND    target2 = '1'
                                  AND    target3 = '0' THEN '교수자 권한'
                                  WHEN target1 = '0'
                                  AND    target2 = '0'
                                  AND    target3 = '1' THEN '운영자 권한'
                                  WHEN target1 = '1'
                                  AND    target2 = '1'
                                  AND    target3 = '0' THEN '수강신청경험자, 교수자권한'
                                  WHEN target1 = '1'
                                  AND    target2 = '0'
                                  AND    target3 = '1' THEN '수강신청경험자한, 운영자권한'
                                  WHEN target1 = '0'
                                  AND    target2 = '1'
                                  AND    target3 = '1' THEN '교수자권한, 운영자 권한'
                                  WHEN target1 = '1'
                                  AND    target2 = '1'
                                  AND    target3 = '1' THEN '수강신청경험자, 교수자권한, 운영자권한'
                           end gubn,
                           au.username,
                           title,
                           Date_format(regist_date, '%Y/%m/%d %h:%m') regist_date,
                           send_count,
                           success_count
                    FROM   edxapp.group_email AS ge
                    JOIN   edxapp.auth_user   AS au
                    ON     ge.regist_id = au.id
                    WHERE   regist_date BETWEEN '{0}' AND '{1}'
                '''.format(startDt, endDt)
                query = query.replace('\xe2\x80\xa8', '')  # query bugfix
                cur.execute(query)
                rows = cur.fetchall()
                columns = [col[0] for col in cur.description]
                result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]
            result = dict()
            result['data'] = result_list
            context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
            return HttpResponse(context, 'applications/json')

        # search base
        if search_mod == '0':
            with connections['default'].cursor() as cur:
                query = '''
                    SELECT mail_id,
                           CASE
                             WHEN target1 = '0'
                                  AND target2 = '0'
                                  AND target3 = '0' THEN '수동발송'
                             WHEN target1 = '1'
                                  AND target2 = '0'
                                  AND target3 = '0' THEN '수강신청경험자'
                             WHEN target1 = '0'
                                  AND target2 = '1'
                                  AND target3 = '0' THEN '교수자 권한'
                             WHEN target1 = '0'
                                  AND target2 = '0'
                                  AND target3 = '1' THEN '운영자 권한'
                             WHEN target1 = '1'
                                  AND target2 = '1'
                                  AND target3 = '0' THEN '수강신청경험자, 교수자권한'
                             WHEN target1 = '1'
                                  AND target2 = '0'
                                  AND target3 = '1' THEN '수강신청경험자한, 운영자권한'
                             WHEN target1 = '0'
                                  AND target2 = '1'
                                  AND target3 = '1' THEN '교수자권한, 운영자 권한'
                             WHEN target1 = '1'
                                  AND target2 = '1'
                                  AND target3 = '1' THEN
                             '수강신청경험자, 교수자권한, 운영자권한'
                           end                                        gubn,
                           au.username,
                           title,
                           Date_format(regist_date, '%Y/%m/%d %h:%m') regist_date,
                           send_count,
                           success_count
                    FROM   edxapp.group_email AS ge
                           JOIN edxapp.auth_user AS au
                             ON ge.regist_id = au.id
                '''
                cur.execute(query)
                rows = cur.fetchall()
                columns = [col[0] for col in cur.description]
                result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]
            result = dict()
            result['data'] = result_list
            context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)
            return HttpResponse(context, 'applications/json')
    return render(request, 'multiple_email/multiple_email.html')


# 메일 전송 공통 모듈
def common_send_mail(to_user, title, content):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_id = 'b930208@gmail.com'
    smtp_pw = '####'
    from_user = smtp_id

    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.ehlo()  # say Hello
    smtp.starttls()  # TLS 사용시 필요
    smtp.login(smtp_id, smtp_pw)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = title
    msg['From'] = from_user
    msg['To'] = to_user

    html = content
    part = MIMEText(html, 'html')
    msg.attach(part)
    s = smtp
    s.sendmail(from_user, to_user, msg.as_string())
    s.quit()


@login_required
def multiple_email_new(request):
    if request.is_ajax():
        # init data
        user_list = []
        user_id_list = []
        fail_cnt = 0

        # get data
        user_id = request.POST.get('userid')
        subject_flag = request.POST.get('subject_flag')
        send_type = request.POST.get('send_type')
        account_type = request.POST.get('account_type')

        print "user_id = {}".format(user_id)
        print "subject_flag = {}".format(subject_flag)  # experienced_student, instructor, operator / 1 2 3
        print "send_type = {}".format(send_type)  # email, message, apppush / E M P
        print "account_type = {}".format(account_type)  # activation, inactive, all / E I A

        # 보내는 타입이 'memo'일 때 로직
        if send_type == 'memo':
            # 보내는 타입이 '수동입력'이 아닐 때 로직
            if subject_flag == 'hello':
                experienced_student = request.POST.get('experienced_student')
                instructor = request.POST.get('instructor')
                operator = request.POST.get('operator')
                # 유저 목록 구해오는 로직
                if (experienced_student == 'true' and instructor == 'true' and operator == 'true') or (instructor == 'true' and operator == 'true'):
                    target1 = '1'
                    target2 = '1'
                    target3 = '1'
                    with connections['default'].cursor() as cur:
                        query = '''
                            SELECT distinct(a.email), a.id
                              FROM auth_user a, student_courseenrollment b
                             WHERE     a.id = b.user_id
                                   AND (   EXISTS
                                              (SELECT 1
                                                 FROM student_courseaccessrole c
                                                WHERE     a.id = c.user_id
                                                      AND b.course_id = c.course_id
                                                      AND c.role = 'instructor')
                                        OR EXISTS
                                              (SELECT 1
                                                 FROM student_courseaccessrole c
                                                WHERE     a.id = c.user_id
                                                      AND b.course_id = c.course_id
                                                      AND c.role = 'staff'))
                        '''
                        if account_type == 'activation':
                            query = query + "AND a.is_active = 1"
                            db_account_type = 'E'
                        elif account_type == 'inactive':
                            query = query + "AND a.is_active = 0"
                            db_account_type = 'I'
                        cur.execute(query)
                        db_account_type = 'A'
                        rows = cur.fetchall()
                    for item in rows:
                        user_list.append(item[0])
                        user_id_list.append(item[1])

                elif (experienced_student == 'true' and instructor == 'true') or (instructor == 'true'):
                    target1 = '1'
                    target2 = '1'
                    target3 = '0'
                    with connections['default'].cursor() as cur:
                        query = '''
                            SELECT distinct(a.email), a.id
                              FROM auth_user a, student_courseenrollment b
                             WHERE     a.id = b.user_id
                                   AND (   EXISTS
                                              (SELECT 1
                                                 FROM student_courseaccessrole c
                                                WHERE     a.id = c.user_id
                                                      AND b.course_id = c.course_id
                                                      AND c.role = 'instructor'))
                        '''
                        if account_type == 'activation':
                            query = query + "AND a.is_active = 1"
                            db_account_type = 'E'
                        elif account_type == 'inactive':
                            query = query + "AND a.is_active = 0"
                            db_account_type = 'I'
                        cur.execute(query)
                        db_account_type = 'A'
                        rows = cur.fetchall()
                    for item in rows:
                        user_list.append(item[0])
                        user_id_list.append(item[1])

                elif (experienced_student == 'true' and operator == 'true') or (operator == 'true'):
                    target1 = '1'
                    target2 = '0'
                    target3 = '1'
                    with connections['default'].cursor() as cur:
                        query = '''
                            SELECT distinct(a.email), a.id
                              FROM auth_user a, student_courseenrollment b
                             WHERE     a.id = b.user_id
                                   AND (   EXISTS
                                              (SELECT 1
                                                 FROM student_courseaccessrole c
                                                WHERE     a.id = c.user_id
                                                      AND b.course_id = c.course_id
                                                      AND c.role = 'staff'))
                        '''
                        if account_type == 'activation':
                            query = query + "AND a.is_active = 1"
                            db_account_type = 'E'
                        elif account_type == 'inactive':
                            query = query + "AND a.is_active = 0"
                            db_account_type = 'I'
                        cur.execute(query)
                        db_account_type = 'A'
                        rows = cur.fetchall()
                    for item in rows:
                        user_list.append(item[0])
                        user_id_list.append(item[1])

                elif experienced_student == 'true':
                    target1 = '1'
                    target2 = '0'
                    target3 = '0'
                    with connections['default'].cursor() as cur:
                        query = '''
                            SELECT distinct(a.email), a.id
                              FROM auth_user a, student_courseenrollment b
                             WHERE     a.id = b.user_id
                        '''
                        if account_type == 'activation':
                            query = query + "AND a.is_active = 1"
                            db_account_type = 'E'
                        elif account_type == 'inactive':
                            query = query + "AND a.is_active = 0"
                            db_account_type = 'I'
                        cur.execute(query)
                        db_account_type = 'A'
                        rows = cur.fetchall()
                    for item in rows:
                        user_list.append(item[0])
                        user_id_list.append(item[1])

            # 보내는 타입이 '수동입력'일 때 로직
            elif subject_flag == 'world':
                notauto = request.POST.get('notauto')
                tmp = notauto.split(',')
                # 유저 목록 구해오는 로직
                for email in tmp:
                    user_list.append(email.strip())

            # 제목, 내용 공통
            title = request.POST.get('title')
            content = request.POST.get('content')

            # ---------- insert data ----------#
            # 보내는 타입이 '수동입력'이 아닐 때 로직
            if subject_flag == 'hello':
                with connections['default'].cursor() as cur:
                    query = '''
                        insert into edxapp.group_email(send_type, account_type, target1, target2, target3, title, contents, regist_id)
                        values('M', '{0}', {1}, {2}, {3}, '{4}', '{5}', {6})
                    '''.format(db_account_type, target1, target2, target3, title, content.replace("'","''"), user_id)
                    cur.execute(query)
                    print query
            # 보내는 타입이 '수동입력'일 때 로직
            elif subject_flag == 'world':
                with connections['default'].cursor() as cur:
                    query = '''
                        insert into edxapp.group_email(send_type, account_type, target1, target2, target3, title, contents, regist_id)
                        values('M', 'N', 0, 0, 0, '{0}', '{1}', {2})
                    '''.format(title, content.replace("'","''"), user_id)
                    cur.execute(query)
                    print query
            # insert 이후 마지막 글 번호 얻어오기
            with connections['default'].cursor() as cur:
                query = '''
                    SELECT LAST_INSERT_ID();
                '''
                cur.execute(query)
                rows = cur.fetchall()
                row_id = rows[0][0]
            # ---------- insert data ----------#

            # making user id
            if subject_flag == 'world':
                for item in user_list:
                    with connections['default'].cursor() as cur:
                        query = '''
                            select id
                            from auth_user
                            where email = '{0}';
                        '''.format(item)
                        print query #DEBUG
                        cur.execute(query)
                        rows = cur.fetchall()
                        try:
                            user_id_list.append(rows[0][0])
                        except BaseException:
                            return JsonResponse({"return":"fail_no_user"})

            # ---------- insert memo ----------#
            for n in range(0, len(user_list)):
                # 보내는 타입이 '수동입력'이 아닐 때 로직
                if subject_flag == 'hello':
                    with connections['default'].cursor() as cur:
                        query = '''
                             insert into edxapp.memo(receive_id, title, contents, regist_id, modify_date)
                             values({0}, '{1}', '{2}', {3}, NULL);
                        '''.format(user_id_list[n], title, content.replace("'","''"), user_id)
                        print query #DEBUG
                        cur.execute(query)
                # 보내는 타입이 '수동입력'일 때 로직
                elif subject_flag == 'world':
                    with connections['default'].cursor() as cur:
                        query = '''
                             insert into edxapp.memo(receive_id, title, contents, regist_id, modify_date)
                             values({0}, '{1}', '{2}', {3}, NULL);
                        '''.format(user_id_list[n] ,title, content.replace("'","''"), user_id)
                        print query #DEBUG
                        cur.execute(query)
            # ---------- insert memo ----------#

            # making success cnt, fail cnt
            total_user = len(user_list)
            fail_cnt = fail_cnt
            success_cnt =  (len(user_list) - fail_cnt)

            # update success cnt, total cnt
            with connections['default'].cursor() as cur:
                query = '''
                    UPDATE edxapp.group_email
                    SET    send_count = {0},
                           success_count = {1}
                    WHERE  mail_id = {2}
                '''.format(total_user, success_cnt, row_id)
                cur.execute(query)

            return JsonResponse({"return":"success"})

        # 보내는 타입이 'email'일 때 로직
        if send_type == 'email':
            # 보내는 타입이 '수동입력'이 아닐 때 로직
            if subject_flag == 'hello':
                experienced_student = request.POST.get('experienced_student')
                instructor = request.POST.get('instructor')
                operator = request.POST.get('operator')
                # 유저 목록 구해오는 로직
                if (experienced_student == 'true' and instructor == 'true' and operator == 'true') or (
                                instructor == 'true' and operator == 'true'):
                    target1 = '1'
                    target2 = '1'
                    target3 = '1'
                    with connections['default'].cursor() as cur:
                        query = '''
                            SELECT distinct(a.email), a.id
                              FROM auth_user a, student_courseenrollment b
                             WHERE     a.id = b.user_id
                                   AND (   EXISTS
                                              (SELECT 1
                                                 FROM student_courseaccessrole c
                                                WHERE     a.id = c.user_id
                                                      AND b.course_id = c.course_id
                                                      AND c.role = 'instructor')
                                        OR EXISTS
                                              (SELECT 1
                                                 FROM student_courseaccessrole c
                                                WHERE     a.id = c.user_id
                                                      AND b.course_id = c.course_id
                                                      AND c.role = 'staff'))
                        '''
                        if account_type == 'activation':
                            query = query + "AND a.is_active = 1"
                            db_account_type = 'E'
                        elif account_type == 'inactive':
                            query = query + "AND a.is_active = 0"
                            db_account_type = 'I'
                        cur.execute(query)
                        db_account_type = 'A'
                        rows = cur.fetchall()
                    for item in rows:
                        user_list.append(item[0])
                        user_id_list.append(item[1])

                elif (experienced_student == 'true' and instructor == 'true') or (instructor == 'true'):
                    target1 = '1'
                    target2 = '1'
                    target3 = '0'
                    with connections['default'].cursor() as cur:
                        query = '''
                            SELECT distinct(a.email), a.id
                              FROM auth_user a, student_courseenrollment b
                             WHERE     a.id = b.user_id
                                   AND (   EXISTS
                                              (SELECT 1
                                                 FROM student_courseaccessrole c
                                                WHERE     a.id = c.user_id
                                                      AND b.course_id = c.course_id
                                                      AND c.role = 'instructor'))
                        '''
                        if account_type == 'activation':
                            query = query + "AND a.is_active = 1"
                            db_account_type = 'E'
                        elif account_type == 'inactive':
                            query = query + "AND a.is_active = 0"
                            db_account_type = 'I'
                        cur.execute(query)
                        db_account_type = 'A'
                        rows = cur.fetchall()
                    for item in rows:
                        user_list.append(item[0])
                        user_id_list.append(item[1])

                elif (experienced_student == 'true' and operator == 'true') or (operator == 'true'):
                    target1 = '1'
                    target2 = '0'
                    target3 = '1'
                    with connections['default'].cursor() as cur:
                        query = '''
                            SELECT distinct(a.email), a.id
                              FROM auth_user a, student_courseenrollment b
                             WHERE     a.id = b.user_id
                                   AND (   EXISTS
                                              (SELECT 1
                                                 FROM student_courseaccessrole c
                                                WHERE     a.id = c.user_id
                                                      AND b.course_id = c.course_id
                                                      AND c.role = 'staff'))
                        '''
                        if account_type == 'activation':
                            query = query + "AND a.is_active = 1"
                            db_account_type = 'E'
                        elif account_type == 'inactive':
                            query = query + "AND a.is_active = 0"
                            db_account_type = 'I'
                        cur.execute(query)
                        db_account_type = 'A'
                        rows = cur.fetchall()
                    for item in rows:
                        user_list.append(item[0])
                        user_id_list.append(item[1])

                elif experienced_student == 'true':
                    target1 = '1'
                    target2 = '0'
                    target3 = '0'
                    with connections['default'].cursor() as cur:
                        query = '''
                            SELECT distinct(a.email), a.id
                              FROM auth_user a, student_courseenrollment b
                             WHERE     a.id = b.user_id
                        '''
                        if account_type == 'activation':
                            query = query + "AND a.is_active = 1"
                            db_account_type = 'E'
                        elif account_type == 'inactive':
                            query = query + "AND a.is_active = 0"
                            db_account_type = 'I'
                        cur.execute(query)
                        db_account_type = 'A'
                        rows = cur.fetchall()
                    for item in rows:
                        user_list.append(item[0])
                        user_id_list.append(item[1])

            # 보내는 타입이 '수동입력'일 때 로직
            elif subject_flag == 'world':
                notauto = request.POST.get('notauto')
                tmp = notauto.split(',')
                # 유저 목록 구해오는 로직
                for email in tmp:
                    user_list.append(email.strip())

            # 제목, 내용 공통
            title = request.POST.get('title')
            content = request.POST.get('content')

            # ---------- insert data ----------#
            # 보내는 타입이 '수동입력'이 아닐 때 로직
            if subject_flag == 'hello':
                with connections['default'].cursor() as cur:
                    query = '''
                        insert into edxapp.group_email(send_type, account_type, target1, target2, target3, title, contents, regist_id)
                        values('E', '{0}', {1}, {2}, {3}, '{4}', '{5}', {6})
                    '''.format(db_account_type, target1, target2, target3, title, content.replace("'", "''"), user_id)
                    cur.execute(query)
            # 보내는 타입이 '수동입력'일 때 로직
            elif subject_flag == 'world':
                with connections['default'].cursor() as cur:
                    query = '''
                        insert into edxapp.group_email(send_type, account_type, target1, target2, target3, title, contents, regist_id)
                        values('E', 'N', 0, 0, 0, '{0}', '{1}', {2})
                    '''.format(title, content.replace("'", "''"), user_id)
                    cur.execute(query)
            # insert 이후 마지막 글 번호 얻어오기
            with connections['default'].cursor() as cur:
                query = '''
                    SELECT LAST_INSERT_ID();
                '''
                cur.execute(query)
                rows = cur.fetchall()
                row_id = rows[0][0]
            # ---------- insert data ----------#

            # ---------- sending email ----------#
            for n in range(0, len(user_list)):
                # 보내는 타입이 '수동입력'이 아닐 때 로직
                if subject_flag == 'hello':
                    try:
                        # common_send_mail(user, title, content) # 메일 보내는 함수
                        with connections['default'].cursor() as cur:
                            query = '''
                                insert into edxapp.group_email_target(mail_id, receive_id, email, success_yn, regist_id)
                                values({0}, {1}, '{2}', 'Y', {3})
                            '''.format(row_id, user_id_list[n], user_list[n].replace("'", "''"), user_id)
                            print query  # DEBUG
                            cur.execute(query)
                    except BaseException:
                        fail_cnt = fail_cnt + 1
                        with connections['default'].cursor() as cur:
                            query = '''
                                insert into edxapp.group_email_target(mail_id, receive_id, email, success_yn, regist_id)
                                values({0}, {1}, '{2}', 'N', {3})
                            '''.format(row_id, user_id_list[n], user_list[n].replace("'", "''"), user_id)
                            print query  # DEBUG
                            cur.execute(query)
                # 보내는 타입이 '수동입력'일 때 로직
                elif subject_flag == 'world':
                    try:
                        # common_send_mail(user, title, content) # 메일 보내는 함수
                        with connections['default'].cursor() as cur:
                            query = '''
                                insert into edxapp.group_email_target(mail_id, email, success_yn, regist_id)
                                values({0}, '{1}', 'Y', {2})
                            '''.format(row_id, user_list[n].replace("'", "''"), user_id)
                            print query  # DEBUG
                            cur.execute(query)
                    except BaseException:
                        fail_cnt = fail_cnt + 1
                        with connections['default'].cursor() as cur:
                            query = '''
                                insert into edxapp.group_email_target(mail_id, email, success_yn, regist_id)
                                values({0}, '{1}', 'N', {2})
                            '''.format(row_id, user_list[n].replace("'", "''"), user_id)
                            print query  # DEBUG
                            cur.execute(query)

            # making success cnt, fail cnt
            total_user = len(user_list)
            fail_cnt = fail_cnt
            success_cnt = (len(user_list) - fail_cnt)

            # update success cnt, total cnt
            with connections['default'].cursor() as cur:
                query = '''
                    UPDATE edxapp.group_email
                    SET    send_count = {0},
                           success_count = {1}
                    WHERE  mail_id = {2}
                '''.format(total_user, success_cnt, row_id)
                cur.execute(query)
            return JsonResponse({"return":"success"})

    return render(request, 'multiple_email/multiple_email_new.html')

#test
def django_mail(request):
    from django.core.mail import send_mail
    from django.core.mail import EmailMultiAlternatives

    html = ""
    f = open("/Users/ahn/workspace/management/home/templates/multiple_email/frame.html", 'r')
    while True:
        line = f.readline()
        if not line: break
        html += line
    f.close()

    print "--------------------"
    print html
    print "--------------------"

    from_email = 'b930208@gmail.com'
    to_email = []
    to_email.append('yumehahimitu@gmail.com')
    to_email.append('b930208@gmail.com')

    subject = 'CCCC'
    text_content = ''
    html_content = '<b>hello world</b>'

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html, "text/html")

    msg.send()

    return JsonResponse({'foo': 'bar'})

# ---------- 2017.11.03 ahn jin yong ---------- #
