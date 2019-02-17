# !usr/bin/python
# -*- coding: utf-8 -*-

import DbUtil
import Config
import Logger
import random
import CommonUtil

class TestData(object):
    """docsTry for TestData"""
    def __init__(self):
        super(TestData, self).__init__()
        self.__db = DbUtil.DbUtil(Config.INPUT_DB_HOST, Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)
        self.__courses = ['rest', 'math', 'chinese', 'english', 'physic', 'history', 'geography']
        self.__classes = 101
        self.__persons = 101
        self.__students = [['201821210001', '小华'], ['201821210002', '小敏'], ['201821210003', '小李']]
        self.__course_names = [['2018001','计算机'], ['2018002', '高等数学'], ['2018003', '解析几何']]
        self.__grades = ['2016', '2017', '2018']
        self.__class_names = ['1班', '2班', '3班']


    def produce(self):
        ''''''
        sql = '''
            INSERT INTO  {0} (camera_id, face_id, pose_stat_time, body_stat, face_pose, face_emotion, face_pose_stat, course_name, class_id) VALUES 
        '''.format(Config.INTERMEDIATE_TABLE_TRAIN)

        for k in xrange(1,1000):
            vSqls = ''
            first = True
            for x in xrange(1, self.__classes):
                for y in xrange(1,self.__persons):
                    if not first:
                        vSqls += ','
                    vSqls += '''
                        ('{0}', '{1}', '1549682797', '{2}', '{3}', '{4}', '0', '{5}', '{0}')
                    '''.format(x, (x - 1) * 100 + y, random.randint(0, 5), random.randint(0, 2), random.randint(0, 2), self.__courses[random.randint(0, len(self.__courses) - 1)])
                    first = False
            self.__db.insert(sql + vSqls)
            self.__logger.info("Try to insert 10000 records to the table {0} in the database {1}".format(Config.INTERMEDIATE_TABLE_TRAIN, Config.INPUT_DB_DATABASE))

    def stu_class(self):
        ''''''
        sql = '''
            INSERT INTO  {0} (grade_name, class_name, student_number, student_name, dt) VALUES 
        '''.format(Config.SCHOOL_STUDENT_CLASS_TABLE)

        vSqls = ''
        first = True
        stu = 1
        student_number = 201821210001
        for g in self.__grades:
            for c in self.__class_names:
                for x in xrange(1, 21):
                    if not first:
                        vSqls += ','
                    vSqls += '''
                        ('{0}', '{1}', '{2}', '{3}', '{4}')
                    '''.format(g, c, str(student_number), '小明_'+ str(stu), '1550309899')
                    first = False
                    student_number += 1
                    stu += 1
        self.__db.insert(sql + vSqls)
        self.__logger.info("Try to insert some records to the table {0} in the database {1}".format(Config.SCHOOL_STUDENT_CLASS_TABLE, Config.INPUT_DB_DATABASE))

    def course(self):
        ''''''
        sql = '''
            INSERT INTO  {0} (course_id, course_name, tea_id, tea_name, class_name, grade_name, start_time, end_time, dt) VALUES 
        '''.format(Config.SCHOOL_COURSE_TABLE)

        vSqls = ''
        first = True
        tea = 1
        cid = 1
        for g in self.__grades:
            for c in self.__class_names:
                start_time = 1550299899
                end_time = 1550300899
                for x in xrange(1, 21):
                    if not first:
                        vSqls += ','
                    vSqls += '''
                        ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')
                    '''.format(cid, 'course_' + str(cid), tea, '教师_'+ str(tea), c, g, start_time, end_time, '20190216')
                    first = False
                    cid += 1
                    tea += 1
                    start_time = end_time
                    end_time += 1000
        self.__db.insert(sql + vSqls)
        self.__logger.info("Try to insert some records to the table {0} in the database {1}".format(Config.SCHOOL_STUDENT_CLASS_TABLE, Config.INPUT_DB_DATABASE))

    def test_sql(self):
        ''''''
        sql = '''
            SELECT
                student_interest, COUNT(*) AS total
            FROM student_mental_status_interest_daily
            WHERE class_id in (SELECT class_id FROM school_camera_class_info WHERE grade_name = '2018') AND dt = 1550309899
            GROUP BY student_interest;
        '''

        for row in self.__db.select(sql):
            print row

if __name__ == '__main__':
    doer = TestData()
    doer.test_sql()