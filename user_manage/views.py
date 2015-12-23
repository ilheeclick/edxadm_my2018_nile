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


"""

def test_query(id):

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


    return data

def test_excel():

    time = main_query_one(query.excel_now_day)

    user_today = main_query_one(query.user_count_today)

    user_total = main_query_one(query.user_count_total)

    workbook = xlsxwriter.Workbook('/work1/statistics_excel/' + time + '.xlsx')
    worksheet1 = workbook.add_worksheet()

    format1 =workbook.add_format({'border' : 1, 'align': 'center'})

    worksheet1.write('B2:C2', '1', format1)
    worksheet1.write('B3', '2', format1)
    worksheet1.write('C3', '3', format1)
    worksheet1.write('B4', user_today, format1)
    worksheet1.write('C4', user_total, format1)

    workbook.close()

def test(requset):

    excel = test_excel()

    test = test_query(query.test)

    template = get_template('excel_test.html')

    context = Context({'test' : test,
                       'excel' : excel})

    return HttpResponse(template.render(context))


time = main_query_one(query.now_day)

workbook = xlsxwriter.Workbook('/work1/share_file/' + time + '.xlsx')
worksheet = workbook.add_worksheet()

expenses = (
    ['Rent', 1000],
    ['Gas',   100],
    ['Food',  300],
    ['Gym',    50],
)

# Start from the first cell. Rows and columns are zero indexed.
row = 0
col = 0

# Iterate over the data and write it out row by row.
for item, cost in (expenses):

    worksheet.write(row, col,     item)
    worksheet.write(row, col + 1, cost)
    row += 1


# Write a total using a formula.
worksheet.write(row, 0, 'Total')
worksheet.write(row, 1, '=SUM(B1:B4)')

workbook.close()


def user_manage_show(request):

    print  os.path.join(BASE_DIR2, 'static/css')

    time = main_query_one(query.now_day)

    temlplate = get_template('manage_main.html')

    context = Context ({'time' : time})

    return HttpResponse(temlplate.render(context))


workbook = xlsxwriter.Workbook('/work1/statistics_excel/' + time + '.xlsx')
worksheet1 = workbook.add_worksheet()


workbook.close()
"""