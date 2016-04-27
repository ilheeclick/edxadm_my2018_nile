# -*- coding: utf-8 -*-
from django.db import connection
from django.shortcuts import render
from django.template import Context
from django.http import HttpResponse
from django.template.loader import get_template
import query
from django.views.generic.base import TemplateView
import os
import statistics_query
from pymongo import MongoClient
from operator import itemgetter
from django.core.context_processors import csrf

def main_query(id):

    html = ""

    row = 0
    col = 0

    cur = connection.cursor()
    cur.execute(id)
    data = cur.fetchall()

    for rows in data:
        html += '<tr align="center">'
        for cols in rows:
            html += '<td><font size ="2">' + str(cols) + '</font></td>'
        html += '</tr>'

    cur.close()

    return str(html)


def main_query_one(id):

    cur = connection.cursor()
    cur.execute(id)
    row = cur.fetchone()[0]

    cur.close()

    return row

def user_manage(request):

    print 'user_manage called ******************'


    lolz = 10

    user_today = main_query_one(query.user_count_today)

    user_total = main_query_one(query.user_count_total)

    course_today = main_query_one(query.course_count_today)

    course_total = main_query_one(query.course_count_total)

    course_distinct = main_query_one(query.course_count_distinct)

    course_count = main_query_one(query.course_count)

    time = main_query_one(query.now_day)

    time2 = main_query_one(query.now_time)

    template = get_template('index.html')




    context = Context({'user_today' : user_today,
                       'user_total' : user_total,
                       'course_today' : course_today,
                       'course_total' : course_total,
                       'course_distinct' : course_distinct,
                       'course_count' : course_count,
                       'time': time,
                       'time2': time2,
                       'lolz': lolz,
                        })

    return HttpResponse(template.render(context))

def excel_manage(request):

    template = get_template('excel_test.html')

    # add certificate option
    pb = ''
    ov = ''
    dn = ''
    courseId = ''
    courseName = ''
    courseInfo = {}

    client = MongoClient('192.168.1.113', 27017)
    db = client.edxapp

    course_ids_cert = statistics_query.course_ids_cert()

    print '[',course_ids_cert,']'

    for c in course_ids_cert:
        cid_org = str(c[0])
        courseId = cid_org

        # cid = cid.replace('course-v1:', '')
        # cid = cid.replace('+', '.')

        # print '1 >>', cid_org

        cid = cid_org.split('+')[1]
        term = cid_org.split('+')[2]

        # print 'courseId ====> ', courseId, cid
        # cursor = db.modulestore.active_versions.find({'search_targets.wiki_slug':cid})
        cursor = db.modulestore.active_versions.find({'course':cid})

        pb = ''

        # if cursor:
        #     print 'cursor exitst'
        # else:
        #     print 'cursor not exists'

        for document in cursor:
            # print '* get published-branch'
            pb = document.get('versions').get('published-branch')
            if pb:
                # print 'pb = ', pb
                break
        cursor.close()

        if pb:
            cursor = db.modulestore.structures.find({'_id':pb})
            ov = ''
            for document in cursor:
                ov = document.get('original_version')

                # if ov is not None:
                #     print 'cid = ',cid, ' ov = ', ov
                # else:
                #     print 'ov is none'

            cursor.close()

            cursor = db.modulestore.structures.find({'_id':ov})

            for document in cursor:
                blocks = document.get('blocks')
                # print 'size = ', len(blocks)
                for block in blocks:
                    fields = block.get('fields')

                    courseName = ''
                    for field in fields:
                        dn = fields['display_name']
                        courseName = dn
                        # print '------------------------------------'
                        # print courseId, ':', courseName
                        # print '------------------------------------'
                        courseInfo[courseId] = courseName + ' : ' + term
                        break
                    break
            cursor.close()
            # print '===================================================================================='

    context = {
        'courseInfo': sorted(courseInfo.items(), key=itemgetter(1)),
    }

    context.update(csrf(request))

    return HttpResponse(template.render(context))
