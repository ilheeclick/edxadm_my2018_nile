# -*- coding: utf-8 -*-
from django.db import connection
from django.shortcuts import render
from django.template import Context
from django.http import HttpResponse
from django.template.loader import get_template
import query
from django.views.generic.base import TemplateView
import os
BASE_DIR2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main_query(id):

    html = ""

    cur = connection.cursor()
    cur.execute(id)
    row = cur.fetchall()

    for rows in row:
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

    user_today = main_query_one(query.user_count_today)

    user_total = main_query_one(query.user_count_total)

    course_today = main_query_one(query.course_count_today)

    course_total = main_query_one(query.course_count_total)

    time = main_query_one(query.now_day)

    time2 = main_query_one(query.now_time)

    template = get_template('manage_main.html')
    context = Context({'user_today' : user_today,
                       'user_total' : user_total,
                       'course_today' : course_today,
                       'course_total' : course_total,
                       'time': time,
                       'time2': time2,
                        })

    return HttpResponse(template.render(context))

"""
def user_manage_show(request):

    #rint  os.path.join(BASE_DIR2, 'static/css')

    time = main_query_one(query.now_day)

    temlplate = get_template('manage_main.html')

    context = Context ({'time' : time})

    return HttpResponse(temlplate.render(context))
"""

