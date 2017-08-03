# -*- coding: utf-8 -*-

from openpyxl import load_workbook
import statistics_query
from django.http import HttpResponse
from pymongo import MongoClient
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font
import os
from operator import itemgetter
import datetime
from management.settings import EXCEL_PATH, dic_univ, database_id, debug, classfy, middle_classfy, countries
from openpyxl.styles import Alignment
from bson.objectid import ObjectId
import logging
import logging.handlers
import time

'''
# 로거 인스턴스를 만든다
#logger = logging.get#logger('statistics log')

# 포매터를 만든다
fomatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')

# 스트림과 파일로 로그를 출력하는 핸들러를 각각 만든다.
fileHandler = logging.FileHandler('./statistics.log')
streamHandler = logging.StreamHandler()

# 각 핸들러에 포매터를 지정한다.
fileHandler.setFormatter(fomatter)
streamHandler.setFormatter(fomatter)

# 로거 인스턴스에 스트림 핸들러와 파일핸들러를 붙인다.
#logger.addHandler(fileHandler)
#logger.addHandler(streamHandler)

if debug:
    #logger.setLevel(logging.DEBUG)
'''


def style_base(cell):
    """
    Apply styles to a range of cells as if they were a single cell.

    :param ws:  Excel worksheet instance
    :param range: An excel range to style (e.g. A1:F20)
    :param border: An openpyxl Border
    :param fill: An openpyxl PatternFill or GradientFill
    :param font: An openpyxl Font object
    """

    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    cell.border = thin_border
    cell.alignment = Alignment(horizontal="center", vertical="center")


def style_range(ws, cell_range, border=Border(), fill=None, font=None, alignment=None):
    """
    Apply styles to a range of cells as if they were a single cell.

    :param ws:  Excel worksheet instance
    :param range: An excel range to style (e.g. A1:F20)
    :param border: An openpyxl Border
    :param fill: An openpyxl PatternFill or GradientFill
    :param font: An openpyxl Font object
    """

    try:
        top = Border(top=border.top)
        left = Border(left=border.left)
        right = Border(right=border.right)
        bottom = Border(bottom=border.bottom)

        first_cell = ws[cell_range.split(":")[0]]
        if alignment:
            ws.merge_cells(cell_range)
            first_cell.alignment = alignment

        rows = ws[cell_range]
        if font:
            first_cell.font = font

        for cell in rows[0]:
            cell.border = cell.border + top
        for cell in rows[-1]:
            cell.border = cell.border + bottom

        for row in rows:
            l = row[0]
            r = row[-1]
            l.border = l.border + left
            r.border = r.border + right
            if fill:
                for c in row:
                    c.fill = fill
    except Exception as e:
        print e


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

        cursor = db.modulestore.active_versions.find({'course': cid})
        for document in cursor:
            print '>> 1'
            pb = document.get('versions').get('published-branch')
            break
        cursor.close()

        cursor = db.modulestore.structures.find({'_id': pb})
        for document in cursor:
            print '>> 2'
            ov = document.get('original_version')
            break
        cursor.close()

        cursor = db.modulestore.structures.find({'_id': ov})
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

    save_name = 'K-Mooc_certificate_' + str(cid) + '_' + str(year) + str(month) + str(day) + '.xlsx'
    save_path = EXCEL_PATH + save_name

    wb.save(save_path)

    return HttpResponse('/manage/static/excel/' + save_name, content_type='application/vnd.ms-excel')


# 일일통계
def statistics_excel(request, date):
    print 'run statistics_excel'
    time.sleep(1)

    save_name = 'K-Mooc{0}.xlsx'.format(date)
    save_path = EXCEL_PATH + save_name

    if os.path.isfile(save_path) and False:
        print 'file exists. so just download.'
    else:
        # Get course name
        course_ids_all = statistics_query.course_ids_all()

        print 'len(course_ids_all) = ', len(course_ids_all)

        client = MongoClient(database_id, 27017)
        db = client.edxapp
        course_orgs = {}
        course_classfys = {}
        course_middle_classfys = {}
        course_names = {}
        course_creates = {}
        course_enroll_starts = {}
        course_enroll_ends = {}
        course_starts = {}
        course_ends = {}
        course_edited = {}

        course_effort = {}
        course_video = {}
        course_week = {}
        course_cert_date = {}

        course_state = {}

        print 'step1 : course_info search'

        for course_id, display_name, course, org, start, end, enrollment_start, enrollment_end, effort, cert_date in course_ids_all:
            print course_id, org, display_name, type(start), start, type(end), end, type(enrollment_start), enrollment_start, type(enrollment_end), enrollment_end

            cid = course_id.split('+')[1]
            run = course_id.split('+')[2]

            # course_state setting
            utc_time = datetime.datetime.utcnow()

            if cert_date:
                course_state[course] = '이수증발급'
            elif utc_time < start:
                course_state[course] = '준비중'
            elif start < utc_time < end:
                course_state[course] = 'ing'
            elif end < utc_time:
                course_state[course] = 'end'
            else:
                pass

            if cert_date:
                course_cert_date[course_id] = cert_date

            cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
            if not cursor:
                print 'not exists: ', cid, run
                continue



            pb = cursor.get('versions').get('published-branch')
            # course_orgs
            course_orgs[course_id] = cursor.get('org')
            course_creates[course_id] = cursor.get('edited_on')

            cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)}, {"blocks": {"$elemMatch": {"block_type": "course"}}})

            _classfy = cursor.get('blocks')[0].get('fields').get('classfy')  # classfy
            _mclassfy = cursor.get('blocks')[0].get('fields').get('middle_classfy')  # middle_classfy

            _course_edited = cursor.get('blocks')[0].get('edit_info').get('edited_on')  # middle_classfy

            if start is not None:
                course_starts[course_id] = start

            if end is not None:
                course_ends[course_id] = end

            if enrollment_start is not None:
                course_enroll_starts[course_id] = enrollment_start

            if enrollment_end is not None:
                course_enroll_ends[course_id] = enrollment_end

            if display_name is not None:
                course_names[course_id] = display_name

            if _classfy is not None and _classfy != 'all':
                course_classfys[course_id] = classfy[_classfy] if _classfy in classfy else _classfy

            if _mclassfy is not None and _mclassfy != 'all':
                course_middle_classfys[course_id] = middle_classfy[_mclassfy] if _mclassfy in middle_classfy else _mclassfy

            if _course_edited is not None:
                course_edited[course_id] = _course_edited

            if effort:
                course_effort[course_id] = effort.split('@')[0] if effort and '@' in effort else '-'
                course_week[course_id] = effort.split('@')[1].split('#')[0] if effort and '@' in effort and '#' in effort else '-'
                course_video[course_id] = effort.split('#')[1] if effort and '#' in effort else '-'

        print 'step2 : mysql search'

        # 요약
        auth_user_info = statistics_query.auth_user_info(date)
        student_courseenrollment_info = statistics_query.student_courseenrollment_info(date)
        certificate_info = statistics_query.overall_only_cert(date)

        # 회원가입/수강신청 세부사항
        overall_auth = statistics_query.overall_auth(date)
        overall_enroll = statistics_query.overall_enroll(date)
        overall_cert = statistics_query.overall_cert(date)

        # 연령구분
        age_new = statistics_query.age_new(date)
        age_total = statistics_query.age_total(date)

        # 학력구분
        edu_new = statistics_query.edu_new(date)
        edu_total = statistics_query.edu_total(date)

        # 연령별 학력
        age_edu = statistics_query.age_edu(date)

        print 'step3: info '
        wb = load_workbook(EXCEL_PATH + 'base.xlsx')

        ws1 = wb['overall']
        ws2 = wb['by_course_KPI']
        ws3 = wb['by_course_demographic']

        # excel style
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        # fill = PatternFill("solid", fgColor="eeeeee")
        fill = None

        font = Font(b=True, color="000000")
        # font = None
        al = Alignment(horizontal="center", vertical="center")

        # sheet1

        # 요약
        style_range(ws1, 'B2:C2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'D2:E2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'F2:G2', border=thin_border, fill=fill, font=font, alignment=al)

        # 세부사항
        style_range(ws1, 'B7:C8', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'D7:E7', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'F7:G7', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'B9:B12', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'B13:B15', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'B16:B17', border=thin_border, fill=fill, font=font, alignment=al)

        # 연령구분
        style_range(ws1, 'B20:B21', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'C20:F20', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'G20:J20', border=thin_border, fill=fill, font=font, alignment=al)

        # 학력구분
        style_range(ws1, 'B31:B32', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'C31:F31', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'G31:J31', border=thin_border, fill=fill, font=font, alignment=al)

        # 연령별 학력
        style_range(ws1, 'B45:B46', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'C45:L45', border=thin_border, fill=fill, font=font, alignment=al)

        # sheet2
        style_range(ws2, 'A1:J2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'K1:Q2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'R1:V1', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'R2:S2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'T2:U2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'W1:X2', border=thin_border, fill=fill, font=font, alignment=al)

        # sheet3
        style_range(ws3, 'A1:J2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'K1:AC1', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'AD1:AV1', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'AW1:BO1', border=thin_border, fill=fill, font=font, alignment=al)

        style_range(ws3, 'K2:M2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'N2:S2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'T2:AB2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'AC2:AC3', border=thin_border, fill=fill, font=font, alignment=al)

        style_range(ws3, 'AD2:AF2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'AG2:AL2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'AM2:AU2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'AV2:AV3', border=thin_border, fill=fill, font=font, alignment=al)

        style_range(ws3, 'AW2:AY2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'AZ2:BE2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'BF2:BN2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws3, 'BO2:BO3', border=thin_border, fill=fill, font=font, alignment=al)

        # 가입현황
        # logger.info('가입현황')
        ws1['B4'] = auth_user_info[0][0]
        ws1['C4'] = auth_user_info[0][1]
        ws1['D4'] = student_courseenrollment_info[0][0]
        ws1['E4'] = student_courseenrollment_info[0][1]
        ws1['F4'] = certificate_info[0][1]
        ws1['G4'] = certificate_info[0][1]

        # 회원가입 / 수강신청 세부사항
        # logger.info('수강신청구분')
        ws1['E9'] = overall_auth[0][0]
        ws1['E10'] = overall_auth[0][1]
        ws1['E12'] = overall_auth[0][2]
        ws1['G9'] = overall_auth[0][3]
        ws1['G10'] = overall_auth[0][4]
        ws1['G12'] = overall_auth[0][5]

        #: 수강신청
        ws1['D13'] = overall_enroll[0][0]
        ws1['D14'] = overall_enroll[0][1]
        ws1['E13'] = overall_enroll[0][2]
        ws1['E14'] = overall_enroll[0][3]
        ws1['F13'] = overall_enroll[0][4]
        ws1['F14'] = overall_enroll[0][5]
        ws1['G13'] = overall_enroll[0][6]
        ws1['G14'] = overall_enroll[0][7]

        #: 이수
        ws1['D16'] = overall_cert[0][0]
        ws1['D17'] = overall_cert[0][1]
        ws1['E16'] = overall_cert[0][2]
        ws1['E17'] = overall_cert[0][3]
        ws1['F16'] = overall_cert[0][4]
        ws1['F17'] = overall_cert[0][5]
        ws1['G16'] = overall_cert[0][6]
        ws1['G17'] = overall_cert[0][7]

        # 연령구분

        # logger.info('연령구분')

        start_row = 22

        print 'len(age_new):', len(age_new)

        for male, female, etc in age_new:
            ws1['C' + str(start_row)] = male

            ws1['D' + str(start_row)] = female

            ws1['E' + str(start_row)] = etc

            start_row += 1

        start_row = 22
        print 'len(age_total):', len(age_total)
        for male, female, etc in age_total:
            ws1['G' + str(start_row)] = male
            ws1['H' + str(start_row)] = female
            ws1['I' + str(start_row)] = etc
            start_row += 1

        # 학력구분
        # logger.info('학력구분')
        print 'step5: edu gubn '
        start_row = 33
        print 'len(edu_new):', len(edu_new)
        for male, female, etc in edu_new:
            ws1['C' + str(start_row)] = male
            ws1['D' + str(start_row)] = female
            ws1['E' + str(start_row)] = etc
            start_row += 1

        start_row = 33
        print 'len(edu_total):', len(edu_total)
        for male, female, etc in edu_total:
            ws1['G' + str(start_row)] = male
            ws1['H' + str(start_row)] = female
            ws1['I' + str(start_row)] = etc
            start_row += 1

        # 연령별 학력
        print 'step6: age + edu gubn '
        start_row = 47
        print 'len(age_edu):', len(age_edu)
        for a, b, c, d, e, f, g, h, i in age_edu:
            ws1['C' + str(start_row)] = a
            ws1['D' + str(start_row)] = b
            ws1['E' + str(start_row)] = c
            ws1['F' + str(start_row)] = d
            ws1['G' + str(start_row)] = e
            ws1['H' + str(start_row)] = f
            ws1['I' + str(start_row)] = g
            ws1['J' + str(start_row)] = h
            ws1['K' + str(start_row)] = i
            start_row += 1

        #: SHEET 2
        # by_course_KPI

        sortlist = list()
        by_course_enroll = statistics_query.by_course_enroll(date)
        for course_id, org, new_enroll_cnt, new_unenroll_cnt, all_enroll_cnt, all_unenroll_cnt, half_cnt, cert_cnt in by_course_enroll:
            row = tuple()
            row += (get_value_from_dict(dic_univ, org),)
            row += (get_value_from_dict(course_classfys, course_id, ''),)
            row += (get_value_from_dict(course_middle_classfys, course_id, ''),)
            row += (get_value_from_dict(course_names, course_id),)
            row += (get_value_from_dict(course_effort, course_id),)
            row += (get_value_from_dict(course_video, course_id),)
            row += (get_value_from_dict(course_week, course_id),)
            row += (org,)
            row += (course_id.split('+')[1],)
            row += (course_id.split('+')[2],)

            row += ('이수증발급' if course_id in course_cert_date else '',)
            row += (get_value_from_dict(course_creates, course_id),)
            row += (get_value_from_dict(course_enroll_starts, course_id),)
            row += (get_value_from_dict(course_enroll_ends, course_id),)
            row += (get_value_from_dict(course_starts, course_id),)
            row += (get_value_from_dict(course_ends, course_id),)
            row += (get_value_from_dict(course_cert_date, course_id, ''),)
            row += (new_enroll_cnt,)
            row += (new_unenroll_cnt,)
            row += (all_enroll_cnt,)
            row += (all_unenroll_cnt,)
            row += (all_enroll_cnt - all_unenroll_cnt,)

            # over 50% cert target
            row += (half_cnt if course_id in course_cert_date else '',)
            # certed target
            row += (cert_cnt if course_id in course_cert_date else '',)
            # course update date
            row += (get_value_from_dict(course_edited, course_id),)

            sortlist.append(row)

        sortlist.sort(key=itemgetter(0, 4, 5))

        start_row = 4
        for course_info in sortlist:
            print 'course_info --- s'
            print course_info
            print 'course_info --- e'

            start_char = 65
            for idx in range(0, len(course_info)):
                ws2[chr(start_char) + str(start_row)] = course_info[idx]
                style_base(ws2[chr(start_char) + str(start_row)])
                start_char += 1
            start_row += 1

        print 'e -----------------------------------------------------'

        # by_course_demographic

        sortlist = list()
        by_course_demographic = statistics_query.by_course_demographics(date)
        for course_id, org, \
            male_1, female_1, etc_1, age1_1, age2_1, age3_1, age4_1, age5_1, age6_1, edu1_1, edu2_1, edu3_1, edu4_1, edu5_1, edu6_1, edu7_1, edu8_1, edu9_1, allcnt_1, \
            male_2, female_2, etc_2, age1_2, age2_2, age3_2, age4_2, age5_2, age6_2, edu1_2, edu2_2, edu3_2, edu4_2, edu5_2, edu6_2, edu7_2, edu8_2, edu9_2, allcnt_2, \
            male_3, female_3, etc_3, age1_3, age2_3, age3_3, age4_3, age5_3, age6_3, edu1_3, edu2_3, edu3_3, edu4_3, edu5_3, edu6_3, edu7_3, edu8_3, edu9_3, allcnt_3 \
                in by_course_demographic:
            row = tuple()
            row += (get_value_from_dict(dic_univ, org),)
            row += (get_value_from_dict(course_classfys, course_id, ''),)
            row += (get_value_from_dict(course_middle_classfys, course_id, ''),)
            row += (get_value_from_dict(course_names, course_id),)
            row += (get_value_from_dict(course_effort, course_id),)
            row += (get_value_from_dict(course_video, course_id),)
            row += (get_value_from_dict(course_week, course_id),)
            row += (org,)
            row += (course_id.split('+')[1],)
            row += (course_id.split('+')[2],)

            row += (male_1,)
            row += (female_1,)
            row += (etc_1,)
            row += (age1_1,)
            row += (age2_1,)
            row += (age3_1,)
            row += (age4_1,)
            row += (age5_1,)
            row += (age6_1,)
            row += (edu1_1,)
            row += (edu2_1,)
            row += (edu3_1,)
            row += (edu4_1,)
            row += (edu5_1,)
            row += (edu6_1,)
            row += (edu7_1,)
            row += (edu8_1,)
            row += (edu9_1,)
            row += (allcnt_1,)

            row += (male_2 if course_id in course_cert_date else '-',)
            row += (female_2 if course_id in course_cert_date else '-',)
            row += (etc_2 if course_id in course_cert_date else '-',)
            row += (age1_2 if course_id in course_cert_date else '-',)
            row += (age2_2 if course_id in course_cert_date else '-',)
            row += (age3_2 if course_id in course_cert_date else '-',)
            row += (age4_2 if course_id in course_cert_date else '-',)
            row += (age5_2 if course_id in course_cert_date else '-',)
            row += (age6_2 if course_id in course_cert_date else '-',)
            row += (edu1_2 if course_id in course_cert_date else '-',)
            row += (edu2_2 if course_id in course_cert_date else '-',)
            row += (edu3_2 if course_id in course_cert_date else '-',)
            row += (edu4_2 if course_id in course_cert_date else '-',)
            row += (edu5_2 if course_id in course_cert_date else '-',)
            row += (edu6_2 if course_id in course_cert_date else '-',)
            row += (edu7_2 if course_id in course_cert_date else '-',)
            row += (edu8_2 if course_id in course_cert_date else '-',)
            row += (edu9_2 if course_id in course_cert_date else '-',)
            row += (allcnt_2 if course_id in course_cert_date else '-',)

            row += (male_3 if course_id in course_cert_date else '-',)
            row += (female_3 if course_id in course_cert_date else '-',)
            row += (etc_3 if course_id in course_cert_date else '-',)
            row += (age1_3 if course_id in course_cert_date else '-',)
            row += (age2_3 if course_id in course_cert_date else '-',)
            row += (age3_3 if course_id in course_cert_date else '-',)
            row += (age4_3 if course_id in course_cert_date else '-',)
            row += (age5_3 if course_id in course_cert_date else '-',)
            row += (age6_3 if course_id in course_cert_date else '-',)
            row += (edu1_3 if course_id in course_cert_date else '-',)
            row += (edu2_3 if course_id in course_cert_date else '-',)
            row += (edu3_3 if course_id in course_cert_date else '-',)
            row += (edu4_3 if course_id in course_cert_date else '-',)
            row += (edu5_3 if course_id in course_cert_date else '-',)
            row += (edu6_3 if course_id in course_cert_date else '-',)
            row += (edu7_3 if course_id in course_cert_date else '-',)
            row += (edu8_3 if course_id in course_cert_date else '-',)
            row += (edu9_3 if course_id in course_cert_date else '-',)
            row += (allcnt_3 if course_id in course_cert_date else '-',)

            sortlist.append(row)

        sortlist.sort(key=itemgetter(0, 4, 5))

        start_row = 4
        for course_info in sortlist:
            print len(course_info), course_info

            start_char = 65
            for idx in range(0, len(course_info)):
                if start_char > 116:
                    print 'type3:', start_char - 52, idx, 'B' + chr(start_char - 52) + str(start_row)

                    ws3['B' + chr(start_char - 52) + str(start_row)] = course_info[idx]
                    style_base(ws3['B' + chr(start_char - 52) + str(start_row)])

                    start_char += 1
                elif start_char > 90:
                    print 'type2:', start_char - 26, idx, 'A' + chr(start_char - 26) + str(start_row)

                    ws3['A' + chr(start_char - 26) + str(start_row)] = course_info[idx]
                    style_base(ws3['A' + chr(start_char - 26) + str(start_row)])

                    start_char += 1
                else:
                    print 'type1:', start_char, idx, chr(start_char) + str(start_row)

                    ws3[chr(start_char) + str(start_row)] = course_info[idx]
                    style_base(ws3[chr(start_char) + str(start_row)])

                    start_char += 1
                    # print 'case2:',  chr(start_char) + str(start_row)

            start_row += 1

        wb.save(save_path)
    return HttpResponse('/manage/home/static/excel/' + save_name, content_type='application/vnd.ms-excel')


"""
# 주간통계 : week
def statistics_excel_week(request, date):
    print 'run statistics_excel_week'
    time.sleep(1)

    save_name = 'K-MoocWeek{0}.xlsx'.format(date)
    save_path = EXCEL_PATH + save_name

    if os.path.isfile(save_path):
        print 'file exists. so just download.'
    else:
        # Get course name
        course_ids_all = statistics_query.course_ids_all()

        print 'len(course_ids_all) = ', len(course_ids_all)
        for cc in course_ids_all:
            print 'cc ================================================>', cc[0]

        time.sleep(3)

        client = MongoClient(database_id, 27017)
        db = client.edxapp
        course_orgs = {}
        course_names = {}
        course_creates = {}
        course_starts = {}
        course_ends = {}
        course_enroll_starts = {}
        course_enroll_ends = {}
        course_classfys = {}
        course_middle_classfys = {}
        course_effort = {}
        course_week = {}
        course_video = {}
        course_cert = {}
        course_last_update = {}
        course_status = {}

        print 'step1 : course_info search'

        for course_id, display_name, course, org, start, end, enrollment_start, enrollment_end, effort, cert_date in course_ids_all:

            if start is None or start == '' or end is None or end == '':
                course_status[course_id] = ''
            elif datetime.datetime.utcnow() < start:
                course_status[course_id] = '개강예정'
            elif start <= datetime.datetime.utcnow() <= end:
                course_status[course_id] = '운영중'
            elif cert_date and end < datetime.datetime.utcnow() and cert_date < datetime.datetime.utcnow():
                course_status[course_id] = '이수증발급'
            elif end < datetime.datetime.utcnow():
                course_status[course_id] = '종료'
            else:
                course_status[course_id] = ''

            print course_id, org, display_name, start, end, enrollment_start, enrollment_end
            cid = course_id.split('+')[1]
            run = course_id.split('+')[2]

            course_effort[course_id] = effort.split('@')[0] if effort and '@' in effort else '-'
            course_week[course_id] = effort.split('@')[1].split('#')[0] if effort and '@' in effort and '#' in effort else '-'
            course_video[course_id] = effort.split('#')[1] if effort and '#' in effort else '-'
            course_cert[course_id] = cert_date if effort and cert_date else ''

            cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
            if not cursor:
                print 'not exists: ', cid, run
                continue

            pb = cursor.get('versions').get('published-branch')
            # course_orgs
            course_orgs[course_id] = cursor.get('org')
            course_creates[course_id] = cursor.get('edited_on')
            course_last_update[course_id] = cursor.get('last_update')

            cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},
                                                        {"blocks": {"$elemMatch": {"block_type": "course"}}})

            _classfy = cursor.get('blocks')[0].get('fields').get('classfy')  # classfy
            _mclassfy = cursor.get('blocks')[0].get('fields').get('middle_classfy')  # middle_classfy

            if start is not None:
                course_starts[course_id] = start

            if end is not None:
                course_ends[course_id] = end

            if enrollment_start is not None:
                course_enroll_starts[course_id] = enrollment_start

            if enrollment_end is not None:
                course_enroll_ends[course_id] = enrollment_end

            if display_name is not None:
                course_names[course_id] = display_name

            if _classfy is not None and _classfy != 'all':
                course_classfys[course_id] = classfy[_classfy] if _classfy in classfy else _classfy

            if _mclassfy is not None and _mclassfy != 'all':
                course_middle_classfys[course_id] = middle_classfy[_mclassfy] if _mclassfy in middle_classfy else _mclassfy

        print 'step2 : mysql search'
        # 요약
        auth_user_info_week = statistics_query.auth_user_info_week(date)
        student_courseenrollment_info_week = statistics_query.student_courseenrollment_info_week(date)
        student_activity_week = statistics_query.student_activity_week(date)
        student_cert_week = statistics_query.student_cert_week(date)

        print 'step3: info '
        wb = load_workbook(EXCEL_PATH + 'base_week.xlsx')
        ws1 = wb['summary']
        ws2 = wb['by_course_KPI']
        ws3 = wb['user']

        # excel style
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        fill = None

        font = Font(b=True, color="000000")
        # font = None
        al = Alignment(horizontal="center", vertical="center")

        # # sheet1
        style_range(ws1, 'B2:C3', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'D2:E2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'F2:G2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'B4:B7', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'B8:B10', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'B11:B14', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'B15:B16', border=thin_border, fill=fill, font=font, alignment=al)

        # style_range(ws1, 'C16:F16', border=thin_border, fill=fill, font=font, alignment=al)
        # style_range(ws1, 'G16:J16', border=thin_border, fill=fill, font=font, alignment=al)
        # style_range(ws1, 'B16:B17', border=thin_border, fill=fill, font=font, alignment=al)
        #
        # style_range(ws1, 'B27:B28', border=thin_border, fill=fill, font=font, alignment=al)
        # style_range(ws1, 'C27:F27', border=thin_border, fill=fill, font=font, alignment=al)
        # style_range(ws1, 'G27:J27', border=thin_border, fill=fill, font=font, alignment=al)
        #
        # style_range(ws1, 'B41:B42', border=thin_border, fill=fill, font=font, alignment=al)
        # style_range(ws1, 'C41:L41', border=thin_border, fill=fill, font=font, alignment=al)
        #
        # # sheet2
        style_range(ws2, 'A1:J2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'K1:Q2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'R1:V1', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'R2:S2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'T2:U2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'W1:Z2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'AA1:AB2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'AC1:AC3', border=thin_border, fill=fill, font=font, alignment=al)
        #
        # # sheet3
        # style_range(ws3, 'A1:K2', border=thin_border, fill=fill, font=font, alignment=al)
        # style_range(ws3, 'L1:AD1', border=thin_border, fill=fill, font=font, alignment=al)
        # style_range(ws3, 'L2:N2', border=thin_border, fill=fill, font=font, alignment=al)
        # style_range(ws3, 'O2:T2', border=thin_border, fill=fill, font=font, alignment=al)
        # style_range(ws3, 'U2:AC2', border=thin_border, fill=fill, font=font, alignment=al)
        # style_range(ws3, 'AD2:AD3', border=thin_border, fill=fill, font=font, alignment=al)

        # summary

        # 회원가입
        ws1['E4'] = auth_user_info_week[0][0]
        ws1['E5'] = auth_user_info_week[0][1]
        ws1['E7'] = auth_user_info_week[0][2]
        ws1['G4'] = auth_user_info_week[0][3]
        ws1['G5'] = auth_user_info_week[0][4]
        ws1['G7'] = auth_user_info_week[0][5]

        # 수강신청
        ws1['D8'] = student_courseenrollment_info_week[0][0]
        ws1['D9'] = student_courseenrollment_info_week[0][1]
        ws1['E8'] = student_courseenrollment_info_week[0][2]
        ws1['E9'] = student_courseenrollment_info_week[0][3]
        ws1['F8'] = student_courseenrollment_info_week[0][4]
        ws1['F9'] = student_courseenrollment_info_week[0][5]
        ws1['G8'] = student_courseenrollment_info_week[0][6]
        ws1['G9'] = student_courseenrollment_info_week[0][7]

        # 학습활동
        ws1['D11'] = student_activity_week[0][0]
        ws1['D12'] = student_activity_week[0][1]
        ws1['D14'] = student_activity_week[0][2]
        ws1['E11'] = student_activity_week[0][0]
        ws1['E12'] = student_activity_week[0][1]
        ws1['E14'] = student_activity_week[0][2]
        ws1['F11'] = student_activity_week[0][0]
        ws1['F12'] = student_activity_week[0][1]
        ws1['F14'] = student_activity_week[0][2]
        ws1['G11'] = student_activity_week[0][0]
        ws1['G12'] = student_activity_week[0][1]
        ws1['G14'] = student_activity_week[0][2]

        # 이수자수
        ws1['D15'] = student_cert_week[0][0]
        ws1['D16'] = student_cert_week[0][1]
        ws1['E15'] = student_cert_week[0][2]
        ws1['E16'] = student_cert_week[0][3]
        ws1['F15'] = student_cert_week[0][4]
        ws1['F16'] = student_cert_week[0][5]
        ws1['G15'] = student_cert_week[0][6]
        ws1['G16'] = student_cert_week[0][7]

        # by_course_KPI
        sortlist = list()
        for c in course_ids_all:
            print 'course_id =======================================>', c

            by_course_enroll_week = statistics_query.by_course_enroll_week(c[0], date)
            by_course_enroll_week_activity = statistics_query.by_course_enroll_week_activity(c[0], date)
            by_course_cert_month = statistics_query.by_course_cert_month(c[0])

            row = tuple()
            for course_id, org, new_enroll_cnt, new_unenroll_cnt, all_enroll_cnt, all_unenroll_cnt in by_course_enroll_week:
                row += (dic_univ[org] if org in dic_univ else org,)
                row += (course_classfys[course_id] if course_id in course_classfys else '',)
                row += (course_middle_classfys[course_id] if course_id in course_middle_classfys else '',)
                row += (course_names[course_id],)

                # 주간 학습 권장시간
                row += (course_effort[course_id],)
                # 총 동영상 재생시간
                row += (course_video[course_id],)
                # 총 주차
                row += (course_week[course_id],)

                row += (org,)
                row += (course_id.split('+')[1],)
                row += (course_id.split('+')[2],)
                row += (course_status[course_id],)
                row += (course_creates[course_id],)
                row += (course_enroll_starts[course_id],)
                row += (course_enroll_ends[course_id],)
                row += (course_starts[course_id],)
                row += (course_ends[course_id],)
                row += (course_cert[course_id],)
                row += (new_enroll_cnt,)
                row += (new_unenroll_cnt,)
                row += (all_enroll_cnt,)
                row += (all_unenroll_cnt,)

                if all_enroll_cnt is None or all_unenroll_cnt is None:
                    row += ('-',)
                else:
                    row += (all_enroll_cnt - all_unenroll_cnt,)

            for video1, problem1, both1, video2, problem2, both2 in by_course_enroll_week_activity:
                # row += (video1, problem1, both1,)
                row += (video2, problem2, both2,)

            for course_id, is_exists, half_cnt, cert_cnt in by_course_cert_month:
                if is_exists:
                    row += (half_cnt, cert_cnt,)
                else:
                    row += ('-', '-',)

            row += (course_last_update[course_id],)

            sortlist.append(row)

        sortlist.sort(key=itemgetter(0, 4, 5))

        start_row = 4
        for course_info in sortlist:
            print 'course_info s --------------------------------------------------------'
            print len(course_info), course_info
            print 'course_info e --------------------------------------------------------'
            ws2['A' + str(start_row)] = course_info[0]
            ws2['B' + str(start_row)] = course_info[1]
            ws2['C' + str(start_row)] = course_info[2]
            ws2['D' + str(start_row)] = course_info[3]
            ws2['E' + str(start_row)] = course_info[4]
            ws2['F' + str(start_row)] = course_info[5]
            ws2['G' + str(start_row)] = course_info[6]
            ws2['H' + str(start_row)] = course_info[7]
            ws2['I' + str(start_row)] = course_info[8]
            ws2['J' + str(start_row)] = course_info[9]
            ws2['K' + str(start_row)] = course_info[10]
            ws2['L' + str(start_row)] = course_info[11]
            ws2['M' + str(start_row)] = course_info[12]
            ws2['N' + str(start_row)] = course_info[13]
            ws2['O' + str(start_row)] = course_info[14]
            ws2['P' + str(start_row)] = course_info[15]
            ws2['Q' + str(start_row)] = course_info[16]
            ws2['R' + str(start_row)] = course_info[17]
            ws2['S' + str(start_row)] = course_info[18]
            ws2['T' + str(start_row)] = course_info[19]
            ws2['U' + str(start_row)] = course_info[20]
            ws2['V' + str(start_row)] = course_info[21]

            # 학습활동자수
            ws2['W' + str(start_row)] = course_info[22] if len(course_info) > 22 else ''
            ws2['X' + str(start_row)] = course_info[23] if len(course_info) > 23 else ''
            # ws2['Y' + str(start_row)] = '-'
            ws2['Z' + str(start_row)] = course_info[24] if len(course_info) > 24 else ''

            # 이수
            ws2['AA' + str(start_row)] = course_info[25] if len(course_info) > 25 else ''
            ws2['AB' + str(start_row)] = course_info[26] if len(course_info) > 26 else ''

            # 업데이트
            ws2['AC' + str(start_row)] = course_info[27] if len(course_info) > 27 else ''

            style_base(ws2['A' + str(start_row)])
            style_base(ws2['B' + str(start_row)])
            style_base(ws2['C' + str(start_row)])
            style_base(ws2['D' + str(start_row)])
            style_base(ws2['E' + str(start_row)])
            style_base(ws2['F' + str(start_row)])
            style_base(ws2['G' + str(start_row)])
            style_base(ws2['H' + str(start_row)])
            style_base(ws2['I' + str(start_row)])
            style_base(ws2['J' + str(start_row)])
            style_base(ws2['K' + str(start_row)])
            style_base(ws2['L' + str(start_row)])
            style_base(ws2['M' + str(start_row)])
            style_base(ws2['N' + str(start_row)])
            style_base(ws2['O' + str(start_row)])
            style_base(ws2['P' + str(start_row)])
            style_base(ws2['Q' + str(start_row)])
            style_base(ws2['R' + str(start_row)])
            style_base(ws2['S' + str(start_row)])
            style_base(ws2['T' + str(start_row)])
            style_base(ws2['U' + str(start_row)])
            style_base(ws2['V' + str(start_row)])
            style_base(ws2['W' + str(start_row)])
            style_base(ws2['X' + str(start_row)])
            # style_base(ws2['Y' + str(start_row)])
            style_base(ws2['Z' + str(start_row)])
            style_base(ws2['AA' + str(start_row)])
            style_base(ws2['AB' + str(start_row)])
            style_base(ws2['AC' + str(start_row)])

            start_row += 1

        # user
        member_statistics = statistics_query.member_statistics(date)
        country_statistics = statistics_query.country_statistics(date)
        thin_border = Border(left=Side(style='thin'),
                             right=Side(style='thin'),
                             top=Side(style='thin'),
                             bottom=Side(style='thin'))

        row = 2
        for c in member_statistics:
            ws3['B' + str(row + 1)] = c[0]
            ws3['B' + str(row + 2)] = c[1]
            ws3['B' + str(row + 3)] = c[2]

        row = 8
        for c in country_statistics:
            ws3['A' + str(row)] = c[0]
            ws3['B' + str(row)] = c[1]
            ws3['C' + str(row)] = countries[c[0]] if c[0] in countries else c[0]

            ws3['A' + str(row)].border = thin_border
            ws3['B' + str(row)].border = thin_border
            ws3['C' + str(row)].border = thin_border
            row += 1

        wb.save(save_path)
    return HttpResponse('/manage/home/static/excel/' + save_name, content_type='application/vnd.ms-excel')


# 월별통계 : month
def statistics_excel_month(request, date):
    print 'run statistics_excel_month'
    time.sleep(1)

    date = date[:6]

    print 'date = ', date

    time.sleep(2)

    save_name = 'K-MoocMonth{0}.xlsx'.format(date)
    save_path = EXCEL_PATH + save_name

    if os.path.isfile(save_path):
        print 'file exists. so just download.'
    else:
        # Get course name
        course_ids_all = statistics_query.course_ids_all()

        print 'len(course_ids_all) = ', len(course_ids_all)
        for cc in course_ids_all:
            print 'cc ================================================>', cc[0]

        time.sleep(3)

        client = MongoClient(database_id, 27017)
        db = client.edxapp
        course_orgs = {}
        course_names = {}
        course_creates = {}
        course_starts = {}
        course_ends = {}
        course_enroll_starts = {}
        course_enroll_ends = {}
        course_classfys = {}
        course_middle_classfys = {}
        course_effort = {}
        course_week = {}
        course_video = {}
        course_cert = {}
        course_last_update = {}
        course_status = {}

        print 'step1 : course_info search'

        for course_id, display_name, course, org, start, end, enrollment_start, enrollment_end, effort, cert_date in course_ids_all:

            if start is None or start == '' or end is None or end == '':
                course_status[course_id] = ''
            elif datetime.datetime.utcnow() < start:
                course_status[course_id] = '개강예정'
            elif start <= datetime.datetime.utcnow() <= end:
                course_status[course_id] = '운영중'
            elif cert_date and end < datetime.datetime.utcnow() and cert_date < datetime.datetime.utcnow():
                course_status[course_id] = '이수증발급'
            elif end < datetime.datetime.utcnow():
                course_status[course_id] = '종료'
            else:
                course_status[course_id] = ''

            print course_id, org, display_name, start, end, enrollment_start, enrollment_end
            cid = course_id.split('+')[1]
            run = course_id.split('+')[2]

            course_effort[course_id] = effort.split('@')[0] if effort and '@' in effort else '-'
            course_week[course_id] = effort.split('@')[1].split('#')[0] if effort and '@' in effort and '#' in effort else '-'
            course_video[course_id] = effort.split('#')[1] if effort and '#' in effort else '-'
            course_cert[course_id] = cert_date if effort and cert_date else ''

            cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
            if not cursor:
                print 'not exists: ', cid, run
                continue

            pb = cursor.get('versions').get('published-branch')
            # course_orgs
            course_orgs[course_id] = cursor.get('org')
            course_creates[course_id] = cursor.get('edited_on')
            course_last_update[course_id] = cursor.get('last_update')

            cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},
                                                        {"blocks": {"$elemMatch": {"block_type": "course"}}})

            _classfy = cursor.get('blocks')[0].get('fields').get('classfy')  # classfy
            _mclassfy = cursor.get('blocks')[0].get('fields').get('middle_classfy')  # middle_classfy

            if start is not None:
                course_starts[course_id] = start

            if end is not None:
                course_ends[course_id] = end

            if enrollment_start is not None:
                course_enroll_starts[course_id] = enrollment_start

            if enrollment_end is not None:
                course_enroll_ends[course_id] = enrollment_end

            if display_name is not None:
                course_names[course_id] = display_name

            if _classfy is not None and _classfy != 'all':
                course_classfys[course_id] = classfy[_classfy] if _classfy in classfy else _classfy

            if _mclassfy is not None and _mclassfy != 'all':
                course_middle_classfys[course_id] = middle_classfy[_mclassfy] if _mclassfy in middle_classfy else _mclassfy

        print 'step2 : mysql search'
        # 요약
        auth_user_info_month = statistics_query.auth_user_info_month(date)
        student_courseenrollment_info_month = statistics_query.student_courseenrollment_info_month(date)
        student_activity_month = statistics_query.student_activity_month(date)
        student_cert_month = statistics_query.student_cert_month(date)

        print 'step3: info '
        wb = load_workbook(EXCEL_PATH + 'base_month.xlsx')
        ws1 = wb['summary']
        ws2 = wb['by_course_KPI']
        ws3 = wb['user']

        # excel style
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        fill = None

        font = Font(b=True, color="000000")
        # font = None
        al = Alignment(horizontal="center", vertical="center")

        # # sheet1
        style_range(ws1, 'B2:C3', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'D2:E2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'F2:G2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'B4:B7', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'B8:B10', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'B11:B14', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws1, 'B15:B16', border=thin_border, fill=fill, font=font, alignment=al)

        # # sheet2
        style_range(ws2, 'A1:J2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'K1:Q2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'R1:V1', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'R2:S2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'T2:U2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'W1:Z2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'AA1:AB2', border=thin_border, fill=fill, font=font, alignment=al)
        style_range(ws2, 'AC1:AC3', border=thin_border, fill=fill, font=font, alignment=al)

        # summary

        # 회원가입
        ws1['E4'] = auth_user_info_month[0][0]
        ws1['E5'] = auth_user_info_month[0][1]
        ws1['E7'] = auth_user_info_month[0][2]
        ws1['G4'] = auth_user_info_month[0][3]
        ws1['G5'] = auth_user_info_month[0][4]
        ws1['G7'] = auth_user_info_month[0][5]

        # 수강신청
        ws1['D8'] = student_courseenrollment_info_month[0][0]
        ws1['D9'] = student_courseenrollment_info_month[0][1]
        ws1['E8'] = student_courseenrollment_info_month[0][2]
        ws1['E9'] = student_courseenrollment_info_month[0][3]
        ws1['F8'] = student_courseenrollment_info_month[0][4]
        ws1['F9'] = student_courseenrollment_info_month[0][5]
        ws1['G8'] = student_courseenrollment_info_month[0][6]
        ws1['G9'] = student_courseenrollment_info_month[0][7]

        # 학습활동
        ws1['D11'] = student_activity_month[0][0]
        ws1['D12'] = student_activity_month[0][1]
        ws1['D14'] = student_activity_month[0][2]
        ws1['E11'] = student_activity_month[0][0]
        ws1['E12'] = student_activity_month[0][1]
        ws1['E14'] = student_activity_month[0][2]
        ws1['F11'] = student_activity_month[0][0]
        ws1['F12'] = student_activity_month[0][1]
        ws1['F14'] = student_activity_month[0][2]
        ws1['G11'] = student_activity_month[0][0]
        ws1['G12'] = student_activity_month[0][1]
        ws1['G14'] = student_activity_month[0][2]

        # 이수자수
        ws1['D15'] = student_cert_month[0][0]
        ws1['D16'] = student_cert_month[0][1]
        ws1['E15'] = student_cert_month[0][2]
        ws1['E16'] = student_cert_month[0][3]
        ws1['F15'] = student_cert_month[0][4]
        ws1['F16'] = student_cert_month[0][5]
        ws1['G15'] = student_cert_month[0][6]
        ws1['G16'] = student_cert_month[0][7]

        # by_course_KPI
        sortlist = list()
        for c in course_ids_all:
            print 'course_id =======================================>', c

            by_course_enroll_month = statistics_query.by_course_enroll_month(c[0], date)
            by_course_enroll_month_activity = statistics_query.by_course_enroll_month_activity(c[0], date)
            by_course_cert_month = statistics_query.by_course_cert_month(c[0])

            row = tuple()
            for course_id, org, new_enroll_cnt, new_unenroll_cnt, all_enroll_cnt, all_unenroll_cnt in by_course_enroll_month:
                row += (dic_univ[org] if org in dic_univ else org,)
                row += (course_classfys[course_id] if course_id in course_classfys else '',)
                row += (course_middle_classfys[course_id] if course_id in course_middle_classfys else '',)
                row += (course_names[course_id],)

                # 주간 학습 권장시간
                row += (course_effort[course_id],)
                # 총 동영상 재생시간
                row += (course_video[course_id],)
                # 총 주차
                row += (course_week[course_id],)

                row += (org,)
                row += (course_id.split('+')[1],)
                row += (course_id.split('+')[2],)
                row += (course_status[course_id],)
                row += (course_creates[course_id],)
                row += (course_enroll_starts[course_id],)
                row += (course_enroll_ends[course_id],)
                row += (course_starts[course_id],)
                row += (course_ends[course_id],)
                row += (course_cert[course_id],)
                row += (new_enroll_cnt,)
                row += (new_unenroll_cnt,)
                row += (all_enroll_cnt,)
                row += (all_unenroll_cnt,)

                if all_enroll_cnt is None or all_unenroll_cnt is None:
                    row += ('-',)
                else:
                    row += (all_enroll_cnt - all_unenroll_cnt,)

            for video1, problem1, both1, video2, problem2, both2 in by_course_enroll_month_activity:
                # row += (video1, problem1, both1,)
                row += (video2, problem2, both2,)

            for course_id, is_exists, half_cnt, cert_cnt in by_course_cert_month:
                if is_exists:
                    row += (half_cnt, cert_cnt,)
                else:
                    row += ('-', '-',)

            row += (course_last_update[course_id],)

            sortlist.append(row)

        sortlist.sort(key=itemgetter(0, 4, 5))

        start_row = 4
        for course_info in sortlist:
            print 'course_info s --------------------------------------------------------'
            print len(course_info), course_info
            print 'course_info e --------------------------------------------------------'
            ws2['A' + str(start_row)] = course_info[0]
            ws2['B' + str(start_row)] = course_info[1]
            ws2['C' + str(start_row)] = course_info[2]
            ws2['D' + str(start_row)] = course_info[3]
            ws2['E' + str(start_row)] = course_info[4]
            ws2['F' + str(start_row)] = course_info[5]
            ws2['G' + str(start_row)] = course_info[6]
            ws2['H' + str(start_row)] = course_info[7]
            ws2['I' + str(start_row)] = course_info[8]
            ws2['J' + str(start_row)] = course_info[9]
            ws2['K' + str(start_row)] = course_info[10]
            ws2['L' + str(start_row)] = course_info[11]
            ws2['M' + str(start_row)] = course_info[12]
            ws2['N' + str(start_row)] = course_info[13]
            ws2['O' + str(start_row)] = course_info[14]
            ws2['P' + str(start_row)] = course_info[15]
            ws2['Q' + str(start_row)] = course_info[16]
            ws2['R' + str(start_row)] = course_info[17]
            ws2['S' + str(start_row)] = course_info[18]
            ws2['T' + str(start_row)] = course_info[19]
            ws2['U' + str(start_row)] = course_info[20]
            ws2['V' + str(start_row)] = course_info[21]

            # 학습활동자수
            ws2['W' + str(start_row)] = course_info[22] if len(course_info) > 22 else ''
            ws2['X' + str(start_row)] = course_info[23] if len(course_info) > 23 else ''
            # ws2['Y' + str(start_row)] = '-'
            ws2['Z' + str(start_row)] = course_info[24] if len(course_info) > 24 else ''

            # 이수
            ws2['AA' + str(start_row)] = course_info[25] if len(course_info) > 25 else ''
            ws2['AB' + str(start_row)] = course_info[26] if len(course_info) > 26 else ''

            # 업데이트
            ws2['AC' + str(start_row)] = course_info[27] if len(course_info) > 27 else ''

            style_base(ws2['A' + str(start_row)])
            style_base(ws2['B' + str(start_row)])
            style_base(ws2['C' + str(start_row)])
            style_base(ws2['D' + str(start_row)])
            style_base(ws2['E' + str(start_row)])
            style_base(ws2['F' + str(start_row)])
            style_base(ws2['G' + str(start_row)])
            style_base(ws2['H' + str(start_row)])
            style_base(ws2['I' + str(start_row)])
            style_base(ws2['J' + str(start_row)])
            style_base(ws2['K' + str(start_row)])
            style_base(ws2['L' + str(start_row)])
            style_base(ws2['M' + str(start_row)])
            style_base(ws2['N' + str(start_row)])
            style_base(ws2['O' + str(start_row)])
            style_base(ws2['P' + str(start_row)])
            style_base(ws2['Q' + str(start_row)])
            style_base(ws2['R' + str(start_row)])
            style_base(ws2['S' + str(start_row)])
            style_base(ws2['T' + str(start_row)])
            style_base(ws2['U' + str(start_row)])
            style_base(ws2['V' + str(start_row)])
            style_base(ws2['W' + str(start_row)])
            style_base(ws2['X' + str(start_row)])
            # style_base(ws2['Y' + str(start_row)])
            style_base(ws2['Z' + str(start_row)])
            style_base(ws2['AA' + str(start_row)])
            style_base(ws2['AB' + str(start_row)])
            style_base(ws2['AC' + str(start_row)])

            start_row += 1

        # user
        member_statistics = statistics_query.member_statistics(date + '31')
        country_statistics = statistics_query.country_statistics(date + '31')
        thin_border = Border(left=Side(style='thin'),
                             right=Side(style='thin'),
                             top=Side(style='thin'),
                             bottom=Side(style='thin'))

        row = 2
        for c in member_statistics:
            ws3['B' + str(row + 1)] = c[0]
            ws3['B' + str(row + 2)] = c[1]
            ws3['B' + str(row + 3)] = c[2]

        row = 8
        for c in country_statistics:
            ws3['A' + str(row)] = c[0]
            ws3['B' + str(row)] = c[1]
            ws3['C' + str(row)] = countries[c[0]] if c[0] in countries else c[0]

            ws3['A' + str(row)].border = thin_border
            ws3['B' + str(row)].border = thin_border
            ws3['C' + str(row)].border = thin_border
            row += 1

        wb.save(save_path)
    return HttpResponse('/manage/home/static/excel/' + save_name, content_type='application/vnd.ms-excel')



def statistics_excel1(request, date):
    save_name = 'K-MoocMonth' + date + '.xlsx'
    save_path = EXCEL_PATH + save_name

    if os.path.isfile(save_path):
        pass
    else:
        member_statistics = statistics_query.member_statistics(date)
        country_statistics = statistics_query.country_statistics(date)
        print 'country_statistics == ', country_statistics
        wb = load_workbook(EXCEL_PATH + 'basic_month.xlsx')
        thin_border = Border(left=Side(style='thin'),
                             right=Side(style='thin'),
                             top=Side(style='thin'),
                             bottom=Side(style='thin'))



        ws1 = wb['Sheet1']

        row = 2
        for c in member_statistics:
            ws1['B' + str(row + 1)] = c[0]
            ws1['B' + str(row + 2)] = c[1]
            ws1['B' + str(row + 3)] = c[2]

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
"""


def get_value_from_dict(dict, key, default=None):
    if default == None:
        default = key
    return dict[key] if key in dict else default
