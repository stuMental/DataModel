# !/usr/bin/python
# -*- coding: utf-8 -*-

import DbUtil
import Config
import Logger
import random

class MakeData(object):
    """docsTry for Preprocessor"""
    def __init__(self):
        super(MakeData, self).__init__()
        self.__db = DbUtil.DbUtil(Config.INPUT_DB_HOST, Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)


    def make_data(self):
        start_time = 1563235200
        end_time = 1563267600
        frame = 0
        sql = '''
        insert into person_body_status_test(camera_id,frame_id,body_id,body_stat,body_track,face_id,face_track,face_pose,face_pose_stat_time,face_emotion,unix_timestamp,pose_stat_time)values
        '''
        face_pose_gap = 300000
        pose_stat_gap = 3000
        insert_sql = sql
        count = 6000000
        i = 0
        while count:
            i += 1
            frame = str(random.randint(0, 200000))
            body_stat = str(random.randint(-1,5))
            face_pose = str(random.randint(-1,2))
            face_id = 'unknown'
            if count > 5000000:
                face_id = str(random.randint(1,200))
            face_track = face_id if face_id != 'unknown' else str(random.randint(201,1200))
            body_track = face_track
            body_id = face_track
            pose_stat_time = random.randint(start_time, end_time)
            face_pose_stat_time = pose_stat_time
            unix_timestamp = pose_stat_time * 1000
            face_emotion = str(random.randint(-1,2))
            values = "('0','"+str(frame)+"',"+str(body_id)+",'"+body_stat+"','"+body_track+"','"+face_id+"','"+face_track+"','"+face_pose+"','"+str(face_pose_stat_time)+"','"+face_emotion+"','"+str(unix_timestamp)+"','"+str(pose_stat_time)+"')"
            if insert_sql == sql:
                insert_sql = insert_sql + values
            else:
                insert_sql = insert_sql + ',' + values
            if i % 10000 == 0:
                self.__db.insert(insert_sql)
                insert_sql = sql
                print i
            count -= 1

    def make_course(self):
        sql='''
            insert into school_course_info(course_name,start_time,end_time,ds) values ('math','1549584000','1549586700','20190208'),('c    hinese','1549587600','1549590300','20190208'),('english','1549591200','1549593900','20190208'),('physic','1549595700','1549598400','201    90208'),('history','1549605600','1549608300','20190208'),('geography','1549609200','1549611900','20190208')
        '''
        self.__db.insert(sql)

    def make_test_data(self):
        #face_track测试，测试点：
        #1:face_track为unknwon
        #2:face_track不为unknown但是face_id全为unknown
        #3:face_track有一个face_id和unknown
        #4:face_track有多个face_id和unknown
        sql='''
                insert into person_body_status2(camera_id,frame_id,body_id,body_stat,body_track,face_id,face_track,face_pose,face_pose_stat_time,face_emotion,unix_timestamp,pose_stat_time)values
        '''
        camera_id="'0'"
        frame_id="'1'"
        body_id=str(0)
        body_stat="'0'"
        body_track="'1'"
        face_id="'unknown'"
        face_track="'1'"
        face_pose="'2'"
        face_pose_stat_time="'1549605600'"
        face_emotion="'1'"
        unix_timestamp="'1549605600'"
        pose_stat_time="'1549605600'"
        val = '('+camera_id+','+frame_id+','+body_id+','+body_stat+','+body_track+','+face_id+','+face_track+','+face_pose+','+face_pose_stat_time+','+face_emotion+','+unix_timestamp+','+pose_stat_time+')'
        sql = sql+val

        camera_id="'0'"
        frame_id="'2'"
        body_id=str(0)
        body_stat="'2'"
        body_track="'1'"
        face_id="'1'"
        face_track="'1'"
        face_pose="'2'"
        face_pose_stat_time="'1549605600'"
        face_emotion="'1'"
        unix_timestamp="'1549605600'"
        pose_stat_time="'1549605600'"
        val = '('+camera_id+','+frame_id+','+body_id+','+body_stat+','+body_track+','+face_id+','+face_track+','+face_pose+','+face_pose_stat_time+','+face_emotion+','+unix_timestamp+','+pose_stat_time+')'
        sql = sql + ',' +val

        camera_id="'0'"
        frame_id="'3'"
        body_id=str(0)
        body_stat="'2'"
        body_track="'1'"
        face_id="'unknown'"
        face_track="'1'"
        face_pose="'2'"
        face_pose_stat_time="'1549605600'"
        face_emotion="'1'"
        unix_timestamp="'1549605600'"
        pose_stat_time="'1549605600'"
        val = '('+camera_id+','+frame_id+','+body_id+','+body_stat+','+body_track+','+face_id+','+face_track+','+face_pose+','+face_pose_stat_time+','+face_emotion+','+unix_timestamp+','+pose_stat_time+')'
        sql = sql + ',' + val

        camera_id="'0'"
        frame_id="'4'"
        body_id=str(0)
        body_stat="'2'"
        body_track="'1'"
        face_id="'unknown'"
        face_track="'2'"
        face_pose="'2'"
        face_pose_stat_time="'1549605600'"
        face_emotion="'1'"
        unix_timestamp="'1549605600'"
        pose_stat_time="'1549605600'"
        val = '('+camera_id+','+frame_id+','+body_id+','+body_stat+','+body_track+','+face_id+','+face_track+','+face_pose+','+face_pose_stat_time+','+face_emotion+','+unix_timestamp+','+pose_stat_time+')'
        sql = sql + ',' + val

        camera_id="'0'"
        frame_id="'4'"
        body_id=str(0)
        body_stat="'2'"
        body_track="'1'"
        face_id="'unknown'"
        face_track="'2'"
        face_pose="'2'"
        face_pose_stat_time="'1549605600'"
        face_emotion="'1'"
        unix_timestamp="'1549605600'"
        pose_stat_time="'1549605600'"
        val = '('+camera_id+','+frame_id+','+body_id+','+body_stat+','+body_track+','+face_id+','+face_track+','+face_pose+','+face_pose_stat_time+','+face_emotion+','+unix_timestamp+','+pose_stat_time+')'
        sql = sql + ',' + val


        camera_id="'0'"
        frame_id="'4'"
        body_id=str(0)
        body_stat="'2'"
        body_track="'1'"
        face_id="'1'"
        face_track="'3'"
        face_pose="'2'"
        face_pose_stat_time="'1549605600'"
        face_emotion="'1'"
        unix_timestamp="'1549605600'"
        pose_stat_time="'1549605600'"
        val = '('+camera_id+','+frame_id+','+body_id+','+body_stat+','+body_track+','+face_id+','+face_track+','+face_pose+','+face_pose_stat_time+','+face_emotion+','+unix_timestamp+','+pose_stat_time+')'
        sql = sql + ',' + val

        camera_id="'0'"
        frame_id="'4'"
        body_id=str(0)
        body_stat="'2'"
        body_track="'1'"
        face_id="'2'"
        face_track="'3'"
        face_pose="'2'"
        face_pose_stat_time="'1549605600'"
        face_emotion="'1'"
        unix_timestamp="'1549605600'"
        pose_stat_time="'1549605600'"
        val = '('+camera_id+','+frame_id+','+body_id+','+body_stat+','+body_track+','+face_id+','+face_track+','+face_pose+','+face_pose_stat_time+','+face_emotion+','+unix_timestamp+','+pose_stat_time+')'
        sql = sql + ',' + val
        self.__db.insert(sql)

    def make_test_pose_stat(self):
        sql='''
            insert into person_body_status_face_track(camera_id,frame_id,body_id,body_stat,body_track,face_id,face_track,face_pose,face_pose_stat_time,face_emotion,unix_timestamp,pose_stat_time)values
        '''
        camera_id="'0'"
        frame_id="'1'"
        body_id=str(0)
        body_stat="'5'"
        body_track="'1'"
        face_id="'1'"
        face_track="'1'"
        face_pose="'1'"
        face_pose_stat_time="'1549605600'"
        face_emotion="'-1'"
        unix_timestamp="'1549605600'"
        pose_stat_time="'1549605600'"
        val = '('+camera_id+','+frame_id+','+body_id+','+body_stat+','+body_track+','+face_id+','+face_track+','+face_pose+','+face_pose_stat_time+','+face_emotion+','+unix_timestamp+','+pose_stat_time+')'
        sql = sql+val

        camera_id="'0'"
        frame_id="'1'"
        body_id=str(0)
        body_stat="'-1'"
        body_track="'1'"
        face_id="'1'"
        face_track="'1'"
        face_pose="'1'"
        face_pose_stat_time="'1549605600'"
        face_emotion="'2'"
        unix_timestamp="'1549605600'"
        pose_stat_time="'1549605600'"
        val = '('+camera_id+','+frame_id+','+body_id+','+body_stat+','+body_track+','+face_id+','+face_track+','+face_pose+','+face_pose_stat_time+','+face_emotion+','+unix_timestamp+','+pose_stat_time+')'
        sql = sql+','+val
        self.__db.insert(sql)

if __name__ == '__main__':
    doer = MakeData()
    doer.make_data()