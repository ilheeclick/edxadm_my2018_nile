# -*- coding: utf-8 -*-
from django.db import connection
from openpyxl import load_workbook
from django.template import Context
from django.http import HttpResponse
from django.template.loader import get_template
from pymongo import MongoClient
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font
from operator import itemgetter
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.conf import settings
from django.db import connection

import os
import datetime
import MySQLdb as mdb
import statistics_query
import json

@csrf_protect
def notice_reg(request):

    if 'seq' not in request.POST:
        title = request.POST['title']
        link = request.POST['link']
        sDate = request.POST['sDate']
        sHH = request.POST['sHH']
        sMI = request.POST['sMI']
        eDate = request.POST['eDate']
        eHH = request.POST['eHH']
        eMI = request.POST['eMI']

        cur = connection.cursor()
        query = " INSERT INTO edxapp.tb_notice(title, link, sdate, stime, edate, etime, useyn) "
        query +=" VALUES ('"+title+"', '"+link+"', '"+sDate+"', concat('"+sHH+"','"+sMI+"'), '"+eDate+"', concat('"+eHH+"','"+eMI+"'), 'Y') "
        cur.execute(query)
        rowid = cur.lastrowid
        cur.close()
        return HttpResponse(rowid)
    else:
        return HttpResponse("fail")

def dictfetchall(cursor):
    """Returns all rows from a cursor as a list of dicts"""
    desc = cursor.description
    return [dict(itertools.izip([col[0] for col in desc], row))
            for row in cursor.fetchall()]

def notice_list(request):
    pageNo = request.POST['pageNo']
    pageSize = request.POST['pageSize']

    print 'pageNo', pageNo
    print 'pageSize', pageSize
    print '(pageNo * pageSize)', (int(pageNo) * int(pageSize))

    cur = connection.cursor()
    query  = " select seq, title, link, sdate, substring(stime,1,2) sHH, substring(stime,3,2) sMI, edate, substring(etime,1,2) eHH, substring(etime,3,2) eMI, (select count(*) from tb_notice where useyn = 'Y') cnt "
    query += " from tb_notice where useyn = 'Y' order by seq desc limit "+str(int(pageNo) * int(pageSize))+", "+str(pageSize)+" "
    cur.execute(query)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    result = []
    for row in rows:
        row = dict(zip(columns, row))
        result.append(row)
    return HttpResponse(json.dumps(result))

def notice_mod(request):

    if 'seq' in request.POST:
        seq = request.POST['seq']
        title = request.POST['title']
        link = request.POST['link']
        sDate = request.POST['sDate']
        sHH = request.POST['sHH']
        sMI = request.POST['sMI']
        eDate = request.POST['eDate']
        eHH = request.POST['eHH']
        eMI = request.POST['eMI']

        cur = connection.cursor()
        query = " UPDATE edxapp.tb_notice               ";
        query += " SET                                  ";
        query += "   title = '"+title+"'                ";
        query += "   ,link = '"+link+"'                 ";
        query += "   ,sdate = '"+sDate+"'               ";
        query += "   ,stime = concat('"+sHH+"','"+sMI+"')   ";
        query += "   ,edate = '"+eDate+"'               ";
        query += "   ,etime = concat('"+eHH+"','"+eMI+"')   ";
        query += " WHERE seq = "+seq+"                  ";

        print "query = ", query
        cur.execute(query)
        rowid = cur.lastrowid
        cur.close()
        return HttpResponse(rowid)
    else:
        return HttpResponse("fail")

def notice_del(request):

    if 'seq' in request.POST:
        seq = request.POST['seq']
        cur = connection.cursor()
        query = " update edxapp.tb_notice set useyn = 'N' where seq = " + seq
        print 'query = ', query
        cur.execute(query)
        rowid = cur.lastrowid
        cur.close()
        return HttpResponse(rowid)
    else:
        return HttpResponse("fail")
