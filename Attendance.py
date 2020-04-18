# !/usr/bin/python
# -*- coding: utf-8 -*-

import DbUtil
import Config
import Logger
from CommonUtil import CommonUtil


class Attendance(object):
    """处理学生的考勤信息"""
    def __init__(self, configs):
        super(Attendance, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)
        self.__date = configs['date']

    def process(self, day):
        CommonUtil.verify()
        if self.__date != '-1':
            day = self.__date

        self.truncate_data(day)
        self.stat_attendance(day)
        self.stat_exist_attendance(day)

    def truncate_data(self, day):
        '''Truncate all data of intermediate tables'''
        # 删除学生出勤相关数据
        attendances = [Config.STUDENT_ATTENDANCE, Config.STUDENT_ATTENDANCE_EXIST]
        for table_name in attendances:
            self.__logger.info("Begin to delete unnecessary data from the table {0}.".format(table_name))
            sql = '''
                DELETE a FROM {0} a WHERE dt = '{1}' OR dt < '{2}'
            '''.format(table_name, day, CommonUtil.get_specific_date(day, Config.DATA_RESERVED_ATTENDANCE_WINDOW))
            self.__db.delete(sql)
            self.__logger.info("End to delete unnecessary data from the table {0}.".format(table_name))

        self.__logger.info("End to truncate or delete all data of intermediate tables in {0}".format(Config.INPUT_DB_DATABASE))

    def stat_attendance(self, day):
        self.__logger.info("Try to stat attendance, then output results to the table {0}".format(Config.STUDENT_ATTENDANCE))

        sql = '''
            INSERT INTO {2}
            SELECT t5.room_addr, t5.course_id, t5.course_name, t5.college_name, t5.class_name, t5.grade_name, t5.start_time, t5.end_time, t5.student_number, t5.student_name, t5.teacher_id, t5.teacher_name, '{4}'
            FROM (
                SELECT
                    room_addr, course_id, course_name, college_name, class_name, grade_name, start_time, end_time, student_number, student_name, teacher_id, teacher_name
                FROM {1}
                WHERE weekday = dayofweek('{4}')
            )t5 LEFT JOIN (
                SELECT t2.room_addr, t1.face_id, t1.pose_stat_time
                FROM (
                    SELECT
                        camera_id, face_id, pose_stat_time
                    FROM {0}
                    WHERE face_id != 'unknown'
                ) t1 JOIN {3} t2
                ON t1.camera_id = t2.camera_id
            )t6 ON t5.student_number=t6.face_id AND cast(from_unixtime(t6.pose_stat_time,'%H:%i') as time) <= t5.end_time AND cast(from_unixtime(t6.pose_stat_time,'%H:%i') as time) >= t5.start_time AND t5.room_addr = t6.room_addr
            WHERE t6.face_id IS NULL
        '''.format(Config.RAW_INPUT_TABLE, Config.SCHOOL_STUDENT_COURSE_TABLE, Config.STUDENT_ATTENDANCE, Config.SCHOOL_CAMERA_ROOM_TABLE, day)

        self.__db.insert(sql)
        self.__logger.info("Finish to compute stat_attendance")

    def stat_exist_attendance(self, day):
        self.__logger.info("Try to stat exist attendance, then output results to the table {0}".format(Config.STUDENT_ATTENDANCE_EXIST))

        sql = '''
            INSERT INTO {3}
            SELECT
                t3.room_addr, t3.course_id, t3.course_name, t3.college_name, t3.class_name, t3.grade_name, t3.start_time, t3.end_time, t3.student_number, t3.student_name, t3.teacher_id, t3.teacher_name, '{0}'
            FROM (
                SELECT
                   room_addr, course_id, course_name, college_name, class_name, grade_name, start_time, end_time, student_number, student_name, teacher_id, teacher_name
                FROM {1}
                WHERE weekday = dayofweek('{0}')
            ) t3 LEFT JOIN (
                SELECT * FROM {2} WHERE dt = '{0}'
            ) t4 ON t3.room_addr = t4.room_addr AND t3.course_name = t4.course_name AND t3.start_time = t4.start_time AND t3.end_time = t4.end_time AND t3.student_number = t4.student_number
            WHERE t4.student_number IS NULL
        '''.format(day, Config.SCHOOL_STUDENT_COURSE_TABLE, Config.STUDENT_ATTENDANCE, Config.STUDENT_ATTENDANCE_EXIST)

        self.__db.insert(sql)
        self.__logger.info("Finish to compute exist stat_attendance")


if __name__ == "__main__":
    configs = {
        'dbhost': '127.0.0.1'
    }
    processor = Attendance(configs)
    processor.process('2019-06-28')