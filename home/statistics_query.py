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


# < 요약 : 회원가입자수 >
def overall_only_auth(date):
    query = '''
        SELECT count(
                  if(
                     date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d')   = '{date}',
                     a.id,
                     NULL))
                  new_cnt,
                 count(a.id)
               - count(
                    if(
                           a.email LIKE 'delete_%'
                       AND date_format(adddate(last_login, INTERVAL 9 HOUR),
                                       '%Y%m%d') BETWEEN '20151014'
                                                     AND '{date}',
                       a.id,
                       NULL))
                  all_cnt
          FROM auth_user a, auth_userprofile b
         WHERE     a.id = b.user_id
               AND date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014'
                                                                                    AND '{date}';
    '''.format(date=date)
    return execute_query(query)


# < 요약 : 수강신청건수 >
def overall_only_enroll(date):
    query = '''
        SELECT sum(
                  if(
                     date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d')   = '{date}',
                     1,
                     0))
                  new_enroll_cnt,
               sum(c.is_active = 1) all_enroll_cnt
          FROM auth_user                       a,
               auth_userprofile                b,
               student_courseenrollment        c,
               course_overviews_courseoverview d
         WHERE     a.id = b.user_id
               AND a.id = c.user_id
               AND c.course_id = d.id
               AND lower(c.course_id) NOT LIKE '%test%'
               AND lower(c.course_id) NOT LIKE '%demo%'
               AND lower(c.course_id) NOT LIKE '%nile%'
               AND date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                  AND '{date}';
    '''.format(date=date)
    return execute_query(query)


# < 요약 : 이수건수 >
def overall_only_cert(date):
    query = '''
        SELECT count(
                  if(
                     date_format(adddate(created_date, INTERVAL 9 HOUR), '%Y%m%d')   = '{date}',
                     id,
                     NULL))
                  new_cnt,
               count(id) all_cnt
          FROM certificates_generatedcertificate
         WHERE     status = 'downloadable'
               AND lower(course_id) NOT LIKE '%test%'
               AND lower(course_id) NOT LIKE '%demo%'
               AND lower(course_id) NOT LIKE '%nile%'
               AND date_format(adddate(created_date, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                     AND '{date}';
    '''.format(date=date)
    return execute_query(query)


# `회원가입 세부사항`
def overall_auth(date):
    query = '''
        SELECT
            count(if(date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d') = '{date}',a.id,NULL)) new_all_cnt,
            count(if(date_format(
          adddate(
             str_to_date(
                substring(substring_index(email, '@delete.', -1), 1, 14),
                '%Y%m%d%H%i%S'),
             INTERVAL 9 HOUR),
          '%Y%m%d')  = '{date}',a.id,NULL)) new_sec_cnt,
            count(if(date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d') = '{date}' and a.is_active = 1 ,a.id,NULL)) new_active_cnt,
            count(a.id) all_cnt,
            count(if(a.email LIKE 'delete_%' AND date_format(adddate(last_login, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014' AND '{date}', a.id, NULL)) all_sec_cnt,
            count(if(a.email not LIKE 'delete_%' and a.is_active = 1, a.id, NULL)) all_active_cnt
          FROM auth_user a, auth_userprofile b
         WHERE     a.id = b.user_id
               AND date_format(adddate(date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014' AND '{date}';
    '''.format(date=date)
    return execute_query(query)


# `수강신청 세부사항`
def overall_enroll(date):
    query = '''
        SELECT sum(if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') = '{date}',1,0)) new_enroll_cnt,
               sum(if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') = '{date}' and c.is_active = 0,1,0)) new_sec_cnt,
               sum(if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') = '{date}', c.is_active,0)) new_total_cnt,
               count(distinct if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') = '{date}', a.id,null)) new_enroll_id,
               count(distinct if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') = '{date}' and c.is_active = 0,a.id,null)) new_sec_id,
               count(distinct if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') = '{date}' and c.is_active = 1, c.user_id, null)) new_total_id,
               sum(if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}',1,0)) all_cnt,
               sum(if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}' and c.is_active = 0,1,0)) all_sec_cnt,
               sum(if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}', c.is_active,0)) all_total_cnt,
               count(distinct if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}',a.id,null)) all_id,
               count(distinct if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}' and c.is_active = 0,a.id,null)) all_sec_id,
               count(distinct if(date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}' and c.is_active = 1,a.id,null)) all_total_id
          FROM auth_user a, auth_userprofile b, student_courseenrollment c, course_overviews_courseoverview d
         WHERE     a.id = b.user_id
               and a.id = c.user_id
               and c.course_id = d.id
               AND lower(c.course_id) NOT LIKE '%test%'
               AND lower(c.course_id) NOT LIKE '%demo%'
               AND lower(c.course_id) NOT LIKE '%nile%'
               AND date_format(adddate(c.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                    AND '{date}';
    '''.format(date=date)
    return execute_query(query)


# `이수 세부사항`
def overall_cert(date):
    query = '''
        SELECT sum(if(a.lowest_passing_grade/2 <= b.grade and date_format(adddate(b.created_date, INTERVAL 9 HOUR), '%Y%m%d') = '{date}', 1, 0))     new_half_cert,
                sum(if(b.status = 'downloadable' and date_format(adddate(b.created_date, INTERVAL 9 HOUR), '%Y%m%d') = '{date}', 1, 0))     new_cert,
                count(distinct if(a.lowest_passing_grade/2 <= b.grade and date_format(adddate(b.created_date, INTERVAL 9 HOUR), '%Y%m%d') = '{date}', b.user_id, null))     cert,
                count(distinct if(b.status = 'downloadable' and date_format(adddate(b.created_date, INTERVAL 9 HOUR), '%Y%m%d') = '{date}', b.user_id, null))     cert,
                sum(if(a.lowest_passing_grade/2 <= b.grade and date_format(adddate(b.created_date, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}', 1, 0))     all_half_cert,
                sum(if(b.status = 'downloadable' and date_format(adddate(b.created_date, INTERVAL 9 HOUR), '%Y%m%d') between '1' and '{date}', 1, 0))     all_cert,
                count(distinct if(a.lowest_passing_grade/2 <= b.grade and date_format(adddate(b.created_date, INTERVAL 9 HOUR), '%Y%m%d') between '1' and  '{date}', b.user_id, null))     all_half_id,
                count(distinct if(b.status = 'downloadable' and date_format(adddate(b.created_date, INTERVAL 9 HOUR), '%Y%m%d') between '1' and  '{date}', b.user_id, null))     all_id
          FROM course_overviews_courseoverview a, certificates_generatedcertificate b
         WHERE a.id = b.course_id
           and lower(a.id) not like '%test%'
           and lower(a.id) not like '%demo%'
           and lower(a.id) not like '%nile%'
         ;
    '''.format(date=date)
    return execute_query(query)


# 'by_course_enroll_audit'
def by_course_enroll_audit(date):
    query = '''
        SELECT id, 
               org, 
               new_enroll_cnt, 
               new_unenroll_cnt, 
               all_enroll_cnt, 
               all_unenroll_cnt, 
               (SELECT Count(*) 
                FROM   certificates_generatedcertificate e 
                WHERE  e.course_id = t1.id 
                       AND e.grade >= lowest_passing_grade / 2 
                       AND Date_format(Adddate(e.created_date, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}') half_cnt, 
               (SELECT Count(*) 
                FROM   certificates_generatedcertificate e 
                WHERE  e.course_id = t1.id 
                       AND e.status = 'downloadable' 
                       AND Date_format(Adddate(e.created_date, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}') cert_cnt 
        FROM   (SELECT a.id, 
                       a.org, 
                       a.lowest_passing_grade, 
                       Sum(IF(Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') = '{date}' and b.mode = 'audit' and b.created >= mm, 1, 0 	))                             `new_enroll_cnt`, 
                       Sum(IF(Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') = '{date}' AND b.is_active = 0 and b.mode = 'audit' and b.created >= mm, 1, 0)) `new_unenroll_cnt`, 
                       Sum(IF(Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}' and b.mode = 'audit' and b.created >= mm, 1, 0))      `all_enroll_cnt`, 
                       Sum(IF(Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}' AND b.is_active = 0 and b.mode = 'audit' and b.created >= mm, 1, 0)) `all_unenroll_cnt` 
                FROM   course_overviews_courseoverview a
                join student_courseenrollment b
                on a.id = b.course_id
        		join auth_user c
                on b.user_id = c.id 
        	    join auth_userprofile d
                on c.id = d.user_id 
        	    left join
                       (
        				select course_id, max(created_date) as mm
        				from certificates_generatedcertificate
        				where status = 'downloadable'
        				group by course_id
                       ) cert
        	    on a.id = cert.course_id
                where Lower(b.course_id) NOT LIKE '%test%' 
                       AND Lower(b.course_id) NOT LIKE '%demo%' 
                       AND Lower(b.course_id) NOT LIKE '%nile%' 
                       AND Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}' 
                       AND Date_format(Adddate(c.date_joined, INTERVAL 9 hour), '%Y%m%d' ) BETWEEN '1' AND '{date}' 
                GROUP  BY a.id, 
                          a.org, 
                          a.lowest_passing_grade) t1; 
    '''.format(date=date)
    return execute_query(query)

# 'by_course_enroll'
def by_course_enroll(date):
    query = '''
        SELECT id, 
               org, 
               new_enroll_cnt, 
               new_unenroll_cnt, 
               all_enroll_cnt, 
               all_unenroll_cnt, 
               (SELECT Count(*) 
                FROM   certificates_generatedcertificate e 
                WHERE  e.course_id = t1.id 
                       AND e.grade >= lowest_passing_grade / 2 
                       AND Date_format(Adddate(e.created_date, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}') half_cnt, 
               (SELECT Count(*) 
                FROM   certificates_generatedcertificate e 
                WHERE  e.course_id = t1.id 
                       AND e.status = 'downloadable' 
                       AND Date_format(Adddate(e.created_date, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}') cert_cnt 
        FROM   (SELECT a.id, 
                       a.org, 
                       a.lowest_passing_grade, 
                       Sum(IF(Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') = '{date}' and b.mode = 'honor' and b.created <= mm, 1, 0 	))                             `new_enroll_cnt`, 
                       Sum(IF(Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') = '{date}' AND b.is_active = 0 and b.mode = 'honor' and b.created <= mm, 1, 0)) `new_unenroll_cnt`, 
                       Sum(IF(Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}' and b.mode = 'honor' and b.created <= mm, 1, 0))      `all_enroll_cnt`, 
                       Sum(IF(Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}' AND b.is_active = 0 and b.mode = 'honor' and b.created <= mm, 1, 0)) `all_unenroll_cnt` 
                FROM   course_overviews_courseoverview a
                join student_courseenrollment b
                on a.id = b.course_id
        		join auth_user c
                on b.user_id = c.id 
        	    join auth_userprofile d
                on c.id = d.user_id 
        	    left join
                       (
        				select course_id, max(created_date) as mm
        				from certificates_generatedcertificate
        				where status = 'downloadable'
        				group by course_id
                       ) cert
        	    on a.id = cert.course_id
                where Lower(b.course_id) NOT LIKE '%test%' 
                       AND Lower(b.course_id) NOT LIKE '%demo%' 
                       AND Lower(b.course_id) NOT LIKE '%nile%' 
                       AND Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}' 
                       AND Date_format(Adddate(c.date_joined, INTERVAL 9 hour), '%Y%m%d' ) BETWEEN '1' AND '{date}' 
                GROUP  BY a.id, 
                          a.org, 
                          a.lowest_passing_grade) t1; 
    '''.format(date=date)
    return execute_query(query)




# 'by_course_demographics_audit'
def by_course_demographics_audit(date):
    query = '''
        SELECT course_id, 
               org, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND gender = 'm', 1, 0)) male , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND gender = 'f', 1, 0)) female, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND gender = 'o', 1, 0)) etc, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND gender NOT IN ( 'm', 'f', 'o' ), 1, 0)) no_gender1, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND age < 20, 1, 0)) age1, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND age BETWEEN 20 AND 29, 1, 0)) age2, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND age BETWEEN 30 AND 39, 1, 0)) age3,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND age BETWEEN 40 AND 49, 1, 0)) age4, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND age BETWEEN 50 AND 59, 1, 0)) age5,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND age > 59, 1, 0)) age6,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND edu = 'p', 1, 0)) edu1,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND edu = 'm', 1, 0)) edu2,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND edu = 'b', 1, 0)) edu3,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND edu = 'a', 1, 0)) edu4,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND edu = 'hs', 1, 0)) edu5,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND edu = 'jhs', 1, 0)) edu6,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND edu = 'el', 1, 0)) edu7,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND edu = 'other', 1, 0)) edu8,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3 AND ( edu IS NULL OR edu NOT IN ( 'p', 'm', 'b', 'a', 'hs', 'jhs', 'el', 'other' ) ), 1, 0)) edu9, 
               Count(IF(real_time >= cert_time AND mode = 'audit' AND is_active = 1 AND pass_type < 3, 1, NULL)) allcnt, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND gender = 'm', 1, 0)) male,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND gender = 'f', 1, 0)) female, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND gender = 'o', 1, 0)) etc, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND gender IN ( 'm', 'f', 'o' ), 1, 0)) no_gender2, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND age < 20, 1, 0)) age1, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND age BETWEEN 20 AND 29, 1, 0)) age2, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND age BETWEEN 30 AND 39, 1, 0)) age3, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND age BETWEEN 40 AND 49, 1, 0)) age4,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND age BETWEEN 50 AND 59, 1, 0)) age5,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND age > 59, 1, 0)) age6,
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND edu = 'p', 1, 0)) edu1, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND edu = 'm', 1, 0)) edu2 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND edu = 'b', 1, 0)) edu3 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND edu = 'a', 1, 0)) edu4 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND edu = 'hs', 1, 0)) edu5 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND edu = 'jhs', 1, 0)) edu6 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND edu = 'el', 1, 0)) edu7 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND edu = 'other', 1, 0)) edu8 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2 AND ( edu IS NULL OR edu NOT IN ( 'p', 'm', 'b', 'a', 'hs', 'jhs', 'el', 'other' ) ), 1, 0)) edu9 , 
               Count(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 2, 1, NULL)) allcnt, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND gender = 'm', 1, 0)) male , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND gender = 'f', 1, 0)) female, 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND gender = 'o', 1, 0)) etc, 
        	   Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND gender NOT IN ( 'm', 'f', 'o' ), 1, 0)) no_gender3, 
        	   Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND age < 20, 1, 0)) age1 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND age BETWEEN 20 AND 29, 1, 0)) age2 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND age BETWEEN 30 AND 39, 1, 0)) age3 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND age BETWEEN 40 AND 49, 1, 0)) age4 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND age BETWEEN 50 AND 59, 1, 0)) age5 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND age > 59, 1, 0)) age6 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND edu = 'p', 1, 0)) edu1 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND edu = 'm', 1, 0)) edu2 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND edu = 'b', 1, 0)) edu3 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND edu = 'a', 1, 0)) edu4 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND edu = 'hs', 1, 0)) edu5 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND edu = 'jhs', 1, 0)) edu6 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND edu = 'el', 1, 0)) edu7 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND edu = 'other', 1, 0)) edu8 , 
               Sum(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1 AND ( edu IS NULL OR edu NOT IN ( 'p', 'm', 'b', 'a', 'hs', 'jhs', 'el', 'other' ) ), 1, 0)) edu9 , 
               Count(IF(real_time >= cert_time AND mode = 'audit' AND pass_type < 1, 1, NULL)) allcnt 
        FROM   (SELECT is_active, 
                       t1.course_id, 
                       org, 
                       gender, 
                       age, 
                       edu, 
                       mm  mode, 
                       CASE 
                         WHEN t2.status = 'downloadable' THEN 0 
                         WHEN t2.grade >= ( lowest_passing_grade / 2 ) THEN 1 
                         ELSE 2 
                       end pass_type,
                       cert.mmd as real_time,
                       t1.ccc as cert_time
                FROM   (SELECT b.is_active, 
                               a.id
                               course_id, 
                               a.org, 
                               a.lowest_passing_grade, 
                               c.id 
                               user_id, 
                               Ifnull(d.gender, '') 
                               gender, 
                               Substring('{year}', 1, 4) + 1 - 
                               Ifnull(d.year_of_birth, 0) age, 
                               d.level_of_education 
                               edu, 
                               b.mode mm,
                               b.created ccc
                        FROM   course_overviews_courseoverview a, 
                               student_courseenrollment b, 
                               auth_user c, 
                               auth_userprofile d 
                        WHERE  a.id = b.course_id 
                               AND b.user_id = c.id 
                               AND c.id = d.user_id 
                               AND Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}' 
                               AND Lower(b.course_id) NOT LIKE '%test%' 
                               AND Lower(b.course_id) NOT LIKE '%demo%' 
                               AND Lower(b.course_id) NOT LIKE '%nile%') t1 
                       LEFT JOIN certificates_generatedcertificate t2 
                              ON t1.course_id = t2.course_id 
                                 AND t1.user_id = t2.user_id 
                                 AND Date_format(Adddate(t2.created_date, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}'
                       left join
                       (
                   				select course_id, max(created_date) as mmd
                   				from certificates_generatedcertificate
                   				where status = 'downloadable'
                   				group by course_id
                        ) cert
                   	    on t1.course_id = cert.course_id) t3 
        GROUP  BY course_id, 
                  org;
    '''.format(
        year=date[:4],
        date=date
    )
    return execute_query(query)


# `by_course_demographic` `코스별 학력`
def by_course_demographics(date):
    query = '''
        SELECT course_id, 
               org, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND gender = 'm', 1, 0)) male , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND gender = 'f', 1, 0)) female, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND gender = 'o', 1, 0)) etc, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND gender NOT IN ( 'm', 'f', 'o' ), 1, 0)) no_gender1, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND age < 20, 1, 0)) age1, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND age BETWEEN 20 AND 29, 1, 0)) age2, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND age BETWEEN 30 AND 39, 1, 0)) age3,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND age BETWEEN 40 AND 49, 1, 0)) age4, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND age BETWEEN 50 AND 59, 1, 0)) age5,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND age > 59, 1, 0)) age6,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND edu = 'p', 1, 0)) edu1,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND edu = 'm', 1, 0)) edu2,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND edu = 'b', 1, 0)) edu3,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND edu = 'a', 1, 0)) edu4,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND edu = 'hs', 1, 0)) edu5,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND edu = 'jhs', 1, 0)) edu6,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND edu = 'el', 1, 0)) edu7,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND edu = 'other', 1, 0)) edu8,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3 AND ( edu IS NULL OR edu NOT IN ( 'p', 'm', 'b', 'a', 'hs', 'jhs', 'el', 'other' ) ), 1, 0)) edu9, 
               Count(IF(real_time <= cert_time AND mode = 'honor' AND is_active = 1 AND pass_type < 3, 1, NULL)) allcnt, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND gender = 'm', 1, 0)) male,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND gender = 'f', 1, 0)) female, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND gender = 'o', 1, 0)) etc, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND gender IN ( 'm', 'f', 'o' ), 1, 0)) no_gender2, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND age < 20, 1, 0)) age1, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND age BETWEEN 20 AND 29, 1, 0)) age2, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND age BETWEEN 30 AND 39, 1, 0)) age3, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND age BETWEEN 40 AND 49, 1, 0)) age4,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND age BETWEEN 50 AND 59, 1, 0)) age5,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND age > 59, 1, 0)) age6,
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND edu = 'p', 1, 0)) edu1, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND edu = 'm', 1, 0)) edu2 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND edu = 'b', 1, 0)) edu3 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND edu = 'a', 1, 0)) edu4 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND edu = 'hs', 1, 0)) edu5 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND edu = 'jhs', 1, 0)) edu6 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND edu = 'el', 1, 0)) edu7 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND edu = 'other', 1, 0)) edu8 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2 AND ( edu IS NULL OR edu NOT IN ( 'p', 'm', 'b', 'a', 'hs', 'jhs', 'el', 'other' ) ), 1, 0)) edu9 , 
               Count(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 2, 1, NULL)) allcnt, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND gender = 'm', 1, 0)) male , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND gender = 'f', 1, 0)) female, 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND gender = 'o', 1, 0)) etc, 
        	   Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND gender NOT IN ( 'm', 'f', 'o' ), 1, 0)) no_gender3, 
        	   Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND age < 20, 1, 0)) age1 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND age BETWEEN 20 AND 29, 1, 0)) age2 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND age BETWEEN 30 AND 39, 1, 0)) age3 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND age BETWEEN 40 AND 49, 1, 0)) age4 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND age BETWEEN 50 AND 59, 1, 0)) age5 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND age > 59, 1, 0)) age6 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND edu = 'p', 1, 0)) edu1 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND edu = 'm', 1, 0)) edu2 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND edu = 'b', 1, 0)) edu3 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND edu = 'a', 1, 0)) edu4 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND edu = 'hs', 1, 0)) edu5 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND edu = 'jhs', 1, 0)) edu6 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND edu = 'el', 1, 0)) edu7 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND edu = 'other', 1, 0)) edu8 , 
               Sum(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1 AND ( edu IS NULL OR edu NOT IN ( 'p', 'm', 'b', 'a', 'hs', 'jhs', 'el', 'other' ) ), 1, 0)) edu9 , 
               Count(IF(real_time <= cert_time AND mode = 'honor' AND pass_type < 1, 1, NULL)) allcnt 
        FROM   (SELECT is_active, 
                       t1.course_id, 
                       org, 
                       gender, 
                       age, 
                       edu, 
                       mm  mode, 
                       CASE 
                         WHEN t2.status = 'downloadable' THEN 0 
                         WHEN t2.grade >= ( lowest_passing_grade / 2 ) THEN 1 
                         ELSE 2 
                       end pass_type,
                       cert.mmd as real_time,
                       t1.ccc as cert_time
                FROM   (SELECT b.is_active, 
                               a.id
                               course_id, 
                               a.org, 
                               a.lowest_passing_grade, 
                               c.id 
                               user_id, 
                               Ifnull(d.gender, '') 
                               gender, 
                               Substring('{year}', 1, 4) + 1 - 
                               Ifnull(d.year_of_birth, 0) age, 
                               d.level_of_education 
                               edu, 
                               b.mode mm,
                               b.created ccc
                        FROM   course_overviews_courseoverview a, 
                               student_courseenrollment b, 
                               auth_user c, 
                               auth_userprofile d 
                        WHERE  a.id = b.course_id 
                               AND b.user_id = c.id 
                               AND c.id = d.user_id 
                               AND Date_format(Adddate(b.created, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}' 
                               AND Lower(b.course_id) NOT LIKE '%test%' 
                               AND Lower(b.course_id) NOT LIKE '%demo%' 
                               AND Lower(b.course_id) NOT LIKE '%nile%') t1 
                       LEFT JOIN certificates_generatedcertificate t2 
                              ON t1.course_id = t2.course_id 
                                 AND t1.user_id = t2.user_id 
                                 AND Date_format(Adddate(t2.created_date, INTERVAL 9 hour), '%Y%m%d') BETWEEN '1' AND '{date}'
                       left join
                       (
                   				select course_id, max(created_date) as mmd
                   				from certificates_generatedcertificate
                   				where status = 'downloadable'
                   				group by course_id
                        ) cert
                   	    on t1.course_id = cert.course_id) t3 
        GROUP  BY course_id, 
                  org;
    '''.format(
        year=date[:4],
        date=date
    )
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
                         AND date_format(adddate(c.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1' AND '{date}'
                         AND date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1' AND '{date}'
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
                                                                                    AND '{date}' and b.created between a.start and a.end
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
                                                                                    AND '{date}' and b.created between a.start and a.end
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
                           a.modified,
                           max(grade) grade
                      FROM courseware_studentmodule a, course_overviews_courseoverview b
                     WHERE     1=1
                           and a.course_id = b.id
                           and course_id =
                                  '{course_id}'
                           AND module_type IN ('video', 'problem')
                           AND CASE
                                  WHEN module_type = 'problem'
                                  THEN
                                     grade IS NOT NULL
                                  ELSE
                                     1 = 1
                               END
                           AND a.created <> a.modified
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
                           a.modified,
                           max(grade) grade
                      FROM courseware_studentmodule a, course_overviews_courseoverview b
                     WHERE 1=1
                           and a.course_id = b.id
                           and course_id =
                                  '{course_id}'
                           AND module_type IN ('video', 'problem')
                           AND CASE
                                  WHEN module_type = 'problem'
                                  THEN
                                     grade IS NOT NULL
                                  ELSE
                                     1 = 1
                               END
                           AND a.created <> a.modified
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
                                                                                    AND '{date}' and b.created between a.start and a.end
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
                                                                                    AND '{date}' and b.created between a.start and a.end
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
               sum(if(email LIKE 'delete_%' and date_format(adddate(last_login, INTERVAL 9 HOUR), '%Y%m%d') between '20151014' and '{date}', 0, 1)) allcnt
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
                                   a.modified,
                                   max(grade) grade
                              FROM courseware_studentmodule a, course_overviews_courseoverview b
                             WHERE     1 = 1
                                   and a.course_id = b.id
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
                                   AND a.created <> a.modified
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
                                   a.modified,
                                   max(grade) grade
                              FROM courseware_studentmodule a, course_overviews_courseoverview b
                             WHERE     1 = 1
                                   and a.course_id = b.id
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
                                   AND a.created <> a.modified
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


def age_gender_join(date):
    query = """
          SELECT age_group,
                 count(DISTINCT male)    male,
                 count(DISTINCT female)  female,
                 count(DISTINCT etc)     etc,
                 count(DISTINCT no_gender) no_gender
            FROM (SELECT CASE
                            WHEN age < 20 THEN 'age1'
                            WHEN age BETWEEN 20 AND 29 THEN 'age2'
                            WHEN age BETWEEN 30 AND 39 THEN 'age3'
                            WHEN age BETWEEN 40 AND 49 THEN 'age4'
                            WHEN age BETWEEN 50 AND 59 THEN 'age5'
                            WHEN age > 59 THEN 'age6'
                            ELSE 'age7'
                         END
                            age_group,
                         if(gender = 'm', user_id, NULL)                male,
                         if(gender = 'f', user_id, NULL)                female,
                         if(gender = 'o', user_id, NULL)                etc,
                         if(gender NOT IN ('m', 'f', 'o'), user_id, NULL) no_gender
                    FROM (SELECT b.user_id,
                                 ('{year}' - b.year_of_birth) + 1 age,
                                 ifnull(b.gender, '')         gender
                            FROM auth_user a, auth_userprofile b
                           WHERE     a.id = b.user_id and not (a.email LIKE 'delete_%' AND date_format(adddate(last_login, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014' AND '{date}')
                                 AND date_format(
                                        adddate(a.date_joined, INTERVAL 9 HOUR),
                                        '%Y%m%d') BETWEEN '20151014'
                                                      AND '{date}') t1) t2
        GROUP BY age_group;
    """.format(
        year=date[:4],
        date=date
    )

    return execute_query(query)


def age_gender_enroll(date):
    query = """
          SELECT age_group,
                 count(DISTINCT male)    male,
                 count(DISTINCT female)  female,
                 count(DISTINCT etc)     etc,
                 count(DISTINCT no_gender) no_gender
            FROM (SELECT CASE
                            WHEN age < 20 THEN 'age1'
                            WHEN age BETWEEN 20 AND 29 THEN 'age2'
                            WHEN age BETWEEN 30 AND 39 THEN 'age3'
                            WHEN age BETWEEN 40 AND 49 THEN 'age4'
                            WHEN age BETWEEN 50 AND 59 THEN 'age5'
                            WHEN age > 59 THEN 'age6'
                            ELSE 'age7'
                         END
                            age_group,
                         if(gender = 'm', user_id, NULL)                male,
                         if(gender = 'f', user_id, NULL)                female,
                         if(gender = 'o', user_id, NULL)                etc,
                         if(gender NOT IN ('m', 'f', 'o'), user_id, NULL) no_gender
                    FROM (SELECT b.user_id,
                                 ('{year}' - b.year_of_birth) + 1 age,
                                 ifnull(b.gender, '')         gender
                            FROM auth_user              a,
                                 auth_userprofile       b,
                                 student_courseenrollment c
                           WHERE     a.id = b.user_id
                                 AND a.id = c.user_id
                                 AND c.is_active = 1
                                 AND EXISTS
                                        (SELECT 1
                                           FROM course_overviews_courseoverview x
                                          WHERE x.id = c.course_id)
                                 AND lower(c.course_id) NOT LIKE '%test%'
                                 AND lower(c.course_id) NOT LIKE '%demo%'
                                 AND lower(c.course_id) NOT LIKE '%nile%'
                                 AND date_format(adddate(c.created, INTERVAL 9 HOUR),
                                                 '%Y%m%d') BETWEEN '1'
                                                               AND '{date}') t1) t2
        GROUP BY age_group;
    """.format(
        year=date[:4],
        date=date
    )

    return execute_query(query)


def age_gender_cert_half(date):
    query = """
          SELECT age_group,
                 count(DISTINCT male)    male,
                 count(DISTINCT female)  female,
                 count(DISTINCT etc)     etc,
                 count(DISTINCT no_gender) no_gender
            FROM (SELECT user_id,
                         CASE
                            WHEN age < 20 THEN 'age1'
                            WHEN age BETWEEN 20 AND 29 THEN 'age2'
                            WHEN age BETWEEN 30 AND 39 THEN 'age3'
                            WHEN age BETWEEN 40 AND 49 THEN 'age4'
                            WHEN age BETWEEN 50 AND 59 THEN 'age5'
                            WHEN age > 59 THEN 'age6'
                            ELSE 'age7'
                         END
                            age_group,
                         if(gender = 'm', user_id, NULL)                male,
                         if(gender = 'f', user_id, NULL)                female,
                         if(gender = 'o', user_id, NULL)                etc,
                         if(gender NOT IN ('m', 'f', 'o'), user_id, NULL) no_gender
                    FROM (SELECT b.user_id,
                                 ('{year}' - b.year_of_birth) + 1 age,
                                 ifnull(b.gender, '') gender
                            FROM auth_user                       a,
                                 auth_userprofile                b,
                                 student_courseenrollment        c,
                                 course_overviews_courseoverview d,
                                 certificates_generatedcertificate e
                           WHERE     a.id = b.user_id
                                 AND a.id = c.user_id
                                 AND c.course_id = d.id
                                 AND d.id = e.course_id
                                 AND a.id = e.user_id
                                 AND d.lowest_passing_grade / 2 <= e.grade
                                 AND lower(e.course_id) NOT LIKE '%test%'
                                 AND lower(e.course_id) NOT LIKE '%demo%'
                                 AND lower(e.course_id) NOT LIKE '%nile%'
                                 AND date_format(
                                        adddate(e.created_date, INTERVAL 9 HOUR),
                                        '%Y%m%d') BETWEEN '1'
                                                      AND '{date}') t1) t2
        GROUP BY age_group;
    """.format(
        year=date[:4],
        date=date
    )

    return execute_query(query)


def age_gender_cert(date):
    query = """
          SELECT age_group,
                 count(DISTINCT male)    male,
                 count(DISTINCT female)  female,
                 count(DISTINCT etc)     etc,
                 count(DISTINCT no_gender) no_gender
            FROM (SELECT CASE
                            WHEN age < 20 THEN 'age1'
                            WHEN age BETWEEN 20 AND 29 THEN 'age2'
                            WHEN age BETWEEN 30 AND 39 THEN 'age3'
                            WHEN age BETWEEN 40 AND 49 THEN 'age4'
                            WHEN age BETWEEN 50 AND 59 THEN 'age5'
                            WHEN age > 59 THEN 'age6'
                            ELSE 'age7'
                         END
                            age_group,
                         if(gender = 'm', user_id, NULL)                male,
                         if(gender = 'f', user_id, NULL)                female,
                         if(gender = 'o', user_id, NULL)                etc,
                         if(gender NOT IN ('m', 'f', 'o'), user_id, NULL) no_gender
                    FROM (SELECT b.user_id,
                                 ('{year}' - b.year_of_birth) + 1 age,
                                 ifnull(b.gender, '')         gender
                            FROM auth_user                       a,
                                 auth_userprofile                b,
                                 student_courseenrollment        c,
                                 course_overviews_courseoverview d,
                                 certificates_generatedcertificate e
                           WHERE     a.id = b.user_id
                                 AND a.id = c.user_id
                                 AND c.course_id = d.id
                                 AND d.id = e.course_id
                                 AND a.id = e.user_id
                                 AND e.status = 'downloadable'
                                 AND lower(e.course_id) NOT LIKE '%test%'
                                 AND lower(e.course_id) NOT LIKE '%demo%'
                                 AND lower(e.course_id) NOT LIKE '%nile%'
                                 AND date_format(
                                        adddate(e.created_date, INTERVAL 9 HOUR),
                                        '%Y%m%d') BETWEEN '1'
                                                      AND '{date}') t1) t2
        GROUP BY age_group;
    """.format(
        year=date[:4],
        date=date
    )

    return execute_query(query)


def edu_gender_join(date):
    query = """
          SELECT edu_group,
                 count(DISTINCT male)    gender,
                 count(DISTINCT female)  femail,
                 count(DISTINCT etc)     etc,
                 count(DISTINCT no_gender) no_gender
            FROM (SELECT CASE
                            WHEN level_of_education = 'p' THEN 1
                            WHEN level_of_education = 'm' THEN 2
                            WHEN level_of_education = 'b' THEN 3
                            WHEN level_of_education = 'a' THEN 4
                            WHEN level_of_education = 'hs' THEN 5
                            WHEN level_of_education = 'jhs' THEN 6
                            WHEN level_of_education = 'el' THEN 7
                            WHEN level_of_education = 'other' THEN 8
                            ELSE 9
                         END
                            edu_group,
                         if(gender = 'm', user_id, NULL)                male,
                         if(gender = 'f', user_id, NULL)                female,
                         if(gender = 'o', user_id, NULL)                etc,
                         if(gender NOT IN ('m', 'f', 'o'), user_id, NULL) no_gender
                    FROM (SELECT b.user_id,
                                 ifnull(level_of_education, '') level_of_education,
                                 ifnull(b.gender, '')         gender
                            FROM auth_user a, auth_userprofile b
                           WHERE     a.id = b.user_id and not (a.email LIKE 'delete_%' AND date_format(adddate(last_login, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014' AND '{date}')
                                 AND date_format(
                                        adddate(a.date_joined, INTERVAL 9 HOUR),
                                        '%Y%m%d') BETWEEN '20151014'
                                                      AND '{date}') t1) t2
        GROUP BY edu_group;
    """.format(
        year=date[:4],
        date=date
    )

    return execute_query(query)


def edu_gender_enroll(date):
    query = """
          SELECT edu_group,
                 count(DISTINCT male)    male,
                 count(DISTINCT female)  female,
                 count(DISTINCT etc)     etc,
                 count(DISTINCT no_gender) no_gender
            FROM (SELECT CASE
                            WHEN level_of_education = 'p' THEN 1
                            WHEN level_of_education = 'm' THEN 2
                            WHEN level_of_education = 'b' THEN 3
                            WHEN level_of_education = 'a' THEN 4
                            WHEN level_of_education = 'hs' THEN 5
                            WHEN level_of_education = 'jhs' THEN 6
                            WHEN level_of_education = 'el' THEN 7
                            WHEN level_of_education = 'other' THEN 8
                            ELSE 9
                         END
                            edu_group,
                         if(gender = 'm', user_id, NULL)                male,
                         if(gender = 'f', user_id, NULL)                female,
                         if(gender = 'o', user_id, NULL)                etc,
                         if(gender NOT IN ('m', 'f', 'o'), user_id, NULL) no_gender
                    FROM (SELECT b.user_id,
                                 ifnull(level_of_education, '') level_of_education,
                                 ('{year}' - b.year_of_birth) + 1 age,
                                 ifnull(b.gender, '')         gender
                            FROM auth_user              a,
                                 auth_userprofile       b,
                                 student_courseenrollment c
                           WHERE     a.id = b.user_id
                                 AND a.id = c.user_id
                                 AND c.is_active = 1
                                 AND EXISTS
                                        (SELECT 1
                                           FROM course_overviews_courseoverview x
                                          WHERE x.id = c.course_id)
                                 AND lower(c.course_id) NOT LIKE '%test%'
                                 AND lower(c.course_id) NOT LIKE '%demo%'
                                 AND lower(c.course_id) NOT LIKE '%nile%'
                                 AND date_format(adddate(c.created, INTERVAL 9 HOUR),
                                                 '%Y%m%d') BETWEEN '1'
                                                               AND '{date}') t1) t2
        GROUP BY edu_group;
    """.format(
        year=date[:4],
        date=date
    )

    return execute_query(query)


def edu_gender_cert_half(date):
    query = """
          SELECT edu_group,
                 count(DISTINCT male)    male,
                 count(DISTINCT female)  female,
                 count(DISTINCT etc)     etc,
                 count(DISTINCT no_gender) no_gender
            FROM (SELECT CASE
                            WHEN level_of_education = 'p' THEN 1
                            WHEN level_of_education = 'm' THEN 2
                            WHEN level_of_education = 'b' THEN 3
                            WHEN level_of_education = 'a' THEN 4
                            WHEN level_of_education = 'hs' THEN 5
                            WHEN level_of_education = 'jhs' THEN 6
                            WHEN level_of_education = 'el' THEN 7
                            WHEN level_of_education = 'other' THEN 8
                            ELSE 9
                         END
                            edu_group,
                         if(gender = 'm', user_id, NULL)                male,
                         if(gender = 'f', user_id, NULL)                female,
                         if(gender = 'o', user_id, NULL)                etc,
                         if(gender NOT IN ('m', 'f', 'o'), user_id, NULL) no_gender
                    FROM (SELECT b.user_id,
                                 ifnull(level_of_education, '') level_of_education,
                                 ('{year}' - b.year_of_birth) + 1 age,
                                 ifnull(b.gender, '')         gender
                            FROM auth_user                       a,
                                 auth_userprofile                b,
                                 student_courseenrollment        c,
                                 course_overviews_courseoverview d,
                                 certificates_generatedcertificate e
                           WHERE     a.id = b.user_id
                                 AND a.id = c.user_id
                                 AND c.course_id = d.id
                                 AND d.id = e.course_id
                                 AND a.id = e.user_id
                                 AND d.lowest_passing_grade / 2 <= e.grade
                                 AND lower(e.course_id) NOT LIKE '%test%'
                                 AND lower(e.course_id) NOT LIKE '%demo%'
                                 AND lower(e.course_id) NOT LIKE '%nile%'
                                 AND date_format(
                                        adddate(e.created_date, INTERVAL 9 HOUR),
                                        '%Y%m%d') BETWEEN '1'
                                                      AND '{date}') t1) t2
        GROUP BY edu_group;
    """.format(
        year=date[:4],
        date=date
    )

    return execute_query(query)


def edu_gender_cert(date):
    query = """
          SELECT edu_group,
                 count(DISTINCT male)    male,
                 count(DISTINCT female)  female,
                 count(DISTINCT etc)     etc,
                 count(DISTINCT no_gender) no_gender
            FROM (SELECT CASE
                            WHEN level_of_education = 'p' THEN 1
                            WHEN level_of_education = 'm' THEN 2
                            WHEN level_of_education = 'b' THEN 3
                            WHEN level_of_education = 'a' THEN 4
                            WHEN level_of_education = 'hs' THEN 5
                            WHEN level_of_education = 'jhs' THEN 6
                            WHEN level_of_education = 'el' THEN 7
                            WHEN level_of_education = 'other' THEN 8
                            ELSE 9
                         END
                            edu_group,
                         if(gender = 'm', user_id, NULL)                male,
                         if(gender = 'f', user_id, NULL)                female,
                         if(gender = 'o', user_id, NULL)                etc,
                         if(gender NOT IN ('m', 'f', 'o'), user_id, NULL) no_gender
                    FROM (SELECT b.user_id,
                                 ifnull(level_of_education, '')
                                    level_of_education,
                                 ifnull(b.gender, '')                      gender
                            FROM auth_user                       a,
                                 auth_userprofile                b,
                                 student_courseenrollment        c,
                                 course_overviews_courseoverview d,
                                 certificates_generatedcertificate e
                           WHERE     a.id = b.user_id
                                 AND a.id = c.user_id
                                 AND c.course_id = d.id
                                 AND d.id = e.course_id
                                 AND a.id = e.user_id
                                 AND e.status = 'downloadable'
                                 AND lower(e.course_id) NOT LIKE '%test%'
                                 AND lower(e.course_id) NOT LIKE '%demo%'
                                 AND lower(e.course_id) NOT LIKE '%nile%'
                                 AND date_format(
                                        adddate(e.created_date, INTERVAL 9 HOUR),
                                        '%Y%m%d') BETWEEN '1'
                                                      AND '{date}') t1) t2
        GROUP BY edu_group;
    """.format(
        year=date[:4],
        date=date
    )

    return execute_query(query)


def age_edu_join(date):
    query = """
          SELECT age_group,
                 sum(if(level_of_education = 'P', 1, 0))   edu1,
                 sum(if(level_of_education = 'm', 1, 0))   edu2,
                 sum(if(level_of_education = 'b', 1, 0))   edu3,
                 sum(if(level_of_education = 'a', 1, 0))   edu4,
                 sum(if(level_of_education = 'hs', 1, 0))  edu5,
                 sum(if(level_of_education = 'jhs', 1, 0)) edu6,
                 sum(if(level_of_education = 'el', 1, 0))  edu7,
                 sum(if(level_of_education = 'other', 1, 0)) edu8,
                 sum(if(level_of_education NOT IN ('p',
                                                   'm',
                                                   'b',
                                                   'a',
                                                   'hs',
                                                   'jhs',
                                                   'el',
                                                   'other'),
                        1,
                        0))
                    edu9
            FROM (SELECT level_of_education,
                         CASE
                            WHEN age < 20 THEN 'age1'
                            WHEN age BETWEEN 20 AND 29 THEN 'age2'
                            WHEN age BETWEEN 30 AND 39 THEN 'age3'
                            WHEN age BETWEEN 40 AND 49 THEN 'age4'
                            WHEN age BETWEEN 50 AND 59 THEN 'age5'
                            WHEN age > 59 THEN 'age6'
                            ELSE 'age7'
                         END
                            age_group
                    FROM (SELECT ifnull(level_of_education, '') level_of_education,
                                 ('{year}' - b.year_of_birth) + 1 age
                            FROM auth_user a, auth_userprofile b
                           WHERE     a.id = b.user_id and not (a.email LIKE 'delete_%' AND date_format(adddate(last_login, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014' AND '{date}')
                                 AND date_format(
                                        adddate(a.date_joined, INTERVAL 9 HOUR),
                                        '%Y%m%d') BETWEEN '20151014'
                                                      AND '{date}') t1) t2
        GROUP BY age_group;
    """.format(
        year=date[:4],
        date=date
    )

    return execute_query(query)


def age_edu_enroll(date):
    query = """
          SELECT age_group,
                 count(distinct if(level_of_education = 'P', user_id, null))   edu1,
                 count(distinct if(level_of_education = 'm', user_id, null))   edu2,
                 count(distinct if(level_of_education = 'b', user_id, null))   edu3,
                 count(distinct if(level_of_education = 'a', user_id, null))   edu4,
                 count(distinct if(level_of_education = 'hs', user_id, null))  edu5,
                 count(distinct if(level_of_education = 'jhs', user_id, null)) edu6,
                 count(distinct if(level_of_education = 'el', user_id, null))  edu7,
                 count(distinct if(level_of_education = 'other', user_id, null)) edu8,
                 count(distinct if(level_of_education NOT IN ('p',
                                                   'm',
                                                   'b',
                                                   'a',
                                                   'hs',
                                                   'jhs',
                                                   'el',
                                                   'other'),
                        user_id, null))
                    edu9
            FROM (SELECT user_id, level_of_education,
                         CASE
                            WHEN age < 20 THEN 'age1'
                            WHEN age BETWEEN 20 AND 29 THEN 'age2'
                            WHEN age BETWEEN 30 AND 39 THEN 'age3'
                            WHEN age BETWEEN 40 AND 49 THEN 'age4'
                            WHEN age BETWEEN 50 AND 59 THEN 'age5'
                            WHEN age > 59 THEN 'age6'
                            ELSE 'age7'
                         END
                            age_group
                    FROM (SELECT b.user_id, ifnull(level_of_education, '') level_of_education,
                                 ('{year}' - b.year_of_birth) + 1 age
                            FROM auth_user              a,
                                 auth_userprofile       b,
                                 student_courseenrollment c
                           WHERE     a.id = b.user_id
                                 AND a.id = c.user_id
                                 AND c.is_active = 1
                                 AND EXISTS
                                        (SELECT 1
                                           FROM course_overviews_courseoverview x
                                          WHERE x.id = c.course_id)
                                 AND lower(c.course_id) NOT LIKE '%test%'
                                 AND lower(c.course_id) NOT LIKE '%demo%'
                                 AND lower(c.course_id) NOT LIKE '%nile%'
                                 AND date_format(adddate(c.created, INTERVAL 9 HOUR),
                                                 '%Y%m%d') BETWEEN '1'
                                                               AND '{date}') t1) t2
        GROUP BY age_group;
    """.format(
        year=date[:4],
        date=date
    )

    return execute_query(query)


def age_edu_cert_half(date):
    query = """
          SELECT age_group,
                 count(distinct if(level_of_education = 'P', user_id, null))   edu1,
                 count(distinct if(level_of_education = 'm', user_id, null))   edu2,
                 count(distinct if(level_of_education = 'b', user_id, null))   edu3,
                 count(distinct if(level_of_education = 'a', user_id, null))   edu4,
                 count(distinct if(level_of_education = 'hs', user_id, null))  edu5,
                 count(distinct if(level_of_education = 'jhs', user_id, null)) edu6,
                 count(distinct if(level_of_education = 'el', user_id, null))  edu7,
                 count(distinct if(level_of_education = 'other', user_id, null)) edu8,
                 count(distinct if(level_of_education NOT IN ('p',
                                                   'm',
                                                   'b',
                                                   'a',
                                                   'hs',
                                                   'jhs',
                                                   'el',
                                                   'other'),
                        user_id, null))
                    edu9
            FROM (SELECT user_id, level_of_education,
                         CASE
                            WHEN age < 20 THEN 'age1'
                            WHEN age BETWEEN 20 AND 29 THEN 'age2'
                            WHEN age BETWEEN 30 AND 39 THEN 'age3'
                            WHEN age BETWEEN 40 AND 49 THEN 'age4'
                            WHEN age BETWEEN 50 AND 59 THEN 'age5'
                            WHEN age > 59 THEN 'age6'
                            ELSE 'age7'
                         END
                            age_group
                    FROM (SELECT b.user_id, ifnull(level_of_education, '') level_of_education,
                                 ('{year}' - b.year_of_birth) + 1 age
                            FROM auth_user                       a,
                                 auth_userprofile                b,
                                 student_courseenrollment        c,
                                 course_overviews_courseoverview d,
                                 certificates_generatedcertificate e
                           WHERE     a.id = b.user_id
                                 AND a.id = c.user_id
                                 AND c.course_id = d.id
                                 AND d.id = e.course_id
                                 AND a.id = e.user_id
                                 AND d.lowest_passing_grade / 2 <= e.grade
                                 AND lower(e.course_id) NOT LIKE '%test%'
                                 AND lower(e.course_id) NOT LIKE '%demo%'
                                 AND lower(e.course_id) NOT LIKE '%nile%'
                                 AND date_format(
                                        adddate(e.created_date, INTERVAL 9 HOUR),
                                        '%Y%m%d') BETWEEN '1'
                                                      AND '{date}') t1) t2
        GROUP BY age_group;
    """.format(
        year=date[:4],
        date=date
    )

    return execute_query(query)

def age_edu_cert(date):
    query = """
          SELECT age_group,
                 count(distinct if(level_of_education = 'P', user_id, null))   edu1,
                 count(distinct if(level_of_education = 'm', user_id, null))   edu2,
                 count(distinct if(level_of_education = 'b', user_id, null))   edu3,
                 count(distinct if(level_of_education = 'a', user_id, null))   edu4,
                 count(distinct if(level_of_education = 'hs', user_id, null))  edu5,
                 count(distinct if(level_of_education = 'jhs', user_id, null)) edu6,
                 count(distinct if(level_of_education = 'el', user_id, null))  edu7,
                 count(distinct if(level_of_education = 'other', user_id, null)) edu8,
                 count(distinct if(level_of_education NOT IN ('p',
                                                   'm',
                                                   'b',
                                                   'a',
                                                   'hs',
                                                   'jhs',
                                                   'el',
                                                   'other'),
                        user_id, null))
                    edu9
            FROM (SELECT user_id, level_of_education,
                         CASE
                            WHEN age < 20 THEN 'age1'
                            WHEN age BETWEEN 20 AND 29 THEN 'age2'
                            WHEN age BETWEEN 30 AND 39 THEN 'age3'
                            WHEN age BETWEEN 40 AND 49 THEN 'age4'
                            WHEN age BETWEEN 50 AND 59 THEN 'age5'
                            WHEN age > 59 THEN 'age6'
                            ELSE 'age7'
                         END
                            age_group
                    FROM (SELECT b.user_id, ifnull(level_of_education, '') level_of_education,
                                 ('{year}' - b.year_of_birth) + 1 age
                            FROM auth_user                       a,
                                 auth_userprofile                b,
                                 student_courseenrollment        c,
                                 course_overviews_courseoverview d,
                                 certificates_generatedcertificate e
                           WHERE     a.id = b.user_id
                                 AND a.id = c.user_id
                                 AND c.course_id = d.id
                                 AND d.id = e.course_id
                                 AND a.id = e.user_id
                                 AND e.status = 'downloadable'
                                 AND lower(e.course_id) NOT LIKE '%test%'
                                 AND lower(e.course_id) NOT LIKE '%demo%'
                                 AND lower(e.course_id) NOT LIKE '%nile%'
                                 AND date_format(
                                        adddate(e.created_date, INTERVAL 9 HOUR),
                                        '%Y%m%d') BETWEEN '1'
                                                      AND '{date}') t1) t2
        GROUP BY age_group;
    """.format(
        year=date[:4],
        date=date
    )

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
                       count(CASE WHEN gender not in ('m', 'f') or gender is null THEN 1 END) etc
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
                       count(CASE WHEN gender not in ('m', 'f') or gender is null THEN 1 END) etc
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
                                      and not (b.email like 'delete_%' and date_format(adddate(last_login, INTERVAL 9 HOUR), '%Y%m%d') between '20151014' and '{date}')
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
                       sum(if(a.gender not in ('m', 'f') or a.gender is null, 1, 0)) AS "etc"
                  FROM auth_userprofile a, auth_user b
                 WHERE     a.user_id = b.id
                       AND date_format(adddate(b.date_joined, INTERVAL 9 HOUR),'%Y%m%d') = '{date}'
                       and not (b.email like 'delete_%' and date_format(adddate(last_login, INTERVAL 9 HOUR), '%Y%m%d') between '20151014' and '{date}')
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
                       if(a.gender not in ('m', 'f') or a.gender is null, 1, 0) AS "etc"
                  FROM auth_userprofile a, auth_user b
                 WHERE     a.user_id = b.id
                        and not (b.email like 'delete_%' and date_format(adddate(last_login, INTERVAL 9 HOUR), '%Y%m%d') between '20151014' and '{date}')
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
                                      and not (b.email like 'delete_%' and date_format(adddate(last_login, INTERVAL 9 HOUR), '%Y%m%d') between '20151014' and '{date}')
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


# `by_course_enroll`
def by_course_enroll_activity(date):
    query = '''
        SELECT id,
               org,
               new_enroll_cnt,
               new_unenroll_cnt,
               all_enroll_cnt,
               all_unenroll_cnt,
               (SELECT count(*)
                  FROM certificates_generatedcertificate e
                 WHERE     e.course_id = t1.id
                       AND e.grade >= lowest_passing_grade / 2
                       AND date_format(adddate(e.created_date, INTERVAL 9 HOUR),
                                       '%Y%m%d') BETWEEN '1'
                                                     AND '{date}')
                  half_cnt,
               (SELECT count(*)
                  FROM certificates_generatedcertificate e
                 WHERE     e.course_id = t1.id
                       AND e.status = 'downloadable'
                       AND date_format(adddate(e.created_date, INTERVAL 9 HOUR),
                                       '%Y%m%d') BETWEEN '1'
                                                     AND '{date}')
                  cert_cnt,
               v_cnt,
               q_cnt,
               f_cnt,
               both_cnt
          FROM (  SELECT a.id,
                         a.org,
                         a.lowest_passing_grade,
                         sum(
                            if(date_format(adddate(b.created, INTERVAL 9 HOUR),
                                           '%Y%m%d') = '{date}',
                               1,
                               0))
                            `new_enroll_cnt`,
                         sum(
                            if(
                                   date_format(adddate(b.created, INTERVAL 9 HOUR),
                                               '%Y%m%d') = '{date}'
                               AND b.is_active = 0,
                               1,
                               0))
                            `new_unenroll_cnt`,
                         sum(
                            if(
                               date_format(adddate(b.created, INTERVAL 9 HOUR),
                                           '%Y%m%d') BETWEEN '1'
                                                         AND '{date}',
                               1,
                               0))
                            `all_enroll_cnt`,
                         sum(
                            if(
                                   date_format(adddate(b.created, INTERVAL 9 HOUR),
                                               '%Y%m%d') BETWEEN '1'
                                                             AND '{date}'
                               AND b.is_active = 0,
                               1,
                               0))
                            `all_unenroll_cnt`
                    FROM course_overviews_courseoverview a,
                         student_courseenrollment      b,
                         auth_user                     c,
                         auth_userprofile              d
                   WHERE     a.id = b.course_id
                         AND b.user_id = c.id
                         AND c.id = d.user_id
                         AND lower(b.course_id) NOT LIKE '%test%'
                         AND lower(b.course_id) NOT LIKE '%demo%'
                         AND lower(b.course_id) NOT LIKE '%nile%'
                         AND date_format(adddate(b.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                            AND '{date}'
                         AND date_format(adddate(c.date_joined, INTERVAL 9 HOUR),
                                         '%Y%m%d') BETWEEN '1'
                                                       AND '{date}'
                GROUP BY a.id, a.org, a.lowest_passing_grade) t1,
               (  SELECT a.id                                  course_id,
                         count(if(c.v_cnt > 0, c.user_id, NULL)) v_cnt,
                         count(if(c.q_cnt > 0, c.user_id, NULL)) q_cnt,
                         count(if(c.f_cnt > 0, c.user_id, NULL)) f_cnt,
                         count(
                            if(c.v_cnt > 0 OR c.q_cnt > 0 OR c.f_cnt > 0,
                               c.user_id,
                               NULL))
                            both_cnt
                    FROM course_overviews_courseoverview a
                         LEFT JOIN student_courseenrollment b
                            ON a.id = b.course_id AND b.is_active = 1
                         LEFT JOIN course_activity c
                            ON b.course_id = c.course_id AND b.user_id = c.user_id
                GROUP BY a.id) t2
         WHERE t1.id = t2.course_id;    
    '''.format(date=date)
    return execute_query(query)
