# -*- coding: utf-8 -*-
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
import logging.handlers

# # 로거 인스턴스를 만든다
# logger = logging.getLogger('mongo_test log')
#
# # 포매터를 만든다
# fomatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
#
# # 스트림과 파일로 로그를 출력하는 핸들러를 각각 만든다.
# fileHandler = logging.FileHandler('./mongo_test.log')
# streamHandler = logging.StreamHandler()
#
# # 각 핸들러에 포매터를 지정한다.
# fileHandler.setFormatter(fomatter)
# streamHandler.setFormatter(fomatter)
#
# # 로거 인스턴스에 스트림 핸들러와 파일핸들러를 붙인다.
# logger.addHandler(fileHandler)
# logger.addHandler(streamHandler)
# logger.setLevel(logging.DEBUG)


pb = ''
ov = ''
org = ''
edited_on = ''
courseOrgs = {}
courseNames = {}
courseCreates = {}
courseStarts = {}
courseEnds = {}

database_id = '192.168.33.12'
client = MongoClient(database_id, 27017)
db = client.edxapp


course_ids_all = {
    'course-v1:BUFSk+KOCW.BUFS01+2016_HR2', 'course-v1:CUKk+KOCW.CUK01+2016_01', 'course-v1:DKUK+KOCW.DKUK0001+201613157501'
}

course_orgs = {}
course_names = {}
course_creates = {}
course_edited_ons = {}
course_starts = {}
course_ends = {}
course_enroll_starts = {}
course_enroll_ends = {}

for c in course_ids_all:

    # cid = str(c[0])
    cid = str(c)
    course_id = cid
    cid = course_id.split('+')[1]
    run = course_id.split('+')[2]

    # db.modulestore.active_versions --------------------------------------
    cursor = db.modulestore.active_versions.find_one({'course': cid, 'run': run})
    pb = cursor.get('versions').get('published-branch')
    # course_orgs
    course_orgs[course_id] = cursor.get('org')
    course_edited_ons[course_id] = cursor.get('edited_on')
    logger.debug('1---------------------------------------------')
    # logger.debug(cursor)
    logger.debug(pb)
    # --------------------------------------

    # db.modulestore.structures --------------------------------------
    cursor = db.modulestore.structures.find_one({'_id': ObjectId(pb)},{"blocks":{"$elemMatch":{"block_type":"course"}}})
    logger.debug('2---------------------------------------------')


    # print len(cursor.get('blocks'))
    # print cursor.get('blocks')[0].get('fields')

    # logger.debug(cursor)
    course_start = cursor.get('blocks')[0].get('fields').get('start')  # course_starts
    course_end = cursor.get('blocks')[0].get('fields').get('end')  # course_ends
    course_enroll_start = cursor.get('blocks')[0].get('fields').get('enrollment_start')  # course_enroll_start
    course_enroll_end = cursor.get('blocks')[0].get('fields').get('enrollment_end')  # course_enroll_end
    course_name = cursor.get('blocks')[0].get('fields').get('display_name')  # course_names

    logger.debug('3---------------------------------------------')
    logger.debug(course_id + " : " + cid + " : " + run)
    logger.debug(course_start)
    logger.debug(course_end)
    logger.debug(course_enroll_start)
    logger.debug(course_enroll_end)
    logger.debug('4---------------------------------------------')


