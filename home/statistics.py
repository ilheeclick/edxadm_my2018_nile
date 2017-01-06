# -*- coding: utf-8 -*-
from django.db import connection
from openpyxl import load_workbook
import statistics_query
from django.template import Context
from django.http import HttpResponse
from django.template.loader import get_template
from pymongo import MongoClient
# from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font, Style
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font
import os
from operator import itemgetter
import datetime
from management.settings import EXCEL_PATH, dic_univ, database_id, debug
from openpyxl.styles import Alignment
from time import gmtime, strftime
from bson.objectid import ObjectId
import logging
import logging.handlers


# # 로거 인스턴스를 만든다
# logger = logging.getLogger('statistics log')
#
# # 포매터를 만든다
# fomatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
#
# # 스트림과 파일로 로그를 출력하는 핸들러를 각각 만든다.
# fileHandler = logging.FileHandler('./statistics.log')
# streamHandler = logging.StreamHandler()
#
# # 각 핸들러에 포매터를 지정한다.
# fileHandler.setFormatter(fomatter)
# streamHandler.setFormatter(fomatter)
#
# # 로거 인스턴스에 스트림 핸들러와 파일핸들러를 붙인다.
# logger.addHandler(fileHandler)
# logger.addHandler(streamHandler)
#
# if debug:
#     logger.setLevel(logging.DEBUG)


# 일일통계
def statistics_excel(request, date):

    logger.info("statistics_excel START")

    # Get course name
    course_ids_all = statistics_query.course_ids_all()

    client = MongoClient(database_id, 27017)
    db = client.edxapp
    course_orgs = {}
    course_names = {}
    course_creates = {}
    course_starts = {}
    course_ends = {}
    course_enroll_starts = {}
    course_enroll_ends = {}

    for c in course_ids_all:
        cid = str(c[0])
        course_id = cid
        cid = course_id.split('+')[1]
        run = course_id.split('+')[2]

        # db.modulestore.active_versions --------------------------------------
        cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
        pb = cursor.get('versions').get('published-branch')
        # course_orgs
        course_orgs[course_id] = cursor.get('org')
        course_creates[course_id] = cursor.get('edited_on')
        # --------------------------------------

        # db.modulestore.structures --------------------------------------
        cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {"$elemMatch": {"block_type": "course"}}})

        course_start = cursor.get('blocks')[0].get('fields').get('start')  # course_starts
        course_end = cursor.get('blocks')[0].get('fields').get('end')  # course_ends
        course_enroll_start = cursor.get('blocks')[0].get('fields').get('enrollment_start')  # course_enroll_start
        course_enroll_end = cursor.get('blocks')[0].get('fields').get('enrollment_end')  # course_enroll_end
        course_name = cursor.get('blocks')[0].get('fields').get('display_name')  # course_names

        if course_start is not None:
            course_starts[course_id] = course_start
        if course_end is not None:
            course_ends[course_id] = course_end
        if course_enroll_start is not None:
            course_enroll_starts[course_id] = course_enroll_start
        if course_enroll_end is not None:
            course_enroll_ends[course_id] = course_enroll_end
        if course_name is not None:
            course_names[course_id] = course_name

        logger.debug('---------------------------------------------')
        logger.debug(course_id + " : " + cid + " : " + run)
        logger.debug(course_start)
        logger.debug(course_end)
        logger.debug(course_enroll_start)
        logger.debug(course_enroll_end)
        logger.debug('---------------------------------------------')





        # --------------------------------------

    # excel style
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    user_join = statistics_query.user_join(date)
    course_count = statistics_query.course_count(date)
    course_count_active = statistics_query.course_count_active(date)
    course_case = statistics_query.course_case(date)
    edu_new = statistics_query.edu_new(date)
    edu_total = statistics_query.edu_total(date)
    age_new = statistics_query.age_new(date)
    age_total = statistics_query.age_total(date)
    age_edu = statistics_query.age_edu(date)
    course_user = statistics_query.course_user(date)
    course_univ = statistics_query.course_univ(date)
    course_user_total = statistics_query.course_user_total(date)
    course_univ_total = statistics_query.course_univ_total(date)
    course_age = statistics_query.course_age(date)
    course_edu = statistics_query.course_edu(date)

    save_name = 'K-Mooc'+date+'.xlsx'
    save_path = EXCEL_PATH + save_name

    if os.path.isfile(save_path) and not debug:
        logger.info('------------------------------ statistics_excel pass ------------------------------')

        pass
    else:
        logger.info('------------------------------ statistics_excel make ------------------------------')

        wb = load_workbook(EXCEL_PATH + 'basic.xlsx')
        ws1 = wb['user_count']
        ws2 = wb['course_count']
        ws3 = wb['course_count_total']
        ws4 = wb['course_age']
        ws5 = wb['course_edu']

        # 가입현황
        logger.info('가입현황')

        ws1['B4'] = user_join[0]
        ws1['C4'] = user_join[2]
        ws1['D4'] = course_count[0]
        ws1['E4'] = course_count[2]
        ws1['F4'] = course_count_active[0]

        # 수강신청구분
        logger.info('수강신청구분')

        sort = [
            (9, 0),
            (10, 1),
            (11, 2)
        ]

        for (number, number1) in sort:
            ws1['C' + str(number)] = '-' if number == 11 else course_case[number1][1]
            ws1['D' + str(number)] = '-' if number == 11 else course_case[number1][2]
            ws1['F' + str(number)] = course_case[number1][3]
            ws1['G' + str(number)] = course_case[number1][4]

        # 연령구분
        logger.info('연령구분')

        sort = [
            (16, 0),
            (17, 1),
            (18, 2),
            (19, 3),
            (20, 4),
            (21, 5)
        ]
        print 'age_new == ',age_new
        for (number, number1) in sort:
            print 'number == ',number
            print 'age_new[number1][0] == ',age_new[number1][0]
            ws1['C' + str(number)] = age_new[number1][0]
            ws1['D' + str(number)] = age_new[number1][1]

        for (number, number1) in sort:
            ws1['F' + str(number)] = age_total[number1][0]
            ws1['G' + str(number)] = age_total[number1][1]

        # 학력구분
        logger.info('학력구분')

        sort = [
            (27, 0),
            (28, 1),
            (29, 2),
            (30, 3),
            (31, 4),
            (32, 5),
            (33, 6),
            (34, 7),
            (35, 8)
        ]

        for (number, number1) in sort:
            ws1['C' + str(number)] = edu_new[number1][0]
            ws1['D' + str(number)] = edu_new[number1][1]

        for (number, number1) in sort:
            ws1['F' + str(number)] = edu_total[number1][0]
            ws1['G' + str(number)] = edu_total[number1][1]

        # 연령별 학력
        sort = [
            (41, 0),
            (42, 1),
            (43, 2),
            (44, 3),
            (45, 4),
            (46, 5)
        ]

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

        # ======================================================================================================================================================

        # 코스별 수강자 # LJH수정
        # sorted(courseInfo.items(), key=itemgetter(1))
        rn1 = 3
        rn2 = 0

        sortlist = list()
        for c in course_user:
            if str(course_orgs[c[0]]) in dic_univ:
                c = (dic_univ[str(course_orgs[c[0]])], course_names[c[0]], ) + c
            else:
                c = (str(course_orgs[c[0]]), course_names[c[0]], ) + c

            edit_date = course_creates[c[2]].strftime("%Y-%m-%d") if c[2] in course_creates else None
            start_date = course_starts[c[2]].strftime("%Y-%m-%d") if c[2] in course_starts else None
            end_date = course_ends[c[2]].strftime("%Y-%m-%d") if c[2] in course_ends else None

            c = c + (edit_date, start_date, end_date,)

            logger.debug(c)
            sortlist.append(c)

        sortlist.sort(key=itemgetter(0, 4, 1))
        # sortlist.sort(key=itemgetter(0, 6, 7, 8, 1))
        for s in sortlist:

            org_name = s[0]
            c_name = s[1]
            c_id1 = s[3]
            c_id2 = s[4]
            cnt = s[5]

            ws2['A' + str(rn1)] = org_name
            ws2['B' + str(rn1)] = c_name
            ws2['C' + str(rn1)] = c_id1
            ws2['D' + str(rn1)] = c_id2
            ws2['E' + str(rn1)] = s[6]
            ws2['F' + str(rn1)] = s[7]
            ws2['G' + str(rn1)] = s[8]
            ws2['H' + str(rn1)] = cnt

            # set border
            ws2['A' + str(rn1)].border = thin_border
            ws2['B' + str(rn1)].border = thin_border
            ws2['C' + str(rn1)].border = thin_border
            ws2['D' + str(rn1)].border = thin_border
            ws2['E' + str(rn1)].border = thin_border
            ws2['F' + str(rn1)].border = thin_border
            ws2['G' + str(rn1)].border = thin_border
            ws2['H' + str(rn1)].border = thin_border

            ws2['A' + str(rn1)].alignment = Alignment(horizontal="left")
            ws2['B' + str(rn1)].alignment = Alignment(horizontal="left")
            ws2['C' + str(rn1)].alignment = Alignment(horizontal="center")
            ws2['D' + str(rn1)].alignment = Alignment(horizontal="center")
            ws2['E' + str(rn1)].alignment = Alignment(horizontal="center")
            ws2['F' + str(rn1)].alignment = Alignment(horizontal="center")
            ws2['G' + str(rn1)].alignment = Alignment(horizontal="center")
            ws2['H' + str(rn1)].alignment = Alignment(horizontal="right")

            rn1 += 1
            rn2 += 1

        rn1 = 3

        # for univ, cnt in course_univ:
        sortlist = list()
        for c in course_univ:
            if c[0] in dic_univ:
                c = (dic_univ[c[0]],) + c
            else:
                c = (c[0], ) + c

            logger.debug(c)
            sortlist.append(c)

        sortlist.sort(key=itemgetter(0))

        startCharNo1 = 75
        startCharNo2 = 65
        positionChar = ''
        isExpension = False

        for s in sortlist:
            orgName = s[0]
            cnt = s[2]

            if startCharNo1 > 90:
                startCharNo1 = 65

                if isExpension:
                    startCharNo2 += 1
                else:
                    isExpension = True

            if not isExpension:
                positionChar = chr(startCharNo1)
            else:
                positionChar = chr(startCharNo2) + chr(startCharNo1)

            print 'positionChar1:', positionChar

            ws2[positionChar + '2'] = orgName
            ws2[positionChar + '3'] = cnt

            # set border
            ws2[positionChar + '2'].border = thin_border
            ws2[positionChar + '3'].border = thin_border

            ws2[positionChar + '2'].alignment = Alignment(horizontal="center")
            ws2[positionChar + '3'].alignment = Alignment(horizontal="right")

            # print cId, cName
            # H 열부터 횡으로 증가. Z 까지 갔을경우 AA 로 다시 시작

            # 기존에 열으로 추가되는 로직
            # ----------------------------------------------

            # ws2['G' + str(rn1)] = orgName
            # ws2['H' + str(rn1)] = cnt
            # # set border
            # ws2['G' + str(rn1)].border = thin_border
            # ws2['H' + str(rn1)].border = thin_border
            # rn1 += 1

            # ----------------------------------------------

            startCharNo1 += 1

        logger.debug('코스별 수강자 누적')
        #코스별 수강자 누적
        # sorted(courseInfo.items(), key=itemgetter(1))
        rn1 = 3
        rn2 = 0
        # for cId, cId1, cId2, cnt in course_user_total:
        sortlist = list()
        for c in course_user_total:
            if str(course_orgs[c[0]]) in dic_univ:
                c = (dic_univ[str(course_orgs[c[0]])],course_names[c[0]], ) + c
            else:
                c = (str(course_orgs[c[0]]),course_names[c[0]], ) + c

            edit_date = course_creates[c[2]].strftime("%Y-%m-%d") if c[2] in course_creates else None
            start_date = course_starts[c[2]].strftime("%Y-%m-%d") if c[2] in course_starts else None
            end_date = course_ends[c[2]].strftime("%Y-%m-%d") if c[2] in course_ends else None

            c = c + (edit_date, start_date, end_date,)

            logger.debug(c)
            sortlist.append(c)

        sortlist.sort(key=itemgetter(0, 4, 1))
        # sortlist.sort(key=itemgetter(0, 7, 8, 9, 1))
        for s in sortlist:
            orgName = s[0]
            cName = s[1]
            cId1 = s[3]
            cId2 = s[4]
            cnt = s[5]
            cnt2 = s[6]

            edit_date = s[7]
            start_date = s[8]
            end_date = s[9]

            # print cId, cName
            ws3['A' + str(rn1)] = orgName
            ws3['B' + str(rn1)] = cName
            ws3['C' + str(rn1)] = cId1
            ws3['D' + str(rn1)] = cId2
            ws3['E' + str(rn1)] = edit_date
            ws3['F' + str(rn1)] = start_date
            ws3['G' + str(rn1)] = end_date
            ws3['H' + str(rn1)] = cnt2
            ws3['I' + str(rn1)] = cnt

            # set border
            ws3['A' + str(rn1)].border = thin_border
            ws3['B' + str(rn1)].border = thin_border
            ws3['C' + str(rn1)].border = thin_border
            ws3['D' + str(rn1)].border = thin_border
            ws3['E' + str(rn1)].border = thin_border
            ws3['F' + str(rn1)].border = thin_border
            ws3['G' + str(rn1)].border = thin_border
            ws3['H' + str(rn1)].border = thin_border
            ws3['I' + str(rn1)].border = thin_border

            ws3['A' + str(rn1)].alignment = Alignment(horizontal="left")
            ws3['B' + str(rn1)].alignment = Alignment(horizontal="left")
            ws3['C' + str(rn1)].alignment = Alignment(horizontal="center")
            ws3['D' + str(rn1)].alignment = Alignment(horizontal="center")
            ws3['E' + str(rn1)].alignment = Alignment(horizontal="center")
            ws3['F' + str(rn1)].alignment = Alignment(horizontal="center")
            ws3['G' + str(rn1)].alignment = Alignment(horizontal="center")
            ws3['H' + str(rn1)].alignment = Alignment(horizontal="right")
            ws3['I' + str(rn1)].alignment = Alignment(horizontal="right")

            rn1 += 1
            rn2 += 1

        rn1 = 3
        # for univ, cnt in course_univ_total:
        sortlist = list()
        for c in course_univ_total:
            if c[0] in dic_univ:
                c = (dic_univ[c[0]],) + c
            else:
                c = (c[0], ) + c

            logger.debug(c)
            sortlist.append(c)

        sortlist.sort(key=itemgetter(0))

        startCharNo1 = 76
        startCharNo2 = 65
        positionChar = ''
        isExpension = False

        for s in sortlist:
            orgName = s[0]
            cnt = s[2]
            cnt2 = s[3]

            if startCharNo1 > 90:
                startCharNo1 = 65

                if isExpension:
                    startCharNo2 += 1
                else:
                    isExpension = True

            if not isExpension:
                positionChar = chr(startCharNo1)
            else:
                positionChar = chr(startCharNo2) + chr(startCharNo1)

            logger.debug(positionChar)

            ws3[positionChar + '2'] = orgName
            ws3[positionChar + '3'] = cnt2
            ws3[positionChar + '4'] = cnt

            # set border
            ws3[positionChar + '2'].border = thin_border
            ws3[positionChar + '3'].border = thin_border
            ws3[positionChar + '4'].border = thin_border

            ws3[positionChar + '2'].alignment = Alignment(horizontal="center")
            ws3[positionChar + '3'].alignment = Alignment(horizontal="right")
            ws3[positionChar + '4'].alignment = Alignment(horizontal="right")

            startCharNo1 += 1

        # 코스별 연령
        logger.debug('코스별 연령')
        rn1 = 3
        sortlist = list()
        for c in course_age:
            if c[0] in dic_univ:
                c = (dic_univ[c[0]],) + c
            else:
                c = (c[0],) + c

            edit_date = course_creates[c[2]].strftime("%Y-%m-%d") if c[2] in course_creates else None
            start_date = course_starts[c[2]].strftime("%Y-%m-%d") if c[2] in course_starts else None
            end_date = course_ends[c[2]].strftime("%Y-%m-%d") if c[2] in course_ends else None
            course_name = course_names[c[2]] if c[2] in course_names else None
            c = c + (edit_date, start_date, end_date, course_name,)

            logger.debug(c)
            sortlist.append(c)

        sortlist.sort(key=itemgetter(0, 4, 1))
        # sortlist.sort(key=itemgetter(0, 12, 13, 14, 15))
        for s in sortlist:
            org = s[0]
            cname = s[15]
            course = s[3]
            run = s[4]
            age1 = s[5]
            age2 = s[6]
            age3 = s[7]
            age4 = s[8]
            age5 = s[9]
            age6 = s[10]
            total = s[11]
            edit_date = s[12]
            start_date = s[13]
            end_date = s[14]

            ws4['A' + str(rn1)] = org
            ws4['B' + str(rn1)] = cname
            ws4['C' + str(rn1)] = course
            ws4['D' + str(rn1)] = run
            ws4['E' + str(rn1)] = edit_date
            ws4['F' + str(rn1)] = start_date
            ws4['G' + str(rn1)] = end_date
            ws4['H' + str(rn1)] = age1
            ws4['I' + str(rn1)] = age2
            ws4['J' + str(rn1)] = age3
            ws4['K' + str(rn1)] = age4
            ws4['L' + str(rn1)] = age5
            ws4['M' + str(rn1)] = age6
            ws4['N' + str(rn1)] = total

            # set border
            ws4['A' + str(rn1)].border = thin_border
            ws4['B' + str(rn1)].border = thin_border
            ws4['C' + str(rn1)].border = thin_border
            ws4['D' + str(rn1)].border = thin_border
            ws4['E' + str(rn1)].border = thin_border
            ws4['F' + str(rn1)].border = thin_border
            ws4['G' + str(rn1)].border = thin_border
            ws4['H' + str(rn1)].border = thin_border
            ws4['I' + str(rn1)].border = thin_border
            ws4['J' + str(rn1)].border = thin_border
            ws4['K' + str(rn1)].border = thin_border
            ws4['L' + str(rn1)].border = thin_border
            ws4['M' + str(rn1)].border = thin_border
            ws4['N' + str(rn1)].border = thin_border

            ws4['A' + str(rn1)].alignment = Alignment(horizontal="left")
            ws4['B' + str(rn1)].alignment = Alignment(horizontal="left")
            ws4['C' + str(rn1)].alignment = Alignment(horizontal="center")
            ws4['D' + str(rn1)].alignment = Alignment(horizontal="center")
            ws4['E' + str(rn1)].alignment = Alignment(horizontal="center")
            ws4['F' + str(rn1)].alignment = Alignment(horizontal="center")
            ws4['G' + str(rn1)].alignment = Alignment(horizontal="center")
            ws4['H' + str(rn1)].alignment = Alignment(horizontal="right")
            ws4['I' + str(rn1)].alignment = Alignment(horizontal="right")
            ws4['J' + str(rn1)].alignment = Alignment(horizontal="right")
            ws4['K' + str(rn1)].alignment = Alignment(horizontal="right")
            ws4['L' + str(rn1)].alignment = Alignment(horizontal="right")
            ws4['M' + str(rn1)].alignment = Alignment(horizontal="right")
            ws4['N' + str(rn1)].alignment = Alignment(horizontal="right")

            rn1 += 1

        # 코스별 학력
        logger.debug('코스별 학력')
        rn1 = 3
        sortlist = list()
        for c in course_edu:
            if c[0] in dic_univ:
                c = (dic_univ[c[0]],) + c
            else:
                c = (c[0],) + c

            edit_date = course_creates[c[2]].strftime("%Y-%m-%d") if c[2] in course_creates else None
            start_date = course_starts[c[2]].strftime("%Y-%m-%d") if c[2] in course_starts else None
            end_date = course_ends[c[2]].strftime("%Y-%m-%d") if c[2] in course_ends else None
            course_name = course_names[c[2]] if c[2] in course_names else None
            c = c + (edit_date, start_date, end_date, course_name,)

            logger.debug(c)
            sortlist.append(c)

        sortlist.sort(key=itemgetter(0, 4, 1))
        # sortlist.sort(key=itemgetter(0, 15, 16, 17, 18))

        for s in sortlist:

            org = s[0]
            cname = s[18]
            course = s[3]
            run = s[4]
            edu1 = s[5]
            edu2 = s[6]
            edu3 = s[7]
            edu4 = s[8]
            edu5 = s[9]
            edu6 = s[10]
            edu7 = s[11]
            edu8 = s[12]
            edu9 = s[13]
            total = s[14]
            edit_date = s[15]
            start_date = s[16]
            end_date = s[17]
            # print cId, cName

            ws5['A' + str(rn1)] = org
            ws5['B' + str(rn1)] = cname
            ws5['C' + str(rn1)] = course
            ws5['D' + str(rn1)] = run
            ws5['E' + str(rn1)] = edit_date
            ws5['F' + str(rn1)] = start_date
            ws5['G' + str(rn1)] = end_date
            ws5['H' + str(rn1)] = edu1
            ws5['I' + str(rn1)] = edu2
            ws5['J' + str(rn1)] = edu3
            ws5['K' + str(rn1)] = edu4
            ws5['L' + str(rn1)] = edu5
            ws5['M' + str(rn1)] = edu6
            ws5['N' + str(rn1)] = edu7
            ws5['O' + str(rn1)] = edu8
            ws5['P' + str(rn1)] = edu9
            ws5['Q' + str(rn1)] = total

            # set border
            ws5['A' + str(rn1)].border = thin_border
            ws5['B' + str(rn1)].border = thin_border
            ws5['C' + str(rn1)].border = thin_border
            ws5['D' + str(rn1)].border = thin_border
            ws5['E' + str(rn1)].border = thin_border
            ws5['F' + str(rn1)].border = thin_border
            ws5['G' + str(rn1)].border = thin_border
            ws5['H' + str(rn1)].border = thin_border
            ws5['I' + str(rn1)].border = thin_border
            ws5['J' + str(rn1)].border = thin_border
            ws5['K' + str(rn1)].border = thin_border
            ws5['L' + str(rn1)].border = thin_border
            ws5['M' + str(rn1)].border = thin_border
            ws5['N' + str(rn1)].border = thin_border
            ws5['O' + str(rn1)].border = thin_border
            ws5['P' + str(rn1)].border = thin_border
            ws5['Q' + str(rn1)].border = thin_border

            ws5['A' + str(rn1)].alignment = Alignment(horizontal="left")
            ws5['B' + str(rn1)].alignment = Alignment(horizontal="left")
            ws5['C' + str(rn1)].alignment = Alignment(horizontal="center")
            ws5['D' + str(rn1)].alignment = Alignment(horizontal="center")
            ws5['E' + str(rn1)].alignment = Alignment(horizontal="center")
            ws5['F' + str(rn1)].alignment = Alignment(horizontal="center")
            ws5['G' + str(rn1)].alignment = Alignment(horizontal="center")
            ws5['H' + str(rn1)].alignment = Alignment(horizontal="right")
            ws5['I' + str(rn1)].alignment = Alignment(horizontal="right")
            ws5['J' + str(rn1)].alignment = Alignment(horizontal="right")
            ws5['K' + str(rn1)].alignment = Alignment(horizontal="right")
            ws5['L' + str(rn1)].alignment = Alignment(horizontal="right")
            ws5['M' + str(rn1)].alignment = Alignment(horizontal="right")
            ws5['N' + str(rn1)].alignment = Alignment(horizontal="right")
            ws5['O' + str(rn1)].alignment = Alignment(horizontal="right")
            ws5['P' + str(rn1)].alignment = Alignment(horizontal="right")
            ws5['Q' + str(rn1)].alignment = Alignment(horizontal="right")

            rn1 += 1

        wb.save(save_path)
    return HttpResponse('/manage/home/static/excel/' + save_name, content_type='application/vnd.ms-excel')


def certificate_excel(request, course_id):

    print 'course_id', course_id

    d = datetime.date.today()
    year = d.year
    month = d.month
    day = d.day

    if month < 10:
        month = '0' + str(month)
    if day < 10:
        day = '0' + str(day)


    print 'month', month
    print 'day', day

    certificates = statistics_query.certificateInfo(course_id)

    courseName = ''
    pb = ''
    ov = ''

    client = MongoClient(database_id, 27017)
    db = client.edxapp

    wb = load_workbook(EXCEL_PATH + '/basic_cert.xlsx')

    for c in certificates:
        cid = str(c[2])

        print 'cid', cid

        cursor = db.modulestore.active_versions.find({'course':cid})
        for document in cursor:
            print '>> 1'
            pb = document.get('versions').get('published-branch')
            break
        cursor.close()

        cursor = db.modulestore.structures.find({'_id':pb})
        for document in cursor:
            print '>> 2'
            ov = document.get('original_version')
            break
        cursor.close()

        cursor = db.modulestore.structures.find({'_id':ov})
        for document in cursor:
            print '>> 3'
            blocks = document.get('blocks')
            for block in blocks:
                print '>> 4'
                fields = block.get('fields')
                for field in fields:
                    print '>> 5'
                    dn = fields['display_name']
                    courseName = dn
                    break
                break
            break
        break
        cursor.close()

    thin_border = Border(left=Side(style='thin'),
                     right=Side(style='thin'),
                     top=Side(style='thin'),
                     bottom=Side(style='thin'))

    ws1 = wb['certificates']

    row = 2
    for c in certificates:

        ws1['A' + str(row)] = dic_univ[c[0]]
        ws1['B' + str(row)] = courseName
        ws1['C' + str(row)] = c[2]
        ws1['D' + str(row)] = c[3]
        ws1['E' + str(row)] = c[4]
        ws1['F' + str(row)] = c[5]

        ws1['A' + str(row)].border = thin_border
        ws1['B' + str(row)].border = thin_border
        ws1['C' + str(row)].border = thin_border
        ws1['D' + str(row)].border = thin_border
        ws1['E' + str(row)].border = thin_border
        ws1['F' + str(row)].border = thin_border
        row += 1

    save_name = 'K-Mooc_certificate_' + str(cid)  + '_' + str(year) + str(month) + str(day) +'.xlsx'
    save_path = EXCEL_PATH + save_name

    wb.save(save_path)

    return HttpResponse('/manage/static/excel/' + save_name, content_type='application/vnd.ms-excel')
# def statistics_excel3(request, date):
def statistics_excel1(request, date):

    save_name = 'K-MoocMonth'+date+'.xlsx'
    save_path = EXCEL_PATH + save_name

    if os.path.isfile(save_path) and not debug:
        pass
    else:
        member_statistics = statistics_query.member_statistics(date)
        country_statistics = statistics_query.country_statistics(date)
        print 'country_statistics == ',country_statistics
        wb = load_workbook(EXCEL_PATH + 'basic_month.xlsx')
        thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))

        COUNTRIES = {
            "AF": "Afghanistan",
            "AX": "Åland Islands",
            "AL": "Albania",
            "DZ": "Algeria",
            "AS": "American Samoa",
            "AD": "Andorra",
            "AO": "Angola",
            "AI": "Anguilla",
            "AQ": "Antarctica",
            "AG": "Antigua and Barbuda",
            "AR": "Argentina",
            "AM": "Armenia",
            "AW": "Aruba",
            "AU": "Australia",
            "AT": "Austria",
            "AZ": "Azerbaijan",
            "BS": "Bahamas",
            "BH": "Bahrain",
            "BD": "Bangladesh",
            "BB": "Barbados",
            "BY": "Belarus",
            "BE": "Belgium",
            "BZ": "Belize",
            "BJ": "Benin",
            "BM": "Bermuda",
            "BT": "Bhutan",
            "BO": "Bolivia (Plurinational State of)",
            "BQ": "Bonaire, Sint Eustatius and Saba",
            "BA": "Bosnia and Herzegovina",
            "BW": "Botswana",
            "BV": "Bouvet Island",
            "BR": "Brazil",
            "IO": "British Indian Ocean Territory",
            "BN": "Brunei Darussalam",
            "BG": "Bulgaria",
            "BF": "Burkina Faso",
            "BI": "Burundi",
            "CV": "Cabo Verde",
            "KH": "Cambodia",
            "CM": "Cameroon",
            "CA": "Canada",
            "KY": "Cayman Islands",
            "CF": "Central African Republic",
            "TD": "Chad",
            "CL": "Chile",
            "CN": "China",
            "CX": "Christmas Island",
            "CC": "Cocos (Keeling) Islands",
            "CO": "Colombia",
            "KM": "Comoros",
            "CD": "Congo (the Democratic Republic of the)",
            "CG": "Congo",
            "CK": "Cook Islands",
            "CR": "Costa Rica",
            "CI": "Côte d'Ivoire",
            "HR": "Croatia",
            "CU": "Cuba",
            "CW": "Curaçao",
            "CY": "Cyprus",
            "CZ": "Czech Republic",
            "DK": "Denmark",
            "DJ": "Djibouti",
            "DM": "Dominica",
            "DO": "Dominican Republic",
            "EC": "Ecuador",
            "EG": "Egypt",
            "SV": "El Salvador",
            "GQ": "Equatorial Guinea",
            "ER": "Eritrea",
            "EE": "Estonia",
            "ET": "Ethiopia",
            "FK": "Falkland Islands  [Malvinas]",
            "FO": "Faroe Islands",
            "FJ": "Fiji",
            "FI": "Finland",
            "FR": "France",
            "GF": "French Guiana",
            "PF": "French Polynesia",
            "TF": "French Southern Territories",
            "GA": "Gabon",
            "GM": "Gambia",
            "GE": "Georgia",
            "DE": "Germany",
            "GH": "Ghana",
            "GI": "Gibraltar",
            "GR": "Greece",
            "GL": "Greenland",
            "GD": "Grenada",
            "GP": "Guadeloupe",
            "GU": "Guam",
            "GT": "Guatemala",
            "GG": "Guernsey",
            "GN": "Guinea",
            "GW": "Guinea-Bissau",
            "GY": "Guyana",
            "HT": "Haiti",
            "HM": "Heard Island and McDonald Islands",
            "VA": "Holy See",
            "HN": "Honduras",
            "HK": "Hong Kong",
            "HU": "Hungary",
            "IS": "Iceland",
            "IN": "India",
            "ID": "Indonesia",
            "IR": "Iran (Islamic Republic of)",
            "IQ": "Iraq",
            "IE": "Ireland",
            "IM": "Isle of Man",
            "IL": "Israel",
            "IT": "Italy",
            "JM": "Jamaica",
            "JP": "Japan",
            "JE": "Jersey",
            "JO": "Jordan",
            "KZ": "Kazakhstan",
            "KE": "Kenya",
            "KI": "Kiribati",
            "KP": "Korea (the Democratic People's Republic of)",
            "KR": "Korea (the Republic of)",
            "KW": "Kuwait",
            "KG": "Kyrgyzstan",
            "LA": "Lao People's Democratic Republic",
            "LV": "Latvia",
            "LB": "Lebanon",
            "LS": "Lesotho",
            "LR": "Liberia",
            "LY": "Libya",
            "LI": "Liechtenstein",
            "LT": "Lithuania",
            "LU": "Luxembourg",
            "MO": "Macao",
            "MK": "Macedonia (the former Yugoslav Republic of)",
            "MG": "Madagascar",
            "MW": "Malawi",
            "MY": "Malaysia",
            "MV": "Maldives",
            "ML": "Mali",
            "MT": "Malta",
            "MH": "Marshall Islands",
            "MQ": "Martinique",
            "MR": "Mauritania",
            "MU": "Mauritius",
            "YT": "Mayotte",
            "MX": "Mexico",
            "FM": "Micronesia (Federated States of)",
            "MD": "Moldova (the Republic of)",
            "MC": "Monaco",
            "MN": "Mongolia",
            "ME": "Montenegro",
            "MS": "Montserrat",
            "MA": "Morocco",
            "MZ": "Mozambique",
            "MM": "Myanmar",
            "NA": "Namibia",
            "NR": "Nauru",
            "NP": "Nepal",
            "NL": "Netherlands",
            "NC": "New Caledonia",
            "NZ": "New Zealand",
            "NI": "Nicaragua",
            "NE": "Niger",
            "NG": "Nigeria",
            "NU": "Niue",
            "NF": "Norfolk Island",
            "MP": "Northern Mariana Islands",
            "NO": "Norway",
            "OM": "Oman",
            "PK": "Pakistan",
            "PW": "Palau",
            "PS": "Palestine, State of",
            "PA": "Panama",
            "PG": "Papua New Guinea",
            "PY": "Paraguay",
            "PE": "Peru",
            "PH": "Philippines",
            "PN": "Pitcairn",
            "PL": "Poland",
            "PT": "Portugal",
            "PR": "Puerto Rico",
            "QA": "Qatar",
            "RE": "Réunion",
            "RO": "Romania",
            "RU": "Russian Federation",
            "RW": "Rwanda",
            "BL": "Saint Barthélemy",
            "SH": "Saint Helena, Ascension and Tristan da Cunha",
            "KN": "Saint Kitts and Nevis",
            "LC": "Saint Lucia",
            "MF": "Saint Martin (French part)",
            "PM": "Saint Pierre and Miquelon",
            "VC": "Saint Vincent and the Grenadines",
            "WS": "Samoa",
            "SM": "San Marino",
            "ST": "Sao Tome and Principe",
            "SA": "Saudi Arabia",
            "SN": "Senegal",
            "RS": "Serbia",
            "SC": "Seychelles",
            "SL": "Sierra Leone",
            "SG": "Singapore",
            "SX": "Sint Maarten (Dutch part)",
            "SK": "Slovakia",
            "SI": "Slovenia",
            "SB": "Solomon Islands",
            "SO": "Somalia",
            "ZA": "South Africa",
            "GS": "South Georgia and the South Sandwich Islands",
            "SS": "South Sudan",
            "ES": "Spain",
            "LK": "Sri Lanka",
            "SD": "Sudan",
            "SR": "Suriname",
            "SJ": "Svalbard and Jan Mayen",
            "SZ": "Swaziland",
            "SE": "Sweden",
            "CH": "Switzerland",
            "SY": "Syrian Arab Republic",
            "TW": "Taiwan (Province of China)",
            "TJ": "Tajikistan",
            "TZ": "Tanzania, United Republic of",
            "TH": "Thailand",
            "TL": "Timor-Leste",
            "TG": "Togo",
            "TK": "Tokelau",
            "TO": "Tonga",
            "TT": "Trinidad and Tobago",
            "TN": "Tunisia",
            "TR": "Turkey",
            "TM": "Turkmenistan",
            "TC": "Turks and Caicos Islands",
            "TV": "Tuvalu",
            "UG": "Uganda",
            "UA": "Ukraine",
            "AE": "United Arab Emirates",
            "GB": "United Kingdom of Great Britain and Northern Ireland",
            "UM": "United States Minor Outlying Islands",
            "US": "United States of America",
            "UY": "Uruguay",
            "UZ": "Uzbekistan",
            "VU": "Vanuatu",
            "VE": "Venezuela (Bolivarian Republic of)",
            "VN": "Viet Nam",
            "VG": "Virgin Islands (British)",
            "VI": "Virgin Islands (U.S.)",
            "WF": "Wallis and Futuna",
            "EH": "Western Sahara",
            "YE": "Yemen",
            "ZM": "Zambia",
            "ZW": "Zimbabwe",
        }

        ws1 = wb['Sheet1']

        row = 2
        for c in member_statistics:
            ws1['B' + str(row+1)] = c[0]
            ws1['B' + str(row+2)] = c[1]
            ws1['B' + str(row+3)] = c[2]

        row = 8
        for c in country_statistics:
            ws1['A' + str(row)] = c[0]
            ws1['B' + str(row)] = c[1]
            ws1['C' + str(row)] = COUNTRIES[c[0]] if c[0] in COUNTRIES else c[0]

            ws1['A' + str(row)].border = thin_border
            ws1['B' + str(row)].border = thin_border
            ws1['C' + str(row)].border = thin_border
            row += 1

        wb.save(save_path)

    return HttpResponse('/manage/home/static/excel/' + save_name, content_type='application/vnd.ms-excel')
