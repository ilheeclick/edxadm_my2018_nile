# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, redirect
from django.template import Context, RequestContext
from django.http import Http404, HttpResponse, FileResponse
from django.utils import timezone
import json
from django.db import connection
from management.settings import UPLOAD_DIR
from django.core.serializers.json import DjangoJSONEncoder
from management.settings import dic_univ, database_id, debug
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import os
from django.views.decorators.csrf import csrf_exempt
import subprocess
import commands
import sys
from models import GeneratedCertificate
import pprint
from django.db import connections
import ast
import urllib

reload(sys)
sys.setdefaultencoding('utf-8')


# Create your views here.

# stastic view
def stastic_index(request):
    return render(request, 'stastic/stastic_index.html')


def test(request):
    if request.is_ajax():
        data = {
            "data": [
                {
                    "name": "Tiger Nixon",
                    "position": "System Architect",
                    "salary": "$320,800",
                    "start_date": "2011/04/25",
                    "office": "Edinburgh",
                    "extn": "5421"
                },
                {
                    "name": "Garrett Winters",
                    "position": "Accountant",
                    "salary": "$170,750",
                    "start_date": "2011/07/25",
                    "office": "Tokyo",
                    "extn": "8422"
                },
                {
                    "name": "Ashton Cox",
                    "position": "Junior Technical Author",
                    "salary": "$86,000",
                    "start_date": "2009/01/12",
                    "office": "San Francisco",
                    "extn": "1562"
                },
                {
                    "name": "Cedric Kelly",
                    "position": "Senior Javascript Developer",
                    "salary": "$433,060",
                    "start_date": "2012/03/29",
                    "office": "Edinburgh",
                    "extn": "6224"
                },
                {
                    "name": "Airi Satou",
                    "position": "Accountant",
                    "salary": "$162,700",
                    "start_date": "2008/11/28",
                    "office": "Tokyo",
                    "extn": "5407"
                },
                {
                    "name": "Brielle Williamson",
                    "position": "Integration Specialist",
                    "salary": "$372,000",
                    "start_date": "2012/12/02",
                    "office": "New York",
                    "extn": "4804"
                },
                {
                    "name": "Herrod Chandler",
                    "position": "Sales Assistant",
                    "salary": "$137,500",
                    "start_date": "2012/08/06",
                    "office": "San Francisco",
                    "extn": "9608"
                },
                {
                    "name": "Rhona Davidson",
                    "position": "Integration Specialist",
                    "salary": "$327,900",
                    "start_date": "2010/10/14",
                    "office": "Tokyo",
                    "extn": "6200"
                },
                {
                    "name": "Colleen Hurst",
                    "position": "Javascript Developer",
                    "salary": "$205,500",
                    "start_date": "2009/09/15",
                    "office": "San Francisco",
                    "extn": "2360"
                },
                {
                    "name": "Sonya Frost",
                    "position": "Software Engineer",
                    "salary": "$103,600",
                    "start_date": "2008/12/13",
                    "office": "Edinburgh",
                    "extn": "1667"
                },
                {
                    "name": "Jena Gaines",
                    "position": "Office Manager",
                    "salary": "$90,560",
                    "start_date": "2008/12/19",
                    "office": "London",
                    "extn": "3814"
                },
                {
                    "name": "Quinn Flynn",
                    "position": "Support Lead",
                    "salary": "$342,000",
                    "start_date": "2013/03/03",
                    "office": "Edinburgh",
                    "extn": "9497"
                },
                {
                    "name": "Charde Marshall",
                    "position": "Regional Director",
                    "salary": "$470,600",
                    "start_date": "2008/10/16",
                    "office": "San Francisco",
                    "extn": "6741"
                },
                {
                    "name": "Haley Kennedy",
                    "position": "Senior Marketing Designer",
                    "salary": "$313,500",
                    "start_date": "2012/12/18",
                    "office": "London",
                    "extn": "3597"
                },
                {
                    "name": "Tatyana Fitzpatrick",
                    "position": "Regional Director",
                    "salary": "$385,750",
                    "start_date": "2010/03/17",
                    "office": "London",
                    "extn": "1965"
                },
                {
                    "name": "Michael Silva",
                    "position": "Marketing Designer",
                    "salary": "$198,500",
                    "start_date": "2012/11/27",
                    "office": "London",
                    "extn": "1581"
                },
                {
                    "name": "Paul Byrd",
                    "position": "Chief Financial Officer (CFO)",
                    "salary": "$725,000",
                    "start_date": "2010/06/09",
                    "office": "New York",
                    "extn": "3059"
                },
                {
                    "name": "Gloria Little",
                    "position": "Systems Administrator",
                    "salary": "$237,500",
                    "start_date": "2009/04/10",
                    "office": "New York",
                    "extn": "1721"
                },
                {
                    "name": "Bradley Greer",
                    "position": "Software Engineer",
                    "salary": "$132,000",
                    "start_date": "2012/10/13",
                    "office": "London",
                    "extn": "2558"
                },
                {
                    "name": "Dai Rios",
                    "position": "Personnel Lead",
                    "salary": "$217,500",
                    "start_date": "2012/09/26",
                    "office": "Edinburgh",
                    "extn": "2290"
                },
                {
                    "name": "Jenette Caldwell",
                    "position": "Development Lead",
                    "salary": "$345,000",
                    "start_date": "2011/09/03",
                    "office": "New York",
                    "extn": "1937"
                },
                {
                    "name": "Yuri Berry",
                    "position": "Chief Marketing Officer (CMO)",
                    "salary": "$675,000",
                    "start_date": "2009/06/25",
                    "office": "New York",
                    "extn": "6154"
                },
                {
                    "name": "Caesar Vance",
                    "position": "Pre-Sales Support",
                    "salary": "$106,450",
                    "start_date": "2011/12/12",
                    "office": "New York",
                    "extn": "8330"
                },
                {
                    "name": "Doris Wilder",
                    "position": "Sales Assistant",
                    "salary": "$85,600",
                    "start_date": "2010/09/20",
                    "office": "Sidney",
                    "extn": "3023"
                },
                {
                    "name": "Angelica Ramos",
                    "position": "Chief Executive Officer (CEO)",
                    "salary": "$1,200,000",
                    "start_date": "2009/10/09",
                    "office": "London",
                    "extn": "5797"
                },
                {
                    "name": "Gavin Joyce",
                    "position": "Developer",
                    "salary": "$92,575",
                    "start_date": "2010/12/22",
                    "office": "Edinburgh",
                    "extn": "8822"
                },
                {
                    "name": "Jennifer Chang",
                    "position": "Regional Director",
                    "salary": "$357,650",
                    "start_date": "2010/11/14",
                    "office": "Singapore",
                    "extn": "9239"
                },
                {
                    "name": "Brenden Wagner",
                    "position": "Software Engineer",
                    "salary": "$206,850",
                    "start_date": "2011/06/07",
                    "office": "San Francisco",
                    "extn": "1314"
                },
                {
                    "name": "Fiona Green",
                    "position": "Chief Operating Officer (COO)",
                    "salary": "$850,000",
                    "start_date": "2010/03/11",
                    "office": "San Francisco",
                    "extn": "2947"
                },
                {
                    "name": "Shou Itou",
                    "position": "Regional Marketing",
                    "salary": "$163,000",
                    "start_date": "2011/08/14",
                    "office": "Tokyo",
                    "extn": "8899"
                },
                {
                    "name": "Michelle House",
                    "position": "Integration Specialist",
                    "salary": "$95,400",
                    "start_date": "2011/06/02",
                    "office": "Sidney",
                    "extn": "2769"
                },
                {
                    "name": "Suki Burks",
                    "position": "Developer",
                    "salary": "$114,500",
                    "start_date": "2009/10/22",
                    "office": "London",
                    "extn": "6832"
                },
                {
                    "name": "Prescott Bartlett",
                    "position": "Technical Author",
                    "salary": "$145,000",
                    "start_date": "2011/05/07",
                    "office": "London",
                    "extn": "3606"
                },
                {
                    "name": "Gavin Cortez",
                    "position": "Team Leader",
                    "salary": "$235,500",
                    "start_date": "2008/10/26",
                    "office": "San Francisco",
                    "extn": "2860"
                },
                {
                    "name": "Martena Mccray",
                    "position": "Post-Sales support",
                    "salary": "$324,050",
                    "start_date": "2011/03/09",
                    "office": "Edinburgh",
                    "extn": "8240"
                },
                {
                    "name": "Unity Butler",
                    "position": "Marketing Designer",
                    "salary": "$85,675",
                    "start_date": "2009/12/09",
                    "office": "San Francisco",
                    "extn": "5384"
                },
                {
                    "name": "Howard Hatfield",
                    "position": "Office Manager",
                    "salary": "$164,500",
                    "start_date": "2008/12/16",
                    "office": "San Francisco",
                    "extn": "7031"
                },
                {
                    "name": "Hope Fuentes",
                    "position": "Secretary",
                    "salary": "$109,850",
                    "start_date": "2010/02/12",
                    "office": "San Francisco",
                    "extn": "6318"
                },
                {
                    "name": "Vivian Harrell",
                    "position": "Financial Controller",
                    "salary": "$452,500",
                    "start_date": "2009/02/14",
                    "office": "San Francisco",
                    "extn": "9422"
                },
                {
                    "name": "Timothy Mooney",
                    "position": "Office Manager",
                    "salary": "$136,200",
                    "start_date": "2008/12/11",
                    "office": "London",
                    "extn": "7580"
                },
                {
                    "name": "Jackson Bradshaw",
                    "position": "Director",
                    "salary": "$645,750",
                    "start_date": "2008/09/26",
                    "office": "New York",
                    "extn": "1042"
                },
                {
                    "name": "Olivia Liang",
                    "position": "Support Engineer",
                    "salary": "$234,500",
                    "start_date": "2011/02/03",
                    "office": "Singapore",
                    "extn": "2120"
                },
                {
                    "name": "Bruno Nash",
                    "position": "Software Engineer",
                    "salary": "$163,500",
                    "start_date": "2011/05/03",
                    "office": "London",
                    "extn": "6222"
                },
                {
                    "name": "Sakura Yamamoto",
                    "position": "Support Engineer",
                    "salary": "$139,575",
                    "start_date": "2009/08/19",
                    "office": "Tokyo",
                    "extn": "9383"
                },
                {
                    "name": "Thor Walton",
                    "position": "Developer",
                    "salary": "$98,540",
                    "start_date": "2013/08/11",
                    "office": "New York",
                    "extn": "8327"
                },
                {
                    "name": "Finn Camacho",
                    "position": "Support Engineer",
                    "salary": "$87,500",
                    "start_date": "2009/07/07",
                    "office": "San Francisco",
                    "extn": "2927"
                },
                {
                    "name": "Serge Baldwin",
                    "position": "Data Coordinator",
                    "salary": "$138,575",
                    "start_date": "2012/04/09",
                    "office": "Singapore",
                    "extn": "8352"
                },
                {
                    "name": "Zenaida Frank",
                    "position": "Software Engineer",
                    "salary": "$125,250",
                    "start_date": "2010/01/04",
                    "office": "New York",
                    "extn": "7439"
                },
                {
                    "name": "Zorita Serrano",
                    "position": "Software Engineer",
                    "salary": "$115,000",
                    "start_date": "2012/06/01",
                    "office": "San Francisco",
                    "extn": "4389"
                },
                {
                    "name": "Jennifer Acosta",
                    "position": "Junior Javascript Developer",
                    "salary": "$75,650",
                    "start_date": "2013/02/01",
                    "office": "Edinburgh",
                    "extn": "3431"
                },
                {
                    "name": "Cara Stevens",
                    "position": "Sales Assistant",
                    "salary": "$145,600",
                    "start_date": "2011/12/06",
                    "office": "New York",
                    "extn": "3990"
                },
                {
                    "name": "Hermione Butler",
                    "position": "Regional Director",
                    "salary": "$356,250",
                    "start_date": "2011/03/21",
                    "office": "London",
                    "extn": "1016"
                },
                {
                    "name": "Lael Greer",
                    "position": "Systems Administrator",
                    "salary": "$103,500",
                    "start_date": "2009/02/27",
                    "office": "London",
                    "extn": "6733"
                },
                {
                    "name": "Jonas Alexander",
                    "position": "Developer",
                    "salary": "$86,500",
                    "start_date": "2010/07/14",
                    "office": "San Francisco",
                    "extn": "8196"
                },
                {
                    "name": "Shad Decker",
                    "position": "Regional Director",
                    "salary": "$183,000",
                    "start_date": "2008/11/13",
                    "office": "Edinburgh",
                    "extn": "6373"
                },
                {
                    "name": "Michael Bruce",
                    "position": "Javascript Developer",
                    "salary": "$183,000",
                    "start_date": "2011/06/27",
                    "office": "Singapore",
                    "extn": "5384"
                },
                {
                    "name": "Donna Snider",
                    "position": "Customer Support",
                    "salary": "$112,000",
                    "start_date": "2011/01/25",
                    "office": "New York",
                    "extn": "4226"
                }
            ]
        }
        print json.dumps(data)

        return HttpResponse(json.dumps(data), 'applications/json')
    else:
        return render(request, 'test01.html')


def month_stastic(request):
    return render(request, 'stastic/month_stastic.html')


# state view
def mana_state(request):
    return render(request, 'state/mana_state.html')


def dev_state(request):
    return render(request, 'state/dev_state.html')


# certificate view
def certificate(request):
    client = MongoClient(database_id, 27017)
    db = client.edxapp
    pb_list = []
    pb_dict = dict()

    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'org':
            data = json.dumps(dic_univ, cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'course':
            course_list = []
            org = request.GET['org']
            cur = connection.cursor()

            query = "select course_id from certificates_generatedcertificate where course_id like '%" + org + "%' group by course_id"
            cur.execute(query)
            course = cur.fetchall()
            cur.close()

            for c in course:
                value_list = []

                print "c[0]", c[0]
                course_id = c[0]

                cid = course_id.split('+')[1]
                run = course_id.split('+')[2]
                cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
                pb = cursor.get('versions').get('published-branch')

                cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},
                                                            {"blocks": {"$elemMatch": {"block_type": "course"}}})
                course_name = cursor.get('blocks')[0].get('fields').get('display_name')  # course_names
                value_list.append(str(pb))
                value_list.append(course_name)
                value_list.append(run)
                print value_list
                course_list.append(value_list)
            data = json.dumps(list(course_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'run':
            course_pb = request.GET['course']
            print 'course_pb', course_pb
            cursor = db.modulestore.active_versions.find({'versions.published-branch': ObjectId(course_pb)})

            for document in cursor:
                run = document.get('run')
                print 'run', run
            cursor.close()
            data = json.dumps(run, cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'certificate':
            course_pb = request.GET['course_id']
            run = request.GET['run']
            course = ''
            cursor = db.modulestore.active_versions.find({'versions.published-branch': ObjectId(course_pb)})
            for document in cursor:
                course = document.get('course')
            print 'course', course
            cursor.close()

            cur = connection.cursor()
            query = "SELECT DISTINCT course_id FROM certificates_generatedcertificate WHERE course_id LIKE '%" + course + "%' AND course_id LIKE '%" + run + "%'"
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            print 'row == ' + str(row)
            for r in row:
                certi = 'O'
                data = json.dumps(certi, cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'create_certi':
            org_name = request.GET['org_name']
            run = request.GET['run']
            for org, name in dic_univ.iteritems():
                if name == org_name:
                    org_id = org
            # print org_id
            cur = connection.cursor()
            query = "select course_id from certificates_generatedcertificate where course_id like '%" + org_id + "%' and course_id like '%" + run + "%' group by course_id"
            cur.execute(query)
            course = cur.fetchall()
            cur.close()

            for c in course:
                value_list = []
                print "c[0]", c[0]
                course_id = c[0]

                cid = course_id.split('+')[1]
                run = course_id.split('+')[2]
                print org_id, '/', cid, '/', run

                cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
                pb = cursor.get('versions').get('published-branch')

                cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},
                                                            {"blocks": {"$elemMatch": {"block_type": "course"}}})
                course_end = cursor.get('blocks')[0].get('fields').get('end')  # course_names
                end_date = datetime.datetime.strptime(str(course_end)[0:10], "%Y-%m-%d").date()
                today = datetime.date.today()

                if end_date > today:
                    data = json.dumps('Error')
                else:
                    print '-----ready make certificate !!-----'
                    subprocess.call('ssh vagrant@192.168.33.12 ./test.sh ' + org_id + ' ' + cid + ' ' + run + '',
                                    shell=True)
                    print '-----end create certificate !!-----'
                    data = json.dumps('Success')
        elif request.GET['method'] == 'uni_certi':
            cur = connection.cursor()
            query = """
				SELECT course_id,
					   date_format(min(created_date),'%Y-%m-%d') cdate,
					   sum(if(status = 'downloadable', 1, 0)) downcnt,
					   sum(if(status = 'notpassing', 1, 0)) notcnt,
					   count(*) cnt
				  FROM certificates_generatedcertificate
			"""
            if 'org_id' in request.GET:
                query += "WHERE course_id like '%" + request.GET['org_id'] + "%'"
            if 'run' in request.GET:
                query += " and course_id LIKE '%" + request.GET['run'] + "%'"
            query += "GROUP BY course_id ORDER BY created_date DESC"
            cur.execute(query)
            course_list = cur.fetchall()
            cur.close()
            course_orgs = {}
            course_end = {}
            course_name = {}

            certi_list = []
            for c, cdate, downcnt, notcnt, cnt in course_list:
                value_list = []
                # print c
                # cid = str(c[0])
                # cid = str(c)
                course_id = c
                cid = c.split('+')[1]
                run = c.split('+')[2]
                cer_per = (downcnt / cnt) * 100
                cer_percent = round(cer_per, 2)

                # db.modulestore.active_versions --------------------------------------
                cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
                pb = cursor.get('versions').get('published-branch')
                # course_orgs
                course_orgs[course_id] = cursor.get('org')

                # db.modulestore.structures --------------------------------------
                cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},
                                                            {"blocks": {"$elemMatch": {"block_type": "course"}}})

                course_name = cursor.get('blocks')[0].get('fields').get('display_name')  # course_names
                course_end = cursor.get('blocks')[0].get('fields').get('end')  # course_ends

                # print course_orgs[course_id],course_name, run, course_end, cdate, cnt, downcnt, notcnt, cer_percent
                end_date = datetime.datetime.strptime(str(course_end)[0:10], "%Y-%m-%d").date()

                value_list.append(dic_univ[course_orgs[course_id]])
                value_list.append(course_name)
                value_list.append(run)
                value_list.append(end_date)
                value_list.append(cdate)
                value_list.append(cnt)
                value_list.append(downcnt)
                value_list.append(notcnt)
                value_list.append(cer_percent)

                # print "value_list == ",value_list
                certi_list.append(value_list)
            # print "certi_list ==", certi_list
            data = json.dumps(list(certi_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    return render(request, 'certificate/certificate.html')


def per_certificate(request):
    client = MongoClient(database_id, 27017)
    db = client.edxapp
    reload(sys)
    sys.setdefaultencoding('utf-8')
    alist = []
    if request.is_ajax():
        data = json.dumps('fail')
        if request.GET['method'] == 'per_certi':
            org_id = request.GET['org_id']
            run = request.GET['run']
            cur = connection.cursor()
            query = """
				SELECT course_id
				  FROM certificates_generatedcertificate
			"""
            if 'org_id' in request.GET:
                query += "WHERE course_id like '%" + org_id + "%'"
            if 'run' in request.GET:
                query += " and course_id LIKE '%" + run + "%'"
            query += "GROUP BY course_id"
            cur.execute(query)
            course_list = cur.fetchall()
            cur.close()

            for c in course_list:
                value_list = []
                course_id = c
                cid = c[0].split('+')[1]
                course = org_id + '+' + cid + '+' + run
                cur = connection.cursor()
                # print dic_univ[org_id], cid, run, course
                query = """
						select @RNUM := @RNUM + 1 AS NO, a.name, b.email,'""" + dic_univ[
                    org_id] + """' org, '""" + cid + """' course, '""" + run + """' run,
							   case when a.status = 'downloadable' then '생성완료'
									when a.status = 'notpassing' then '생성 전'
									when a.status = 'generated' then '생성오류' else '' end status
						  from ( SELECT @RNUM := 0 ) c, certificates_generatedcertificate a inner join auth_user b
							on (a.user_id = b.id)
						 where a.course_id like '%""" + str(course) + """%'
						 limit 2000
 				"""

                cur.execute(query)
                row = cur.fetchall()
                cur.close()
            # print str(row)

            data = json.dumps(list(row), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'email_search':
            course = ""
            user_list = []

            email = request.GET['email']
            cur = connection.cursor()
            query = """
					select course_id, email
					from certificates_generatedcertificate a inner join auth_user b
					on a.user_id = b.id
					where b.email like '%""" + email + """%'
			"""
            if 'org_id' in request.GET:
                query += "and a.course_id like '%" + request.GET['org_id'] + "%'"
            if 'run' in request.GET:
                query += " and a.course_id LIKE '%" + request.GET['run'] + "%'"
            cur.execute(query)
            course_list = cur.fetchall()
            cur.close()
            i = 1
            for c, email in course_list:
                value_list = []
                course_id = c
                org_start = c.find(':') + 1
                org_end = c.find('+', org_start)
                org = c[org_start:org_end]
                cid = c.split('+')[1]
                run = c.split('+')[2]

                cur = connection.cursor()
                # print dic_univ[org_id], cid, run, course
                query = """
						select a.name, b.email,'""" + dic_univ[org] + """' org, '""" + cid + """' course, '""" + run + """' run,
							   case when a.status = 'downloadable' then '생성완료'
									when a.status = 'notpassing' then '생성 전'
									when a.status = 'generated' then '생성오류' else '' end status
						  from ( SELECT @RNUM := 0 ) c, certificates_generatedcertificate a inner join auth_user b
							on (a.user_id = b.id)
						 where b.email like '%""" + email + """%'
 				"""

                cur.execute(query)
                row = cur.fetchone()
                cur.close()
                value_list.append(i)
                value_list.append(row[0])
                value_list.append(row[1])
                value_list.append(row[2])
                value_list.append(row[3])
                value_list.append(row[4])
                value_list.append(row[5])
                user_list.append(value_list)
                i += 1

            data = json.dumps(list(user_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(data, 'applications/json')

    return render(request, 'certificate/per_certificate.html')


def uni_certificate(request):
    # cert = GeneratedCertificate.objects.get(course_id='course-v1:KoreaUnivK+ku_hum_001+2015_A02')
    cert = GeneratedCertificate.objects.filter(course_id='course-v1:KoreaUnivK+ku_hum_001+2015_A02').only('course_id')

    print '@@@ uni_certificate called @@@', len(cert)
    print 'sql s --------------------'
    print cert.query
    print 'sql e --------------------'

    context = dict()
    context['test'] = '1'

    return render(request, 'certificate/uni_certificate.html', context)


# community view
def comm_notice(request):
    noti_list = []
    if request.is_ajax():
        aaData = {}
        if request.GET['method'] == 'notice_list':
            cur = connection.cursor()
            query = """
                SELECT board_id,
                       content,
                       subject,
                       SUBSTRING(reg_date, 1, 11),
                       CASE
                          WHEN use_yn = 'Y' THEN '보임'
                          WHEN use_yn = 'N' THEN '숨김'
                          ELSE ''
                       END
                          use_yn,
                       CASE WHEN odby = '0' THEN '' ELSE odby END odby,
                       CASE
                          WHEN head_title = 'noti_n' THEN '공지'
                          WHEN head_title = 'advert_n' THEN '공고'
                          WHEN head_title = 'guide_n' THEN '안내'
                          WHEN head_title = 'event_n' THEN '이벤트'
                          WHEN head_title = 'etc_n' THEN '기타'
                          ELSE ''
                       END
                          head_title,
                       use_yn
                  FROM tb_board
                 WHERE section = 'N' AND NOT use_yn = 'D'
			"""

            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                query += "and " + title + " like '%" + search + "%'"

            # query += " ORDER BY board_id"

            # print 'query', query

            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            index = 1
            for noti in row:
                value_list = []
                notice = noti
                # print notice
                value_list.append(notice[0])
                value_list.append(index)
                value_list.append(notice[6])
                value_list.append(notice[2])
                value_list.append(notice[1])
                value_list.append(notice[3])
                value_list.append(notice[4])
                value_list.append(notice[5])
                value_list.append(notice[7])
                noti_list.append(value_list)
                index += 1

            aaData = json.dumps(list(noti_list), cls=DjangoJSONEncoder, ensure_ascii=False)

        elif request.GET['method'] == 'notice_del':
            noti_id = request.GET['noti_id']
            use_yn = request.GET['use_yn']
            yn = ''
            if use_yn == 'Y':
                yn = 'N'
            else:
                yn = 'Y'
            # print 'use_yn == ',use_yn,' yn == ',yn
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + noti_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        elif request.GET['method'] == 'notice_delete':
            noti_id = request.GET['noti_id']
            use_yn = request.GET['use_yn']
            yn = 'D'

            # print 'use_yn == ',use_yn,' yn == ',yn
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + noti_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        return HttpResponse(aaData, 'applications/json')

    return render(request, 'community/comm_notice.html')


@csrf_exempt
def new_notice(request):
    if 'file' in request.FILES:
        print 'file process start .'

        value_list = []
        file = request.FILES['file']
        filename = ''
        file_ext = ''
        file_size = ''
        print 'file:', file
        filename = file._name
        file_ext = filename.split('.')[1]

        fp = open('%s/%s' % (UPLOAD_DIR, filename), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        data = '성공'

        n = os.path.getsize(UPLOAD_DIR + filename)
        file_size = str(n / 1024) + "KB"  # 킬로바이트 단위로

        value_list.append(filename)
        value_list.append(file_ext)
        value_list.append(file_size)
        data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    elif request.method == 'POST':
        data = json.dumps({'status': "fail", 'msg': "오류가 발생했습니다"})
        if request.POST['method'] == 'add':

            title = request.POST.get('nt_title')
            title = title.replace("'", "''")
            content = request.POST.get('nt_cont')
            content = content.replace("'", "''")
            section = request.POST.get('notice')
            head_title = request.POST.get('head_title')
            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')
            print file_name, '/', file_ext, '/', file_size

            cur = connection.cursor()
            query = "insert into edxapp.tb_board(subject, content, head_title, section)"
            query += " VALUES ('" + title + "', '" + content + "', '" + head_title + "', '" + section + "') "
            cur.execute(query)

            query2 = "select board_id from tb_board where subject ='" + title + "' and content='" + content + "'"
            cur.execute(query2)
            board_id = cur.fetchall()
            cur.close()
            # print board_id[0][0]
            if upload_file != '':
                cur = connection.cursor()
                query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
                        "VALUES ('" + str(board_id[0][0]) + "','" + str(file_name) + "','" + str(
                    file_ext) + "','" + str(file_size) + "')"
                cur.execute(query)
                cur.close()

            data = json.dumps({'status': "success"})

        elif request.POST['method'] == 'modi':
            title = request.POST.get('nt_title')
            title = title.replace("'", "''")
            content = request.POST.get('nt_cont')
            content = content.replace("'", "''")
            noti_id = request.POST.get('noti_id')
            odby = request.POST.get('odby')
            head_title = request.POST.get('head_title')

            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')

            cur = connection.cursor()
            # query = "update edxapp.tb_board set subject = '"+title+"', content = '"+content+"', odby = '"+odby+"' where board_id = '"+noti_id+"'"
            query = "update edxapp.tb_board set subject = '" + title + "', content = '" + content + "', head_title = '" + head_title + "', mod_date = now() where board_id = '" + noti_id + "'"
            cur.execute(query)
            cur.close()

            if upload_file != '':
                cur = connection.cursor()
                query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
                        "VALUES ('" + str(noti_id) + "','" + str(file_name) + "','" + str(file_ext) + "','" + str(
                    file_size) + "')"
                cur.execute(query)
                cur.close()
            data = json.dumps({'status': "success"})

        return HttpResponse(data, 'applications/json')

    return render(request, 'community/comm_newnotice.html')


@csrf_exempt
def modi_notice(request, id, use_yn):
    mod_notice = []

    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            # query = "SELECT subject, content, odby, head_title from tb_board WHERE section = 'N' and board_id = "+id
            query = """
					SELECT subject,
						   content,
						   odby,
						   CASE
							  WHEN head_title = 'noti_n' THEN '공지'
							  WHEN head_title = 'advert_n' THEN '공고'
							  WHEN head_title = 'guide_n' THEN '안내'
							  WHEN head_title = 'event_n' THEN '이벤트'
							  WHEN head_title = 'etc_n' THEN '기타'
							  ELSE ''
						   END
							  head_title
					  FROM tb_board
					 WHERE section = 'N' and board_id = """ + id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            # print 'query', query
            # print 'row[0] == ',row[0][0]
            # print 'row[1] == ',row[0][1]
            # print 'row[2] == ',row[0][2]
            # print 'row[3] == ',row[0][3]

            cur = connection.cursor()
            query = "select attatch_file_name from tb_board_attach " \
                    "where board_id = " + id
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            # print 'files == ',files

            mod_notice.append(row[0][0])
            mod_notice.append(row[0][1])
            mod_notice.append(row[0][2])
            mod_notice.append(row[0][3])

            if files:
                mod_notice.append(files)
            # print 'mod_notice == ',mod_notice

            data = json.dumps(list(mod_notice), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'file_download':
            pass

            print 'file_download with ajax is not working'

        return HttpResponse(data, 'applications/json')

    variables = RequestContext(request, {
        'id': id,
        'use_yn': use_yn
    })

    return render_to_response('community/comm_modinotice.html', variables)


def test_index(request):
    return render(request, 'test_index.html')


def file_download_test(request):
    print 'called  file_download_test'

    file_path = '/Users/redukyo/workspace/management/home/static/upload/create_table1.txt'
    # file_path = '/Users/redukyo/workspace/management/home/static/upload/test.jpg'

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    raise Http404


def comm_k_news(request):
    knews_list = []
    if request.is_ajax():
        aaData = {}
        if request.GET['method'] == 'knews_list':
            cur = connection.cursor()
            query = """
                SELECT board_id,
                       content,
                       subject,
                       SUBSTRING(reg_date, 1, 11),
                       CASE
                          WHEN use_yn = 'Y' THEN '보임'
                          WHEN use_yn = 'N' THEN '숨김'
                          ELSE ''
                       END
                          use_yn,
                       CASE WHEN odby = '0' THEN '' ELSE odby END odby,
                       CASE
                          WHEN head_title = 'k_news_k' THEN 'K-MOOC소식'
                          WHEN head_title = 'report_k' THEN '보도자료'
                          WHEN head_title = 'u_news_k' THEN '대학뉴스'
                          WHEN head_title = 'support_k' THEN '서포터즈이야기'
                          WHEN head_title = 'n_new_k' THEN 'NILE소식'
                          WHEN head_title = 'etc_k' THEN '기타'
                          ELSE ''
                       END
                          head_title,
                       use_yn
                  FROM tb_board
                 WHERE section = 'K' AND NOT use_yn = 'D'
			"""

            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                query += "and " + title + " like '%" + search + "%'"
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            index = 1
            for news in row:
                value_list = []
                k_news = news
                # print 'news == ',news
                value_list.append(k_news[0])
                value_list.append(index)
                value_list.append(k_news[6])
                value_list.append(k_news[2])
                value_list.append(k_news[1])
                value_list.append(k_news[3])
                value_list.append(k_news[4])
                value_list.append(k_news[5])
                value_list.append(k_news[7])
                knews_list.append(value_list)
                index += 1

            aaData = json.dumps(list(knews_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'knews_del':
            noti_id = request.GET['noti_id']
            use_yn = request.GET['use_yn']
            yn = ''
            if use_yn == 'Y':
                yn = 'N'
            else:
                yn = 'Y'
            print 'use_yn == ', use_yn, ' yn == ', yn
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + noti_id
            print 'query == ', query
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        elif request.GET['method'] == 'knews_delete':
            noti_id = request.GET['noti_id']
            use_yn = request.GET['use_yn']
            yn = 'D'

            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + noti_id
            print 'query == ', query
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        return HttpResponse(aaData, 'applications/json')

    return render(request, 'community/comm_k_news.html')


def new_knews(request):
    if 'file' in request.FILES:
        value_list = []
        file = request.FILES['file']
        filename = ''
        file_ext = ''
        file_size = ''
        # print file
        filename = file._name
        file_ext = filename.split('.')[1]

        fp = open('%s/%s' % (UPLOAD_DIR, filename), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        data = '성공'

        n = os.path.getsize(UPLOAD_DIR + filename)
        file_size = str(n / 1024) + "KB"  # 킬로바이트 단위로

        value_list.append(filename)
        value_list.append(file_ext)
        value_list.append(file_size)
        data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    elif request.method == 'POST':
        data = json.dumps({'status': "fail", 'msg': "오류가 발생했습니다"})
        if request.POST['method'] == 'add':

            title = request.POST.get('knews_title')
            content = request.POST.get('knews_content')
            section = request.POST.get('k_news')
            head_title = request.POST.get('head_title')
            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')
            # print file_name,'/',file_ext,'/',file_size
            # print 'head_title == ',head_title
            print 'content == ', content

            cur = connection.cursor()
            query = "insert into edxapp.tb_board(subject, content, section, head_title)"
            query += " VALUES ('" + title + "', '" + content + "', '" + section + "', '" + head_title + "') "
            cur.execute(query)

            query2 = "select board_id from tb_board where subject ='" + title + "' and content='" + content + "'"
            cur.execute(query2)
            board_id = cur.fetchall()
            cur.close()
            # print board_id[0][0]
            if upload_file != '':
                cur = connection.cursor()
                query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
                        "VALUES ('" + str(board_id[0][0]) + "','" + str(file_name) + "','" + str(
                    file_ext) + "','" + str(file_size) + "')"
                cur.execute(query)
                cur.close()

            data = json.dumps({'status': "success"})

        elif request.POST['method'] == 'modi':
            title = request.POST.get('k_news_title')
            content = request.POST.get('k_news_cont')
            noti_id = request.POST.get('k_news_id')
            odby = request.POST.get('odby')
            head_title = request.POST.get('head_title')
            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')

            cur = connection.cursor()

            print 'param check s --------------------------'
            print 'title:', title
            print 'content:', content
            print 'odby:', odby
            print 'head_title:', head_title
            print 'noti_id:', noti_id
            print 'param check e --------------------------'

            query = '''
                UPDATE edxapp.tb_board
                   SET subject = '{title}',
                       content = '{content}',
                       odby = '{odby}',
                       mod_date = now(),
                       head_title = '{head_title}'
                 WHERE board_id = '{noti_id}'

            '''.format(
                title=title,
                content=content,
                odby=odby,
                head_title=head_title,
                noti_id=noti_id
            )

            print 'query:', query

            cur.execute(query)

            cur.close()

            print query

            print 'str(file_ext) == ', str(file_ext)
            if upload_file != '':
                cur = connection.cursor()
                query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
                        "VALUES ('" + str(noti_id) + "','" + str(file_name) + "','" + str(file_ext) + "','" + str(
                    file_size) + "')"
                cur.execute(query)
                cur.close()
            data = json.dumps({'status': "success"})

        return HttpResponse(data, 'applications/json')
    return render(request, 'community/comm_newknews.html')


def modi_knews(request, id, use_yn):
    mod_knews = []
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            # query = "SELECT subject, content, odby from tb_board WHERE section = 'K' and board_id = "+id
            query = """
					SELECT subject,
						   content,
						   odby,
						   CASE
							  WHEN head_title = 'k_news_k' THEN 'K-MOOC소식'
							  WHEN head_title = 'report_k' THEN '보도자료'
							  WHEN head_title = 'u_news_k' THEN '대학뉴스'
							  WHEN head_title = 'support_k' THEN '서포터즈이야기'
							  WHEN head_title = 'n_new_k' THEN 'NILE소식'
							  WHEN head_title = 'etc_k' THEN '기타'
							  ELSE ''
						   END
							  head_title
					  FROM tb_board
					 WHERE section = 'K' and board_id = """ + id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            # print 'query', query

            cur = connection.cursor()
            query = "select attatch_file_name from tb_board_attach where board_id = " + id
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            # print id
            # print 'files == ',files
            # print row
            mod_knews.append(row[0][0])
            mod_knews.append(row[0][1])
            mod_knews.append(row[0][2])
            mod_knews.append(row[0][3])
            if files:
                mod_knews.append(files)
            data = json.dumps(list(mod_knews), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'file_download':
            file_name = request.GET['file_name']
            # print 'file_name == ',file_name
            data = json.dumps(UPLOAD_DIR + file_name, cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(data, 'applications/json')

    variables = RequestContext(request, {
        'id': id,
        'use_yn': use_yn
    })

    return render_to_response('community/comm_modi_knews.html', variables)


def comm_faq(request):
    faq_list = []
    data = json.dumps({'status': "fail"})
    if request.is_ajax():
        if request.GET['method'] == 'faq_list':
            aaData = {}
            cur = connection.cursor()
            query = """
					SELECT board_id,
						   content,
						   subject,
						   SUBSTRING(reg_date, 1, 11),
						   CASE
							  WHEN use_yn = 'Y' THEN '보임'
							  WHEN use_yn = 'N' THEN '숨김'
							  ELSE ''
						   END
							  use_yn,
						   CASE
							  WHEN head_title = 'kmooc_f' THEN 'K-MOOC'
							  WHEN head_title = 'regist_f ' THEN '회원가입'
							  WHEN head_title = 'login_f ' THEN '로그인/계정'
							  WHEN head_title = 'enroll_f ' THEN '수강신청/취소'
							  WHEN head_title = 'course_f ' THEN '강좌수강'
							  WHEN head_title = 'certi_f  ' THEN '성적/이수증'
							  WHEN head_title = 'tech_f ' THEN '기술적문제'
							  WHEN head_title = 'mobile_f ' THEN '모바일문제'
							  ELSE ''
						   END
							  head_title,
						   use_yn
					  FROM tb_board
					 WHERE section = 'F' AND NOT use_yn = 'D'
			"""
            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                query += "and " + title + " like '%" + search + "%'"

            # query += " ORDER BY board_id"

            # print 'query', query

            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            index = 1
            for f in row:
                value_list = []
                faq = f
                # print faq
                value_list.append(faq[0])
                value_list.append(index)
                value_list.append(faq[5])
                value_list.append(faq[2])
                value_list.append(faq[1])
                value_list.append(faq[3])
                value_list.append(faq[4])
                value_list.append(faq[6])
                faq_list.append(value_list)
                index += 1
            # print 'faq_list == ',faq_list
            aaData = json.dumps(list(faq_list), cls=DjangoJSONEncoder, ensure_ascii=False)
            return HttpResponse(aaData, 'applications/json')

        elif request.GET['method'] == 'faq_del':
            faq_id = request.GET['faq_id']
            use_yn = request.GET['use_yn']
            yn = ''
            if use_yn == 'Y':
                yn = 'N'
            else:
                yn = 'Y'
            # print 'use_yn == ',use_yn,' yn == ',yn
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + faq_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
            return HttpResponse(aaData, 'applications/json')
        elif request.GET['method'] == 'faq_delete':
            faq_id = request.GET['faq_id']
            use_yn = request.GET['use_yn']
            yn = 'D'

            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + faq_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
            return HttpResponse(aaData, 'applications/json')

        # elif request.GET['method'] == 'total_page':
        # 	if 'search_con' in request.GET:
        # 		subject = request.GET['search_con']
        # 		search = request.GET['search_search']
        # 		cur = connection.cursor()
        # 		cur.execute('''
        # 		select ceil(count(board_id)/10) from tb_board where section="F" and '''+subject+''' like "%'''+search+'''%"
        # 		''')
        # 		row = cur.fetchall()
        # 		cur.close()
        # 	else:
        # 		cur =connection.cursor()
        # 		cur.execute('''
        # 		select ceil(count(board_id)/10) from tb_board where section="F"
        # 		''')
        # 		row =cur.fetchall()
        # 		cur.close()
        # 	data = json.dumps(list(row), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    return render(request, 'community/comm_faq.html')


def new_faq(request):
    if request.method == 'POST':
        data = json.dumps({'status': "fail"})
        if request.POST.get('method') == 'add':
            head_title = request.POST.get('head_title')
            faq_question = request.POST.get('faq_question')
            faq_question = faq_question.replace("'", "''")
            faq_answer = request.POST.get('faq_answer')
            faq_answer = faq_answer.replace("'", "''")
            section = request.POST.get('section')

            print 'head_title == ', head_title, ' faq_question == ', faq_question, ' faq_answer == ', faq_answer, ' section == ', section
            cur = connection.cursor()
            query = "insert into edxapp.tb_board(subject, content, section, head_title)"
            query += " VALUES ('" + faq_question + "', '" + faq_answer + "', '" + section + "', '" + head_title + "') "
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})

        if request.POST['method'] == 'modi':
            question = request.POST.get('faq_question')
            question = question.replace("'", "''")
            answer = request.POST.get('faq_answer')
            answer = answer.replace("'", "''")
            head_title = request.POST.get('head_title')
            faq_id = request.POST.get('faq_id')
            cur = connection.cursor()
            query = "update edxapp.tb_board set subject = '" + question + "', content = '" + answer + "', head_title = '" + head_title + "', mod_date = now() where board_id = '" + faq_id + "'"
            cur.execute(query)
            cur.close()
            data = json.dumps({'status': "success"})
        return HttpResponse(data, 'applications/json')

    return render(request, 'community/comm_newfaq.html')


def modi_faq(request, id, use_yn):
    mod_faq = []
    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            query = """
					SELECT subject,
						   content,
						   CASE
							  WHEN head_title = 'kmooc_f' THEN 'K-MOOC'
							  WHEN head_title = 'regist_f ' THEN '회원가입'
							  WHEN head_title = 'login_f ' THEN '로그인/계정'
							  WHEN head_title = 'enroll_f ' THEN '수강신청/취소'
							  WHEN head_title = 'course_f ' THEN '강좌수강'
							  WHEN head_title = 'certi_f  ' THEN '성적/이수증'
							  WHEN head_title = 'tech_f ' THEN '기술적문제'
							  WHEN head_title = 'mobile_f ' THEN '모바일문제'
							  ELSE ''
						   END
							  head_title
					  FROM tb_board
					 WHERE board_id = """ + id
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            print 'query', query
            for f in row:
                faq = f
                mod_faq.append(faq)
            data = json.dumps(list(mod_faq), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    variables = RequestContext(request, {
        'id': id,
        'use_yn': use_yn
    })

    return render_to_response('community/comm_modifaq.html', variables)


def comm_faqrequest(request):
    if request.is_ajax():
        aaData = json.dumps({'status': "fail"})
        f_request_list = []
        if request.GET['method'] == 'faqrequest_list':
            cur = connection.cursor()
            query = """
					SELECT id,
						   head_title,
						   question,
						   student_email,
						   response_email,
						   SUBSTRING(reg_date, 1, 11)
					  FROM faq_request;
			"""
            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            index = 1
            for fr in row:
                value_list = []
                faq_request = fr
                value_list.append(faq_request[0])
                value_list.append(index)
                value_list.append(faq_request[1])
                value_list.append(faq_request[2])
                value_list.append(faq_request[3])
                value_list.append(faq_request[4])
                value_list.append(faq_request[5])
                f_request_list.append(value_list)
                index += 1
            aaData = json.dumps(list(f_request_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(aaData, 'applications/json')
    return render_to_response('community/comm_faqrequest.html')


def comm_reference_room(request):
    refer_list = []
    if request.is_ajax():
        aaData = {}
        if request.GET['method'] == 'refer_list':
            cur = connection.cursor()
            query = """
					SELECT board_id,
						   use_yn,
						   CASE
							  WHEN head_title = 'publi_r' THEN '홍보자료'
							  WHEN head_title = 'data_r' THEN '자료집'
							  WHEN head_title = 'repo_r' THEN '보고서'
							  WHEN head_title = 'etc_r' THEN '기타'
							  ELSE ''
						   END
							  head_title,
						   subject,
						   SUBSTRING(reg_date, 1, 11),
						   CASE
							  WHEN use_yn = 'Y' THEN '보임'
							  WHEN use_yn = 'N' THEN '숨김'
							  ELSE ''
						   END
							  use_yn,
						   CASE WHEN odby = '0' THEN '' ELSE odby END odby
					  FROM tb_board
					 WHERE section = 'R' AND NOT use_yn = 'D'
			"""
            if 'search_con' in request.GET:
                title = request.GET['search_con']
                search = request.GET['search_search']
                query += "and " + title + " like '%" + search + "%'"

            # query += " ORDER BY board_id"

            # print 'query', query

            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            index = 1
            for r in row:
                value_list = []
                refer = r
                # print 'row == ',row
                value_list.append(refer[0])
                value_list.append(refer[1])
                value_list.append(index)
                value_list.append(refer[2])
                value_list.append(refer[3])
                value_list.append(refer[4])
                value_list.append(refer[5])
                refer_list.append(value_list)
                index += 1

            aaData = json.dumps(list(refer_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'refer_del':
            refer_id = request.GET['refer_id']
            use_yn = request.GET['use_yn']
            yn = ''
            if use_yn == 'Y':
                yn = 'N'
            else:
                yn = 'Y'
            # print 'use_yn == ',use_yn,' yn == ',yn
            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + refer_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')
        elif request.GET['method'] == 'refer_delete':
            refer_id = request.GET['refer_id']
            use_yn = request.GET['use_yn']
            yn = 'D'

            cur = connection.cursor()
            query = "update edxapp.tb_board SET use_yn = '" + yn + "' where board_id = " + refer_id
            cur.execute(query)
            cur.close()
            aaData = json.dumps('success')

        return HttpResponse(aaData, 'applications/json')
    return render(request, 'community/comm_reference_room.html')


def new_refer(request):
    if 'file' in request.FILES:
        value_list = []
        file = request.FILES['file']
        filename = ''
        file_ext = ''
        file_size = ''
        # print file
        filename = file._name
        file_ext = filename.split('.')[1]

        fp = open('%s/%s' % (UPLOAD_DIR, filename), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        data = '성공'

        n = os.path.getsize(UPLOAD_DIR + filename)
        file_size = str(n / 1024) + "KB"  # 킬로바이트 단위로

        value_list.append(filename)
        value_list.append(file_ext)
        value_list.append(file_size)
        data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    elif request.method == 'POST':
        data = json.dumps({'status': "fail", 'msg': "오류가 발생했습니다"})
        if request.POST['method'] == 'add':

            title = request.POST.get('refer_title')
            title = title.replace("'", "''")
            content = request.POST.get('refer_cont')
            content = content.replace("'", "''")
            section = request.POST.get('refer')
            head_title = request.POST.get('head_title')
            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')
            # print file_name,'/',file_ext,'/',file_size

            cur = connection.cursor()
            query = "insert into edxapp.tb_board(subject, content, section, head_title)"
            query += " VALUES ('" + title + "', '" + content + "', '" + section + "', '" + head_title + "') "
            cur.execute(query)

            query2 = "select board_id from tb_board where subject ='" + title + "' and content='" + content + "'"
            cur.execute(query2)
            board_id = cur.fetchall()
            cur.close()
            # print board_id[0][0]
            if upload_file != '':
                cur = connection.cursor()
                query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
                        "VALUES ('" + str(board_id[0][0]) + "','" + str(file_name) + "','" + str(
                    file_ext) + "','" + str(file_size) + "')"
                cur.execute(query)
                cur.close()

            data = json.dumps({'status': "success"})

        elif request.POST['method'] == 'modi':
            title = request.POST.get('refer_title')
            title = title.replace("'", "''")
            content = request.POST.get('refer_cont')
            content = content.replace("'", "''")
            refer_id = request.POST.get('refer_id')
            odby = request.POST.get('odby')
            head_title = request.POST.get('head_title')
            upload_file = request.POST.get('uploadfile')
            file_name = request.POST.get('file_name')
            file_ext = request.POST.get('file_ext')
            file_size = request.POST.get('file_size')

            cur = connection.cursor()
            # query = "update edxapp.tb_board set subject = '"+title+"', content = '"+content+"', odby = '"+odby+"' where board_id = '"+noti_id+"'"
            query = "update edxapp.tb_board set subject = '" + title + "', content = '" + content + "', mod_date = now(), head_title = '" + head_title + "' where board_id = '" + refer_id + "'"
            cur.execute(query)
            cur.close()

            if upload_file != '':
                cur = connection.cursor()
                query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
                        "VALUES ('" + str(refer_id) + "','" + str(file_name) + "','" + str(file_ext) + "','" + str(
                    file_size) + "')"
                cur.execute(query)
                cur.close()
            data = json.dumps({'status': "success"})

        return HttpResponse(data, 'applications/json')
    return render(request, 'community/comm_newrefer.html')


def modi_refer(request, id, use_yn):
    mod_refer = []

    if request.is_ajax():
        data = json.dumps({'status': "fail"})
        if request.GET['method'] == 'modi':
            cur = connection.cursor()
            # query = "SELECT subject, content, odby, head_title from tb_board WHERE section = 'R' and board_id = "+id
            query = """
					SELECT subject,
						   content,
						   odby,
						   CASE
							  WHEN head_title = 'publi_r' THEN '홍보자료'
							  WHEN head_title = 'data_r' THEN '자료집'
							  WHEN head_title = 'repo_r' THEN '보고서'
							  WHEN head_title = 'etc_r' THEN '기타'
							  ELSE ''
						   END
							  head_title
					  FROM tb_board
					 WHERE section = 'R' AND board_id = """ + id

            cur.execute(query)
            row = cur.fetchall()
            cur.close()
            # print 'query', query

            cur = connection.cursor()
            query = "select attatch_file_name from tb_board_attach where board_id = " + id
            cur.execute(query)
            files = cur.fetchall()
            cur.close()
            # print 'files == ',files

            mod_refer.append(row[0][0])
            mod_refer.append(row[0][1])
            mod_refer.append(row[0][2])
            mod_refer.append(row[0][3])
            if files:
                mod_refer.append(files)
            # print 'mod_knews == ',mod_refer
            data = json.dumps(list(mod_refer), cls=DjangoJSONEncoder, ensure_ascii=False)
        elif request.GET['method'] == 'file_download':
            file_name = request.GET['file_name']
            # print 'file_name == ',file_name
            data = json.dumps(UPLOAD_DIR + file_name, cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(data, 'applications/json')

    variables = RequestContext(request, {
        'id': id,
        'use_yn': use_yn
    })

    return render_to_response('community/comm_modirefer.html', variables)


# RSA 설정 필요
# monitoring view
def moni_storage(request):
    if request.is_ajax():
        if request.GET['method'] == 'storage_list':
            aaData = {}
            data_list = []
            a = commands.getoutput('df -h /video')
            a_list = [1, a.split()[7], a.split()[9], a.split()[10], a.split()[11]]
            data_list.append(a_list)
            # print 'data_list == ',data_list
            aaData = json.dumps(list(data_list), cls=DjangoJSONEncoder, ensure_ascii=False)
        return HttpResponse(aaData, 'applications/json')
    return render(request, 'monitoring/moni_storage.html')


@csrf_exempt
def summer_upload(request):
    if 'file' in request.FILES:
        file = request.FILES['file']
        filename = file._name
        fp = open('%s/%s' % (UPLOAD_DIR, filename), 'wb')

        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        # return HttpResponse('http://192.168.33.15:8000/home/static/excel/notice_file/'+filename)
        return HttpResponse('/manage/home/static/upload/' + filename)
    return HttpResponse('fail')


def history(request):
    if request.is_ajax():
        pageNo = request.POST.get('pageNo')
        pageLength = request.POST.get('pageLength')
        startNo = 0

        system = request.POST.get('system')
        operation = request.POST.get('operation')
        function = request.POST.get('function')
        function_detail = request.POST.get('function_detail')
        user = request.POST.get('user')
        target = request.POST.get('target')
        # search_string = urllib.quote('검색').encode('utf8')

        if pageLength == '-1':
            pageLength = '999999'
        else:
            startNo = int(pageNo) * int(pageLength)

        with connections['default'].cursor() as cur:
            query1 = """
                SELECT SQL_CALC_FOUND_ROWS b.content_type_id, b.id, date_format(b.action_time, '%Y/%m/%d %H:%i:%s') action_time,
                         a.app_label,
                         b.user_id,
                         (select username from auth_user where id = b.user_id) username,
                         b.object_repr,
                         b.change_message,
                         b.action_flag
                    FROM django_content_type a, django_admin_log b, auth_user c
                   WHERE     a.id = b.content_type_id
                             and b.user_id = c.id
                         AND (a.app_label = 'auth' OR a.model = 'custom')
                         and b.id > 247
            """

            if system:
                if system == 'a':
                    query1 += " and a.id = 3 "
                elif system == 'k':
                    query1 += " and a.id not in (3, 311) "
                elif system == 'i':
                    query1 += " and a.id = 311 "

            if operation is not None:
                print '1'
                query1 += " and b.action_flag = %s " % operation

            if function is not None:
                print '2'
                query1 += " and a.id = %s " % operation

            if function_detail is not None:
                print '3'
                query1 += " and b.action_flag = %s " % operation

            if user is not None:
                print '4'
                query1 += " and (c.id = {user} or c.username = {user})".format(user=user)

            if target is not None:
                print '5'
                query1 += " and b.action_flag = %s " % operation

            query2 = """
                ORDER BY b.action_time DESC
                   LIMIT {startNo}, {pageLength}
            """.format(startNo=startNo, pageLength=pageLength)

            query = query1 + query2

            print 'query:', query
            print startNo, pageLength

            cur.execute(query)
            rows = cur.fetchall()
            columns = [col[0] for col in cur.description]

            cur.execute('SELECT found_rows();')
            recordsTotal = cur.fetchone()[0]

            print 'recordsTotal:', recordsTotal

            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(connection.queries)

        result = dict()
        # result_list = [dict(zip(columns, (content_type_dict[col] if idx == 0 and col in content_type_dict else col for idx, col in enumerate(row)))) for row in rows]
        result_list = [dict(zip(columns, (str(col) for col in row))) for row in rows]

        '''
        content_type_id 에 따른 기능 구분 추가
        [306]강좌 운영팀 관리 (운영팀 - staff, 교수자 - instructor, 베타 테스터 - beta)
        [295]강좌 운영팀 관리 (게시판 관리자 - Administrator, 토의 진행자 - Moderator, 게시판 조교 - Community TA)
        :param request:
        :return:
        '''

        # 기능 구분 값 한글화

        for result_dict in result_list:
            content_type_id = result_dict['content_type_id']
            change_message_dict = get_change_message_dict(result_dict['change_message'])
            object_repr_dict = get_object_repr_dict(result_dict['object_repr'])

            # 기능 구분에 따라 시스템 표시 구분
            result_dict['system'] = get_system_name(content_type_id)
            # 기능 구분에 따라 상세구분 표시 내용 추가
            result_dict['content_type_detail'] = get_content_detail(content_type_id, object_repr_dict, change_message_dict)

            result_dict['search_string'] = get_searcy_string(content_type_id, change_message_dict)

            result_dict['content_type_id'] = content_type_dict[content_type_id]

            result_dict['action_flag'] = action_flag_dict[result_dict['action_flag']]

            result_dict['ip'] = change_message_dict['ip'] if 'ip' in change_message_dict else '-'

            result_dict['cnt'] = change_message_dict['count'] if 'count' in change_message_dict and content_type_id not in ['303', '304'] else '-'

        result['data'] = result_list
        result['recordsTotal'] = recordsTotal
        result['recordsFiltered'] = recordsTotal

        context = json.dumps(result, cls=DjangoJSONEncoder, ensure_ascii=False)

        return HttpResponse(context, 'applications/json')

    else:
        return render(request, 'history/history.html')


def get_content_detail(content_type_id, object_repr_dict, change_message_dict):
    if not content_type_id:
        return ''
    elif content_type_id == '3':
        # auth_user
        pass
    elif content_type_id == '297':
        # file downlaod

        print object_repr_dict

        return object_repr_dict['filename']
    elif content_type_id in ['295', '306']:
        # role
        rolename_en = object_repr_dict['rolename']
        if rolename_en == 'staff':
            rolename = '운영팀'
        elif rolename_en == 'instructor':
            rolename = '교수자'
        elif rolename_en == 'beta':
            rolename = '베타 테스터'
        elif rolename_en == 'Administrator':
            rolename = '게시판 관리자'
        elif rolename_en == 'Moderator':
            rolename = '토의 게시자'
        elif rolename_en == 'Community TA':
            rolename = '게시판 커뮤니티 조교'
        else:
            print 'rolename_en:', rolename_en
            rolename = ''
        return rolename
    else:
        pass

    return ''


def get_system_name(content_type_id):
    if content_type_id in ['3', ]:
        system = 'admin'
    elif content_type_id in ['310', ]:
        system = 'insight'
    else:
        system = 'k-mooc'
    return system


def get_change_message_dict(change_message):
    try:
        change_message_dict = ast.literal_eval(change_message)
    except:
        try:
            temp_string = change_message[:change_message.find('query') - 1] + change_message[
                                                                              change_message.find('>') + 2:]
            change_message_dict = ast.literal_eval(temp_string)
        except Exception as e:
            change_message_dict = dict()
            print 'Exception:', e, change_message
    finally:
        return change_message_dict


def get_object_repr_dict(object_repr):
    object_repr_temp = object_repr[object_repr.find('[') + 1:].replace(']', '')
    list1 = object_repr_temp.split(';')
    result = dict()
    for l1 in list1:
        list2 = l1.split(':')
        # print 'len(list2) = ', len(list2)
        if len(list2) == 1:
            result[list2[0]] = list2[0]
        else:
            result[list2[0]] = list2[1]
    return result


def get_searcy_string(content_type_id, change_message_dict):
    if content_type_id == '292' and 'query' in change_message_dict:
        search_query = urllib.unquote(change_message_dict['query']).decode('utf8')
        search_query = search_query.split('=')[1] if search_query else ''
    else:
        search_query = ''
    return search_query


action_flag_dict = {
    '0': u'조회',
    '1': u'생성',
    '2': u'수정',
    '3': u'삭제',
}
content_type_dict = {
    '0': u'조회',
    '1': u'회원권한 수정',
    '2': u'회원그룹 수정',
    '3': u'회원정보 수정',
    '291': u'회원 정보 상세',
    '292': u'회원 정보 리스트',
    '293': u'베타 테스터',
    '294': u'성적 보고서',
    '295': u'강좌 운영팀 관리',
    '296': u'ORA 데이터 보고 생성하기',
    '297': u'파일 다운로드',
    '298': u'익명 학습자 아이디 CSV 파일',
    '299': u'발급된 이수증 조회',
    '300': u'발급된 이수증 CSV 파일',
    '301': u'문제 답변 CSV 파일 다운로드',
    '302': u'학습자의 진도 페이지 조회',
    '303': u'등록된 학습자의 프로필 목록',
    '304': u'개인정보를 CSV 파일로 다운로드',
    '305': u'등록할 수 있는 학습자의 CSV 다운로드',
    '306': u'강좌 운영팀 관리',
    '307': u'문항 성적 보고서 생성',
    '308': u'문제 풀이 횟수 설정 초기화',
    '309': u'학습 집단 추가',
    '310': u'',
    '311': u'인사이트 조회',
}
