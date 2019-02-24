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
            SELECT t1.camera_id AS class_id, t1.face_id, t1.pose_stat_time, t1.body_stat, t1.face_pose, t1.face_emotion, t1.face_pose_stat,
                   (CASE WHEN t2.course_name IS NULL THEN 'rest' ELSE t2.course_name END) AS course_name
            FROM
            (
                SELECT camera_id, face_id, pose_stat_time, body_stat, face_pose, face_emotion, face_pose_stat
                    FROM {3}
                    WHERE pose_stat_time >= {0} AND pose_stat_time <= {1}
            ) t1 LEFT OUTER JOIN (
                SELECT
                    t4.class_id, t3.course_name, t3.start_time, t3.end_time
                FROM
                (
                    SELECT grade_name, class_name, course_name, start_time, end_time
                    FROM {4}
                    WHERE dt = {2}
                ) t3 LEFT OUTER JOIN
                (
                    SELECT
                        DISTINCT class_id, class_name, grade_name
                    FROM {6}
                    WHERE dt = {2}
                ) t4 ON t3.grade_name = t4.grade_name AND t3.class_name = t4.class_name
            ) t2 ON t1.camera_id = t2.class_id AND  t1.pose_stat_time >= t2.start_time AND t1.pose_stat_time <= t2.end_time
        '''.format('1550676', '1550763', '20190221', Config.INTERMEDIATE_RES_TABLE, Config.SCHOOL_COURSE_TABLE, Config.INTERMEDIATE_TABLE_TRAIN, Config.SCHOOL_CAMERA_CLASS_TABLE)

        for row in self.__db.select(sql):
            print row

if __name__ == '__main__':
    doer = TestData()
    doer.test_sql()