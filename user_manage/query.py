# -*- coding: utf-8 -*-

# 회원 가입자 수 (신규)

user_count_today = ('''Select count(*)
                      FROM auth_userprofile a, auth_user b
                      WHERE a.user_id = b.id AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and b.date_joined > CURDATE();''')


# 회원 가입자 수 (누적)

user_count_total = (''' Select count(*)
                    FROM auth_userprofile a, auth_user b
                    WHERE a.user_id = b.id AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format(b.date_joined,'%Y%m%d')  > '20151013';''')

# 강좌 수강자 수(신규)

course_count_today = (''' select count(a.user_id) cnt
                        from student_courseenrollment a, auth_user b
                        where a.user_id = b.id
                          and a.created > CURDATE()
                          and a.is_active = 1
                          and not (b.email) like '%delete_%'
                          and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1'
                          and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'; ''')

# 강좌 수강자 수(누적)

course_count_total = (''' select count(a.user_id) cnt
                        from student_courseenrollment a, auth_user b
                        where a.user_id = b.id
                          and date_format(a.created,'%Y%m%d') > '20151013'
                          and a.is_active = 1
                          and not (b.email) like '%delete_%'
                          and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1'
                          and not a.course_id = 'course-v1:edX+DemoX+Demo_Course';''')


# 강좌 수강자 수(누적/중복제외)

course_count_distinct = ('''select count(distinct a.user_id) cnt
                            from student_courseenrollment a, auth_user b
                            where a.user_id = b.id
                              and date_format(a.created,'%Y%m%d') > '20151013'
                              and a.is_active = 1
                              and not (b.email) like '%delete_%';''')

#운영 강좌수

course_count = ('''select count(distinct a.course_id) cnt
                from student_courseenrollment a, auth_user b
                where a.user_id = b.id
                  and a.is_active = 1
                  and not a.course_id = 'course-v1:KMOOC+DEMOk+2015_1'
                  and not a.course_id = 'course-v1:edX+DemoX+Demo_Course'
                  and not a.course_id = 'edX/DemoX/Demo_Course';''')

#현재 날짜

now_day = ('''select date_format(now( ), '%Y.%m.%d %H:%i:%s' );''')

#현재 시간

now_time = ('''select curtime();''')

#엑셀 시

excel_now_day = ('''select date_format(now( ), '%Y%m%d' );''')

#Test

test = ('''SELECT case when a.level_of_education is null or a.level_of_education = '' or a.level_of_education = 'null'  then 'none' else level_of_education end level_of_education,
       sum(if(a.gender = 'm', 1, 0)) AS "male",
       sum(if(a.gender = 'f', 1, 0)) AS "female",
       count(*) total
  FROM auth_userprofile a, auth_user b
 WHERE a.user_id = b.id AND NOT (b.is_staff = 1 OR b.is_superuser = 1) and date_format(b.date_joined,'%Y%m%d') between '20151014' and '20151221'
 group by case when a.level_of_education is null or a.level_of_education = '' or a.level_of_education = 'null' then 'none' else level_of_education end
 order by case
         when a.level_of_education = 'p' then 1
         when a.level_of_education = 'm' then 2
         when a.level_of_education = 'b' then 3
         when a.level_of_education = 'a' then 4
         when a.level_of_education = 'hs' then 5
         when a.level_of_education = 'jhs' then 6
         when a.level_of_education = 'el' then 7
         when a.level_of_education = 'other' then 8
         when a.level_of_education is null or a.level_of_education = '' or a.level_of_education = 'null' then 9 end;''')