# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, redirect
from django.template import Context, RequestContext
from django.http import Http404, HttpResponse
from django.utils import timezone
import json
from django.db import connection
from management.settings import UPLOAD_DIR
from django.core.serializers.json import DjangoJSONEncoder
from management.settings import dic_univ,database_id,debug
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime


import subprocess
import sys


# Create your views here.

# stastic view
def stastic_index(request):
	return render(request, 'stastic/stastic_index.html')

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
		data=json.dumps({'status':"fail"})
		if request.GET['method'] == 'org':
			data = json.dumps(dic_univ, cls=DjangoJSONEncoder, ensure_ascii=False)

		elif request.GET['method'] == 'course':
			course_list=[]
			org = request.GET['org']
			cur = connection.cursor()

			query = "select course_id from certificates_generatedcertificate where course_id like '%"+org+"%' group by course_id"
			cur.execute(query)
			course = cur.fetchall()
			cur.close()

			for c in course:
				value_list = []

				print "c[0]",c[0]
				course_id = c[0]

				cid = course_id.split('+')[1]
				run = course_id.split('+')[2]
				cursor = db.modulestore.active_versions.find_one({'course':cid, 'run':run})
				pb = cursor.get('versions').get('published-branch')

				cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},{"blocks":{"$elemMatch":{"block_type":"course"}}})
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
			cursor = db.modulestore.active_versions.find({'versions.published-branch':ObjectId(course_pb)})

			for document in cursor:
				run = document.get('run')
				print 'run', run
			cursor.close()
			data = json.dumps(run, cls=DjangoJSONEncoder, ensure_ascii=False)
		elif request.GET['method'] == 'certificate':
			course_pb = request.GET['course_id']
			run = request.GET['run']
			course = ''
			cursor = db.modulestore.active_versions.find({'versions.published-branch':ObjectId(course_pb)})
			for document in cursor:
				course = document.get('course')
			print 'course', course
			cursor.close()

			cur = connection.cursor()
			query = "SELECT DISTINCT course_id FROM certificates_generatedcertificate WHERE course_id LIKE '%"+course+"%' AND course_id LIKE '%"+run+"%'"
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
			query = "select course_id from certificates_generatedcertificate where course_id like '%"+org_id+"%' and course_id like '%"+run+"%' group by course_id"
			cur.execute(query)
			course = cur.fetchall()
			cur.close()

			for c in course:
				value_list = []
				print "c[0]",c[0]
				course_id = c[0]

				cid = course_id.split('+')[1]
				run = course_id.split('+')[2]
				print org_id,'/',cid,'/',run

				cursor = db.modulestore.active_versions.find_one({'course':cid, 'run':run})
				pb = cursor.get('versions').get('published-branch')

				cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},{"blocks":{"$elemMatch":{"block_type":"course"}}})
				course_end = cursor.get('blocks')[0].get('fields').get('end')  # course_names
				end_date = datetime.datetime.strptime(str(course_end)[0:10], "%Y-%m-%d").date()
				today = datetime.date.today()

				if end_date > today:
					data=json.dumps('Error')
				else:
					print '-----ready make certificate !!-----'
					subprocess.call('ssh vagrant@192.168.33.12 ./test.sh '+org_id+' '+cid+' '+run+'', shell=True)
					print '-----end create certificate !!-----'
					data = json.dumps('Success')
		elif request.GET['method'] == 'uni_certi' :
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
				query+="WHERE course_id like '%"+request.GET['org_id']+"%'"
			if 'run' in request.GET:
				query+=" and course_id LIKE '%"+request.GET['run']+"%'"
			query+="GROUP BY course_id ORDER BY created_date DESC"
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
				cer_per = (downcnt/cnt)*100
				cer_percent = round(cer_per,2)

				# db.modulestore.active_versions --------------------------------------
				cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
				pb = cursor.get('versions').get('published-branch')
				# course_orgs
				course_orgs[course_id] = cursor.get('org')

				# db.modulestore.structures --------------------------------------
				cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},{"blocks":{"$elemMatch":{"block_type":"course"}}})

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
	if request.is_ajax() :
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
				query+="WHERE course_id like '%"+org_id+"%'"
			if 'run' in request.GET:
				query+=" and course_id LIKE '%"+run+"%'"
			query+="GROUP BY course_id"
			cur.execute(query)
			course_list = cur.fetchall()
			cur.close()

			for c in course_list:
				value_list = []
				course_id = c
				cid = c[0].split('+')[1]
				course = org_id+'+'+cid+'+'+run
				cur = connection.cursor()
				# print dic_univ[org_id], cid, run, course
				query = """
						select @RNUM := @RNUM + 1 AS NO, a.name, b.email,'"""+dic_univ[org_id]+"""' org, '"""+cid+"""' course, '"""+run+"""' run,
							   case when a.status = 'downloadable' then '생성완료'
									when a.status = 'notpassing' then '생성 전'
									when a.status = 'generated' then '생성오류' else '' end status
						  from ( SELECT @RNUM := 0 ) c, certificates_generatedcertificate a inner join auth_user b
							on (a.user_id = b.id)
						 where a.course_id like '%"""+str(course)+"""%'
						 limit 2000
 				"""

				cur.execute(query)
				row = cur.fetchall()
				cur.close()
				# print str(row)

			data = json.dumps(list(row), cls=DjangoJSONEncoder, ensure_ascii=False)
		elif request.GET['method'] == 'email_search':
			course = ""
			user_list=[]

			email = request.GET['email']
			cur = connection.cursor()
			query = """
					select course_id, email
					from certificates_generatedcertificate a inner join auth_user b
					on a.user_id = b.id
					where b.email like '%"""+email+"""%'
			"""
			if 'org_id' in request.GET:
				query+="and a.course_id like '%"+request.GET['org_id']+"%'"
			if 'run' in request.GET:
				query+=" and a.course_id LIKE '%"+request.GET['run']+"%'"
			cur.execute(query)
			course_list = cur.fetchall()
			cur.close()
			i=1
			for c, email in course_list:
				value_list=[]
				course_id = c
				org_start= c.find(':')+1
				org_end = c.find('+', org_start)
				org = c[org_start:org_end]
				cid = c.split('+')[1]
				run = c.split('+')[2]

				cur = connection.cursor()
				# print dic_univ[org_id], cid, run, course
				query = """
						select a.name, b.email,'"""+dic_univ[org]+"""' org, '"""+cid+"""' course, '"""+run+"""' run,
							   case when a.status = 'downloadable' then '생성완료'
									when a.status = 'notpassing' then '생성 전'
									when a.status = 'generated' then '생성오류' else '' end status
						  from ( SELECT @RNUM := 0 ) c, certificates_generatedcertificate a inner join auth_user b
							on (a.user_id = b.id)
						 where b.email like '%"""+email+"""%'

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
				i+=1

			data = json.dumps(list(user_list), cls=DjangoJSONEncoder, ensure_ascii=False)


		return HttpResponse(data, 'applications/json')

	return render(request,'certificate/per_certificate.html')

def uni_certificate(request):
	return render(request,'certificate/uni_certificate.html')

# community view
def comm_notice(request):
	noti_list = []
	if request.is_ajax():
		aaData={}
		if request.GET['method'] == 'notice_list':
			cur = connection.cursor()
			query = "SELECT board_id, use_yn yn, subject, SUBSTRING(reg_date,1,11)," \
					"case when use_yn = 'Y' then '보임'" \
					"	  when use_yn = 'N' then '숨김'" \
					"	  else '' end use_yn," \
					"case when odby = '0' then ''" \
					"	  else odby end odby " \
					"FROM tb_board WHERE section ='N' "
			if 'search_con' in request.GET :
				title = request.GET['search_con']
				search = request.GET['search_search']
				query += "and "+title+" like '%"+search+"%'"

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
				value_list.append(notice[1])
				value_list.append(index)
				value_list.append(notice[2])
				value_list.append(notice[3])
				value_list.append(notice[4])
				value_list.append(notice[5])
				noti_list.append(value_list)
				index+=1

			aaData = json.dumps(list(noti_list), cls=DjangoJSONEncoder, ensure_ascii=False)
		elif request.GET['method'] == 'notice_del' :
			noti_id = request.GET['noti_id']
			use_yn = request.GET['use_yn']
			yn = ''
			if use_yn == 'Y':
				yn='N'
			else:
				yn='Y'
			# print 'use_yn == ',use_yn,' yn == ',yn
			cur = connection.cursor()
			query = "update edxapp.tb_board SET use_yn = '"+yn+"' where board_id = "+noti_id
			cur.execute(query)
			cur.close()
			aaData = json.dumps('success')
		elif request.GET['method'] == 'file_upload' :
			print 'file_upload'
		return HttpResponse(aaData,'applications/json')

	return render(request, 'community/comm_notice.html')

def new_notice(request):
	if 'file' in request.FILES:
		file = request.FILES['file']
		print file
		filename = file._name

		fp = open('%s/%s' % ('home/static/excel/', filename) , 'wb')
		for chunk in file.chunks():
			fp.write(chunk)
		fp.close()

		data ='성공'

		print data

	elif request.method == 'POST':
		data = json.dumps({'status':"fail", 'msg':"오류가 발생했습니다"})
		if request.POST['method'] == 'add':
			title = request.POST.get('nt_title')
			content = request.POST.get('nt_cont')
			section = request.POST.get('notice')

			cur = connection.cursor()
			query = "insert into edxapp.tb_board(subject, content, section)"
			query +=" VALUES ('"+title+"', '"+content+"', '"+section+"') "
			cur.execute(query)
			cur.close()
			data = json.dumps({'status' : "success"})

		elif request.POST['method'] == 'modi':
			title = request.POST.get('nt_title')
			content = request.POST.get('nt_cont')
			noti_id = request.POST.get('noti_id')
			odby = request.POST.get('odby')

			cur = connection.cursor()
			query = "update edxapp.tb_board set subject = '"+title+"', content = '"+content+"', odby = '"+odby+"' where board_id = '"+noti_id+"'"


			cur.execute(query)
			cur.close()
			data = json.dumps({'status' : "success"})

		return HttpResponse(data, 'applications/json')
	return render(request, 'community/comm_newnotice.html')

def file_upload(request):
	if 'file' in request.FILES:
		print 'ddddddd'
		file = request.FILES['file']
		print file
		filename = file._name
		fp = open('%s/%s' % ('home/static/excel/', filename) , 'wb')
		for chunk in file.chunks():
			fp.write(chunk)
		fp.close()

		data ='성공'

		print data

	return HttpResponse('application/json')


def modi_notice(request, id, use_yn):
	mod_notice = []

	if request.is_ajax():
		data=json.dumps({'status':"fail"})
		if request.GET['method'] == 'modi':
			cur = connection.cursor()
			query = "SELECT subject, content, odby from tb_board WHERE board_id = "+id
			cur.execute(query)
			row = cur.fetchall()
			cur.close()
			# print 'query', query

			for n in row :
				notice = n
				print notice
				mod_notice.append(notice)

		data = json.dumps(list(mod_notice), cls=DjangoJSONEncoder, ensure_ascii=False)
		return HttpResponse(data, 'applications/json')


	variables = RequestContext(request, {
		'id' : id,
		'use_yn' : use_yn
    })

	return render_to_response('community/comm_modinotice.html',variables)


def comm_faq(request):
	faq_list = []
	data=json.dumps({'status':"fail"})
	if request.is_ajax():
		if request.GET['method'] == 'faq_list':
			aaData={}
			cur = connection.cursor()
			query = "SELECT board_id, use_yn yn, subject, SUBSTRING(reg_date,1,11)," \
					"case when use_yn = 'Y' then '보임'" \
					"	  when use_yn = 'N' then '숨김'" \
					"	  else '' end use_yn " \
					"FROM tb_board WHERE section ='F' "
			if 'search_con' in request.GET :
				title = request.GET['search_con']
				search = request.GET['search_search']
				query += "and "+title+" like '%"+search+"%'"

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
				value_list.append(faq[1])
				value_list.append(index)
				value_list.append(faq[2])
				value_list.append(faq[3])
				value_list.append(faq[4])
				faq_list.append(value_list)
				index+=1

			aaData = json.dumps(list(faq_list), cls=DjangoJSONEncoder, ensure_ascii=False)
			return HttpResponse(aaData,'applications/json')

		elif request.GET['method'] == 'faq_del' :
			faq_id = request.GET['faq_id']
			use_yn = request.GET['use_yn']
			yn = ''
			if use_yn == 'Y':
				yn='N'
			else:
				yn='Y'
			# print 'use_yn == ',use_yn,' yn == ',yn
			cur = connection.cursor()
			query = "update edxapp.tb_board SET use_yn = '"+yn+"' where board_id = "+faq_id
			cur.execute(query)
			cur.close()
			aaData = json.dumps('success')
			return HttpResponse(aaData,'applications/json')

		elif request.GET['method'] == 'total_page':
			if 'search_con' in request.GET:
				subject = request.GET['search_con']
				search = request.GET['search_search']
				cur = connection.cursor()
				cur.execute('''
				select ceil(count(board_id)/10) from tb_board where section="F" and '''+subject+''' like "%'''+search+'''%"
				''')
				row = cur.fetchall()
				cur.close()
			else:
				cur =connection.cursor()
				cur.execute('''
				select ceil(count(board_id)/10) from tb_board where section="F"
				''')
				row =cur.fetchall()
				cur.close()
			data = json.dumps(list(row), cls=DjangoJSONEncoder, ensure_ascii=False)
		return HttpResponse(data,'applications/json')

	return render(request, 'community/comm_faq.html')

def new_faq(request):
	if request.method == 'POST':
		data = json.dumps({'status' : "fail"})
		if request.POST.get('method') == 'add':
			faq_question = request.POST.get('faq_question')
			faq_answer = request.POST.get('faq_answer')
			section = request.POST.get('section')

			print 'faq_question', faq_question, 'faq_answer', faq_answer, 'section', section
			cur = connection.cursor()
			query = "insert into edxapp.tb_board(subject, content, section)"
			query +=" VALUES ('"+faq_question+"', '"+faq_answer+"', '"+section+"') "
			cur.execute(query)
			cur.close()
			data = json.dumps({'status' : "success"})

		if request.POST['method'] == 'modi':
			question = request.POST.get('faq_question')
			answer = request.POST.get('faq_answer')

			faq_id = request.POST.get('faq_id')
			cur = connection.cursor()
			query = "update edxapp.tb_board set subject = '"+question+"', content = '"+answer+"' where board_id = '"+faq_id+"'"
			cur.execute(query)
			cur.close()
			data = json.dumps({'status' : "success"})
		return HttpResponse(data, 'applications/json')

	return render(request, 'community/comm_newfaq.html')

def modi_faq(request, id, use_yn):
	mod_faq = []
	if request.is_ajax():
		data = json.dumps({'status':"fail"})
		if request.GET['method'] == 'modi':
			cur = connection.cursor()
			query = "SELECT subject, content from tb_board WHERE board_id = "+id
			cur.execute(query)
			row = cur.fetchall()
			cur.close()
			print 'query', query
			for f in row :
				faq = f
				mod_faq.append(faq)
			data = json.dumps(list(mod_faq), cls=DjangoJSONEncoder, ensure_ascii=False)
		return HttpResponse(data, 'applications/json')

	variables = RequestContext(request, {
		'id' : id,
		'use_yn' : use_yn
    })

	return render_to_response('community/comm_modifaq.html',variables)


def comm_reference_room(request):
	return render(request, 'community/comm_reference_room.html')

def new_refer(request):
	if request.method == 'POST':
		# data = json.dumps({'status' : "fail"})
		# if 'file' in request.FILES:
		# 	print 'file_upload'
		# 	file = request.FILES['file']
		# 	filename = file._name
		# 	fq = open('%s/%s' % (UPLOAD_DIR, filename), 'wb')
		# 	for chunk in file.chunks():
		# 		fq.write(chunk)
		# 	fq.close()
		if request.POST.get('method') == 'add':
			refer_title = request.POST.get('refer_title')
			refer_cont = request.POST.get('refer_cont')

			cur = connection.cursor()
			query = "insert into edxapp.reference_room(refer_title, refer_content, refer_del )"
			query += "value ('"+refer_title+"','"+refer_cont+"','x')"
			cur.execute(query)
			cur.close()
			print 'file_upload'
			file = request.FILES['file']
			filename = file._name
			fq = open('%s/%s' % (UPLOAD_DIR, filename), 'wb')
			for chunk in file.chunks():
				fq.write(chunk)
			fq.close()
			print 'file_uploaded'
			data = json.dumps({'status' : "success"})



	if request.is_ajax():
		print "ajax ready"
	return render(request, 'community/comm_newrefer.html')

# monitoring view
def moni_storage(request):
	return render(request, 'monitoring/moni_storage.html')
