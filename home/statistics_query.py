# -*- coding: utf-8 -*-
import statistics
from django.db import connection
import logging
import logging.handlers
from management.settings import EXCEL_PATH, dic_univ, database_id, debug


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


# 엑셀 시간
def excel_now_day():
    query = """
      select date_format(now(),'%Y%m%d');
    """
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchone()[0]
    cur.close()
    return row


# 회원 가입자수
def user_join(date):
    query = """
      SELECT sum(if(date_format(adddate(b.date_joined, INTERVAL 9 HOUR), '%Y%m%d') = '{date}' ,1,0)) newcnt,
                       sum(if(b.email LIKE 'delete_%', 0, 1)) cnt,
                       count(b.id) allcnt
                  FROM auth_userprofile a, auth_user b
                 WHERE     a.user_id = b.id
                       AND date_format(adddate(b.date_joined, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '20151014' AND '{date}';
    """.format(date=date)
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cur.close()
    return row


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
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cur.close()
    return row


# 수강신청자수(통합 <중복제거> : 취소 미반영)
def course_count_active(date):

    query = """
        SELECT count(DISTINCT a.user_id) distcnt
          FROM student_courseenrollment a, auth_user b
         WHERE     a.user_id = b.id
               AND date_format(adddate(a.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1' AND '{date}'
               AND a.is_active = 1
               and exists (select 1 from student_courseaccessrole c where a.course_id = c.course_id)
               AND lower(a.course_id) NOT LIKE '%test%'
               AND lower(a.course_id) NOT LIKE '%demo%'
               AND lower(a.course_id) NOT LIKE '%nile%';
    """.format(date=date)
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cur.close()
    return row


# 수강신청구분
def course_case(date):
    query = """
        SELECT 1                                              gubn,
               (select count(*) from auth_user a, auth_userprofile b where a.id = b.user_id and email not like 'delete_%' and date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') = '{date}') is_secession,
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
               (select count(*) from auth_user a, auth_userprofile b where a.id = b.user_id and email not like 'delete_%' and date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') between '20151014' and '{date}') is_secession,
               (select count(*) from auth_user a, auth_userprofile b where a.id = b.user_id and email like 'delete_%' and date_format(adddate(a.date_joined, INTERVAL 9 HOUR), '%Y%m%d') between '20151014' and '{date}') no_secession,
               count(if(c.is_active = 1, a.id, NULL))         is_active,
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
                 count(DISTINCT if(c.is_active = 1, a.id, NULL))       is_active,
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
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


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
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


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
                       AND date_format(adddate(b.date_joined, INTERVAL 9 HOUR),'%Y%m%d') BETWEEN '20151014' AND '{date}'
                ) b
                  ON a.r = b.result
        group by a.r
        ORDER BY a.r;
    """.format(date=date)
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


# 연령구분(신규)
def age_new(date):
    query = """
        SELECT ifnull(b.male, 0), ifnull(b.female, 0), ifnull(b.etc, 0)
          FROM (SELECT (@rn := @rn + 1) r
                  FROM auth_user a, (SELECT @rn := 0) b
                 LIMIT 7) a
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
                          FROM (SELECT   ('{year}' - a.year_of_birth)
                                       + 1
                                          age,
                                       a.gender
                                  FROM auth_userprofile a, auth_user b
                                 WHERE     a.user_id = b.id
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


    print query



    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


# 연령구분(누적)
def age_total(date):
    query = """
        SELECT b.male, b.female, b.etc
          FROM (SELECT (@rn := @rn + 1) r
                  FROM auth_user a, (SELECT @rn := 0) b
                 LIMIT 7) a
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
                          FROM (SELECT   ('{year}' - a.year_of_birth)
                                       + 1
                                          age,
                                       a.gender
                                  FROM auth_userprofile a, auth_user b
                                 WHERE     a.user_id = b.id
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
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


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
                 LIMIT 7) a
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
                          FROM (SELECT   ('{year}' - a.year_of_birth)
                                       + 1
                                          age,
                                       ifnull(a.level_of_education, '') lv,
                                       a.gender
                                  FROM auth_userprofile a, auth_user b
                                 WHERE     a.user_id = b.id
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
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


# 코스별 수강자수
def course_user(date):
    query = """
        SELECT a.course_id,
               substring(substring_index(a.course_id, '+', 2),
                         instr(a.course_id, '+') + 1)
                  course_id1,
               substring_index(a.course_id, '+', -1) course_id2,
               ifnull(cnt, 0)
          FROM (SELECT DISTINCT a.course_id
                  FROM course_structures_coursestructure a,
                       student_courseaccessrole b
                 WHERE     a.course_id = b.course_id
                       AND lower(a.course_id) NOT LIKE '%test%'
                       AND lower(a.course_id) NOT LIKE '%demo%'
                       AND lower(a.course_id) NOT LIKE '%nile%') a
               LEFT JOIN
               (SELECT course_id, cnt
                  FROM (SELECT a.course_id, count(*) cnt
                          FROM student_courseenrollment a, auth_user b
                         WHERE     a.user_id = b.id
                               AND date_format(adddate(a.created, INTERVAL 9 HOUR),
                                               '%Y%m%d') = '{date}'
                               and exists (select 1 from student_courseaccessrole c where a.course_id = c.course_id)
                               AND a.is_active = 1
                               AND lower(a.course_id) NOT LIKE '%test%'
                               AND lower(a.course_id) NOT LIKE '%demo%'
                               AND lower(a.course_id) NOT LIKE '%nile%'
                        GROUP BY a.course_id) aa) b
                  ON a.course_id = b.course_id;
    """.format(date=date)
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


# 코스별 수강자수(누적)
def course_user_total(date):
    query = """
        SELECT a.course_id,
               substring(substring_index(a.course_id, '+', 2),
                         instr(a.course_id, '+') + 1)
                  course_id1,
               substring_index(a.course_id, '+', -1) course_id2,
               ifnull(cnt, 0),
               ifnull(cnt2, 0)
          FROM (SELECT DISTINCT a.course_id
                  FROM course_structures_coursestructure a,
                       student_courseaccessrole b
                 WHERE     a.course_id = b.course_id
                       AND lower(a.course_id) NOT LIKE '%test%'
                       AND lower(a.course_id) NOT LIKE '%demo%'
                       AND lower(a.course_id) NOT LIKE '%nile%') a
               LEFT JOIN
               (SELECT course_id, cnt, cnt2
                  FROM (SELECT a.course_id, count(*) cnt, sum(if(a.is_active = 1, 1, 0)) cnt2
                          FROM student_courseenrollment a, auth_user b
                         WHERE     a.user_id = b.id
                               AND date_format(adddate(a.created, INTERVAL 9 HOUR),
                                               '%Y%m%d') BETWEEN '1'
                                                             AND '{date}'
                               and exists (select 1 from student_courseaccessrole c where a.course_id = c.course_id)
                               AND lower(a.course_id) NOT LIKE '%test%'
                               AND lower(a.course_id) NOT LIKE '%demo%'
                               AND lower(a.course_id) NOT LIKE '%nile%'
                        GROUP BY a.course_id) aa) b
                  ON a.course_id = b.course_id;
    """.format(date=date)
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


# 코스별 연령
def course_age(date):
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
               sum(if(age < 20, 1, 0)),
               sum(if(age BETWEEN 20 AND 29, 1, 0)),
               sum(if(age BETWEEN 30 AND 39, 1, 0)),
               sum(if(age BETWEEN 40 AND 49, 1, 0)),
               sum(if(age BETWEEN 50 AND 59, 1, 0)),
               sum(if(age >= 60, 1, 0)),
               count(age)
          FROM (SELECT DISTINCT a.course_id
                  FROM course_structures_coursestructure a,
                       student_courseaccessrole b
                 WHERE     a.course_id = b.course_id
                       AND lower(a.course_id) NOT LIKE '%test%'
                       AND lower(a.course_id) NOT LIKE '%demo%'
                       AND lower(a.course_id) NOT LIKE '%nile%') a
               LEFT JOIN
               (SELECT course_id,
                       ifnull(('{year}' - year_of_birth), 0) + 1 age
                  FROM (SELECT a.course_id, c.year_of_birth
                          FROM student_courseenrollment a,
                               auth_user b,
                               auth_userprofile c
                         WHERE     a.user_id = b.id
                               AND b.id = c.user_id
                               and exists (select 1 from student_courseaccessrole d where a.course_id = d.course_id)
                               AND date_format(adddate(a.created, INTERVAL 9 HOUR),
                                               '%Y%m%d') BETWEEN '1'
                                                             AND '{date}'
                               AND a.is_active = 1
                               AND lower(a.course_id) NOT LIKE '%test%'
                               AND lower(a.course_id) NOT LIKE '%demo%'
                               AND lower(a.course_id) NOT LIKE '%nile%') aa) b
                  ON a.course_id = b.course_id
        GROUP BY a.course_id;
    """.format(
        year=date[:4],
        date=date
    )
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


# 코스별 학력
def course_edu(date):
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
                 sum(if(level_of_education = 'p', 1, 0)),
                 sum(if(level_of_education = 'm', 1, 0)),
                 sum(if(level_of_education = 'b', 1, 0)),
                 sum(if(level_of_education = 'a', 1, 0)),
                 sum(if(level_of_education = 'hs', 1, 0)),
                 sum(if(level_of_education = 'jhs', 1, 0)),
                 sum(if(level_of_education = 'el', 1, 0)),
                 sum(if(level_of_education = 'other', 1, 0)),
                 sum(if(level_of_education NOT IN ('p',
                                                               'm',
                                                               'b',
                                                               'a',
                                                               'hs',
                                                               'jhs',
                                                               'el',
                                                               'other'),
                        1,
                        0)),
                 count(level_of_education)
            FROM (SELECT DISTINCT a.course_id
                    FROM course_structures_coursestructure a,
                         student_courseaccessrole        b
                   WHERE     a.course_id = b.course_id
                         AND lower(a.course_id) NOT LIKE '%test%'
                         AND lower(a.course_id) NOT LIKE '%demo%'
                         AND lower(a.course_id) NOT LIKE '%nile%') a
                 LEFT JOIN
                 (SELECT course_id, ifnull(level_of_education, '') level_of_education
                    FROM (SELECT a.course_id, c.level_of_education
                            FROM student_courseenrollment a,
                                 auth_user              b,
                                 auth_userprofile       c
                           WHERE     a.user_id = b.id
                                 AND b.id = c.user_id
                                 and exists (select 1 from student_courseaccessrole d where a.course_id = d.course_id)
                                 AND date_format(adddate(a.created, INTERVAL 9 HOUR),
                                                 '%Y%m%d') BETWEEN '1'
                                                               AND '{date}'
                                 AND a.is_active = 1
                                 AND lower(a.course_id) NOT LIKE '%test%'
                                 AND lower(a.course_id) NOT LIKE '%demo%'
                                 AND lower(a.course_id) NOT LIKE '%nile%') aa) b
                    ON a.course_id = b.course_id
        GROUP BY a.course_id
        ORDER BY a.course_id;
    """.format(date=date)
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


# 강좌 아이디 조회
def course_ids_all():
    query = """
        SELECT id,
               display_name,
               display_number_with_default course,
               display_org_with_default    org,
               start,
               end,
               a.enrollment_start,
               a.enrollment_end
          FROM course_overviews_courseoverview a
         WHERE     1 = 1
               AND lower(a.id) NOT LIKE '%test%'
               AND lower(a.id) NOT LIKE '%demo%'
               AND lower(a.id) NOT LIKE '%nile%';
    """
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row

# 강좌별 수강신청자
def course_univ(date):
    query = """
        SELECT if(instr(a.org, 'SKP.') > 0, 'SKP.SNUk', a.org), count(b.org) cnt
          FROM (SELECT DISTINCT
                       substring(
                          a.course_id,
                          instr(a.course_id, ':') + 1,
                          (instr(a.course_id, '+')) - instr(a.course_id, ':') - 1)
                          org
                  FROM course_structures_coursestructure a,
                       student_courseaccessrole b
                 WHERE     1 = 1
                       AND a.course_id = b.course_id
                       AND lower(a.course_id) NOT LIKE '%test%'
                       AND lower(a.course_id) NOT LIKE '%demo%'
                       AND lower(a.course_id) NOT LIKE '%nile%'
                GROUP BY a.course_id) a
               LEFT JOIN
               (SELECT substring(
                          a.course_id,
                          instr(a.course_id, ':') + 1,
                          (instr(a.course_id, '+')) - instr(a.course_id, ':') - 1)
                          org
                  FROM student_courseenrollment a, auth_user b
                 WHERE     a.user_id = b.id
                       AND date_format(adddate(a.created, INTERVAL 9 HOUR), '%Y%m%d') =
                              '{date}'
                       and exists (select 1 from student_courseaccessrole c where a.course_id = c.course_id)
                       AND a.is_active = 1
                       AND lower(a.course_id) NOT LIKE '%test%'
                       AND lower(a.course_id) NOT LIKE '%demo%'
                       AND lower(a.course_id) NOT LIKE '%nile%') b
                  ON a.org = b.org
        GROUP BY if(instr(a.org, 'SKP.') > 0, 'SKP.SNUk', a.org)
        ORDER BY if(instr(a.org, 'SKP.') > 0, 'SKP.SNUk', a.org);
    """.format(date=date)
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


# 강좌별 수강신청자 누적
def course_univ_total(date):
    query = """
        SELECT if(instr(a.org, 'SKP.') > 0, 'SKP.SNUk', a.org), count(b.org) cnt, sum(b.is_active) cnt2
          FROM (SELECT DISTINCT
                       substring(
                          a.course_id,
                          instr(a.course_id, ':') + 1,
                          (instr(a.course_id, '+')) - instr(a.course_id, ':') - 1)
                          org
                  FROM course_structures_coursestructure a,
                       student_courseaccessrole b
                 WHERE     1 = 1
                       AND a.course_id = b.course_id
                       AND lower(a.course_id) NOT LIKE '%test%'
                       AND lower(a.course_id) NOT LIKE '%demo%'
                       AND lower(a.course_id) NOT LIKE '%nile%'
                GROUP BY a.course_id) a
               LEFT JOIN
               (SELECT substring(
                          a.course_id,
                          instr(a.course_id, ':') + 1,
                          (instr(a.course_id, '+')) - instr(a.course_id, ':') - 1)
                          org, a.is_active
                  FROM student_courseenrollment a, auth_user b
                 WHERE     a.user_id = b.id
                       and exists (select 1 from student_courseaccessrole c where a.course_id = c.course_id)
                       AND date_format(adddate(a.created, INTERVAL 9 HOUR), '%Y%m%d') BETWEEN '1'
                                                                                          AND '{date}'
                       AND lower(a.course_id) NOT LIKE '%test%'
                       AND lower(a.course_id) NOT LIKE '%demo%'
                       AND lower(a.course_id) NOT LIKE '%nile%') b
                  ON a.org = b.org
        GROUP BY if(instr(a.org, 'SKP.') > 0, 'SKP.SNUk', a.org)
        ORDER BY if(instr(a.org, 'SKP.') > 0, 'SKP.SNUk', a.org);
    """.format(date=date)
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


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
    #logger.debug(query)

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
    #logger.debug(query)

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
    #logger.debug(query)

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
    #logger.debug(query)

    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()
    return row


