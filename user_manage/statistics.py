# -*- coding: utf-8 -*-
from django.db import connection
from openpyxl import load_workbook
import statistics_query
from django.template import Context
from django.http import HttpResponse
from django.template.loader import get_template
import os

def statistics_excel(request, date):

    # date = date.replace("-","")
    #
    # print statistics_query.course_age(date)

    # print date
    # print date

    # print '----------------------------'
    # #print '/excel_select/'.GET.get('datepicker1', '')
    # print "'"+ date +"'"
    # print  '''"''' + date + '''"'''
    # print '----------------------------'
    #
    #
    # print statistics_query.edu_total(date)

    user_join_new = statistics_query.user_join_new(date)
    user_join_total = statistics_query.user_join_total(date)
    course_count_distinct = statistics_query.course_count_distinct(date)
    course_count_new = statistics_query.course_count_new(date)
    course_count_total = statistics_query.course_count_total(date)
    edu_new = statistics_query.edu_new(date)
    edu_total = statistics_query.edu_total(date)
    age_new = statistics_query.age_new(date)
    age_total = statistics_query.age_total(date)
    age_edu = statistics_query.age_edu(date)
    course_user = statistics_query.course_user(date)
    course_user_total =statistics_query.course_user_total(date)
    course_age = statistics_query.course_age(date)
    course_edu = statistics_query.course_edu(date)

    saveName = 'K-Mooc'+date+'.xlsx'
    savePath = '/home/project/management/static/excel/' + saveName

    if os.path.isfile(savePath):
        pass

    else:
        wb = load_workbook('/home/project/management/static/excel/basic.xlsx')
        ws1 = wb['user_count']
        ws2 = wb['course_count']
        ws3 = wb['course_age']
        ws4 = wb['course_edu']
        ws5 = wb['course_count_total']

        #가입현황

        ws1['B4'] = user_join_new
        ws1['C4'] = user_join_total
        ws1['D4'] = course_count_distinct
        ws1['E4'] = course_count_new
        ws1['F4'] = course_count_total

        #학력구분

        sort = [(9,0),(10,1),(11,2),(12,3),(13,4),
                (14,5),(15,6),(16,7),(17,8)]

        for (number, number1) in sort:
            ws1['C' + str(number)] = edu_new[number1][0]
            ws1['D' + str(number)] = edu_new[number1][1]

        for (number, number1) in sort:
            ws1['F' + str(number)] = edu_total[number1][0]
            ws1['G' + str(number)] = edu_total[number1][1]

        #연령구분

        sort = [(23,0),(24,1),(25,2),(26,3),(27,4),(28,5)]

        for (number, number1) in sort:
            ws1['C' + str(number)] = age_new[number1][0]
            ws1['D' + str(number)] = age_new[number1][1]

        for (number, number1) in sort:
            ws1['F' + str(number)] = age_total[number1][0]
            ws1['G' + str(number)] = age_total[number1][1]

        #연령학력

        sort = [(34,0),(35,1),(36,2),(37,3),(38,4),(39,5)]

        for (number, number1) in sort:
            ws1['C' + str(number)] = age_edu[number1][0]
            ws1['D' + str(number)] = age_edu[number1][1]
            ws1['E' + str(number)] = age_edu[number1][2]
            ws1['F' + str(number)] = age_edu[number1][3]
            ws1['G' + str(number)] = age_edu[number1][4]
            ws1['H' + str(number)] = age_edu[number1][5]
            ws1['I' + str(number)] = age_edu[number1][6]
            ws1['J' + str(number)] = age_edu[number1][7]
            ws1['K' + str(number)] = age_edu[number1][8]

        #코스별 수강자

        sort = [(3,0),(4,1),(5,2),(6,3),(7,4),(8,5),(9,6),(10,7),
                (11,8),(12,9),(13,10),(14,11),(15,12),(16,13),
                (17,14),(18,15),(19,16),(20,17),(21,18),(22,19),
                (23,20),(24,21),(25,22),(26,23),(27,24),(28,25),(29,26)]

        for (number, number1) in sort:
            ws2['D' + str(number)] = course_user[number1][0]

        #코스별 수강자 누적

        sort = [(3,0),(4,1),(5,2),(6,3),(7,4),(8,5),(9,6),(10,7),
                (11,8),(12,9),(13,10),(14,11),(15,12),(16,13),
                (17,14),(18,15),(19,16),(20,17),(21,18),(22,19),
                (23,20),(24,21),(25,22),(26,23),(27,24),(28,25),(29,26)]

        for (number, number1) in sort:
            ws5['D' + str(number)] = course_user_total[number1][0]

        #코스별 연령

        sort = [(4,0),(5,1),(6,2),(7,3),(8,4),(9,5),(10,6),(11,7),
                (12,8),(13,9),(14,10),(15,11),(16,12),(17,13),(18,14),
                (19,15),(20,16),(21,17),(22,18),(23,19),(24,20),
                (25,21),(26,22),(27,23),(28,24),(29,25),(30,26)]

        for (number, number1) in sort:
            ws3['B' + str(number)] = course_age[number1][0]
            ws3['C' + str(number)] = course_age[number1][1]
            ws3['D' + str(number)] = course_age[number1][2]
            ws3['E' + str(number)] = course_age[number1][3]
            ws3['F' + str(number)] = course_age[number1][4]
            ws3['G' + str(number)] = course_age[number1][5]

        #코스별 학력

        sort = [(4,0),(5,1),(6,2),(7,3),(8,4),(9,5),(10,6),(11,7),
                (12,8),(13,9),(14,10),(15,11),(16,12),(17,13),
                (18,14),(19,15),(20,16),(21,17),(22,18),(23,19),(24,20),
                (25,21),(26,22),(27,23),(28,24),(29,25),(30,26)]

        for (number, number1) in sort:
            ws4['B' + str(number)] = course_edu[number1][0]
            ws4['C' + str(number)] = course_edu[number1][1]
            ws4['D' + str(number)] = course_edu[number1][2]
            ws4['E' + str(number)] = course_edu[number1][3]
            ws4['F' + str(number)] = course_edu[number1][4]
            ws4['G' + str(number)] = course_edu[number1][5]
            ws4['H' + str(number)] = course_edu[number1][6]
            ws4['I' + str(number)] = course_edu[number1][7]
            ws4['J' + str(number)] = course_edu[number1][8]

        wb.save(savePath)

    # # template = get_template('excel_test.html')
    # context = Context({'time': time,
    #                    'user_join_new': user_join_new,
    #                    'user_join_total': user_join_total,
    #                    'course_count_distinct': course_count_distinct,
    #                    'course_count_new': course_count_new,
    #                    'course_count_total': course_count_total,
    #                    'edu_new': edu_new,
    #                    'edu_total': edu_total,
    #                    'age_new': age_new,
    #                    'age_total': age_total,
    #                    'age_edu': age_edu,
    #                    'course_user': course_user,
    #                    'course_age': course_age,
    #                    'course_edu': course_edu,
    #                     })
    #
    # print 'a'
    #
    # downloader = fileDownloader.DownloadFile('http://mme.kmoocs.kr/vod/pop-up.htm')
    # downloader.download()
    #
    # print 'a'

    # return response

    return HttpResponse('/manage/static/excel/' + saveName, content_type='application/vnd.ms-excel')


