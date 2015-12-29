# -*- coding: utf-8 -*-
from django.db import connection
from django.shortcuts import render
from django.template import Context
from django.http import HttpResponse
from django.template.loader import get_template
import query
from django.views.generic.base import TemplateView
import os

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

    return HttpResponse(template.render())