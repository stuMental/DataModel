# !usr/bin/python
# -*- coding: utf-8 -*-

import DbUtil
import Config
import Logger
import random
from CommonUtil import CommonUtil

class TestData(object):
    """docsTry for TestData"""
    def __init__(self):
        super(TestData, self).__init__()
        self.__db = DbUtil.DbUtil(Config.INPUT_DB_HOST, Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)
        self.__courses = ['course_1', 'course_2', 'course_2']
        self.__students = ['201821210001', '201821210002', '201821210003']
        self.__class_ids = ['2018_1']
        self.__grades = ['2018']
        self.__classes = ['1班']


    def produce(self):
        ''''''
        sql = '''
            INSERT INTO  {0} (camera_id, face_id, pose_stat_time, body_stat, face_pose, face_emotion, face_pose_stat, course_name, class_id) VALUES 
        '''.format(Config.INTERMEDIATE_TABLE_TRAIN)

        vSqls = ''
        first = True
        count = 0
        for x in xrange(0, 1000):
            if not first:
                vSqls += ','
            vSqls += '''
                ('{0}', '{1}', '{2}', '{3}', '{4}', {5}, '{6}', '{7}', '{8}')
            '''.format(1, self.__students[random.randint(0, len(self.__students) - 1)], '1549882797', random.randint(0, 5), random.randint(0, 2), random.randint(0, 2), '0', self.__courses[random.randint(0, len(self.__courses) - 1)], self.__class_ids[random.randint(0, len(self.__class_ids) - 1)])
            first = False
            count += 1
            if count % Config.INSERT_BATCH_THRESHOLD == 0:
                self.__db.insert(sql + vSqls)
        if vSqls != '':
            self.__db.insert(sql + vSqls)
        self.__logger.info("Try to insert {2} records to the table {0} in the database {1}".format(Config.INTERMEDIATE_TABLE_TRAIN, Config.INPUT_DB_DATABASE, count))

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
            for c in self.__classes:
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
            for c in self.__classes:
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
            SELECT IF(names IS NULL, '无', names) as names
            FROM (
                SELECT GROUP_CONCAT(student_name separator ',') as names
                FROM (
                    SELECT student_number, student_name, count(*) as num
                    FROM student_mental_status_ld
                    WHERE dt>=date_add('2019-05-30', interval -15 day) AND dt<='2019-05-30' AND student_emotion='2' AND grade_name='2017' AND class_name='17动漫'
                    GROUP BY student_number, student_name
                    HAVING num>=6
                ) t1
            ) t2
        '''# .format(CommonUtil.get_specific_date('2019-03-03', Config.LOOKBACKWINDOW), '2019-03-03', Config.OUTPUT_UI_COURSE_TABLE)
        for row in self.__db.select(sql):
            print row

if __name__ == '__main__':
    doer = TestData()
    doer.test_sql()