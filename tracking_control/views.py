# -*- coding: utf-8 -*-

from django.shortcuts import render
from management.settings import WEB1_HOST, WEB2_HOST, WEB1_LOG, WEB2_LOG, LOCAL1_DIR, LOCAL2_DIR, CHANGE_DIR, COMPRESS_DIR, HOST_NAME, UPLOAD_DIR, STATIC_URL
import functools
import paramiko
import re
import gzip
import io
import os
import zipfile
import glob
import datetime
import shutil
import json
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder



def log_download(request):
    return render(request, 'trackingLog.html')


def logfile_download(request, date):
    split_str = date.find("/")
    start_date = date[:split_str]
    end_date = date[split_str+1:]

    date_list = []
    cnt = 0

    start = datetime.datetime.strptime(start_date, "%y%m%d")
    end = datetime.datetime.strptime(end_date, "%y%m%d")

    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days+1)]

    for date in date_generated:
        date_list.append(date.strftime("%y%m%d"))

    for searchDate in date_list:
        logFileDownload(searchDate, WEB1_HOST, WEB1_LOG, LOCAL1_DIR)
        logFileDownload(searchDate, WEB2_HOST, WEB2_LOG, LOCAL2_DIR)
        cnt += 1
    cnt = len(date_list)
    if cnt >= len(date_list):
        log_compress('999999', None)
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
def logFileDownload(searchDate, host, log_dir, local_dir):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(AllowAnythingPolicy())
    client.connect(host, username=HOST_NAME)

    sftp = client.open_sftp()
    sftp.chdir(log_dir)

    fileList = sftp.listdir()
    searchName = []

    web_server = 1

    # 원래는 host로 하여야하나 테스트 위해서 log_dir로 조건 줌
    if log_dir == WEB1_LOG:
        web_server = 1
    elif log_dir == WEB2_LOG:
        web_server = 2

    sDate = re.compile(r'20(\d{6})')

    for i in sorted(fileList):
        if re.search(sDate, i) != None:
            splitDate = i.find('-20')

            sFile = str(i)
            searchFile = sFile[splitDate+3:splitDate+9]

            if searchFile == searchDate:
                searchName.append(i)
                callback_for_filename = functools.partial(my_callback, i)
                sftp.get(i, local_dir+sFile)
                sftp.get(i, local_dir+sFile, callback=callback_for_filename)

    log_change(local_dir, CHANGE_DIR, searchDate, web_server)

    client.close()



def log_change(path_dir, change_local, searchDate, web_server):
    file_list = os.listdir(path_dir)

    file_pattern = re.compile(r'.gz$')

    for log in file_list:
        if re.search(file_pattern, log) != None:
            readFile = gzip.open(path_dir + log, 'rb')

            if web_server == 1:
                outfilename = log[:-3] + "_1.gz"
            elif web_server == 2:
                outfilename = log[:-3] + "_2.gz"

            output = gzip.open(change_local + outfilename, 'wb')
            f = io.BufferedReader(readFile)
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
                        joinName_index = text.find('\"username\\\":')
                        joinName_idx = text[joinName_index + 16:]
                        joinName_change = joinName_idx.find(',')
                        joinName_pattern = joinName_idx[0:joinName_change - 3]
                        r6 = re.compile(joinName_pattern)

                        uniName_index = text.find('\"name\\\":')
                        uniName_idx = text[uniName_index + 11:]
                        uniName_change = uniName_idx.find(',')
                        uniName_pattern = uniName_idx[:uniName_change - 1]

                        pwd2_idx = text[pwd2_index + 17:]
                        pwd2_change = pwd2_idx.find(',')
                        pwd2_pattern = pwd2_idx[0:pwd2_change - 3]

                        if pwd2_pattern != "":
                            data = data.replace(pwd2_pattern, '********')
                        data = re.sub(r6, '******', data, count=1)
                        data = data.replace(uniName_pattern, "\"******\\\"")

                    output.write(data)

            f.close()

            output.close()
            readFile.close()

    oldLog_remove(path_dir, 1)
    if web_server == 2:
        log_compress(searchDate, change_local)



def log_compress(search_date, dir_path):
    if search_date != '999999':
        zipName = search_date + "_tracking_log.zip"
        fantasy_zip = zipfile.ZipFile('/Users/kotech/workspace/scpTest/zip_tracking/'+zipName, 'w')

        for folder, subfolders, files in os.walk(dir_path):

            for file in files:
                if file.endswith('.gz'):
                    fantasy_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder, file), dir_path), compress_type = zipfile.ZIP_DEFLATED)

        fantasy_zip.close()
        oldLog_remove(dir_path, 1)
    else:
        shutil.make_archive(UPLOAD_DIR+'tracking_log', 'zip', '/Users/kotech/workspace/scpTest/zip_tracking/')
        oldLog_remove('/Users/kotech/workspace/scpTest/zip_tracking/', 2)




# fileType 1: .gz 2: .zip 3: tracking_log.zip(최종 파일)
def oldLog_remove(dir_path, fileType):
    if fileType == 1:
        rm_fileList = glob.glob(dir_path+'*.gz')
    elif fileType == 2:
        rm_fileList = glob.glob(dir_path+'*.zip')
    elif fileType == 3:
        rm_fileList = glob.glob(dir_path)
    for rm_file in rm_fileList:
        try:
            os.remove(rm_file)
        except:
            print "remove error"

@csrf_exempt
def data_insert(request):
    if request.method == 'POST':
        prodate = request.POST.get('processingdate')
        client = request.POST.get('client')
        startDate = request.POST.get('startDate')
        endDate = request.POST.get('endDate')

        query = """
            INSERT INTO edxapp.trackinglog_download(processingdate,
                                        client,
                                        startDate,
                                        endDate)
             VALUES (%s,
                     '%s',
                     %s,
                     %s);
        """ % (prodate, client, startDate, endDate)

        cur = connection.cursor()
        cur.execute(query)
        cur.close()
        data = json.dumps({"status": "success"})

        return HttpResponse(data, 'applications/json')

def log_board(request):
    log_list = []
    if request.is_ajax():
        logData = {}
        if request.GET['method'] == 'logDown_list':
            cur = connection.cursor()
            query = """
                 SELECT no,
                       DATE_ADD((DATE_FORMAT(processingdate, "%Y-%c-%d %r")), INTERVAL +9 HOUR ),
                       client,
                       DATE_FORMAT(startdate, "%Y/%c/%d"),
                       DATE_FORMAT(enddate, "%Y/%c/%d")
                  FROM edxapp.trackinglog_download;
            """

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

            log_list.append(log_value)
            idx += 1

        aaData = json.dumps(list(log_list), cls=DjangoJSONEncoder, ensure_ascii=False)

    return HttpResponse(aaData, 'application/json')
