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
                WHERE a.user_id = b.id AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format(b.date_joined,'%Y%m%d') ="'''+ date +'''";''')
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
                and date_format(b.date_joined,'%Y%m%d') between '20151014' and "'''+ date +'''"''')
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
                              and date_format(a.created,'%Y%m%d') between '20151014' and"'''+date+'''"
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
                          and date_format(a.created,'%Y%m%d') ="'''+date+'''"
                          and a.is_active = 1
                          and not (b.email) like '%delete_%'
                          and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
                          and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1';''')
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
                           and date_format(a.created,'%Y%m%d') between '20151014' and "'''+date+'''"
                           and a.is_active = 1
                           and not (b.email) like '%delete_%'
                           and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
                           and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1';''')
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
                 WHERE a.user_id = b.id AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format(b.date_joined,'%Y%m%d') = "'''+date+'''"
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
                 WHERE a.user_id = b.id AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format(b.date_joined,'%Y%m%d') between '20151014' and "'''+date+'''"
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
                                   AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format(b.date_joined,'%Y%m%d') = "'''+date+'''") aa) bb
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
                                       and date_format(b.date_joined,'%Y%m%d') between '20151014' and "'''+date+'''") aa) bb
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
                                   AND date_format(b.date_joined, '%Y%m%d') between '20151014' and "'''+date+'''" )
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

    cur = connection.cursor()
    cur.execute('''SELECT
                 ifnull(b.cnt, 0)
                 FROM (SELECT (@rn := @rn + 1) r
                          FROM auth_user a, (SELECT @rn := 0) b
                         LIMIT 30) a
                       LEFT OUTER JOIN
                       (select case
                         when course_id = 'course-v1:KHUk+KH102+2015_KH02' then 1
                         when course_id = 'course-v1:KHUk+KH101+2015_KH01' then 2
                         when course_id = 'course-v1:KoreaUnivK+ku_phy_001+2015_A04' then 3
                         when course_id = 'course-v1:KoreaUnivK+ku_cpx_001+2015_A03' then 4
                         when course_id = 'course-v1:KoreaUnivK+ku_soc_001+2015_A01' then 5
                         when course_id = 'course-v1:KoreaUnivK+ku_hum_001+2015_A02' then 6
                         when course_id = 'course-v1:PNUk+PL_C01+2015_KM_001' then 7
                         when course_id = 'course-v1:PNUk+SE_C01+2015_KM_002' then 8
                         when course_id = 'course-v1:SNUk+SNU044.008k+2015' then 9
                         when course_id = 'course-v1:SNUk+SNU046.101k+2015' then 10
                         when course_id = 'course-v1:SKKUk+COS2034.01x+2015_SKKU1' then 11
                         when course_id = 'course-v1:SKKUk+GEDT011.01x+2015_SKKU2' then 12
                         when course_id = 'course-v1:YSUk+YSU_KOR02k+2015_T2' then 13
                         when course_id = 'course-v1:YSUk+YSU_BIZ03k+2015_T2' then 14
                         when course_id = 'course-v1:YSUk+YSU_UCC01k+2015_T2' then 15
                         when course_id = 'course-v1:EwhaK+EW10164K+2015-01' then 16
                         when course_id = 'course-v1:EwhaK+EW11151K+2015-02' then 17
                         when course_id = 'course-v1:EwhaK+EW10771K+2015-03' then 18
                         when course_id = 'course-v1:EwhaK+EW36387K+2015-04' then 19
                         when course_id = 'course-v1:POSTECHk+POSTECH.MECH583k+2015-01' then 20
                         when course_id = 'course-v1:POSTECHk+POSTECH.EECE341k+2015-01' then 21
                         when course_id = 'course-v1:KAISTk+KMAE251+2015_K0101' then 22
                         when course_id = 'course-v1:KAISTk+KCS470+2015_K0201' then 23
                         when course_id = 'course-v1:HYUk+HYUARE4100k+2015_C1' then 24
                         when course_id = 'course-v1:HYUk+HYUPAD3004k+2015_C1' then 25
                         when course_id = 'course-v1:HYUk+HYUBUS3099k+2015_C1' then 26
                         when course_id = 'course-v1:HYUk+HYUSOC1053k+2015_C1' then 27
                         when course_id = 'course-v1:edX+DemoX+Demo_Course' then 28
                         when course_id = 'course-v1:KMOOC+DEMOk+2015_1' then 29 end course, course_id, cnt from (
                select a.course_id , count(*) cnt
                from student_courseenrollment a, auth_user b
                where a.user_id = b.id
                  and date_format(a.created,'%Y%m%d') = "'''+date+'''"
                  and a.is_active = 1
                  and not (b.email) like '%delete_%'
                  and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1'
                  and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
                group by a.course_id)aa) b
                 ON a.r = b.course
                ORDER BY a.r;''')
    row = cur.fetchall()
    cur.close()

    return row

#코스별 수강자수(누적)

def course_user_total(date):

    cur = connection.cursor()
    cur.execute('''SELECT
                 ifnull(b.cnt, 0)
                 FROM (SELECT (@rn := @rn + 1) r
                          FROM auth_user a, (SELECT @rn := 0) b
                         LIMIT 30) a
                       LEFT OUTER JOIN
                       (select case
                         when course_id = 'course-v1:KHUk+KH102+2015_KH02' then 1
                         when course_id = 'course-v1:KHUk+KH101+2015_KH01' then 2
                         when course_id = 'course-v1:KoreaUnivK+ku_phy_001+2015_A04' then 3
                         when course_id = 'course-v1:KoreaUnivK+ku_cpx_001+2015_A03' then 4
                         when course_id = 'course-v1:KoreaUnivK+ku_soc_001+2015_A01' then 5
                         when course_id = 'course-v1:KoreaUnivK+ku_hum_001+2015_A02' then 6
                         when course_id = 'course-v1:PNUk+PL_C01+2015_KM_001' then 7
                         when course_id = 'course-v1:PNUk+SE_C01+2015_KM_002' then 8
                         when course_id = 'course-v1:SNUk+SNU044.008k+2015' then 9
                         when course_id = 'course-v1:SNUk+SNU046.101k+2015' then 10
                         when course_id = 'course-v1:SKKUk+COS2034.01x+2015_SKKU1' then 11
                         when course_id = 'course-v1:SKKUk+GEDT011.01x+2015_SKKU2' then 12
                         when course_id = 'course-v1:YSUk+YSU_KOR02k+2015_T2' then 13
                         when course_id = 'course-v1:YSUk+YSU_BIZ03k+2015_T2' then 14
                         when course_id = 'course-v1:YSUk+YSU_UCC01k+2015_T2' then 15
                         when course_id = 'course-v1:EwhaK+EW10164K+2015-01' then 16
                         when course_id = 'course-v1:EwhaK+EW11151K+2015-02' then 17
                         when course_id = 'course-v1:EwhaK+EW10771K+2015-03' then 18
                         when course_id = 'course-v1:EwhaK+EW36387K+2015-04' then 19
                         when course_id = 'course-v1:POSTECHk+POSTECH.MECH583k+2015-01' then 20
                         when course_id = 'course-v1:POSTECHk+POSTECH.EECE341k+2015-01' then 21
                         when course_id = 'course-v1:KAISTk+KMAE251+2015_K0101' then 22
                         when course_id = 'course-v1:KAISTk+KCS470+2015_K0201' then 23
                         when course_id = 'course-v1:HYUk+HYUARE4100k+2015_C1' then 24
                         when course_id = 'course-v1:HYUk+HYUPAD3004k+2015_C1' then 25
                         when course_id = 'course-v1:HYUk+HYUBUS3099k+2015_C1' then 26
                         when course_id = 'course-v1:HYUk+HYUSOC1053k+2015_C1' then 27
                         when course_id = 'course-v1:edX+DemoX+Demo_Course' then 28
                         when course_id = 'course-v1:KMOOC+DEMOk+2015_1' then 29 end course, course_id, cnt from (
                select a.course_id , count(*) cnt
                from student_courseenrollment a, auth_user b
                where a.user_id = b.id
                  and date_format(a.created,'%Y%m%d') between '20151014' and "'''+date+'''"
                  and a.is_active = 1
                  and not (b.email) like '%delete_%'
                  and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1'
                  and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
                group by a.course_id)aa) b
                 ON a.r = b.course
                ORDER BY a.r;''')
    row = cur.fetchall()
    cur.close()

    return row

# course_user = ('''SELECT
#                  ifnull(b.cnt, 0)
#                  FROM (SELECT (@rn := @rn + 1) r
#                           FROM auth_user a, (SELECT @rn := 0) b
#                          LIMIT 30) a
#                        LEFT OUTER JOIN
#                        (select case
#                          when course_id = 'course-v1:KHUk+KH102+2015_KH02' then 1
#                          when course_id = 'course-v1:KHUk+KH101+2015_KH01' then 2
#                          when course_id = 'course-v1:KoreaUnivK+ku_phy_001+2015_A04' then 3
#                          when course_id = 'course-v1:KoreaUnivK+ku_cpx_001+2015_A03' then 4
#                          when course_id = 'course-v1:KoreaUnivK+ku_soc_001+2015_A01' then 5
#                          when course_id = 'course-v1:KoreaUnivK+ku_hum_001+2015_A02' then 6
#                          when course_id = 'course-v1:PNUk+PL_C01+2015_KM_001' then 7
#                          when course_id = 'course-v1:PNUk+SE_C01+2015_KM_002' then 8
#                          when course_id = 'course-v1:SNUk+SNU044.008k+2015' then 9
#                          when course_id = 'course-v1:SNUk+SNU046.101k+2015' then 10
#                          when course_id = 'course-v1:SKKUk+COS2034.01x+2015_SKKU1' then 11
#                          when course_id = 'course-v1:SKKUk+GEDT011.01x+2015_SKKU2' then 12
#                          when course_id = 'course-v1:YSUk+YSU_KOR02k+2015_T2' then 13
#                          when course_id = 'course-v1:YSUk+YSU_BIZ03k+2015_T2' then 14
#                          when course_id = 'course-v1:YSUk+YSU_UCC01k+2015_T2' then 15
#                          when course_id = 'course-v1:EwhaK+EW10164K+2015-01' then 16
#                          when course_id = 'course-v1:EwhaK+EW11151K+2015-02' then 17
#                          when course_id = 'course-v1:EwhaK+EW10771K+2015-03' then 18
#                          when course_id = 'course-v1:EwhaK+EW36387K+2015-04' then 19
#                          when course_id = 'course-v1:POSTECHk+POSTECH.MECH583k+2015-01' then 20
#                          when course_id = 'course-v1:POSTECHk+POSTECH.EECE341k+2015-01' then 21
#                          when course_id = 'course-v1:KAISTk+KMAE251+2015_K0101' then 22
#                          when course_id = 'course-v1:KAISTk+KCS470+2015_K0201' then 23
#                          when course_id = 'course-v1:HYUk+HYUARE4100k+2015_C1' then 24
#                          when course_id = 'course-v1:HYUk+HYUPAD3004k+2015_C1' then 25
#                          when course_id = 'course-v1:HYUk+HYUBUS3099k+2015_C1' then 26
#                          when course_id = 'course-v1:HYUk+HYUSOC1053k+2015_C1' then 27
#                          when course_id = 'course-v1:edX+DemoX+Demo_Course' then 28
#                          when course_id = 'course-v1:KMOOC+DEMOk+2015_1' then 29 end course, course_id, cnt from (
#                 select a.course_id , count(*) cnt
#                 from student_courseenrollment a, auth_user b
#                 where a.user_id = b.id
#                   and date_format(a.created,'%Y%m%d') = date_format(DATE_ADD(now(), INTERVAL -1 day), '%Y%m%d')
#                   and a.is_active = 1
#                   and not (b.email) like '%delete_%'
#                   and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1'
#                   and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
#                 group by a.course_id)aa) b
#                  ON a.r = b.course
#                 ORDER BY a.r;''')

#코스별 연령

def course_age(date):

    cur = connection.cursor()
    cur.execute('''SELECT
                       ifnull(sum(IF(agegroup = 'a', 1, NULL)),0) a,
                       ifnull(sum(IF(agegroup = 'b', 1, NULL)),0) b,
                       ifnull(sum(IF(agegroup = 'c', 1, NULL)),0) c,
                       ifnull(sum(IF(agegroup = 'd', 1, NULL)),0) d,
                       ifnull(sum(IF(agegroup = 'e', 1, NULL)),0) e,
                       ifnull(sum(IF(agegroup = 'f', 1, NULL)),0) f,
                       ifnull(sum(IF(agegroup = 'x', 1, NULL)),0) x
                  FROM (SELECT course_id,
                          CASE
                                  WHEN age < 20 THEN 'a'
                                  WHEN age BETWEEN 20 AND 29 THEN 'b'
                                  WHEN age BETWEEN 30 AND 39 THEN 'c'
                                  WHEN age BETWEEN 40 AND 49 THEN 'd'
                                  WHEN age BETWEEN 50 AND 59 THEN 'e'
                                  WHEN age >= 60 THEN 'f'
                                  ELSE 'x'
                               END agegroup
                          FROM (SELECT a.course_id,
                                       ifnull((date_format(NOW(), '%Y') - b.year_of_birth), 0) + 1 age
                                  FROM student_courseenrollment a,
                                       auth_userprofile b,
                                       auth_user c
                                 WHERE     a.user_id = b.user_id
                                       AND a.user_id = c.id
                                       and a.is_active = 1
                                       and not (c.email) like '%delete_%'
                                       and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
                                       and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1'
                                       AND date_format(a.created, '%Y%m%d') between '20151014' and "'''+date+'''")
                                  aa) bb
                GROUP BY course_id
                ORDER by case
                         when course_id = 'course-v1:KHUk+KH102+2015_KH02' then 1
                         when course_id = 'course-v1:KHUk+KH101+2015_KH01' then 2
                         when course_id = 'course-v1:KoreaUnivK+ku_phy_001+2015_A04' then 3
                         when course_id = 'course-v1:KoreaUnivK+ku_cpx_001+2015_A03' then 4
                         when course_id = 'course-v1:KoreaUnivK+ku_soc_001+2015_A01' then 5
                         when course_id = 'course-v1:KoreaUnivK+ku_hum_001+2015_A02' then 6
                         when course_id = 'course-v1:PNUk+PL_C01+2015_KM_001' then 7
                         when course_id = 'course-v1:PNUk+SE_C01+2015_KM_002' then 8
                         when course_id = 'course-v1:SNUk+SNU044.008k+2015' then 9
                         when course_id = 'course-v1:SNUk+SNU046.101k+2015' then 10
                         when course_id = 'course-v1:SKKUk+COS2034.01x+2015_SKKU1' then 11
                         when course_id = 'course-v1:SKKUk+GEDT011.01x+2015_SKKU2' then 12
                         when course_id = 'course-v1:YSUk+YSU_KOR02k+2015_T2' then 13
                         when course_id = 'course-v1:YSUk+YSU_BIZ03k+2015_T2' then 14
                         when course_id = 'course-v1:YSUk+YSU_UCC01k+2015_T2' then 15
                         when course_id = 'course-v1:EwhaK+EW10164K+2015-01' then 16
                         when course_id = 'course-v1:EwhaK+EW11151K+2015-02' then 17
                         when course_id = 'course-v1:EwhaK+EW10771K+2015-03' then 18
                         when course_id = 'course-v1:EwhaK+EW36387K+2015-04' then 19
                         when course_id = 'course-v1:POSTECHk+POSTECH.MECH583k+2015-01' then 20
                         when course_id = 'course-v1:POSTECHk+POSTECH.EECE341k+2015-01' then 21
                         when course_id = 'course-v1:KAISTk+KMAE251+2015_K0101' then 22
                         when course_id = 'course-v1:KAISTk+KCS470+2015_K0201' then 23
                         when course_id = 'course-v1:HYUk+HYUARE4100k+2015_C1' then 24
                         when course_id = 'course-v1:HYUk+HYUPAD3004k+2015_C1' then 25
                         when course_id = 'course-v1:HYUk+HYUBUS3099k+2015_C1' then 26
                         when course_id = 'course-v1:HYUk+HYUSOC1053k+2015_C1' then 27
                         when course_id = 'course-v1:edX+DemoX+Demo_Course' then 28 end;''')
    row = cur.fetchall()
    cur.close()

    return row
#
# course_age = ('''SELECT
#                        ifnull(sum(IF(agegroup = 'a', 1, NULL)),0) a,
#                        ifnull(sum(IF(agegroup = 'b', 1, NULL)),0) b,
#                        ifnull(sum(IF(agegroup = 'c', 1, NULL)),0) c,
#                        ifnull(sum(IF(agegroup = 'd', 1, NULL)),0) d,
#                        ifnull(sum(IF(agegroup = 'e', 1, NULL)),0) e,
#                        ifnull(sum(IF(agegroup = 'f', 1, NULL)),0) f,
#                        ifnull(sum(IF(agegroup = 'x', 1, NULL)),0) x
#                   FROM (SELECT course_id,
#                           CASE
#                                   WHEN age < 20 THEN 'a'
#                                   WHEN age BETWEEN 20 AND 29 THEN 'b'
#                                   WHEN age BETWEEN 30 AND 39 THEN 'c'
#                                   WHEN age BETWEEN 40 AND 49 THEN 'd'
#                                   WHEN age BETWEEN 50 AND 59 THEN 'e'
#                                   WHEN age >= 60 THEN 'f'
#                                   ELSE 'x'
#                                END agegroup
#                           FROM (SELECT a.course_id,
#                                        ifnull((date_format(NOW(), '%Y') - b.year_of_birth), 0) + 1 age
#                                   FROM student_courseenrollment a,
#                                        auth_userprofile b,
#                                        auth_user c
#                                  WHERE     a.user_id = b.user_id
#                                        AND a.user_id = c.id
#                                        and a.is_active = 1
#                                        and not (c.email) like '%delete_%'
#                                        and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
#                                        and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1'
#                                        AND date_format(a.created, '%y%m%d') between '151014' and date_format(DATE_ADD(now(), INTERVAL -1 day), '%y%m%d'))
#                                   aa) bb
#                 GROUP BY course_id
#                 ORDER by case
#                          when course_id = 'course-v1:KHUk+KH102+2015_KH02' then 1
#                          when course_id = 'course-v1:KHUk+KH101+2015_KH01' then 2
#                          when course_id = 'course-v1:KoreaUnivK+ku_phy_001+2015_A04' then 3
#                          when course_id = 'course-v1:KoreaUnivK+ku_cpx_001+2015_A03' then 4
#                          when course_id = 'course-v1:KoreaUnivK+ku_soc_001+2015_A01' then 5
#                          when course_id = 'course-v1:KoreaUnivK+ku_hum_001+2015_A02' then 6
#                          when course_id = 'course-v1:PNUk+PL_C01+2015_KM_001' then 7
#                          when course_id = 'course-v1:PNUk+SE_C01+2015_KM_002' then 8
#                          when course_id = 'course-v1:SNUk+SNU044.008k+2015' then 9
#                          when course_id = 'course-v1:SNUk+SNU046.101k+2015' then 10
#                          when course_id = 'course-v1:SKKUk+COS2034.01x+2015_SKKU1' then 11
#                          when course_id = 'course-v1:SKKUk+GEDT011.01x+2015_SKKU2' then 12
#                          when course_id = 'course-v1:YSUk+YSU_KOR02k+2015_T2' then 13
#                          when course_id = 'course-v1:YSUk+YSU_BIZ03k+2015_T2' then 14
#                          when course_id = 'course-v1:YSUk+YSU_UCC01k+2015_T2' then 15
#                          when course_id = 'course-v1:EwhaK+EW10164K+2015-01' then 16
#                          when course_id = 'course-v1:EwhaK+EW11151K+2015-02' then 17
#                          when course_id = 'course-v1:EwhaK+EW10771K+2015-03' then 18
#                          when course_id = 'course-v1:EwhaK+EW36387K+2015-04' then 19
#                          when course_id = 'course-v1:POSTECHk+POSTECH.MECH583k+2015-01' then 20
#                          when course_id = 'course-v1:POSTECHk+POSTECH.EECE341k+2015-01' then 21
#                          when course_id = 'course-v1:KAISTk+KMAE251+2015_K0101' then 22
#                          when course_id = 'course-v1:KAISTk+KCS470+2015_K0201' then 23
#                          when course_id = 'course-v1:HYUk+HYUARE4100k+2015_C1' then 24
#                          when course_id = 'course-v1:HYUk+HYUPAD3004k+2015_C1' then 25
#                          when course_id = 'course-v1:HYUk+HYUBUS3099k+2015_C1' then 26
#                          when course_id = 'course-v1:HYUk+HYUSOC1053k+2015_C1' then 27
#                          when course_id = 'course-v1:edX+DemoX+Demo_Course' then 28 end;''')

#코스별 학력

def course_edu(date):

    cur = connection.cursor()
    cur.execute('''SELECT
                       ifnull(sum(IF(edugroup = '1', 1, NULL)) , 0)p,
                       ifnull(sum(IF(edugroup = '2', 1, NULL)) ,0) m,
                       ifnull(sum(IF(edugroup = '3', 1, NULL)) ,0) b,
                       ifnull(sum(IF(edugroup = '4', 1, NULL)) ,0) a,
                       ifnull(sum(IF(edugroup = '5', 1, NULL)) ,0) hs,
                       ifnull(sum(IF(edugroup = '6', 1, NULL)) ,0) jhs,
                       ifnull(sum(IF(edugroup = '7', 1, NULL)) ,0) el,
                       ifnull(sum(IF(edugroup = '8', 1, NULL)) ,0) other,
                       ifnull(sum(IF(edugroup = '9', 1, NULL)) ,0) none
                  FROM (SELECT course_id,
                        case
                          when level_of_education = 'p' then '1'
                          when level_of_education = 'm' then '2'
                          when level_of_education = 'b' then '3'
                          when level_of_education = 'a' then '4'
                          when level_of_education = 'hs' then '5'
                          when level_of_education = 'jhs' then '6'
                          when level_of_education = 'el' then '7'
                          when level_of_education = 'other' then '8'
                          else '9'
                        end edugroup

                          FROM (SELECT a.course_id, b.level_of_education
                                  FROM student_courseenrollment a,
                                       auth_userprofile b,
                                       auth_user c
                                 WHERE     a.user_id = b.user_id
                                       AND a.user_id = c.id
                                       and a.is_active = 1
                                       AND date_format(a.created , '%Y%m%d') between '20151014' and "'''+date+'''"
                                       and not (c.email) like '%delete_%'
                                       and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
                                       and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1')
                               aa) bb
                GROUP BY course_id
                ORDER by case
                         when course_id = 'course-v1:KHUk+KH102+2015_KH02' then 1
                         when course_id = 'course-v1:KHUk+KH101+2015_KH01' then 2
                         when course_id = 'course-v1:KoreaUnivK+ku_phy_001+2015_A04' then 3
                         when course_id = 'course-v1:KoreaUnivK+ku_cpx_001+2015_A03' then 4
                         when course_id = 'course-v1:KoreaUnivK+ku_soc_001+2015_A01' then 5
                         when course_id = 'course-v1:KoreaUnivK+ku_hum_001+2015_A02' then 6
                         when course_id = 'course-v1:PNUk+PL_C01+2015_KM_001' then 7
                         when course_id = 'course-v1:PNUk+SE_C01+2015_KM_002' then 8
                         when course_id = 'course-v1:SNUk+SNU044.008k+2015' then 9
                         when course_id = 'course-v1:SNUk+SNU046.101k+2015' then 10
                         when course_id = 'course-v1:SKKUk+COS2034.01x+2015_SKKU1' then 11
                         when course_id = 'course-v1:SKKUk+GEDT011.01x+2015_SKKU2' then 12
                         when course_id = 'course-v1:YSUk+YSU_KOR02k+2015_T2' then 13
                         when course_id = 'course-v1:YSUk+YSU_BIZ03k+2015_T2' then 14
                         when course_id = 'course-v1:YSUk+YSU_UCC01k+2015_T2' then 15
                         when course_id = 'course-v1:EwhaK+EW10164K+2015-01' then 16
                         when course_id = 'course-v1:EwhaK+EW11151K+2015-02' then 17
                         when course_id = 'course-v1:EwhaK+EW10771K+2015-03' then 18
                         when course_id = 'course-v1:EwhaK+EW36387K+2015-04' then 19
                         when course_id = 'course-v1:POSTECHk+POSTECH.MECH583k+2015-01' then 20
                         when course_id = 'course-v1:POSTECHk+POSTECH.EECE341k+2015-01' then 21
                         when course_id = 'course-v1:KAISTk+KMAE251+2015_K0101' then 22
                         when course_id = 'course-v1:KAISTk+KCS470+2015_K0201' then 23
                         when course_id = 'course-v1:HYUk+HYUARE4100k+2015_C1' then 24
                         when course_id = 'course-v1:HYUk+HYUPAD3004k+2015_C1' then 25
                         when course_id = 'course-v1:HYUk+HYUBUS3099k+2015_C1' then 26
                         when course_id = 'course-v1:HYUk+HYUSOC1053k+2015_C1' then 27 end;''')
    row = cur.fetchall()
    cur.close()

    return row

# course_edu = ('''SELECT
#                        ifnull(sum(IF(edugroup = '1', 1, NULL)) , 0)p,
#                        ifnull(sum(IF(edugroup = '2', 1, NULL)) ,0) m,
#                        ifnull(sum(IF(edugroup = '3', 1, NULL)) ,0) b,
#                        ifnull(sum(IF(edugroup = '4', 1, NULL)) ,0) a,
#                        ifnull(sum(IF(edugroup = '5', 1, NULL)) ,0) hs,
#                        ifnull(sum(IF(edugroup = '6', 1, NULL)) ,0) jhs,
#                        ifnull(sum(IF(edugroup = '7', 1, NULL)) ,0) el,
#                        ifnull(sum(IF(edugroup = '8', 1, NULL)) ,0) other,
#                        ifnull(sum(IF(edugroup = '9', 1, NULL)) ,0) none
#                   FROM (SELECT course_id,
#                         case
#                           when level_of_education = 'p' then '1'
#                           when level_of_education = 'm' then '2'
#                           when level_of_education = 'b' then '3'
#                           when level_of_education = 'a' then '4'
#                           when level_of_education = 'hs' then '5'
#                           when level_of_education = 'jhs' then '6'
#                           when level_of_education = 'el' then '7'
#                           when level_of_education = 'other' then '8'
#                           else '9'
#                         end edugroup
#
#                           FROM (SELECT a.course_id, b.level_of_education
#                                   FROM student_courseenrollment a,
#                                        auth_userprofile b,
#                                        auth_user c
#                                  WHERE     a.user_id = b.user_id
#                                        AND a.user_id = c.id
#                                        and a.is_active = 1
#                                        AND date_format(a.created , '%y%m%d') between '151014' and date_format(DATE_ADD(now(), INTERVAL -1 day), '%y%m%d')
#                                        and not (c.email) like '%delete_%'
#                                        and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
#                                        and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1')
#                                aa) bb
#                 GROUP BY course_id
#                 ORDER by case
#                          when course_id = 'course-v1:KHUk+KH102+2015_KH02' then 1
#                          when course_id = 'course-v1:KHUk+KH101+2015_KH01' then 2
#                          when course_id = 'course-v1:KoreaUnivK+ku_phy_001+2015_A04' then 3
#                          when course_id = 'course-v1:KoreaUnivK+ku_cpx_001+2015_A03' then 4
#                          when course_id = 'course-v1:KoreaUnivK+ku_soc_001+2015_A01' then 5
#                          when course_id = 'course-v1:KoreaUnivK+ku_hum_001+2015_A02' then 6
#                          when course_id = 'course-v1:PNUk+PL_C01+2015_KM_001' then 7
#                          when course_id = 'course-v1:PNUk+SE_C01+2015_KM_002' then 8
#                          when course_id = 'course-v1:SNUk+SNU044.008k+2015' then 9
#                          when course_id = 'course-v1:SNUk+SNU046.101k+2015' then 10
#                          when course_id = 'course-v1:SKKUk+COS2034.01x+2015_SKKU1' then 11
#                          when course_id = 'course-v1:SKKUk+GEDT011.01x+2015_SKKU2' then 12
#                          when course_id = 'course-v1:YSUk+YSU_KOR02k+2015_T2' then 13
#                          when course_id = 'course-v1:YSUk+YSU_BIZ03k+2015_T2' then 14
#                          when course_id = 'course-v1:YSUk+YSU_UCC01k+2015_T2' then 15
#                          when course_id = 'course-v1:EwhaK+EW10164K+2015-01' then 16
#                          when course_id = 'course-v1:EwhaK+EW11151K+2015-02' then 17
#                          when course_id = 'course-v1:EwhaK+EW10771K+2015-03' then 18
#                          when course_id = 'course-v1:EwhaK+EW36387K+2015-04' then 19
#                          when course_id = 'course-v1:POSTECHk+POSTECH.MECH583k+2015-01' then 20
#                          when course_id = 'course-v1:POSTECHk+POSTECH.EECE341k+2015-01' then 21
#                          when course_id = 'course-v1:KAISTk+KMAE251+2015_K0101' then 22
#                          when course_id = 'course-v1:KAISTk+KCS470+2015_K0201' then 23
#                          when course_id = 'course-v1:HYUk+HYUARE4100k+2015_C1' then 24
#                          when course_id = 'course-v1:HYUk+HYUPAD3004k+2015_C1' then 25
#                          when course_id = 'course-v1:HYUk+HYUBUS3099k+2015_C1' then 26
#                          when course_id = 'course-v1:HYUk+HYUSOC1053k+2015_C1' then 27 end;''')
