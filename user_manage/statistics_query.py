# -*- coding: utf-8 -*-

import statistics
from django.db import connection

# 엑셀 시간

def excel_now_day():

    cur = connection.cursor()
    cur.execute('''select date_format(now( ), '%Y%m%d' );''')
    row = cur.fetchone()[0]
    cur.close()

    return row

# excel_now_day = ('''select date_format(now( ), '%Y%m%d' );''')

# 회원 가입자수(신규)

def user_join_new(date):

    cur = connection.cursor()
    cur.execute('''Select count(*)
                FROM auth_userprofile a, auth_user b
                WHERE a.user_id = b.id AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format( adddate(b.date_joined, interval 9 hour),'%Y%m%d') ="'''+ date +'''";''')
    row = cur.fetchone()[0]
    cur.close()

    return row

# 회원 가입자수(누적)

def user_join_total(date):

    cur = connection.cursor()
    cur.execute('''Select count(*)
                FROM auth_userprofile a, auth_user b
                WHERE a.user_id = b.id
                AND NOT (b.is_staff = 1 OR b.is_superuser = 1)
                and date_format( adddate(b.date_joined, interval 9 hour),'%Y%m%d') between '20151014' and "'''+ date +'''"''')
    row = cur.fetchone()[0]
    cur.close()

    return row

# user_join_total =('''Select count(*)
#                 FROM auth_userprofile a, auth_user b
#                 WHERE a.user_id = b.id
#                 AND NOT (b.is_staff = 1 OR b.is_superuser = 1)
#                 and date_format(b.date_joined,'%Y%m%d') between '20151014' and date_format(DATE_ADD(now(), INTERVAL -1 day), '%Y%m%d');''')

# 수강신청자수(중복제거)

def course_count_distinct(date):

    cur = connection.cursor()
    cur.execute('''select count(distinct a.user_id) cnt
                            from student_courseenrollment a, auth_user b
                            where a.user_id = b.id
                              and date_format( adddate(a.created, interval 9 hour),'%Y%m%d') between '20151014' and"'''+date+'''"
                              and a.is_active = 1
                              and not (b.email) like '%delete_%';''')
    row = cur.fetchone()[0]
    cur.close()

    return row

# course_count_distinct =('''select count(distinct a.user_id) cnt
#                             from student_courseenrollment a, auth_user b
#                             where a.user_id = b.id
#                               and date_format(a.created,'%Y%m%d') between '20151014' and date_format(DATE_ADD(now(), INTERVAL -1 day), '%Y%m%d')
#                               and a.is_active = 1
#                               and not (b.email) like '%delete_%';''')

# 수강신청자수(신규)

def course_count_new(date):

    cur = connection.cursor()
    cur.execute('''select count(a.user_id) cnt
                        from student_courseenrollment a, auth_user b
                        where a.user_id = b.id
                          and date_format( adddate(a.created, interval 9 hour),'%Y%m%d') ="'''+date+'''"
                          and a.is_active = 1
                          and not (b.email) like '%delete_%'
                          and lower(a.course_id) not like '%test%'
                          AND lower(a.course_id) NOT LIKE '%demo%'
                          AND lower(a.course_id) NOT LIKE '%nile%';''')
    row = cur.fetchone()[0]
    cur.close()

    return row

# course_count_new = ('''select count(a.user_id) cnt
#                         from student_courseenrollment a, auth_user b
#                         where a.user_id = b.id
#                           and date_format(a.created,'%Y%m%d') = date_format(DATE_ADD(now(), INTERVAL -1 day), '%Y%m%d')
#                           and a.is_active = 1
#                           and not (b.email) like '%delete_%'
#                           and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
#                           and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1';''')

# 수강신청자수(누적)

def course_count_total(date):

    cur = connection.cursor()
    cur.execute('''select count(a.user_id) cnt
                         from student_courseenrollment a, auth_user b
                         where a.user_id = b.id
                           and date_format( adddate(a.created, interval 9 hour),'%Y%m%d') between '20151014' and "'''+date+'''"
                           and a.is_active = 1
                           and not (b.email) like '%delete_%'
                           and lower(a.course_id) not like '%test%'
                          AND lower(a.course_id) NOT LIKE '%demo%'
                          AND lower(a.course_id) NOT LIKE '%nile%';''')
    row = cur.fetchone()[0]
    cur.close()

    return row


# course_count_total = ('''select count(a.user_id) cnt
#                         from student_courseenrollment a, auth_user b
#                         where a.user_id = b.id
#                           and date_format(a.created,'%Y%m%d') between '20151014' and date_format(DATE_ADD(now(), INTERVAL -1 day), '%Y%m%d')
#                           and a.is_active = 1
#                           and not (b.email) like '%delete_%'
#                           and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
#                           and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1';''')

# 학력구분(신규)

def edu_new(date):

    cur = connection.cursor()
    cur.execute('''SELECT
                 ifnull(b.male, 0),
                 ifnull(b.female,0)
                 FROM (SELECT (@rn := @rn + 1) r
                          FROM auth_user a, (SELECT @rn := 0) b
                         LIMIT 9) a
                       LEFT OUTER JOIN
                       (SELECT case
                         when a.level_of_education = 'p' then 1
                         when a.level_of_education = 'm' then 2
                         when a.level_of_education = 'b' then 3
                         when a.level_of_education = 'a' then 4
                         when a.level_of_education = 'hs' then 5
                         when a.level_of_education = 'jhs' then 6
                         when a.level_of_education = 'el' then 7
                         when a.level_of_education = 'other' then 8
                         when a.level_of_education is null or a.level_of_education = '' or a.level_of_education = 'null' then 9 end result,
                       sum(if(a.gender = 'm', 1, 0)) AS "male",
                       sum(if(a.gender = 'f', 1, 0)) AS "female"
                  FROM auth_userprofile a, auth_user b
                 WHERE a.user_id = b.id AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format( adddate(b.date_joined, interval 9 hour),'%Y%m%d') = "'''+date+'''"
                 group by case when a.level_of_education is null or a.level_of_education = '' or a.level_of_education = 'null' then 'none' else level_of_education end
                 order by level_of_education) b
                 ON a.r = b.result
                ORDER BY a.r;''')
    row = cur.fetchall()
    cur.close()

    return row

# edu_new = ('''SELECT
#                  ifnull(b.male, 0),
#                  ifnull(b.female,0)
#                  FROM (SELECT (@rn := @rn + 1) r
#                           FROM auth_user a, (SELECT @rn := 0) b
#                          LIMIT 9) a
#                        LEFT OUTER JOIN
#                        (SELECT case
#                          when a.level_of_education = 'p' then 1
#                          when a.level_of_education = 'm' then 2
#                          when a.level_of_education = 'b' then 3
#                          when a.level_of_education = 'a' then 4
#                          when a.level_of_education = 'hs' then 5
#                          when a.level_of_education = 'jhs' then 6
#                          when a.level_of_education = 'el' then 7
#                          when a.level_of_education = 'other' then 8
#                          when a.level_of_education is null or a.level_of_education = '' or a.level_of_education = 'null' then 9 end result,
#                        sum(if(a.gender = 'm', 1, 0)) AS "male",
#                        sum(if(a.gender = 'f', 1, 0)) AS "female"
#                   FROM auth_userprofile a, auth_user b
#                  WHERE a.user_id = b.id AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format(b.date_joined,'%Y%m%d') = date_format(DATE_ADD(now(), INTERVAL -1 day), '%Y%m%d')
#                  group by case when a.level_of_education is null or a.level_of_education = '' or a.level_of_education = 'null' then 'none' else level_of_education end
#                  order by level_of_education) b
#                  ON a.r = b.result
#                 ORDER BY a.r;''')

# 학력구분(누적)

def edu_total(date):

    cur = connection.cursor()
    cur.execute('''SELECT
                 b.male,
                 b.female
                 FROM (SELECT (@rn := @rn + 1) r
                          FROM auth_user a, (SELECT @rn := 0) b
                         LIMIT 9) a
                       LEFT OUTER JOIN
                       (SELECT case
                         when a.level_of_education = 'p' then 1
                         when a.level_of_education = 'm' then 2
                         when a.level_of_education = 'b' then 3
                         when a.level_of_education = 'a' then 4
                         when a.level_of_education = 'hs' then 5
                         when a.level_of_education = 'jhs' then 6
                         when a.level_of_education = 'el' then 7
                         when a.level_of_education = 'other' then 8
                         when a.level_of_education is null or a.level_of_education = '' or a.level_of_education = 'null' then 9 end result,
                       sum(if(a.gender = 'm', 1, 0)) AS "male",
                       sum(if(a.gender = 'f', 1, 0)) AS "female"
                  FROM auth_userprofile a, auth_user b
                 WHERE a.user_id = b.id AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format( adddate(b.date_joined, interval 9 hour),'%Y%m%d') between '20151014' and "'''+date+'''"
                 group by case when a.level_of_education is null or a.level_of_education = '' or a.level_of_education = 'null' then 'none' else level_of_education end
                 order by level_of_education) b
                 ON a.r = b.result
                ORDER BY a.r;''')
    row = cur.fetchall()
    cur.close()

    return row
#
# edu_total = ('''SELECT
#                  b.male,
#                  b.female
#                  FROM (SELECT (@rn := @rn + 1) r
#                           FROM auth_user a, (SELECT @rn := 0) b
#                          LIMIT 9) a
#                        LEFT OUTER JOIN
#                        (SELECT case
#                          when a.level_of_education = 'p' then 1
#                          when a.level_of_education = 'm' then 2
#                          when a.level_of_education = 'b' then 3
#                          when a.level_of_education = 'a' then 4
#                          when a.level_of_education = 'hs' then 5
#                          when a.level_of_education = 'jhs' then 6
#                          when a.level_of_education = 'el' then 7
#                          when a.level_of_education = 'other' then 8
#                          when a.level_of_education is null or a.level_of_education = '' or a.level_of_education = 'null' then 9 end result,
#                        sum(if(a.gender = 'm', 1, 0)) AS "male",
#                        sum(if(a.gender = 'f', 1, 0)) AS "female"
#                   FROM auth_userprofile a, auth_user b
#                  WHERE a.user_id = b.id AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format(b.date_joined,'%Y%m%d') between '20151014' and date_format(DATE_ADD(now(), INTERVAL -1 day), '%Y%m%d')
#                  group by case when a.level_of_education is null or a.level_of_education = '' or a.level_of_education = 'null' then 'none' else level_of_education end
#                  order by level_of_education) b
#                  ON a.r = b.result
#                 ORDER BY a.r;''')

# 연령구분(신규)

def age_new(date):

    cur = connection.cursor()
    cur.execute('''SELECT
             ifnull(b.male,0),
             ifnull(b.female,0)
             FROM (SELECT (@rn := @rn + 1) r
                      FROM auth_user a, (SELECT @rn := 0) b
                     LIMIT 7) a
                   LEFT OUTER JOIN
                   (SELECT age,
                   count(CASE WHEN gender = 'm' THEN 1 END) male,
                   count(CASE WHEN gender = 'f' THEN 1 END) female
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
                      FROM (SELECT (date_format(now(), '%Y') - a.year_of_birth) + 1 age,
                                   a.gender
                              FROM auth_userprofile a, auth_user b
                             WHERE     a.user_id = b.id
                                   AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format( adddate(b.date_joined, interval 9 hour),'%Y%m%d') = "'''+date+'''") aa) bb
            GROUP BY age) b
             ON a.r = b.age
            ORDER BY a.r;''')
    row = cur.fetchall()
    cur.close()

    return row

# age_new = ('''SELECT
#              ifnull(b.male,0),
#              ifnull(b.female,0)
#              FROM (SELECT (@rn := @rn + 1) r
#                       FROM auth_user a, (SELECT @rn := 0) b
#                      LIMIT 7) a
#                    LEFT OUTER JOIN
#                    (SELECT age,
#                    count(CASE WHEN gender = 'm' THEN 1 END) male,
#                    count(CASE WHEN gender = 'f' THEN 1 END) female
#               FROM (SELECT CASE
#                               WHEN age < 20 THEN '1'
#                               WHEN age BETWEEN 20 AND 29 THEN '2'
#                               WHEN age BETWEEN 30 AND 39 THEN '3'
#                               WHEN age BETWEEN 40 AND 49 THEN '4'
#                               WHEN age BETWEEN 50 AND 59 THEN '5'
#                               WHEN age >= 60 THEN '6'
#                               ELSE '7'
#                            END
#                               age,
#                            gender
#                       FROM (SELECT (date_format(now(), '%Y') - a.year_of_birth) + 1 age,
#                                    a.gender
#                               FROM auth_userprofile a, auth_user b
#                              WHERE     a.user_id = b.id
#                                    AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format(b.date_joined,'%Y%m%d') = date_format(DATE_ADD(now(), INTERVAL -1 day), '%Y%m%d')) aa) bb
#             GROUP BY age) b
#              ON a.r = b.age
#             ORDER BY a.r;''')

# 연령구분(누적)

def age_total(date):

    cur = connection.cursor()
    cur.execute('''SELECT
                 b.male,
                 b.female
                 FROM (SELECT (@rn := @rn + 1) r
                          FROM auth_user a, (SELECT @rn := 0) b
                         LIMIT 7) a
                       LEFT OUTER JOIN
                       (SELECT age,
                       count(CASE WHEN gender = 'm' THEN 1 END) male,
                       count(CASE WHEN gender = 'f' THEN 1 END) female
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
                          FROM (SELECT (date_format(now(), '%Y') - a.year_of_birth) + 1 age,
                                       a.gender
                                  FROM auth_userprofile a, auth_user b
                                 WHERE     a.user_id = b.id
                                       AND NOT (b.is_staff = 1 OR b.is_superuser = 1)
                                       and date_format( adddate(b.date_joined, interval 9 hour),'%Y%m%d') between '20151014' and "'''+date+'''") aa) bb
                GROUP BY age) b
                 ON a.r = b.age
                ORDER BY a.r;''')
    row = cur.fetchall()
    cur.close()

    return row

# age_total = ('''SELECT
#                  b.male,
#                  b.female
#                  FROM (SELECT (@rn := @rn + 1) r
#                           FROM auth_user a, (SELECT @rn := 0) b
#                          LIMIT 7) a
#                        LEFT OUTER JOIN
#                        (SELECT age,
#                        count(CASE WHEN gender = 'm' THEN 1 END) male,
#                        count(CASE WHEN gender = 'f' THEN 1 END) female
#                   FROM (SELECT CASE
#                                   WHEN age < 20 THEN '1'
#                                   WHEN age BETWEEN 20 AND 29 THEN '2'
#                                   WHEN age BETWEEN 30 AND 39 THEN '3'
#                                   WHEN age BETWEEN 40 AND 49 THEN '4'
#                                   WHEN age BETWEEN 50 AND 59 THEN '5'
#                                   WHEN age >= 60 THEN '6'
#                                   ELSE '7'
#                                END
#                                   age,
#                                gender
#                           FROM (SELECT (date_format(now(), '%Y') - a.year_of_birth) + 1 age,
#                                        a.gender
#                                   FROM auth_userprofile a, auth_user b
#                                  WHERE     a.user_id = b.id
#                                        AND NOT (b.is_staff = 1 OR b.is_superuser = 1)
#                                        and date_format(b.date_joined,'%Y%m%d') between '20151014' and date_format(DATE_ADD(now(), INTERVAL -1 day), '%Y%m%d')) aa) bb
#                 GROUP BY age) b
#                  ON a.r = b.age
#                 ORDER BY a.r;''')

# 연령학력

def age_edu(date):

    cur = connection.cursor()
    cur.execute('''SELECT b.aa,
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
                   sum(CASE WHEN lv = 'p' THEN 1 else 0 END) aa,
                   sum(CASE WHEN lv = 'm' THEN 1 else 0  END) bb,
                   sum(CASE WHEN lv = 'b' THEN 1 else 0  END) cc,
                   sum(CASE WHEN lv = 'a' THEN 1 else 0  END) dd,
                   sum(CASE WHEN lv = 'hs' THEN 1 else 0  END) ee,
                   sum(CASE WHEN lv = 'jhs' THEN 1 else 0  END) ff,
                   sum(CASE WHEN lv = 'el' THEN 1 else 0  END) gg,
                   sum(CASE WHEN lv = 'other' THEN 1 else 0  END) hh,
                   sum(CASE WHEN lv = 'none' or lv = '' or lv = 'null' THEN 1 else 0  END) ii

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
                      FROM (SELECT (date_format(now(), '%Y') - a.year_of_birth) + 1 age,
                                   ifnull(a.level_of_education,'') lv,
                                   a.gender
                              FROM auth_userprofile a, auth_user b
                             WHERE     a.user_id = b.id
                                   AND NOT (b.is_staff = 1 OR b.is_superuser = 1)
                                   AND date_format( adddate(b.date_joined, interval 9 hour), '%Y%m%d') between '20151014' and "'''+date+'''" )
                           aa) bb
            GROUP BY age) b
            ON a.r = b.age
            ORDER BY a.r;''')
    row = cur.fetchall()
    cur.close()

    return row

# age_edu =('''SELECT b.aa,
#                   b.bb,
#                   b.cc,
#                   b.dd,
#                   b.ee,
#                   b.ff,
#                   b.gg,
#                   b.hh,
#                   b.ii
#                FROM (SELECT (@rn := @rn + 1) r
#                       FROM auth_user a, (SELECT @rn := 0) b
#                      LIMIT 7) a
#                    LEFT OUTER JOIN
#                    (SELECT age,
#                    sum(CASE WHEN lv = 'p' THEN 1 else 0 END) aa,
#                    sum(CASE WHEN lv = 'm' THEN 1 else 0  END) bb,
#                    sum(CASE WHEN lv = 'b' THEN 1 else 0  END) cc,
#                    sum(CASE WHEN lv = 'a' THEN 1 else 0  END) dd,
#                    sum(CASE WHEN lv = 'hs' THEN 1 else 0  END) ee,
#                    sum(CASE WHEN lv = 'jhs' THEN 1 else 0  END) ff,
#                    sum(CASE WHEN lv = 'el' THEN 1 else 0  END) gg,
#                    sum(CASE WHEN lv = 'other' THEN 1 else 0  END) hh,
#                    sum(CASE WHEN lv = 'none' or lv = '' or lv = 'null' THEN 1 else 0  END) ii
#
#                    FROM (SELECT CASE
#                               WHEN age < 20 THEN '1'
#                               WHEN age BETWEEN 20 AND 29 THEN '2'
#                               WHEN age BETWEEN 30 AND 39 THEN '3'
#                               WHEN age BETWEEN 40 AND 49 THEN '4'
#                               WHEN age BETWEEN 50 AND 59 THEN '5'
#                               WHEN age >= 60 THEN '6'
#                               ELSE '7'
#                            END
#                               age,
#                            lv,
#                            gender
#                       FROM (SELECT (date_format(now(), '%Y') - a.year_of_birth) + 1 age,
#                                    ifnull(a.level_of_education,'') lv,
#                                    a.gender
#                               FROM auth_userprofile a, auth_user b
#                              WHERE     a.user_id = b.id
#                                    AND NOT (b.is_staff = 1 OR b.is_superuser = 1)
#                                    AND date_format(b.date_joined, '%Y%m%d') between '20151014' and date_format(DATE_ADD(now(), INTERVAL -1 day), '%Y%m%d') )
#                            aa) bb
#             GROUP BY age) b
#             ON a.r = b.age
#             ORDER BY a.r;''')


#코스별 수강자수

def course_user(date):
    query = '''SELECT a.course_id, substring(substring_index(a.course_id, '+', 2), instr(a.course_id,'+')+1) course_id1,
                substring_index(a.course_id, '+',-1) course_id2, ifnull(cnt, 0)
          FROM (SELECT DISTINCT a.course_id
          FROM course_structures_coursestructure a,
               student_courseaccessrole b
         WHERE     a.course_id = b.course_id
               and lower(a.course_id) not like '%test%'
               AND lower(a.course_id) NOT LIKE '%demo%'
               AND lower(a.course_id) NOT LIKE '%nile%')
               a
               LEFT JOIN
               (SELECT course_id, cnt
                  FROM (SELECT a.course_id, count(*) cnt
                          FROM student_courseenrollment a, auth_user b
                         WHERE     a.user_id = b.id
                               AND date_format( adddate(a.created, interval 9 hour), '%Y%m%d') = '''+date+'''
                               AND a.is_active = 1
                               AND NOT (b.email) LIKE '%delete_%'
                               and lower(a.course_id) not like '%test%'
                               AND lower(a.course_id) NOT LIKE '%demo%'
                               AND lower(a.course_id) NOT LIKE '%nile%'
                        GROUP BY a.course_id) aa) b
                  ON a.course_id = b.course_id;'''
    # print query
    cur = connection.cursor()
    cur.execute(query)
    row = cur.fetchall()
    cur.close()

    return row

#코스별 수강자수(누적)

def course_user_total(date):

    cur = connection.cursor()
    cur.execute('''SELECT a.course_id, substring(substring_index(a.course_id, '+', 2), instr(a.course_id,'+')+1) course_id1,
                          substring_index(a.course_id, '+',-1) course_id2, ifnull(cnt, 0)
                      FROM (SELECT DISTINCT a.course_id
          FROM course_structures_coursestructure a,
               student_courseaccessrole b
         WHERE     a.course_id = b.course_id
               and lower(a.course_id) not like '%test%'
               AND lower(a.course_id) NOT LIKE '%demo%'
               AND lower(a.course_id) NOT LIKE '%nile%')
                           a
                           LEFT JOIN
                           (SELECT course_id, cnt
                              FROM (SELECT a.course_id, count(*) cnt
                                      FROM student_courseenrollment a, auth_user b
                                     WHERE     a.user_id = b.id
                                           AND date_format( adddate(a.created, interval 9 hour), '%Y%m%d') between '20151014' and  "'''+date+'''"
                                           AND a.is_active = 1
                                           AND NOT (b.email) LIKE '%delete_%'
                                           and lower(a.course_id) not like '%test%'
                                           AND lower(a.course_id) NOT LIKE '%demo%'
                                           AND lower(a.course_id) NOT LIKE '%nile%'
                                    GROUP BY a.course_id) aa) b
                              ON a.course_id = b.course_id;
                    ''')
    row = cur.fetchall()
    cur.close()

    return row

#코스별 연령

def course_age(date):

    cur = connection.cursor()
    cur.execute('''
        SELECT substring(a.course_id,
                         instr(a.course_id, ':') + 1,
                         (instr(a.course_id, '+')) - instr(a.course_id, ':') - 1)
                  org, a.course_id,
                  substring(substring_index(a.course_id, '+', 2), instr(a.course_id,'+')+1) course_id1,
                  substring_index(a.course_id, '+',-1) course_id2,
               sum(if(age < 20, 1, 0)),
               sum(if(age BETWEEN 20 AND 29, 1, 0)),
               sum(if(age BETWEEN 30 AND 39, 1, 0)),
               sum(if(age BETWEEN 40 AND 49, 1, 0)),
               sum(if(age BETWEEN 50 AND 59, 1, 0)),
               sum(if(age > 60, 1, 0))
          FROM (SELECT DISTINCT a.course_id
          FROM course_structures_coursestructure a,
               student_courseaccessrole b
         WHERE     a.course_id = b.course_id
               and lower(a.course_id) not like '%test%'
               AND lower(a.course_id) NOT LIKE '%demo%'
               AND lower(a.course_id) NOT LIKE '%nile%')
               a
               LEFT JOIN
               (SELECT course_id,
                       ifnull((date_format(NOW(), '%Y') - year_of_birth), 0) + 1 age
                  FROM (SELECT a.course_id, c.year_of_birth
                          FROM student_courseenrollment a,
                               auth_user b,
                               auth_userprofile c
                         WHERE     a.user_id = b.id
                               AND b.id = c.user_id
                               AND date_format( adddate(a.created, interval 9 hour), '%Y%m%d') BETWEEN '20151014' and
                                                                        "'''+date+'''"
                               AND a.is_active = 1
                               AND NOT (b.email) LIKE '%delete_%'
                               and lower(a.course_id) not like '%test%'
                               AND lower(a.course_id) NOT LIKE '%demo%'
                               AND lower(a.course_id) NOT LIKE '%nile%') aa) b
                  ON a.course_id = b.course_id
        GROUP BY a.course_id
        ;

    ''')
    row = cur.fetchall()
    cur.close()

    return row

#코스별 학력

def course_edu(date):

    cur = connection.cursor()
    cur.execute('''
        SELECT substring(a.course_id,
                         instr(a.course_id, ':') + 1,
                         (instr(a.course_id, '+')) - instr(a.course_id, ':') - 1)
                  org, a.course_id,
               substring(substring_index(a.course_id, '+', 2), instr(a.course_id,'+')+1) course_id1,
                substring_index(a.course_id, '+',-1) course_id2,
               sum(if(level_of_education = 'p', 1, 0)),
               sum(if(level_of_education = 'm', 1, 0)),
               sum(if(level_of_education = 'b', 1, 0)),
               sum(if(level_of_education = 'a', 1, 0)),
               sum(if(level_of_education = 'hs', 1, 0)),
               sum(if(level_of_education = 'jhs', 1, 0)),
               sum(if(level_of_education = 'el', 1, 0)),
               sum(if(level_of_education = 'other', 1, 0)),
               sum(
                  if(
                        level_of_education = ''
                     OR level_of_education = 'null'
                     OR level_of_education IS NULL,
                     1,
                     0))
          FROM (SELECT DISTINCT a.course_id
          FROM course_structures_coursestructure a,
               student_courseaccessrole b
         WHERE     a.course_id = b.course_id
               and lower(a.course_id) not like '%test%'
               AND lower(a.course_id) NOT LIKE '%demo%'
               AND lower(a.course_id) NOT LIKE '%nile%')
               a
               LEFT JOIN
               (SELECT course_id, level_of_education
                  FROM (SELECT a.course_id, c.level_of_education
                          FROM student_courseenrollment a,
                               auth_user b,
                               auth_userprofile c
                         WHERE     a.user_id = b.id
                               AND b.id = c.user_id
                               AND date_format( adddate(a.created, interval 9 hour), '%Y%m%d') BETWEEN '20151014'
                                                                        AND "'''+date+'''"
                               AND a.is_active = 1
                               AND NOT (b.email) LIKE '%delete_%'
                               and lower(a.course_id) not like '%test%'
                               AND lower(a.course_id) NOT LIKE '%demo%'
                               AND lower(a.course_id) NOT LIKE '%nile%'
                               ) aa) b
                  ON a.course_id = b.course_id
        GROUP BY a.course_id
        ORDER BY a.course_id;
    ''')
    row = cur.fetchall()
    cur.close()

    return row

def course_ids_all():
    cur = connection.cursor()
    cur.execute('''
SELECT DISTINCT a.course_id
          FROM course_structures_coursestructure a,
               student_courseaccessrole b
         WHERE     a.course_id = b.course_id
            and lower(a.course_id) not like '%test%'
            AND lower(a.course_id) NOT LIKE '%demo%'
            AND lower(a.course_id) NOT LIKE '%nile%';
            ''')
    row = cur.fetchall()
    cur.close()
    return row

def course_univ(date):
    cur = connection.cursor()
    cur.execute('''
        SELECT a.org, count(b.org) cnt
          FROM (SELECT DISTINCT
                       substring(
                          a.course_id,
                          instr(a.course_id, ':') + 1,
                          (instr(a.course_id, '+')) - instr(a.course_id, ':') - 1)
                          org
                  FROM course_structures_coursestructure a, student_courseaccessrole b
                 WHERE 1=1
                   and a.course_id = b.course_id
                       and lower(a.course_id) not like '%test%'
                          AND lower(a.course_id) NOT LIKE '%demo%'
                          AND lower(a.course_id) NOT LIKE '%nile%'
                GROUP BY a.course_id)  a
               LEFT JOIN
               (SELECT substring(
                          a.course_id,
                          instr(a.course_id, ':') + 1,
                          (instr(a.course_id, '+')) - instr(a.course_id, ':') - 1)
                          org
                  FROM student_courseenrollment a, auth_user b
                 WHERE     a.user_id = b.id
                       AND date_format( adddate(a.created, interval 9 hour), '%Y%m%d') = "'''+date+'''"
                       AND a.is_active = 1
                       AND NOT (b.email) LIKE '%delete_%'
                       and lower(a.course_id) not like '%test%'
                          AND lower(a.course_id) NOT LIKE '%demo%'
                          AND lower(a.course_id) NOT LIKE '%nile%') b
                  ON a.org = b.org
        GROUP BY a.org
        ORDER BY a.org;
    ''')
    row = cur.fetchall()
    cur.close()
    return row

def course_univ_total(date):
    cur = connection.cursor()
    cur.execute('''
        SELECT a.org, count(b.org) cnt
          FROM (SELECT DISTINCT
                       substring(
                          a.course_id,
                          instr(a.course_id, ':') + 1,
                          (instr(a.course_id, '+')) - instr(a.course_id, ':') - 1)
                          org
                  FROM course_structures_coursestructure a, student_courseaccessrole b
                 WHERE 1=1
                   and a.course_id = b.course_id
                   and a.course_id NOT LIKE '%DEMOk%'
                   and lower(a.course_id) not like '%test%'
                          AND lower(a.course_id) NOT LIKE '%demo%'
                          AND lower(a.course_id) NOT LIKE '%nile%'
                GROUP BY a.course_id)  a
               LEFT JOIN
               (SELECT substring(
                          a.course_id,
                          instr(a.course_id, ':') + 1,
                          (instr(a.course_id, '+')) - instr(a.course_id, ':') - 1)
                          org
                  FROM student_courseenrollment a, auth_user b
                 WHERE     a.user_id = b.id
                       AND date_format( adddate(a.created, interval 9 hour), '%Y%m%d') between '20151014' and "'''+date+'''"
                       AND a.is_active = 1
                       AND NOT (b.email) LIKE '%delete_%'
                       and lower(a.course_id) not like '%test%'
                          AND lower(a.course_id) NOT LIKE '%demo%'
                          AND lower(a.course_id) NOT LIKE '%nile%') b
                  ON a.org = b.org
        GROUP BY a.org
        ORDER BY a.org;
    ''')
    row = cur.fetchall()
    cur.close()
    return row

def course_ids_cert():
    cur = connection.cursor()
    cur.execute('''
	SELECT a.course_id
	  FROM (SELECT course_id, count(a.user_id) cnt, max(a.created_date) cdate
	          FROM certificates_generatedcertificate a
	        GROUP BY a.course_id) a,
	       (SELECT a.course_id, a.created cdate
	          FROM student_courseenrollment a
	         WHERE a.is_active = 1) b
	 WHERE a.course_id = b.course_id
	   and a.cdate >= b.cdate
	 group by a.course_id
	 having max(a.cnt) >= count(b.course_id)
    ''')
    row = cur.fetchall()
    cur.close()
    return row

def certificateInfo(courseId):
    cur = connection.cursor()
    cur.execute('''
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
               AND NOT (b.is_staff = 1 OR b.is_superuser = 1)
               AND a.course_id = "'''+courseId+'''"
        GROUP BY a.course_id, a.status
        ORDER BY a.course_id, a.status;
    ''')
    row = cur.fetchall()
    cur.close()
    return row


## 월별 통계 자료
def member_statistics(date):
    cur = connection.cursor()
    cur.execute('''
        SELECT sum(if(a.is_active = '1', 1, 0)) active,
               sum(if(a.is_active = '1', 0, 1)) unactive,
               count(*)
          FROM auth_user a, auth_userprofile b
         WHERE a.id = b.user_id
           AND NOT (a.is_staff = 1 OR a.is_superuser = 1)
           and date_format( adddate(a.date_joined, interval 9 hour), '%Y%m%d') BETWEEN '20151014' AND '''+date+''';
    ''')
    row = cur.fetchall()
    cur.close()
    return row

def country_statistics(date):
    cur = connection.cursor()
    cur.execute('''
        SELECT b.country, count(*) cnt
          FROM auth_user a, auth_userprofile b
         WHERE     a.id = b.user_id
               AND NOT (a.is_staff = 1 OR a.is_superuser = 1)
               AND date_format( adddate(a.date_joined, interval 9 hour), '%Y%m%d') BETWEEN '20151014'
                                                            AND '''+date+'''
        GROUP BY b.country
        ORDER BY count(*) DESC;
    ''')
    row = cur.fetchall()
    cur.close()
    return row



