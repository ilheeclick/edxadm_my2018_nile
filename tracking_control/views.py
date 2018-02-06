# -*- coding: utf-8 -*-

from django.shortcuts import render
from management.settings import WEB1_HOST, WEB2_HOST, WEB1_LOG, WEB2_LOG, LOCAL1_DIR, LOCAL2_DIR, CHANGE_DIR, USER_NAME, LOGZIP_DIR, LOG_COMPLETE_DIR
import functools
import paramiko
import re
import gzip
import io
import glob
import os
import zipfile
import datetime
import shutil
import json
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required


@login_required
def log_download(request):
    return render(request, 'trackingLog.html')


def logfile_check(request):
    check = os.path.isfile(LOGZIP_DIR+'tracking_log.zip')
    print 'check log_complete  ------------>>>> ', check
    if check is True:
        first_size = logfile_size(LOGZIP_DIR+'tracking_log.zip')
        return JsonResponse({'check': 'true', 'first_size': first_size})
    else:
        return JsonResponse({'filename': '', 'check': 'false'})


def logfile_size(file_path):
    file_size = os.path.getsize(file_path)
    print 'compress size ======== ', file_size
    return file_size


def second_check(request):
    second_size = logfile_size(LOGZIP_DIR+'tracking_log.zip')
    return JsonResponse({'filename': 'tracking_log.zip', 'second_size': second_size})


def makedir(sftp):
    dir_list = [LOCAL1_DIR, LOCAL2_DIR, CHANGE_DIR, LOGZIP_DIR, LOG_COMPLETE_DIR]
    for dir in dir_list:
        print 'make dir   ', dir
        mkdir_p(sftp, dir)
        # if not os.path.exists(dir):
        #     os.mkdir(dir)


def mkdir_p(sftp, remote_directory):
    """Change to this directory, recursively making new folders if needed.
    Returns True if any folders were created."""
    if remote_directory == '/':
        # absolute path so change directory to root
        sftp.chdir('/')
        return
    if remote_directory == '':
        # top-level relative directory must exist
        return
    try:
        print 'mkdir_p -> try s ---- '
        sftp.chdir(remote_directory)  # sub-directory exists
    except IOError:
        print 'mkdir_p -> except s -------'
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        mkdir_p(sftp, dirname)  # make parent directories
        sftp.mkdir(basename)  # sub-directory missing, so created it
        sftp.chdir(basename)
        return True


def logfile_download(request, date):
    global logfile_check
    logfile_check = 1
    split_str = date.find("/")
    start_date = date[:split_str]
    end_date = date[split_str+1:]

    date_list = []
    cnt = 0

    start = datetime.datetime.strptime(start_date, "%Y%m%d")
    end = datetime.datetime.strptime(end_date, "%Y%m%d")

    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days+1)]

    for date in date_generated:
        date_list.append(date.strftime("%Y%m%d"))

    for searchDate in date_list:
        logFileDownload(searchDate, WEB1_HOST, WEB1_LOG, LOCAL1_DIR, 1)
        logFileDownload(searchDate, WEB2_HOST, WEB2_LOG, LOCAL2_DIR, 2)
        # ------------------------------- 실제 서버 반영시 하단 내용으로 반영
        # logFileDownload(searchDate, WEB1_HOST, WEB1_LOG, LOCAL1_DIR)
        # logFileDownload(searchDate, WEB2_HOST, WEB2_LOG, LOCAL2_DIR)
        # -------------------------------------------------------
        cnt += 1
        print 'cnt ====== ', cnt
    # cnt = len(date_list)

    if cnt >= len(date_list):
        logfile_check = log_compress('999999', None)
        if logfile_check == 1:
            return JsonResponse({'filename': 'empty'})
        else:
            zip_file = 'tracking_log.zip'
            return JsonResponse({'filename': zip_file})
    raise Http404


class AllowAnythingPolicy(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return


def my_callback(filename, bytes_so_far, bytes_total):
    print 'Transfer of %r is at %d/%d bytes (%.1f%%)' % (
        filename, bytes_so_far, bytes_total, 100. * bytes_so_far / bytes_total)


# web_server는 나중에 실제 반영시에 아이피로 조건을 줘서 처리 예정
def logFileDownload(search_date, host, log_dir, local_dir, web_server):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(AllowAnythingPolicy())
    client.connect(host, username=USER_NAME, password='?kmooc')

    sftp = client.open_sftp()

    # 폴더가 없으면 생성
    makedir(sftp)

    sftp.chdir(log_dir)

    file_list = sftp.listdir()
    search_name = []
    # ---------------------------------------------------
    # web_server = 1

    # 원래는 host로 하여야하나 테스트 위해서 log_dir로 조건 줌
    # if host == WEB1_HOST:
    #     web_server = 1
    # elif host == WEB2_HOST:
    #     web_server = 2
    # ----------------------------------------------------
    date_compile = re.compile(r'20(\d{6})')
    for i in sorted(file_list):
        if re.search(date_compile, i) is not None:
            split_date = i.find('-20')

            sfile = str(i)
            searchfile = sfile[split_date+1:split_date+9]
            if searchfile == search_date:
                search_name.append(i)
                callback_for_filename = functools.partial(my_callback, i)
                # sftp.get(i, local_dir+sfile)
                sftp.get(i, local_dir+sfile, callback=callback_for_filename)
    log_change(local_dir, CHANGE_DIR, search_date, web_server)
    client.close()


def log_change(path_dir, change_local, search_date, web_server):
    print 'log_change s ---------------------', web_server
    file_list = os.listdir(path_dir)

    file_pattern = re.compile(r'.gz$')

    for log in file_list:
        if re.search(file_pattern, log) is not None:
            read_file = gzip.open(path_dir + log, 'rb')

            if web_server == 1:
                outfilename = log[:-3] + "_1.gz"
            elif web_server == 2:
                outfilename = log[:-3] + "_2.gz"

            output = gzip.open(change_local + outfilename, 'wb')
            f = io.BufferedReader(read_file)
            for text in f.readlines():
                username_index = text.find('\"username\":')
                ip_index = text.find('\"ip\":')
                id_index = text.find('\"user_id\":')
                email_index = text.find('\"email\\\":')
                pwd2_index = text.find('\"password2\\\":')

                if username_index != -1:
                    name_idx = text[username_index + 12:]
                    ip_idx = text[ip_index + 6:]
                    id_idx = text[id_index:]
                    email_idx = text[email_index + 13:]

                    username_change = name_idx.find(',')
                    ip_change = ip_idx.find(',')
                    id_change = id_idx.find(',')
                    email_change = email_idx.find(',')

                    name_pattern = name_idx[0:username_change]
                    ip_pattern = ip_idx[0:ip_change]
                    id_pattern = id_idx[0:id_change]
                    email_pattern = email_idx[0:email_change - 2]

                    r1 = re.compile(name_pattern)
                    r2 = re.compile(ip_pattern)
                    r3 = re.compile(id_pattern)

                    data = text

                    if name_pattern != '""':
                        data = re.sub(r1, '"******"', text, count=1)

                    if ip_pattern != '""':
                        data = re.sub(r2, '"***.***.***.***"', data, count=1)

                    if id_pattern != '"user_id": null':
                        data = re.sub(r3, '"user_id": ******', data, count=1)

                    if email_index != -1 and email_pattern != '\\':
                        if email_idx[email_change - 1] == "}":
                            data = data.replace(email_pattern, '******@****.**\\\"')
                        data = data.replace(email_pattern, '******@****.**\\')

                    # 회원 가입시에 들어가는 개인정보를 처리

                    if pwd2_index != -1:
                        joinname_index = text.find('\"username\\\":')
                        joinname_idx = text[joinname_index + 16:]
                        joinname_change = joinname_idx.find(',')
                        joinname_pattern = joinname_idx[0:joinname_change - 3]
                        r6 = re.compile(joinname_pattern)

                        uniname_index = text.find('\"name\\\":')
                        uniname_idx = text[uniname_index + 11:]
                        uniname_change = uniname_idx.find(',')
                        uniname_pattern = uniname_idx[:uniname_change - 1]

                        pwd2_idx = text[pwd2_index + 17:]
                        pwd2_change = pwd2_idx.find(',')
                        pwd2_pattern = pwd2_idx[0:pwd2_change - 3]

                        if pwd2_pattern != "":
                            data = data.replace(pwd2_pattern, '********')
                        data = re.sub(r6, '******', data, count=1)
                        data = data.replace(uniname_pattern, "\"******\\\"")

                    output.write(data)

            f.close()

            output.close()
            read_file.close()

    oldLog_remove(path_dir, 1)
    if web_server == 2:
        file_cnt = 0
        chdir_list = os.listdir(change_local)
        for filename in chdir_list:
            full_filename = os.path.join(change_local, filename)
            ext = os.path.splitext(full_filename)[-1]
            if ext == '.gz':
                file_cnt += 1
        if file_cnt != 0:
            log_compress(search_date, change_local)


def log_compress(search_date, dir_path):
    logfile_cnt = 0
    if search_date != '-1' and search_date != '999999':
        zipname = search_date + "_tracking_log.zip"
        fantasy_zip = zipfile.ZipFile(LOG_COMPLETE_DIR+zipname, 'w')

        for folder, subfolders, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.gz'):
                    fantasy_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder, file), dir_path),
                                      compress_type=zipfile.ZIP_DEFLATED)

        fantasy_zip.close()
        oldLog_remove(dir_path, 1)
    elif search_date == '999999':
        file_cnt = 0
        chdir_list = os.listdir(LOG_COMPLETE_DIR)
        for filename in chdir_list:
            full_filename = os.path.join(LOG_COMPLETE_DIR, filename)
            ext = os.path.splitext(full_filename)[-1]
            if ext == '.zip':
                file_cnt += 1
        if file_cnt == 0:
            logfile_cnt = 1
        else:
            shutil.make_archive(LOGZIP_DIR+'tracking_log', 'zip', LOG_COMPLETE_DIR)
        oldLog_remove(LOG_COMPLETE_DIR, 2)

    return logfile_cnt


# fileType 1: .gz 2: .zip 3: tracking_log.zip(최종 파일)
def oldLog_remove(dir_path, filetype):
    if filetype == 1:
        rm_file_list = glob.glob(dir_path+'*.gz')
    elif filetype == 2:
        rm_file_list = glob.glob(dir_path+'*.zip')
    elif filetype == 3:
        rm_file_list = glob.glob(dir_path)
    for rm_file in rm_file_list:
        try:
            os.remove(rm_file)
        except:
            print "remove error"


@csrf_exempt
def data_insert(request):
    if request.method == 'POST':
        print 'data insert s ==================='
        client = request.POST.get('client')
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        log_note = request.POST.get('log_note')

        query = """
            INSERT INTO edxapp.trackinglog_download(processingdate,
                                        client,
                                        startDate,
                                        endDate,
                                        note)
             VALUES (now(),
                     {client},
                     '{startDate}',
                     '{endDate}',
                     '{log_note}'
                     );
        """ .format(client=client, startDate=startdate, endDate=enddate, log_note=log_note)

        print 'query ===========================   ', query

        cur = connection.cursor()
        cur.execute(query)
        cur.close()
        data = json.dumps({"status": "success"})

        return HttpResponse(data, 'applications/json')


def log_board(request):
    print 'log_board s -------------------'
    log_list = []
    if request.is_ajax():

        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        menu_select = request.POST.get('menu_select')

        cur = connection.cursor()
        query = """
            SELECT no,
                   date_format(processingdate,
                               '%Y-%m-%d %H:%i:%s'),
                   username,
                   DATE_FORMAT(startdate, "%Y/%m/%d"),
                   DATE_FORMAT(enddate, "%Y/%m/%d"),
                   a.note
              FROM edxapp.trackinglog_download a
                   JOIN edxapp.auth_user b ON a.client = b.id
        """

        if startdate != "" and enddate != "" and menu_select == '2':
            query += """
                WHERE DATE_FORMAT(processingdate, '%Y%m%d') >= '{start_date}'
                    AND DATE_FORMAT(processingdate, '%Y%m%d') <= '{end_date}'
            """.format(start_date=startdate, end_date=enddate)

        print 'query ------------- ', query

        cur.execute(query)

        row = cur.fetchall()
        cur.close()

        idx = 1

        for log in row:
            log_value = []

            log_value.append(log[0])
            log_value.append(log[1])
            log_value.append(log[2])
            log_value.append(log[3])
            log_value.append(log[4])
            log_value.append(log[5])

            log_list.append(log_value)
            idx += 1

        aaData = json.dumps(list(log_list), cls=DjangoJSONEncoder, ensure_ascii=False)

    return HttpResponse(aaData, 'application/json')
