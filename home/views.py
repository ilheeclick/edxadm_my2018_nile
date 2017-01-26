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
import os
from django.views.decorators.csrf import csrf_exempt
import subprocess
import commands
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


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
				value_list.append(index)
				value_list.append(notice[6])
				value_list.append(notice[2])
				value_list.append(notice[1])
				value_list.append(notice[3])
				value_list.append(notice[4])
				value_list.append(notice[5])
				value_list.append(notice[7])
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
		elif request.GET['method'] == 'notice_delete' :
			noti_id = request.GET['noti_id']
			use_yn = request.GET['use_yn']
			yn = 'D'

			# print 'use_yn == ',use_yn,' yn == ',yn
			cur = connection.cursor()
			query = "update edxapp.tb_board SET use_yn = '"+yn+"' where board_id = "+noti_id
			cur.execute(query)
			cur.close()
			aaData = json.dumps('success')
		return HttpResponse(aaData,'applications/json')

	return render(request, 'community/comm_notice.html')

def new_notice(request):
	if 'file' in request.FILES:
		value_list = []
		file = request.FILES['file']
		filename=''
		file_ext=''
		file_size=''
		print file
		filename = file._name
		file_ext = filename.split('.')[1]

		fp = open('%s/%s' % (UPLOAD_DIR, filename) , 'wb')
		for chunk in file.chunks():
			fp.write(chunk)
		fp.close()
		data ='성공'

		n = os.path.getsize(UPLOAD_DIR+filename)
		file_size = str(n / 1024)+"KB"                       # 킬로바이트 단위로

		value_list.append(filename)
		value_list.append(file_ext)
		value_list.append(file_size)
		data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)
		return HttpResponse(data, 'applications/json')

	elif request.method == 'POST':
		data = json.dumps({'status':"fail", 'msg':"오류가 발생했습니다"})
		if request.POST['method'] == 'add':

			title = request.POST.get('nt_title')
			title = title.replace("'", "''")
			content = request.POST.get('nt_cont')
			content = content.replace("'", "''")
			section = request.POST.get('notice')
			head_title = request.POST.get('head_title')
			upload_file = request.POST.get('uploadfile')
			file_name = request.POST.getlist('file_name')
			file_ext = request.POST.getlist('file_ext')
			file_size = request.POST.getlist('file_size')
			print file_name,'/',file_ext,'/',file_size

			cur = connection.cursor()
			query = "insert into edxapp.tb_board(subject, content, head_title, section)"
			query +=" VALUES ('"+title+"', '"+content+"', '"+head_title+"', '"+section+"') "
			cur.execute(query)

			query2 = "select board_id from tb_board where subject ='"+title+"' and content='"+content+"'"
			cur.execute(query2)
			board_id = cur.fetchall()
			cur.close()
			# print board_id[0][0]
			if file_name != '' :
				index = 0
				for f in file_name:
					cur = connection.cursor()
					query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
							"VALUES ('"+str(board_id[0][0])+"','"+str(f)+"','"+str(file_ext[index])+"','"+str(file_size[index])+"')"
					cur.execute(query)
					cur.close()
					index = index+1
			data = json.dumps({'status' : "success"})

		elif request.POST['method'] == 'modi':
			title = request.POST.get('nt_title')
			title = title.replace("'", "''")
			content = request.POST.get('nt_cont')
			content = content.replace("'", "''")
			noti_id = request.POST.get('noti_id')
			odby = request.POST.get('odby')
			head_title = request.POST.get('head_title')

			upload_file = request.POST.get('uploadfile')
			file_name = request.POST.getlist('file_name')
			file_ext = request.POST.getlist('file_ext')
			file_size = request.POST.getlist('file_size')

			cur = connection.cursor()
			# query = "update edxapp.tb_board set subject = '"+title+"', content = '"+content+"', odby = '"+odby+"' where board_id = '"+noti_id+"'"
			query = "update edxapp.tb_board set subject = '"+title+"', content = '"+content+"', head_title = '"+head_title+"', mod_date = now() where board_id = '"+noti_id+"'"
			cur.execute(query)
			cur.close()

			if file_name != '' :
				index = 0
				for f in file_name:
					cur = connection.cursor()
					query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
							"VALUES ('"+str(noti_id)+"','"+str(f)+"','"+str(file_ext[index])+"','"+str(file_size[index])+"')"
					cur.execute(query)
					cur.close()
					index = index+1
			data = json.dumps({'status' : "success"})
		elif request.POST['method'] == 'delete_file' :
			board_id = request.POST.get('board_id')
			del_file = request.POST.get('del_file')
			cur = connection.cursor()
			query = "delete from tb_board_attach where board_id = "+board_id+" and attatch_file_name like '%"+del_file+"%'"
			cur.execute(query)
			row = cur.fetchall()
		return HttpResponse(data, 'applications/json')

	return render(request, 'community/comm_newnotice.html')

def modi_notice(request, id, use_yn):
	mod_notice = []

	if request.is_ajax():
		data=json.dumps({'status':"fail"})
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
					 WHERE section = 'N' and board_id = """+id
			cur.execute(query)
			row = cur.fetchall()
			cur.close()
			# print 'query', query
			# print 'row[0] == ',row[0][0]
			# print 'row[1] == ',row[0][1]
			# print 'row[2] == ',row[0][2]
			# print 'row[3] == ',row[0][3]

			cur = connection.cursor()
			query ="select attatch_file_name from tb_board_attach " \
				   "where board_id = "+id
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
		elif request.GET['method'] == 'file_download' :
			file_name = request.GET['file_name']
			# print 'file_name == ',file_name
			data = json.dumps(UPLOAD_DIR+file_name, cls=DjangoJSONEncoder, ensure_ascii=False)


		return HttpResponse(data, 'applications/json')


	variables = RequestContext(request, {
		'id' : id,
		'use_yn' : use_yn
    })

	return render_to_response('community/comm_modinotice.html',variables)

def comm_k_news(request):
	knews_list = []
	if request.is_ajax():
		aaData={}
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
			if 'search_con' in request.GET :
				title = request.GET['search_con']
				search = request.GET['search_search']
				query += "and "+title+" like '%"+search+"%'"
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
				index+=1

			aaData = json.dumps(list(knews_list), cls=DjangoJSONEncoder, ensure_ascii=False)
		elif request.GET['method'] == 'knews_del' :
			noti_id = request.GET['noti_id']
			use_yn = request.GET['use_yn']
			yn = ''
			if use_yn == 'Y':
				yn='N'
			else:
				yn='Y'
			print 'use_yn == ',use_yn,' yn == ',yn
			cur = connection.cursor()
			query = "update edxapp.tb_board SET use_yn = '"+yn+"' where board_id = "+noti_id
			print 'query == ', query
			cur.execute(query)
			cur.close()
			aaData = json.dumps('success')
		elif request.GET['method'] == 'knews_delete' :
			noti_id = request.GET['noti_id']
			use_yn = request.GET['use_yn']
			yn = 'D'

			cur = connection.cursor()
			query = "update edxapp.tb_board SET use_yn = '"+yn+"' where board_id = "+noti_id
			print 'query == ', query
			cur.execute(query)
			cur.close()
			aaData = json.dumps('success')
		return HttpResponse(aaData,'applications/json')

	return render(request, 'community/comm_k_news.html')

def new_knews(request):
	if 'file' in request.FILES:
		value_list = []
		file = request.FILES['file']
		filename=''
		file_ext=''
		file_size=''
		# print file
		filename = file._name
		file_ext = filename.split('.')[1]

		fp = open('%s/%s' % (UPLOAD_DIR, filename) , 'wb')
		for chunk in file.chunks():
			fp.write(chunk)
		fp.close()
		data ='성공'

		n = os.path.getsize(UPLOAD_DIR+filename)
		file_size = str(n / 1024)+"KB"                       # 킬로바이트 단위로

		value_list.append(filename)
		value_list.append(file_ext)
		value_list.append(file_size)
		data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)
		return HttpResponse(data, 'applications/json')

	elif request.method == 'POST':
		data = json.dumps({'status':"fail", 'msg':"오류가 발생했습니다"})
		if request.POST['method'] == 'add':

			title = request.POST.get('knews_title')
			title = title.replace("'", "''")
			content = request.POST.get('knews_content')
			content = content.replace("'", "''")
			section = request.POST.get('k_news')
			head_title = request.POST.get('head_title')
			upload_file = request.POST.get('uploadfile')
			file_name = request.POST.getlist('file_name')
			file_ext = request.POST.getlist('file_ext')
			file_size = request.POST.getlist('file_size')
			# print file_name,'/',file_ext,'/',file_size
			# print 'head_title == ',head_title
			print 'content == ', content

			cur = connection.cursor()
			query = "insert into edxapp.tb_board(subject, content, section, head_title)"
			query +=" VALUES ('"+title+"', '"+content+"', '"+section+"', '"+head_title+"') "
			cur.execute(query)

			query2 = "select board_id from tb_board where subject ='"+title+"' and content='"+content+"'"
			cur.execute(query2)
			board_id = cur.fetchall()
			cur.close()
			# print board_id[0][0]
			if file_name != '' :
				index = 0
				for f in file_name:
					cur = connection.cursor()
					query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
							"VALUES ('"+str(board_id[0][0])+"','"+str(f)+"','"+str(file_ext[index])+"','"+str(file_size[index])+"')"
					cur.execute(query)
					cur.close()
					index = index+1

			data = json.dumps({'status' : "success"})

		elif request.POST['method'] == 'modi':
			title = request.POST.get('k_news_title')
			title = title.replace("'", "''")
			content = request.POST.get('k_news_cont')
			content = content.replace("'", "''")
			k_news_id = request.POST.get('k_news_id')
			odby = request.POST.get('odby')
			head_title = request.POST.get('head_title')
			upload_file = request.POST.get('uploadfile')
			file_name = request.POST.getlist('file_name')
			file_ext = request.POST.getlist('file_ext')
			file_size = request.POST.getlist('file_size')

			cur = connection.cursor()
			query = "update edxapp.tb_board set subject = '"+title+"', content = '"+content+"', odby = '"+odby+"', mod_date = now(), head_title = '"+head_title+"' where board_id = '"+k_news_id+"'"
			cur.execute(query)
			cur.close()
			print 'str(file_ext) == ', str(file_ext)
			if file_name != '' :
				index = 0
				for f in file_name:
					cur = connection.cursor()
					query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
							"VALUES ('"+str(k_news_id)+"','"+str(f)+"','"+str(file_ext[index])+"','"+str(file_size[index])+"')"
					cur.execute(query)
					cur.close()
					index = index+1
			data = json.dumps({'status' : "success"})
		elif request.POST['method'] == 'delete_file' :
			# print 'delete_file'
			board_id = request.POST.get('board_id')
			del_file = request.POST.get('del_file')
			# print 'board_id ==',board_id, ' del_file ==',del_file
			cur = connection.cursor()
			query = "delete from tb_board_attach where board_id = "+board_id+" and attatch_file_name like '%"+del_file+"%'"
			cur.execute(query)
			row = cur.fetchall()
		return HttpResponse(data, 'applications/json')
	return render(request,'community/comm_newknews.html')

def modi_knews(request, id, use_yn):
	mod_knews = []
	if request.is_ajax():
		data=json.dumps({'status':"fail"})
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
					 WHERE section = 'K' and board_id = """+id
			cur.execute(query)
			row = cur.fetchall()
			cur.close()
			# print 'query', query

			cur = connection.cursor()
			query ="select attatch_file_name from tb_board_attach where board_id = "+id
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
		elif request.GET['method'] == 'file_download' :
			file_name = request.GET['file_name']
			# print 'file_name == ',file_name
			data = json.dumps(UPLOAD_DIR+file_name, cls=DjangoJSONEncoder, ensure_ascii=False)

		return HttpResponse(data, 'applications/json')


	variables = RequestContext(request, {
		'id' : id,
		'use_yn' : use_yn
    })

	return render_to_response('community/comm_modi_knews.html',variables)


def comm_faq(request):
	faq_list = []
	data=json.dumps({'status':"fail"})
	if request.is_ajax():
		if request.GET['method'] == 'faq_list':
			aaData={}
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
							  ELSE ''
						   END
							  head_title,
						   use_yn
					  FROM tb_board
					 WHERE section = 'F' AND NOT use_yn = 'D'
			"""
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
				value_list.append(index)
				value_list.append(faq[5])
				value_list.append(faq[2])
				value_list.append(faq[1])
				value_list.append(faq[3])
				value_list.append(faq[4])
				value_list.append(faq[6])
				faq_list.append(value_list)
				index+=1
			# print 'faq_list == ',faq_list
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
		elif request.GET['method'] == 'faq_delete' :
			faq_id = request.GET['faq_id']
			use_yn = request.GET['use_yn']
			yn = 'D'

			cur = connection.cursor()
			query = "update edxapp.tb_board SET use_yn = '"+yn+"' where board_id = "+faq_id
			cur.execute(query)
			cur.close()
			aaData = json.dumps('success')
			return HttpResponse(aaData,'applications/json')


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
		return HttpResponse(data,'applications/json')

	return render(request, 'community/comm_faq.html')

def new_faq(request):
	if request.method == 'POST':
		data = json.dumps({'status' : "fail"})
		if request.POST.get('method') == 'add':
			head_title = request.POST.get('head_title')
			faq_question = request.POST.get('faq_question')
			faq_question = faq_question.replace("'", "''")
			faq_answer = request.POST.get('faq_answer')
			faq_answer = faq_answer.replace("'", "''")
			section = request.POST.get('section')

			print 'head_title == ',head_title,' faq_question == ', faq_question, ' faq_answer == ', faq_answer, ' section == ', section
			cur = connection.cursor()
			query = "insert into edxapp.tb_board(subject, content, section, head_title)"
			query +=" VALUES ('"+faq_question+"', '"+faq_answer+"', '"+section+"', '"+head_title+"') "
			cur.execute(query)
			cur.close()
			data = json.dumps({'status' : "success"})

		if request.POST['method'] == 'modi':
			question = request.POST.get('faq_question')
			question = question.replace("'", "''")
			answer = request.POST.get('faq_answer')
			answer = answer.replace("'", "''")
			head_title = request.POST.get('head_title')
			faq_id = request.POST.get('faq_id')
			cur = connection.cursor()
			query = "update edxapp.tb_board set subject = '"+question+"', content = '"+answer+"', head_title = '"+head_title+"', mod_date = now() where board_id = '"+faq_id+"'"
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
							  ELSE ''
						   END
							  head_title
					  FROM tb_board
					 WHERE board_id = """+id
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

def comm_faqrequest(request) :
	if request.is_ajax() :
		aaData = json.dumps({'status':"fail"})
		f_request_list = []
		if request.GET['method'] == 'faqrequest_list' :
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
			for fr in row :
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
				index+=1
			aaData = json.dumps(list(f_request_list), cls=DjangoJSONEncoder, ensure_ascii=False)
		return HttpResponse(aaData, 'applications/json')
	return render_to_response('community/comm_faqrequest.html')



def comm_reference_room(request):
	refer_list = []
	if request.is_ajax():
		aaData={}
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
				index+=1

			aaData = json.dumps(list(refer_list), cls=DjangoJSONEncoder, ensure_ascii=False)
		elif request.GET['method'] == 'refer_del' :
			refer_id = request.GET['refer_id']
			use_yn = request.GET['use_yn']
			yn = ''
			if use_yn == 'Y':
				yn='N'
			else:
				yn='Y'
			# print 'use_yn == ',use_yn,' yn == ',yn
			cur = connection.cursor()
			query = "update edxapp.tb_board SET use_yn = '"+yn+"' where board_id = "+refer_id
			cur.execute(query)
			cur.close()
			aaData = json.dumps('success')
		elif request.GET['method'] == 'refer_delete' :
			refer_id = request.GET['refer_id']
			use_yn = request.GET['use_yn']
			yn = 'D'

			cur = connection.cursor()
			query = "update edxapp.tb_board SET use_yn = '"+yn+"' where board_id = "+refer_id
			cur.execute(query)
			cur.close()
			aaData = json.dumps('success')

		return HttpResponse(aaData,'applications/json')
	return render(request, 'community/comm_reference_room.html')

def new_refer(request):
	if 'file' in request.FILES:
		value_list = []
		file = request.FILES['file']
		filename=''
		file_ext=''
		file_size=''
		# print file
		filename = file._name
		file_ext = filename.split('.')[1]

		fp = open('%s/%s' % (UPLOAD_DIR, filename) , 'wb')
		for chunk in file.chunks():
			fp.write(chunk)
		fp.close()
		data ='성공'

		n = os.path.getsize(UPLOAD_DIR+filename)
		file_size = str(n / 1024)+"KB"                       # 킬로바이트 단위로

		value_list.append(filename)
		value_list.append(file_ext)
		value_list.append(file_size)
		data = json.dumps(list(value_list), cls=DjangoJSONEncoder, ensure_ascii=False)
		return HttpResponse(data, 'applications/json')

	elif request.method == 'POST':
		data = json.dumps({'status':"fail", 'msg':"오류가 발생했습니다"})
		if request.POST['method'] == 'add':

			title = request.POST.get('refer_title')
			title = title.replace("'", "''")
			content = request.POST.get('refer_cont')
			content = content.replace("'", "''")
			section = request.POST.get('refer')
			head_title = request.POST.get('head_title')
			upload_file = request.POST.get('uploadfile')
			file_name = request.POST.getlist('file_name')
			file_ext = request.POST.getlist('file_ext')
			file_size = request.POST.getlist('file_size')
			# print file_name,'/',file_ext,'/',file_size

			cur = connection.cursor()
			query = "insert into edxapp.tb_board(subject, content, section, head_title)"
			query +=" VALUES ('"+title+"', '"+content+"', '"+section+"', '"+head_title+"') "
			cur.execute(query)

			query2 = "select board_id from tb_board where subject ='"+title+"' and content='"+content+"'"
			cur.execute(query2)
			board_id = cur.fetchall()
			cur.close()
			# print board_id[0][0]
			if file_name != '' :
				index = 0
				for f in file_name:
					cur = connection.cursor()
					query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
							"VALUES ('"+str(board_id[0][0])+"','"+str(f)+"','"+str(file_ext[index])+"','"+str(file_size[index])+"')"
					cur.execute(query)
					cur.close()
					index = index+1

			data = json.dumps({'status' : "success"})

		elif request.POST['method'] == 'modi':
			title = request.POST.get('refer_title')
			title = title.replace("'", "''")
			content = request.POST.get('refer_cont')
			content = content.replace("'", "''")
			refer_id = request.POST.get('refer_id')
			odby = request.POST.get('odby')
			head_title = request.POST.get('head_title')
			upload_file = request.POST.get('uploadfile')
			file_name = request.POST.getlist('file_name')
			file_ext = request.POST.getlist('file_ext')
			file_size = request.POST.getlist('file_size')

			cur = connection.cursor()
			# query = "update edxapp.tb_board set subject = '"+title+"', content = '"+content+"', odby = '"+odby+"' where board_id = '"+noti_id+"'"
			query = "update edxapp.tb_board set subject = '"+title+"', content = '"+content+"', mod_date = now(), head_title = '"+head_title+"' where board_id = '"+refer_id+"'"
			cur.execute(query)
			cur.close()

			if file_name != '' :
				index = 0
				for f in file_name:
					cur = connection.cursor()
					query = "insert into edxapp.tb_board_attach(board_id, attatch_file_name, attatch_file_ext, attatch_file_size) " \
							"VALUES ('"+str(refer_id)+"','"+str(f)+"','"+str(file_ext[index])+"','"+str(file_size[index])+"')"
					cur.execute(query)
					cur.close()
					index = index+1
			data = json.dumps({'status' : "success"})
		elif request.POST['method'] == 'delete_file' :
			# print 'delete_file'
			board_id = request.POST.get('board_id')
			del_file = request.POST.get('del_file')
			print 'board_id ==',board_id, ' del_file ==',del_file
			cur = connection.cursor()
			query = "delete from tb_board_attach where board_id = "+board_id+" and attatch_file_name like '%"+del_file+"%'"
			cur.execute(query)
			row = cur.fetchall()
		return HttpResponse(data, 'applications/json')

		return HttpResponse(data, 'applications/json')

	return render(request, 'community/comm_newrefer.html')

def modi_refer(request, id, use_yn):
	mod_refer = []

	if request.is_ajax():
		data=json.dumps({'status':"fail"})
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
					 WHERE section = 'R' AND board_id = """+id

			cur.execute(query)
			row = cur.fetchall()
			cur.close()
			# print 'query', query

			cur = connection.cursor()
			query ="select attatch_file_name from tb_board_attach where board_id = "+id
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
		elif request.GET['method'] == 'file_download' :
			file_name = request.GET['file_name']
			# print 'file_name == ',file_name
			data = json.dumps(UPLOAD_DIR+file_name, cls=DjangoJSONEncoder, ensure_ascii=False)
		return HttpResponse(data, 'applications/json')


	variables = RequestContext(request, {
		'id' : id,
		'use_yn' : use_yn
    })

	return render_to_response('community/comm_modirefer.html',variables)

# RSA 설정 필요
# monitoring view
def moni_storage(request):
	if request.is_ajax() :
		if request.GET['method'] == 'storage_list' :
			aaData = {}
			data_list = []
			a = commands.getoutput('df -h /video')
			a_list = [1, a.split()[7], a.split()[9], a.split()[10], a.split()[11]]
			data_list.append(a_list)
			# print 'data_list == ',data_list
			aaData = json.dumps(list(data_list), cls=DjangoJSONEncoder, ensure_ascii=False)
		return HttpResponse(aaData,'applications/json')
	return render(request, 'monitoring/moni_storage.html')

@csrf_exempt
def summer_upload(request):
	if 'file' in request.FILES:
		file = request.FILES['file']
		# filename = file._name
		now = datetime.datetime.now()
		filename = now.strftime("%Y%m%d%H%M")+"."+file._name.split('.')[1]
		fp = open('%s/%s' % (UPLOAD_DIR, filename) , 'wb')

		for chunk in file.chunks():
			fp.write(chunk)
		fp.close()
		# return HttpResponse('http://192.168.33.15:8000/home/static/excel/notice_file/'+filename)
		return HttpResponse('/manage/home/static/upload/'+filename)
	return HttpResponse('fail')
