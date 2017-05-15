# -*- coding: utf-8 -*-
import statistics
from django.db import connection
import logging
import logging.handlers
from management.settings import EXCEL_PATH, dic_univ, database_id, debug
import time, threading


# # 로거 인스턴스를 만든다
# logger = logging.getLogger('statistics_query log')
#
# # 포매터를 만든다
# fomatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
#
# # 스트림과 파일로 로그를 출력하는 핸들러를 각각 만든다.
# fileHandler = logging.FileHandler('./statistics_query.log')
# streamHandler = logging.StreamHandler()
#
# # 각 핸들러에 포매터를 지정한다.
# fileHandler.setFormatter(fomatter)
# streamHandler.setFormatter(fomatter)
#
# # 로거 인스턴스에 스트림 핸들러와 파일핸들러를 붙인다.
# #logger.addHandler(fileHandler)
# #logger.addHandler(streamHandler)
#
# if debug:
#     #logger.setLevel(logging.DEBUG)

class TimePrint(threading.Thread):
    def __init__(self):
        print 'TimePrint __init__ called'
        threading.Thread.__init__(self)
        time.sleep(1)
        self.__exit = False

    def run(self):
        sec = 1
        while True:
            if self.__exit:
                break
            print 'sec:', sec

            # Suspend
            time.sleep(1)

            # Process
            sec = sec + 1

            # Exit


    def my_exit(self):
        self.__exit = True


def execute_query_one(query):
    start_time = time.time()

    print '--> query:\n', query

    with connection.cursor() as cur:
        cur.execute(query)
        row = cur.fetchone()[0]

    end_time = time.time()

    print '--> duration time:', end_time - start_time

    return row


def execute_query(query):
    start_time = time.time()

    print '-->> query:\n', query

    tp = TimePrint()
    tp.start()
    with connection.cursor() as cur:
        cur.execute(query)
        row = cur.fetchall()
    tp.my_exit()

    end_time = time.time()

    print '-->> duration time:\n-------------------------------------->', end_time - start_time

    return row


# `회원가입 세부사항`
def overall_auth(date):
    query = '''
        SELECT sum(if(date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d') = '{date}',1,0)) new_cnt,
               sum(if(date_format(adddate(last_login, INTERVAL 9 HOUR), '%Y%m%d') = '{date}' and a.email like 'delete_%',1,0)) new_sec_cnt,
               sum(if(date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}',1,0)) all_cnt,
               sum(if(date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}' and a.email like 'delete_%',1,0)) all_sec_cnt
          FROM auth_user a, auth_userprofile b
         WHERE     a.id = b.user_id
               AND date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014'
                                                                                    AND '{date}';
    '''.format(date=date)
    return execute_query(query)


# `수강신청 세부사항`
def overall_enroll(date):
    query = '''
        SELECT sum(if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') = '{date}',1,0)) new_enroll_cnt1,
               sum(if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') = '{date}' and c.is_active = 0,1,0)) new_sec_cnt1,
               sum(if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}',1,0)) all_cnt1,
               sum(if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}' and c.is_active = 0,1,0)) all_sec_cnt1,
               count(distinct if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') = '{date}', a.id,null)) new_enroll_cnt2,
               count(distinct if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') = '{date}' and c.is_active = 0,a.id,null)) new_sec_cnt2,
               count(distinct if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}',a.id,null)) all_cnt2,
               count(distinct if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}' and c.is_active = 0,a.id,null)) all_sec_cnt2
          FROM auth_user a, auth_userprofile b, student_courseenrollment c, course_overviews_courseoverview d
         WHERE     a.id = b.user_id
               and a.id = c.user_id
               and c.course_id = d.id
               AND lower(c.course_id) NOT LIKE '%test%'
               AND lower(c.course_id) NOT LIKE '%demo%'
               AND lower(c.course_id) NOT LIKE '%nile%'
               AND date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                    AND '{date}'
               AND date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                    AND '{date}';
    '''.format(date=date)
    return execute_query(query)


# `by_course_enroll`
def by_course_enroll(course_id, date):
    query = '''
        SELECT a.id,
               a.org,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m%d') = '{date}', 1, 0)) `new_enroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m%d') = '{date}' AND b.is_active = 0, 1, 0)) `new_unenroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}', 1, 0)) `all_enroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}' AND b.is_active = 0, 1, 0)) `all_unenroll_cnt`
          FROM course_overviews_courseoverview a,
               student_courseenrollment        b,
               auth_user                       c,
               auth_userprofile                d
         WHERE     a.id = b.course_id
               AND b.user_id = c.id
               AND c.id = d.user_id
               AND date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                    AND '{date}'
               AND date_format(adddate(c.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                    AND '{date}'
               AND a.id = '{course_id}'
         group by a.id,  a.org;
    '''.format(course_id=course_id, date=date)
    # query = '''
    #       SELECT a.id,
    #              a.org,
    #              sum(
    #                 if(
    #                    date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN   '{date}'
    #                                                                                       - 6
    #                                                                                   AND '{date}',
    #                    1,
    #                    0))
    #                 `new_enroll_cnt`,
    #              sum(
    #                 if(
    #                        date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN   '{date}'
    #                                                                                           - 6
    #                                                                                       AND '{date}'
    #                    AND b.is_active = 0,
    #                    1,
    #                    0))
    #                 `new_unenroll_cnt`,
    #              sum(
    #                 if(
    #                    date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
    #                                                                                   AND '{date}',
    #                    1,
    #                    0))
    #                 `all_enroll_cnt`,
    #              sum(
    #                 if(
    #                        date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
    #                                                                                       AND '{date}'
    #                    AND b.is_active = 0,
    #                    1,
    #                    0))
    #                 `all_unenroll_cnt`
    #         FROM course_overviews_courseoverview a
    #              LEFT JOIN student_courseenrollment b
    #                 ON     a.id = b.course_id
    #                    AND date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
    #                                                                                       AND '{date}'
    #              LEFT JOIN auth_user c
    #                 ON     b.user_id = c.id
    #                    AND date_format(adddate(c.date_joined, INTERVAL 9 HOUR),
    #                                    '%Y%m%d') BETWEEN '1'
    #                                                  AND '{date}'
    #              LEFT JOIN auth_userprofile d ON c.id = d.user_id
    #        WHERE a.id = '{course_id}'
    #     GROUP BY a.id, a.org;
    # '''.format(course_id=course_id, date=date)
    return execute_query(query)


# `by_course_demographic` `코스별 학력`
def by_course_demographic(course_id, date):
    query = '''
          SELECT course_id,
                 org,
                 sum(if(gender = 'm', 1, 0))        male,
                 sum(if(gender = 'f', 1, 0))        female,
                 sum(if(gender is null or gender not in ('m', 'f'), 1, 0))        etc,
                 sum(if(age < 20, 1, 0))            age1,
                 sum(if(age BETWEEN 20 AND 29, 1, 0)) age2,
                 sum(if(age BETWEEN 30 AND 39, 1, 0)) age3,
                 sum(if(age BETWEEN 40 AND 49, 1, 0)) age4,
                 sum(if(age BETWEEN 50 AND 59, 1, 0)) age5,
                 sum(if(age > 59, 1, 0))            age6,
                 sum(if(edu = 'p', 1, 0))           edu1,
                 sum(if(edu = 'm', 1, 0))           edu2,
                 sum(if(edu = 'b', 1, 0))           edu3,
                 sum(if(edu = 'a', 1, 0))           edu4,
                 sum(if(edu = 'hs', 1, 0))          edu5,
                 sum(if(edu = 'jhs', 1, 0))         edu6,
                 sum(if(edu = 'el', 1, 0))          edu7,
                 sum(if(edu = 'other', 1, 0))       edu8,
                 sum(if(edu is null or edu NOT IN ('p',
                                    'm',
                                    'b',
                                    'a',
                                    'hs',
                                    'jhs',
                                    'el',
                                    'other'),
                        1,
                        0))
                    edu9,
                 count(*)                           allcnt
            FROM (SELECT a.id                       course_id,
                         a.org,
                         d.gender,
                         substring('{date}', 1, 4) + 1 - ifnull(d.year_of_birth, 0) age,
                         d.level_of_education       edu
                    FROM course_overviews_courseoverview a,
                         student_courseenrollment      b,
                         auth_user                     c,
                         auth_userprofile              d
                   WHERE     a.id = b.course_id
                         AND b.user_id = c.id
                         AND c.id = d.user_id
                         AND date_format(adddate(c.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                    AND '{date}'
                         AND date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                            AND '{date}'
                         AND b.is_active = 1
                         AND a.id = '{course_id}') t1
        GROUP BY course_id, org;
    '''.format(course_id=course_id, date=date)
    return execute_query(query)


# `by_course_enroll_week`
def by_course_enroll_week(course_id, date):
    query = '''
        SELECT a.id,
               a.org,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m%d') between '{date}' - 6 and '{date}', 1, 0)) `new_enroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m%d') between '{date}' - 6 and '{date}' AND b.is_active = 0, 1, 0)) `new_unenroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}', 1, 0)) `all_enroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}' AND b.is_active = 0, 1, 0)) `all_unenroll_cnt`
          FROM course_overviews_courseoverview a
                left join student_courseenrollment        b on a.id = b.course_id AND date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                    AND '{date}'
                left join auth_user                       c on b.user_id = c.id AND date_format(adddate(c.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                    AND '{date}'
                left join auth_userprofile                d on c.id = d.user_id
         WHERE     a.id = '{course_id}'
         group by a.id,  a.org;
    '''.format(course_id=course_id, date=date)
    return execute_query(query)


def by_course_enroll_month(course_id, date):
    query = '''
        SELECT a.id,
               a.org,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m') = '{date}', 1, 0)) `new_enroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m') = '{date}' AND b.is_active = 0, 1, 0)) `new_unenroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m') BETWEEN '1' AND '{date}', 1, 0)) `all_enroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m') BETWEEN '1' AND '{date}' AND b.is_active = 0, 1, 0)) `all_unenroll_cnt`
          FROM course_overviews_courseoverview a
                left join student_courseenrollment        b on a.id = b.course_id AND date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m') BETWEEN '1'
                                                                                    AND '{date}'
                left join auth_user                       c on b.user_id = c.id AND date_format(adddate(c.date_joined, INTERVAL 9 HOUR), '%Y%m') BETWEEN '1'
                                                                                    AND '{date}'
                left join auth_userprofile                d on c.id = d.user_id
         WHERE     a.id = '{course_id}'
         group by a.id,  a.org;
    '''.format(course_id=course_id, date=date)
    return execute_query(query)


# `by_course_enroll_week`
def by_course_enroll_week_activity(course_id, date):
    query = '''
        SELECT sum(if(modified BETWEEN '{date}' - 6 AND '{date}', `video`, 0))   video1,
               sum(if(modified BETWEEN '{date}' - 6 AND '{date}', `problem`, 0)) problem1,
               sum(if(modified BETWEEN '{date}' - 6 AND '{date}', `both`, 0))    both1,
               sum(if(modified BETWEEN '1' AND '{date}', `video`, 0))   video2,
               sum(if(modified BETWEEN '1' AND '{date}', `problem`, 0)) problem2,
               sum(if(modified BETWEEN '1' AND '{date}', `both`, 0))    both2
          FROM (  SELECT student_id,
                         sum(if(module_type = 'video', 1, 0)) `video`,
                         sum(if(module_type = 'problem', 1, 0))`problem`,
                         date_format(adddate(max(modified), INTERVAL 9 HOUR), '%Y%m%d')
                            `modified`,
                         count(
                            DISTINCT if(
                                           module_type = 'video'
                                        OR module_type = 'problem',
                                        student_id,
                                        0))
                            `both`
                    FROM (  SELECT student_id,
                           module_type,
                           modified,
                           max(grade) grade
                      FROM courseware_studentmodule
                     WHERE     course_id =
                                  '{course_id}'
                           AND module_type IN ('video', 'problem')
                           AND CASE
                                  WHEN module_type = 'problem'
                                  THEN
                                     grade IS NOT NULL
                                  ELSE
                                     1 = 1
                               END
                           AND created <> modified
                  GROUP BY student_id, module_type) t1
                GROUP BY student_id) t2;
        '''.format(course_id=course_id, date=date)
    return execute_query(query)


def by_course_enroll_month_activity(course_id, date):
    query = '''
        SELECT sum(if(modified = '{date}', `video`, 0))   video1,
               sum(if(modified = '{date}', `problem`, 0)) problem1,
               sum(if(modified = '{date}', `both`, 0))    both1,
               sum(if(modified BETWEEN '1' AND '{date}', `video`, 0))   video2,
               sum(if(modified BETWEEN '1' AND '{date}', `problem`, 0)) problem2,
               sum(if(modified BETWEEN '1' AND '{date}', `both`, 0))    both2
          FROM (  SELECT student_id,
                         sum(if(module_type = 'video', 1, 0)) `video`,
                         sum(if(module_type = 'problem', 1, 0))`problem`,
                         date_format(adddate(max(modified), INTERVAL 9 HOUR), '%Y%m')
                            `modified`,
                         count(
                            DISTINCT if(
                                           module_type = 'video'
                                        OR module_type = 'problem',
                                        student_id,
                                        0))
                            `both`
                    FROM (  SELECT student_id,
                           module_type,
                           modified,
                           max(grade) grade
                      FROM courseware_studentmodule
                     WHERE     course_id =
                                  '{course_id}'
                           AND module_type IN ('video', 'problem')
                           AND CASE
                                  WHEN module_type = 'problem'
                                  THEN
                                     grade IS NOT NULL
                                  ELSE
                                     1 = 1
                               END
                           AND created <> modified
                  GROUP BY student_id, module_type) t1
                GROUP BY student_id) t2;
        '''.format(course_id=course_id, date=date)
    return execute_query(query)


# `by_course_enroll_month`
def by_course_enroll_month(date):
    query = '''
        SELECT a.id,
               a.org,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m') = '{date}', 1, 0)) `new_enroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m') = '{date}' AND b.is_active = 0, 1, 0)) `new_unenroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}', 1, 0)) `all_enroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}' AND b.is_active = 0, 1, 0)) `all_unenroll_cnt`
          FROM course_overviews_courseoverview a
                left join student_courseenrollment        b on a.id = b.course_id AND date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                    AND '{date}'
                left join auth_user                       c on b.user_id = c.id AND date_format(adddate(c.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                    AND '{date}'
                left join auth_userprofile                d on c.id = d.user_id
         WHERE    1=1
         group by a.id,  a.org;
    '''.format(date=date)
    return execute_query(query)


# `by_course_enroll_month`
def by_course_enroll_month(course_id, date):
    query = '''
        SELECT a.id,
               a.org,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m') = '{date}', 1, 0)) `new_enroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m') = '{date}' AND b.is_active = 0, 1, 0)) `new_unenroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m') BETWEEN '1' AND '{date}', 1, 0)) `all_enroll_cnt`,
               sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m') BETWEEN '1' AND '{date}' AND b.is_active = 0, 1, 0)) `all_unenroll_cnt`
          FROM course_overviews_courseoverview a
                left join student_courseenrollment        b on a.id = b.course_id AND date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m') BETWEEN '1'
                                                                                    AND '{date}'
                left join auth_user                       c on b.user_id = c.id AND date_format(adddate(c.date_joined, INTERVAL 9 HOUR), '%Y%m') BETWEEN '1'
                                                                                    AND '{date}'
                left join auth_userprofile                d on c.id = d.user_id
         WHERE     a.id = '{course_id}'
         group by a.id,  a.org;
    '''.format(course_id=course_id, date=date)
    return execute_query(query)


# `by_course_cert_month`
def by_course_cert_month(course_id):
    query = '''
      SELECT a.id,
             if(b.course_id IS NOT NULL, TRUE, FALSE)           is_exists,
             sum(if(a.lowest_passing_grade / 2 <= b.grade, 1, 0)) half_cnt,
             sum(if(b.status = 'downloadable', 1, 0))           cert_cnt
        FROM course_overviews_courseoverview a
             LEFT JOIN certificates_generatedcertificate b ON a.id = b.course_id
       WHERE a.id = '{course_id}'
    '''.format(course_id=course_id)
    return execute_query(query)


# `강좌 아이디 조회`
def course_ids_all():
    query = """
        SELECT id,
               display_name,
               display_number_with_default course,
               display_org_with_default    org,
               start,
               end,
               a.enrollment_start,
               a.enrollment_end,
               effort,
               (select min(created_date) from certificates_generatedcertificate b where b.course_id = a.id) cert_date
          FROM course_overviews_courseoverview a
         WHERE     1 = 1
               AND lower(a.id) NOT LIKE '%test%'
               AND lower(a.id) NOT LIKE '%demo%'
               AND lower(a.id) NOT LIKE '%nile%'
               ;
    """
    return execute_query(query)


# `요약`
def auth_user_info(date):
    query = '''
        SELECT sum(
                  if(
                     date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d')   = '{date}',
                     1,
                     0))
                  newcnt,
               sum(if(email LIKE 'delete_%', 0, 1)) allcnt
          FROM auth_user a, auth_userprofile b
         WHERE     a.id = b.user_id
               AND date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014'
                                                                                    AND '{date}';
    '''.format(date=date)
    return execute_query(query)


# `요약 주간`
def auth_user_info_week(date):
    query = '''
        SELECT sum(
                  if(
                     date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN   '{date}'
                                                                                            - 6
                                                                                        AND '{date}',
                     1,
                     0))
                  join_cnt_week,
               sum(
                  if(
                         date_format(adddate(a.date_joined, INTERVAL 9 HOUR),
                                     '%Y%m%d') BETWEEN '{date}' - 6
                                                   AND '{date}'
                     AND a.email LIKE 'delete_%',
                     1,
                     0))
                  sece_cnt_week,
               sum(
                  if(
                         date_format(adddate(a.date_joined, INTERVAL 9 HOUR),
                                     '%Y%m%d') BETWEEN '{date}' - 6
                                                   AND '{date}'
                     AND a.email NOT LIKE 'delete_%'
                     AND a.is_active = 1,
                     1,
                     0))
                  active_cnt_week,
               count(*)                               join_cnt_all,
               sum(if(a.email LIKE 'delete_%', 1, 0)) sece_cnt_all,
               sum(if(a.email NOT LIKE 'delete_%' AND a.is_active = 1, 1, 0))
                  active_cnt_all
          FROM auth_user a, auth_userprofile b
         WHERE     a.id = b.user_id
               AND date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014'
                                                                                      AND '{date}';
    '''.format(date=date)
    return execute_query(query)


def auth_user_info_month(date):
    query = '''
        SELECT sum(
                  if(
                     date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m') = '{date}',
                     1,
                     0))
                  join_cnt_month,
               sum(
                  if(
                         date_format(adddate(a.date_joined, INTERVAL 9 HOUR),
                                     '%Y%m') = '{date}'
                     AND a.email LIKE 'delete_%',
                     1,
                     0))
                  sece_cnt_month,
               sum(
                  if(
                         date_format(adddate(a.date_joined, INTERVAL 9 HOUR),
                                     '%Y%m') = '{date}'
                     AND a.email NOT LIKE 'delete_%'
                     AND a.is_active = 1,
                     1,
                     0))
                  active_cnt_month,
               count(*)                               join_cnt_all,
               sum(if(a.email LIKE 'delete_%', 1, 0)) sece_cnt_all,
               sum(if(a.email NOT LIKE 'delete_%' AND a.is_active = 1, 1, 0))
                  active_cnt_all
          FROM auth_user a, auth_userprofile b
         WHERE     a.id = b.user_id
               AND date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014'
                                                                                      AND '{date}31';
    '''.format(date=date)
    return execute_query(query)


# `수강신청건수`
def student_courseenrollment_info(date):
    query = '''
        SELECT sum(if(date_format(adddate(b.created, interval 9 hour), '%Y%m%d') = '{date}', 1, 0)) newcnt,
               sum(b.is_active)                                           allcnt
          FROM auth_user a, student_courseenrollment b, course_overviews_courseoverview c
         WHERE     1 = 1
               AND a.id = b.user_id
               and b.course_id = c.id
               AND lower(b.course_id) NOT LIKE '%test%'
               AND lower(b.course_id) NOT LIKE '%demo%'
               AND lower(b.course_id) NOT LIKE '%nile%'
               AND date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') <= '{date}'
               AND date_format(adddate(b.created, interval 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}';
    '''.format(date=date)
    return execute_query(query)


# `수강신청건수 주간`
def student_courseenrollment_info_week(date):
    query = '''
        SELECT sum(if(created BETWEEN '{date}' - 6 AND '{date}', 1, 0))
                  week_enroll_cnt,
               sum(
                  if(created BETWEEN '{date}' - 6 AND '{date}' AND is_active = 0,
                     1,
                     0))
                  week_unenroll_cnt,
               count(
                  DISTINCT if(created BETWEEN '{date}' - 6 AND '{date}',
                              id,
                              NULL))
                  week_enroll_person_cnt,
               count(
                  DISTINCT if(
                                  created BETWEEN '{date}' - 6 AND '{date}'
                              AND is_active = 0,
                              id,
                              NULL))
                  week_unenroll_person_cnt,
               sum(if(created BETWEEN '1' AND '{date}', 1, 0)) all_enroll_cnt,
               sum(if(created BETWEEN '1' AND '{date}' AND is_active = 0, 1, 0))
                  all_unenroll_cnt,
               count(DISTINCT if(created BETWEEN '1' AND '{date}', id, NULL))
                  all_enroll_person_cnt,
               count(
                  DISTINCT if(created BETWEEN '1' AND '{date}' AND is_active = 0,
                              id,
                              NULL))
                  all_unenroll_person_cnt
          FROM (SELECT a.id,
                       date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d')
                          created,
                       b.is_active
                  FROM auth_user                       a,
                       student_courseenrollment        b,
                       course_overviews_courseoverview c
                 WHERE     1 = 1
                       AND a.id = b.user_id
                       AND b.course_id = c.id
                       AND lower(b.course_id) NOT LIKE '%test%'
                       AND lower(b.course_id) NOT LIKE '%demo%'
                       AND lower(b.course_id) NOT LIKE '%nile%'
                       AND date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                          AND '{date}')
               t1;    '''.format(date=date)
    return execute_query(query)


def student_courseenrollment_info_month(date):
    query = '''
        SELECT sum(if(created = '{date}', 1, 0))
                  week_enroll_cnt,
               sum(
                  if(created = '{date}' AND is_active = 0,
                     1,
                     0))
                  week_unenroll_cnt,
               count(
                  DISTINCT if(created = '{date}',
                              id,
                              NULL))
                  week_enroll_person_cnt,
               count(
                  DISTINCT if(
                                  created = '{date}'
                              AND is_active = 0,
                              id,
                              NULL))
                  week_unenroll_person_cnt,
               sum(if(created BETWEEN '1' AND '{date}', 1, 0)) all_enroll_cnt,
               sum(if(created BETWEEN '1' AND '{date}' AND is_active = 0, 1, 0))
                  all_unenroll_cnt,
               count(DISTINCT if(created BETWEEN '1' AND '{date}', id, NULL))
                  all_enroll_person_cnt,
               count(
                  DISTINCT if(created BETWEEN '1' AND '{date}' AND is_active = 0,
                              id,
                              NULL))
                  all_unenroll_person_cnt
          FROM (SELECT a.id,
                       date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m')
                          created,
                       b.is_active
                  FROM auth_user                       a,
                       student_courseenrollment        b,
                       course_overviews_courseoverview c
                 WHERE     1 = 1
                       AND a.id = b.user_id
                       AND b.course_id = c.id
                       AND lower(b.course_id) NOT LIKE '%test%'
                       AND lower(b.course_id) NOT LIKE '%demo%'
                       AND lower(b.course_id) NOT LIKE '%nile%'
                       AND date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m') BETWEEN '1'
                                                                                          AND '{date}')
               t1;    '''.format(date=date)
    return execute_query(query)


# 학습활동 주간
def student_activity_week(date):
    query = '''
        SELECT sum(if(modified BETWEEN '{date}' - 6 AND '{date}', `video`, 0))
                  video1,
               sum(if(modified BETWEEN '{date}' - 6 AND '{date}', `problem`, 0))
                  problem1,
               sum(if(modified BETWEEN '{date}' - 6 AND '{date}', `both`, 0))
                  both1,
               count(
                  DISTINCT if(modified BETWEEN '{date}' - 6 AND '{date}',
                              student_id,
                              0))
                  video2,
               count(
                  DISTINCT if(modified BETWEEN '{date}' - 6 AND '{date}',
                              student_id,
                              0))
                  problem2,
               count(
                  DISTINCT if(modified BETWEEN '{date}' - 6 AND '{date}',
                              student_id,
                              0))
                  both2,
               sum(if(modified BETWEEN '1' AND '{date}', `video`, 0))   video3,
               sum(if(modified BETWEEN '1' AND '{date}', `problem`, 0)) problem3,
               sum(if(modified BETWEEN '1' AND '{date}', `both`, 0))    both3,
               count(DISTINCT if(modified BETWEEN '1' AND '{date}', student_id, 0))
                  video4,
               count(DISTINCT if(modified BETWEEN '1' AND '{date}', student_id, 0))
                  problem4,
               count(DISTINCT if(modified BETWEEN '1' AND '{date}', student_id, 0))
                  both4
          FROM (  SELECT student_id,
                         sum(if(module_type = 'video', 1, 0)) `video`,
                         sum(if(module_type = 'problem', 1, 0))`problem`,
                         date_format(adddate(max(modified), INTERVAL 9 HOUR), '%Y%m%d')
                            `modified`,
                         count(
                            DISTINCT if(
                                           module_type = 'video'
                                        OR module_type = 'problem',
                                        student_id,
                                        0))
                            `both`
                    FROM (  SELECT course_id,
                                   student_id,
                                   module_type,
                                   modified,
                                   max(grade) grade
                              FROM courseware_studentmodule
                             WHERE     1 = 1
                                   AND lower(course_id) NOT LIKE '%test%'
                                   AND lower(course_id) NOT LIKE '%demo%'
                                   AND lower(course_id) NOT LIKE '%nile%'
                                   AND module_type IN ('video', 'problem')
                                   AND CASE
                                          WHEN module_type = 'problem'
                                          THEN
                                             grade IS NOT NULL
                                          ELSE
                                             1 = 1
                                       END
                                   AND created <> modified
                          GROUP BY student_id, module_type, course_id) t1
                GROUP BY course_id, student_id) t2;
    '''.format(date=date)
    return execute_query(query)


def student_activity_month(date):
    query = '''
        SELECT sum(if(modified = '{date}', `video`, 0))
                  video1,
               sum(if(modified = '{date}', `problem`, 0))
                  problem1,
               sum(if(modified = '{date}', `both`, 0))
                  both1,
               count(
                  DISTINCT if(modified = '{date}',
                              student_id,
                              0))
                  video2,
               count(
                  DISTINCT if(modified = '{date}',
                              student_id,
                              0))
                  problem2,
               count(
                  DISTINCT if(modified = '{date}',
                              student_id,
                              0))
                  both2,
               sum(if(modified BETWEEN '1' AND '{date}', `video`, 0))   video3,
               sum(if(modified BETWEEN '1' AND '{date}', `problem`, 0)) problem3,
               sum(if(modified BETWEEN '1' AND '{date}', `both`, 0))    both3,
               count(DISTINCT if(modified BETWEEN '1' AND '{date}', student_id, 0))
                  video4,
               count(DISTINCT if(modified BETWEEN '1' AND '{date}', student_id, 0))
                  problem4,
               count(DISTINCT if(modified BETWEEN '1' AND '{date}', student_id, 0))
                  both4
          FROM (  SELECT student_id,
                         sum(if(module_type = 'video', 1, 0)) `video`,
                         sum(if(module_type = 'problem', 1, 0))`problem`,
                         date_format(adddate(max(modified), INTERVAL 9 HOUR), '%Y%m')
                            `modified`,
                         count(
                            DISTINCT if(
                                           module_type = 'video'
                                        OR module_type = 'problem',
                                        student_id,
                                        0))
                            `both`
                    FROM (  SELECT course_id,
                                   student_id,
                                   module_type,
                                   modified,
                                   max(grade) grade
                              FROM courseware_studentmodule
                             WHERE     1 = 1
                                   AND lower(course_id) NOT LIKE '%test%'
                                   AND lower(course_id) NOT LIKE '%demo%'
                                   AND lower(course_id) NOT LIKE '%nile%'
                                   AND module_type IN ('video', 'problem')
                                   AND CASE
                                          WHEN module_type = 'problem'
                                          THEN
                                             grade IS NOT NULL
                                          ELSE
                                             1 = 1
                                       END
                                   AND created <> modified
                          GROUP BY student_id, module_type, course_id) t1
                GROUP BY course_id, student_id) t2;
    '''.format(date=date)
    return execute_query(query)


# 이수자수 주간
def student_cert_week(date):
    query = '''
        SELECT sum(if(a.lowest_passing_grade / 2 <= b.grade and date_format(adddate(b.created_date, interval 9 hour), '%Y%m%d') between '{date}' - 6 and '{date}', 1, 0)) half_cnt1,
               sum(if(b.status = 'downloadable' and date_format(adddate(b.created_date, interval 9 hour), '%Y%m%d') between '{date}' - 6 and '{date}', 1, 0))             downloadable_cnt1,
               count(distinct if(a.lowest_passing_grade / 2 <= b.grade and date_format(adddate(b.created_date, interval 9 hour), '%Y%m%d') between '{date}' - 6 and '{date}', b.user_id, 0)) half_cnt2,
               count(distinct if(b.status = 'downloadable' and date_format(adddate(b.created_date, interval 9 hour), '%Y%m%d') between '{date}' - 6 and '{date}', b.user_id, 0))             downloadable_cnt2,
               sum(if(a.lowest_passing_grade / 2 <= b.grade and date_format(adddate(b.created_date, interval 9 hour), '%Y%m%d') between '1' and '{date}', 1, 0)) half_cnt3,
               sum(if(b.status = 'downloadable' and date_format(adddate(b.created_date, interval 9 hour), '%Y%m%d') between '1' and '{date}', 1, 0))             downloadable_cnt3,
               count(distinct if(a.lowest_passing_grade / 2 <= b.grade and date_format(adddate(b.created_date, interval 9 hour), '%Y%m%d') between '1' and '{date}', b.user_id, 0)) half_cnt4,
               count(distinct if(b.status = 'downloadable' and date_format(adddate(b.created_date, interval 9 hour), '%Y%m%d') between '1' and '{date}', b.user_id, 0))             downloadable_cnt4
          FROM course_overviews_courseoverview a, certificates_generatedcertificate b
         WHERE a.id = b.course_id;
    '''.format(date=date)
    return execute_query(query)


# 이수자수 주간
def student_cert_month(date):
    query = '''
        SELECT sum(if(a.lowest_passing_grade / 2 <= b.grade and date_format(adddate(b.created_date, interval 9 hour), '%Y%m') = '{date}', 1, 0)) half_cnt1,
               sum(if(b.status = 'downloadable' and date_format(adddate(b.created_date, interval 9 hour), '%Y%m') = '{date}', 1, 0))             downloadable_cnt1,
               count(distinct if(a.lowest_passing_grade / 2 <= b.grade and date_format(adddate(b.created_date, interval 9 hour), '%Y%m') = '{date}', b.user_id, 0)) half_cnt2,
               count(distinct if(b.status = 'downloadable' and date_format(adddate(b.created_date, interval 9 hour), '%Y%m') = '{date}', b.user_id, 0))             downloadable_cnt2,
               sum(if(a.lowest_passing_grade / 2 <= b.grade and date_format(adddate(b.created_date, interval 9 hour), '%Y%m') between '1' and '{date}', 1, 0)) half_cnt3,
               sum(if(b.status = 'downloadable' and date_format(adddate(b.created_date, interval 9 hour), '%Y%m') between '1' and '{date}', 1, 0))             downloadable_cnt3,
               count(distinct if(a.lowest_passing_grade / 2 <= b.grade and date_format(adddate(b.created_date, interval 9 hour), '%Y%m') between '1' and '{date}', b.user_id, 0)) half_cnt4,
               count(distinct if(b.status = 'downloadable' and date_format(adddate(b.created_date, interval 9 hour), '%Y%m') between '1' and '{date}', b.user_id, 0))             downloadable_cnt4
          FROM course_overviews_courseoverview a, certificates_generatedcertificate b
         WHERE a.id = b.course_id;
    '''.format(date=date)
    return execute_query(query)


# `엑셀 시간`
def excel_now_day():
    query = """
      select date_format(now(),'%Y%m%d');
    """
    return execute_query_one(query)


# `회원 가입자수`
def user_join(date):
    query = """
      SELECT sum(if(date_format(adddate(b.date_joined, INTERVAL 9 HOUR), '%Y%m%d') = '{date}' ,1,0)) newcnt,
                       sum(if(b.email LIKE 'delete_%', 0, 1)) cnt,
                       count(b.id) allcnt
                  FROM auth_userprofile a, auth_user b
                 WHERE     a.user_id = b.id
                       AND date_format(adddate(b.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014' AND '{date}';
    """.format(date=date)
    return execute_query(query)


# 수강신청자수(통합)
def course_count(date):
    query = """
        SELECT sum(if(date_format(adddate(a.created, INTERVAL 9 HOUR), '%Y%m%d') = '{date}' and a.is_active = 1, 1, 0)) newcnt,
               count(a.user_id) allcnt,
               sum(if(a.is_active = 1, 1, 0)) cnt,
               count(DISTINCT a.user_id) distcnt
          FROM student_courseenrollment a, auth_user b
         WHERE     a.user_id = b.id
               AND date_format(adddate(a.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1' AND '{date}'
               and exists (select 1 from student_courseaccessrole c where a.course_id = c.course_id)
               AND lower(a.course_id) NOT LIKE '%test%'
               AND lower(a.course_id) NOT LIKE '%demo%'
               AND lower(a.course_id) NOT LIKE '%nile%';
    """.format(date=date)
    return execute_query(query)


# 수강신청구분
def course_case(date):
    query = """
        SELECT 1                                              gubn,
               (select count(*) from auth_user a, auth_userprofile b where a.id = b.user_id and date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') = '{date}') is_secession,
               (select count(*) from auth_user a, auth_userprofile b where a.id = b.user_id and email like 'delete_%' and date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') = '{date}') no_secession,
               count(if(c.is_active = 1, a.id, NULL))         is_active,
               count(if(c.is_active = 1, NULL, a.id))         no_active
          FROM auth_user a, auth_userprofile b, student_courseenrollment c
         WHERE     a.id = b.user_id
               AND a.id = c.user_id
               and exists (select 1 from student_courseaccessrole d where c.course_id = d.course_id)
               AND lower(c.course_id) NOT LIKE '%test%'
               AND lower(c.course_id) NOT LIKE '%demo%'
               AND lower(c.course_id) NOT LIKE '%nile%'
               AND date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') =
                      '{date}'
        UNION ALL
        SELECT 2                                              gubn,
               (select count(*) from auth_user a, auth_userprofile b where a.id = b.user_id and date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') between '20151014' and '{date}') is_secession,
               (select count(*) from auth_user a, auth_userprofile b where a.id = b.user_id and email like 'delete_%' and date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') between '20151014' and '{date}') no_secession,
               count(1)         is_active,
               count(if(c.is_active = 1, NULL, a.id))         no_active
          FROM auth_user a, auth_userprofile b, student_courseenrollment c
         WHERE     a.id = b.user_id
               AND a.id = c.user_id
               and exists (select 1 from student_courseaccessrole d where c.course_id = d.course_id)
               AND lower(c.course_id) NOT LIKE '%test%'
               AND lower(c.course_id) NOT LIKE '%demo%'
               AND lower(c.course_id) NOT LIKE '%nile%'
               AND date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                  AND '{date}'
        UNION ALL
          SELECT 3                                                     gubn,
                 0 is_secession,
                 0 no_secession,
                 count(DISTINCT a.id)       is_active,
                 count(DISTINCT if(c.is_active = 1, NULL, a.id))       no_active
            FROM auth_user a, auth_userprofile b, student_courseenrollment c
           WHERE     a.id = b.user_id
                 AND a.id = c.user_id
                 and exists (select 1 from student_courseaccessrole d where c.course_id = d.course_id)
                 AND lower(c.course_id) NOT LIKE '%test%'
                 AND lower(c.course_id) NOT LIKE '%demo%'
                 AND lower(c.course_id) NOT LIKE '%nile%'
                 AND date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                    AND '{date}'
        ORDER BY gubn
    """.format(date=date)
    return execute_query(query)


# 연령구분(신규)
def age_new(date):
    query = """
        SELECT ifnull(b.male, 0), ifnull(b.female, 0), ifnull(b.etc, 0)
          FROM (SELECT (@rn := @rn + 1) r
                  FROM auth_user a, (SELECT @rn := 0) b
                 LIMIT 6) a
               LEFT OUTER JOIN
               (SELECT age,
                       count(CASE WHEN gender = 'm' THEN 1 END) male,
                       count(CASE WHEN gender = 'f' THEN 1 END) female,
                       count(CASE WHEN gender = 'o' THEN 1 END) etc
                  FROM (SELECT CASE
                                  WHEN age < 20 THEN '1'
                                  WHEN age BETWEEN 20 AND 29 THEN '2'
                                  WHEN age BETWEEN 30 AND 39 THEN '3'
                                  WHEN age BETWEEN 40 AND 49 THEN '4'
                                  WHEN age BETWEEN 50 AND 59 THEN '5'
                                  WHEN age >= 60 THEN '6'
                                  ELSE '7'
                               END
                                  age,
                               gender
                          FROM (SELECT   ('{year}' - ifnull(a.year_of_birth, 0))
                                       + 1
                                          age,
                                       a.gender
                                  FROM auth_userprofile a, auth_user b
                                 WHERE     a.user_id = b.id
                                      and b.email not like 'delete_%'
                                       AND date_format(
                                              adddate(b.date_joined, INTERVAL 9 HOUR),
                                              '%Y%m%d') = '{date}') aa) bb
                GROUP BY age) b
                  ON a.r = b.age
        ORDER BY a.r;
    """.format(
        year=date[:4],
        date=date
    )
    return execute_query(query)


# 연령구분(누적)
def age_total(date):
    query = """
        SELECT b.male, b.female, b.etc
          FROM (SELECT (@rn := @rn + 1) r
                  FROM auth_user a, (SELECT @rn := 0) b
                 LIMIT 6) a
               LEFT OUTER JOIN
               (SELECT age,
                       count(CASE WHEN gender = 'm' THEN 1 END) male,
                       count(CASE WHEN gender = 'f' THEN 1 END) female,
                       count(CASE WHEN gender = 'o' THEN 1 END) etc
                  FROM (SELECT CASE
                                  WHEN age < 20 THEN '1'
                                  WHEN age BETWEEN 20 AND 29 THEN '2'
                                  WHEN age BETWEEN 30 AND 39 THEN '3'
                                  WHEN age BETWEEN 40 AND 49 THEN '4'
                                  WHEN age BETWEEN 50 AND 59 THEN '5'
                                  WHEN age >= 60 THEN '6'
                                  ELSE '7'
                               END
                                  age,
                               gender
                          FROM (SELECT   ('{year}' - ifnull(a.year_of_birth, 0))
                                       + 1
                                          age,
                                       a.gender
                                  FROM auth_userprofile a, auth_user b
                                 WHERE     a.user_id = b.id
                                      and b.email not like 'delete_%'
                                       AND date_format(
                                              adddate(b.date_joined, INTERVAL 9 HOUR),
                                              '%Y%m%d') BETWEEN '20151014'
                                                            AND '{date}') aa) bb
                GROUP BY age) b
                  ON a.r = b.age
        ORDER BY a.r;
    """.format(
        year=date[:4],
        date=date
    )
    return execute_query(query)


# 학력구분(신규)
def edu_new(date):
    query = """
        SELECT ifnull(b.male, 0), ifnull(b.female, 0), ifnull(b.etc, 0)
          FROM (SELECT (@rn := @rn + 1) r
                  FROM auth_user a, (SELECT @rn := 0) b
                 LIMIT 9) a
               LEFT OUTER JOIN
               (SELECT CASE
                          WHEN a.level_of_education = 'p'
                          THEN
                             1
                          WHEN a.level_of_education = 'm'
                          THEN
                             2
                          WHEN a.level_of_education = 'b'
                          THEN
                             3
                          WHEN a.level_of_education = 'a'
                          THEN
                             4
                          WHEN a.level_of_education = 'hs'
                          THEN
                             5
                          WHEN a.level_of_education = 'jhs'
                          THEN
                             6
                          WHEN a.level_of_education = 'el'
                          THEN
                             7
                          WHEN a.level_of_education = 'other'
                          THEN
                             8
                          else
                             9
                       END
                          result,
                       sum(if(a.gender = 'm', 1, 0)) AS "male",
                       sum(if(a.gender = 'f', 1, 0)) AS "female",
                       sum(if(a.gender = 'o', 1, 0)) AS "etc"
                  FROM auth_userprofile a, auth_user b
                 WHERE     a.user_id = b.id
                       AND date_format(adddate(b.date_joined, INTERVAL 9 HOUR),'%Y%m%d') = '{date}'
                       and b.email not like 'delete_%'
                GROUP BY CASE
                            WHEN    a.level_of_education IS NULL
                                 OR a.level_of_education = ''
                                 OR a.level_of_education = 'null'
                            THEN
                               'none'
                            ELSE
                               level_of_education
                         END
                ORDER BY level_of_education) b
                  ON a.r = b.result
        ORDER BY a.r;
    """.format(date=date)
    return execute_query(query)


# 학력구분(누적)
def edu_total(date):
    query = """
        SELECT sum(b.male), sum(b.female), sum(b.etc)
          FROM (SELECT (@rn := @rn + 1) r
                  FROM auth_user a, (SELECT @rn := 0) b
                 LIMIT 9) a
               LEFT OUTER JOIN
               (SELECT CASE
                          WHEN a.level_of_education = 'p'
                          THEN
                             1
                          WHEN a.level_of_education = 'm'
                          THEN
                             2
                          WHEN a.level_of_education = 'b'
                          THEN
                             3
                          WHEN a.level_of_education = 'a'
                          THEN
                             4
                          WHEN a.level_of_education = 'hs'
                          THEN
                             5
                          WHEN a.level_of_education = 'jhs'
                          THEN
                             6
                          WHEN a.level_of_education = 'el'
                          THEN
                             7
                          WHEN a.level_of_education = 'other'
                          THEN
                             8
                          else
                             9
                       END
                          result,
                       if(a.gender = 'm', 1, 0) AS "male",
                       if(a.gender = 'f', 1, 0) AS "female",
                       if(a.gender = 'o', 1, 0) AS "etc"
                  FROM auth_userprofile a, auth_user b
                 WHERE     a.user_id = b.id
                        and b.email not like 'delete_%'
                       AND date_format(adddate(b.date_joined, INTERVAL 9 HOUR),'%Y%m%d') BETWEEN '20151014' AND '{date}'
                ) b
                  ON a.r = b.result
        group by a.r
        ORDER BY a.r;
    """.format(date=date)
    return execute_query(query)


# 연령학력
def age_edu(date):
    query = """
        SELECT b.aa,
               b.bb,
               b.cc,
               b.dd,
               b.ee,
               b.ff,
               b.gg,
               b.hh,
               b.ii
          FROM (SELECT (@rn := @rn + 1) r
                  FROM auth_user a, (SELECT @rn := 0) b
                 LIMIT 6) a
               LEFT OUTER JOIN
               (SELECT age,
                       sum(CASE WHEN lv = 'p' THEN 1 ELSE 0 END) aa,
                       sum(CASE WHEN lv = 'm' THEN 1 ELSE 0 END) bb,
                       sum(CASE WHEN lv = 'b' THEN 1 ELSE 0 END) cc,
                       sum(CASE WHEN lv = 'a' THEN 1 ELSE 0 END) dd,
                       sum(CASE WHEN lv = 'hs' THEN 1 ELSE 0 END) ee,
                       sum(CASE WHEN lv = 'jhs' THEN 1 ELSE 0 END) ff,
                       sum(CASE WHEN lv = 'el' THEN 1 ELSE 0 END) gg,
                       sum(CASE WHEN lv = 'other' THEN 1 ELSE 0 END) hh,
                       sum(CASE
                              WHEN lv NOT IN ('p',
                                              'm',
                                              'b',
                                              'a',
                                              'hs',
                                              'jhs',
                                              'el',
                                              'other')
                              THEN
                                 1
                              ELSE
                                 0
                           END)
                          ii
                  FROM (SELECT CASE
                                  WHEN age < 20 THEN '1'
                                  WHEN age BETWEEN 20 AND 29 THEN '2'
                                  WHEN age BETWEEN 30 AND 39 THEN '3'
                                  WHEN age BETWEEN 40 AND 49 THEN '4'
                                  WHEN age BETWEEN 50 AND 59 THEN '5'
                                  WHEN age >= 60 THEN '6'
                                  ELSE '7'
                               END
                                  age,
                               lv,
                               gender
                          FROM (SELECT   ('{year}' - ifnull(a.year_of_birth, 0))
                                       + 1
                                          age,
                                       ifnull(a.level_of_education, '') lv,
                                       a.gender
                                  FROM auth_userprofile a, auth_user b
                                 WHERE     a.user_id = b.id
                                      and b.email not like 'delete_%'
                                       AND date_format(
                                              adddate(b.date_joined, INTERVAL 9 HOUR),
                                              '%Y%m%d') BETWEEN '20151014'
                                                            AND '{date}') aa) bb
                GROUP BY age) b
                  ON a.r = b.age
        ORDER BY a.r;
    """.format(
        year=date[:4],
        date=date
    )
    return execute_query(query)


# 이수증 생성 강좌 아이디
def course_ids_cert():
    query = """
        SELECT a.course_id
          FROM (SELECT course_id, count(a.user_id) cnt, max(a.created_date) cdate
                  FROM certificates_generatedcertificate a
                GROUP BY a.course_id) a,
               (SELECT a.course_id, a.created cdate
                  FROM student_courseenrollment a
                 WHERE a.is_active = 1) b
         WHERE a.course_id = b.course_id AND a.cdate >= b.cdate
        GROUP BY a.course_id
        HAVING max(a.cnt) >= count(b.course_id)
    """
    print query

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


# 이수증 생성 결과
def certificateInfo(courseId):
    query = """
        SELECT substring(a.course_id,
                         instr(a.course_id, ':') + 1,
                         (instr(a.course_id, '+')) - instr(a.course_id, ':') - 1)
                  org,
               a.course_id,
               substring(substring_index(a.course_id, '+', 2),
                         instr(a.course_id, '+') + 1)
                  course_id1,
               substring_index(a.course_id, '+', -1) course_id2,
               a.status,
               count(*) cnt
          FROM certificates_generatedcertificate a,
               auth_user b,
               student_courseenrollment c
         WHERE     1 = 1
               AND a.user_id = b.id
               AND c.user_id = b.id
               AND a.course_id = c.course_id
               AND c.is_active = 1
               AND a.course_id = '{date}'
        GROUP BY a.course_id, a.status
        ORDER BY a.course_id, a.status;
    """.format(courseId)
    print query

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


# 월별 통계 자료
def member_statistics(date):
    query = """
        SELECT sum(if(a.is_active = '1', 1, 0)) active,
               sum(if(a.is_active = '1', 0, 1)) unactive,
               count(*)
          FROM auth_user a, auth_userprofile b
         WHERE     a.id = b.user_id
               AND date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014'
                                                                                      AND '{date}';
    """.format(date=date)
    print query

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


# 지역별 통계
def country_statistics(date):
    query = """
        SELECT b.country, count(*) cnt
          FROM auth_user a, auth_userprofile b
         WHERE     a.id = b.user_id
               AND date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014'
                                                                                      AND '{date}'
        GROUP BY b.country
        ORDER BY count(*) DESC;
    """.format(date=date)
    print query

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row
