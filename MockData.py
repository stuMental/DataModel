# !/usr/bin/python
# -*- coding: utf-8 -*-

import Config
import DbUtil
import Logger
import random
import datetime
import time
from CommonUtil import CommonUtil


class MockData(object):
    """MockData class"""
    def __init__(self, configs):
        super(MockData, self).__init__()
        self.__logger = Logger.Logger(__name__)
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD if configs['pwd'] is None else configs['pwd'], Config.INPUT_DB_DATABASE if configs['dbname'] is None else configs['dbname'], Config.INPUT_DB_CHARSET)
        self.__students = [['9001', '李小霖', '语文'], ['9002', '黄小莹', '英语'], ['9003', '贺小文', '数学'], ['9004', '梁小浩', '物理'], ['9005', '李小霞', '英语']]
        self.__classid = '201901'
        self.__grade = '2019'
        self.__class = '演示1班'
        self.__date = configs['date']
        self.__courses = ['语文', '英语', '数学', '物理', '化学', '德育']
        self.__times = [['09:00:00', '09:59:59'], ['10:00:00', '10:59:59'], ['11:00:00', '11:59:59'], ['14:00:00', '14:59:59'], ['15:00:00', '15:59:59'], ['16:00:00', '16:59:59']]

    def run(self):
        cur_dt = CommonUtil.get_date_day() if self.__date == '-1' else self.__date
        self.__db.delete("delete from student_mental_status_ld where dt = '{0}'".format(cur_dt))
        self.__db.delete("delete from student_mental_status_interest_daily where dt = '{0}".format(cur_dt))
        self.__db.delete("delete from student_mental_status_grade_study_daily where student_number in ('9001', '9002', '9003', '9004', '9005')")
        self.__db.delete("delete from school_student_attendance_info where dt = '{0}".format(cur_dt))
        # self.__db.delete("delete from school_student_attendance_exist_info where dt = '{0}".format(cur_dt))

        for item in self.__students:
            self.__logger.info('学生: {0}'.format(item[1]))
            student_relationship = str(random.randint(0,3))
            student_emotion = str(random.randint(0,2))
            student_mental_stat = str(random.randint(0,2))
            student_study_stat = str(random.randint(0,3))

            sql1 = '''
                insert  into `student_mental_status_ld`(`student_number`,`student_name`,`class_id`,`grade_name`,`class_name`,`student_relationship`,`student_emotion`,`student_mental_stat`,`student_study_stat`,`student_interest`,`dt`) values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}')
            '''.format(item[0], item[1], self.__classid, self.__grade, self.__class, student_relationship, student_emotion, student_mental_stat, student_study_stat, item[2], cur_dt)
            self.__db.insert(sql1)

            sql2 = '''
                insert  into `student_mental_status_interest_daily`(`student_number`,`student_name`,`class_id`,`grade_name`,`class_name`,`student_interest`,`dt`) values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')
            '''.format(item[0], item[1], self.__classid, self.__grade, self.__class, item[2], cur_dt)
            self.__db.insert(sql2)

            for index in range(0, len(self.__courses)):
                grade_level = str(round(random.uniform(-1,0.7), 2) if self.__courses[index] != item[2] else 0.75)
                study_level = str(round(random.uniform(-1,0.7), 2) if self.__courses[index] != item[2] else 0.85)
                sql3 = '''
                    insert  into `student_mental_status_grade_study_daily`(`student_number`,`course_name`,`grade_level`,`study_level`,`dt`) values ('{0}', '{1}', '{2}', '{3}', '{4}')
                '''.format(item[0], self.__courses[index], grade_level, study_level, cur_dt)
                self.__db.insert(sql3)

                sql5 = '''
                    insert  into `school_student_attendance_info`(`course_name`,`class_name`,`grade_name`,`start_time`,`end_time`,`student_number`,`student_name`,`dt`) values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')
                '''.format(self.__courses[index], self.__class, self.__grade, self.__times[index][0], self.__times[index][1], item[0], item[1], cur_dt)
                # sql6 = '''
                #     insert  into `school_student_attendance_exist_info`(`course_name`,`class_name`,`grade_name`,`start_time`,`end_time`,`student_number`,`student_name`,`dt`) values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')
                # '''.format(self.__courses[index], self.__class, self.__grade, self.__times[index][0], self.__times[index][1], item[0], item[1], cur_dt)
                seed = random.randint(1,10)
                if seed >= 8:
                    self.__db.insert(sql5)

            self.__logger.info('Done')


if __name__ == '__main__':
    obj = MockData(CommonUtil.parse_arguments())
    obj.run()
