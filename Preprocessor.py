# !/usr/bin/python
# -*- coding: utf-8 -*-

import DbUtil
import Config
import Logger
from CommonUtil import CommonUtil


class Preprocessor(object):
    """预处理raw数据"""
    def __init__(self, configs):
        super(Preprocessor, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)
        self.__multi = configs['multi']

    def preprocessor(self, day):
        CommonUtil.verify()
        self.truncate_data(day)
        self.update_face_id()
        self.update_course(day)
        self.preprocess_aggregate(day)
        self.update_student_info(day)

    def truncate_data(self, day):
        '''Truncate all data of intermediate tables'''
        self.__logger.info("Try to truncate all data of intermediate tables in {0}".format(Config.INPUT_DB_DATABASE))
        tmp_tables = [Config.INTERMEDIATE_TRACK_TABLE, Config.INTERMEDIATE_TABLE, Config.INTERMEDIATE_COURSE_TABLE, Config.INTERMEDIATE_AGG_TABLE]
        for table_name in tmp_tables:
            self.__logger.info("Begin to drop {0}".format(table_name))
            sql = '''
                DROP TABLE {0}
            '''.format(table_name)
            self.__db.truncate(sql)
            self.__logger.info("End to drop {0}".format(table_name))

        # 对于Config.INTERMEDIATE_TABLE_TRAIN，我们需要保留历史数据(半年) 便于计算人际关系和课堂兴趣
        self.__logger.info("Begin to delete unnecessary data for the table {0}.".format(Config.INTERMEDIATE_TABLE_TRAIN))
        sql = '''
            DELETE a FROM {0} a WHERE dt = '{1}' OR dt < '{2}'
        '''.format(Config.INTERMEDIATE_TABLE_TRAIN, day, CommonUtil.get_specific_date(day, Config.DATA_RESERVED_WINDOW))
        self.__db.delete(sql)
        self.__logger.info("End to delete unnecessary data for the table {0}.".format(Config.INTERMEDIATE_TABLE_TRAIN))

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

    def update_face_id(self):
        ''' Update face_id accroding to face_track '''
        self.__logger.info("Try to update face_id based on face_track, then output results to the table {0}".format(Config.INTERMEDIATE_TRACK_TABLE))

        # TODO(xufeng):解决同一个track被识别为多个人的问题，目前是将这样的track直接舍弃
        sql = '''
            CREATE TABLE {1}
            SELECT
                t1.camera_id, t1.body_stat, t2.face_id, t1.face_track, t1.face_pose, t1.face_emotion, t1.pose_stat_time
            FROM (
                SELECT
                    camera_id, body_stat, face_track, face_pose, face_emotion, pose_stat_time
                FROM {0}
                    WHERE face_track != 'unknown'
                )t1 JOIN (
                    SELECT
                        t21.camera_id, t21.face_track, t21.face_id
                    FROM (
                        SELECT
                            camera_id, face_track, face_id
                        FROM {0}
                        WHERE face_id != 'unknown' AND face_track != 'unknown'
                        GROUP BY camera_id, face_track, face_id
                    )t21 JOIN (
                        SELECT
                            camera_id, face_track, count(DISTINCT face_id) as face_num
                        FROM {0}
                        WHERE face_id != 'unknown' AND face_track != 'unknown'
                        GROUP BY camera_id, face_track
                        HAVING face_num = 1
                    )t22 ON t21.camera_id=t22.camera_id AND t21.face_track=t22.face_track
            )t2 ON t1.camera_id=t2.camera_id AND t1.face_track=t2.face_track
        '''.format(Config.RAW_INPUT_TABLE, Config.INTERMEDIATE_TRACK_TABLE)

        self.__db.insert(sql)
        self.__logger.info("[Step1] Finish to update face_id")

        self.__logger.info("[Update face_id] add index")
        self.__db.execute("CREATE INDEX pose_stat_time_index ON {0} (pose_stat_time);".format(Config.INTERMEDIATE_TRACK_TABLE))
        self.__db.execute("CREATE INDEX camera_id_index ON {0} (camera_id);".format(Config.INTERMEDIATE_TRACK_TABLE))

    def update_course(self, day):
        '''关联课程信息
        '''

        self.__logger.info("Try to insert course according to room_addr and timespan, then output results to the table {0}".format(Config.INTERMEDIATE_COURSE_TABLE))

        sql = '''
            CREATE TABLE {4}
            SELECT
                t1.room_addr, t1.face_id, t1.pose_stat_time, t1.body_stat, t1.face_pose, t1.face_emotion, (CASE WHEN t2.course_id IS NULL THEN '-1' ELSE t2.course_id END) AS course_id, (CASE WHEN t2.course_name IS NULL THEN 'rest' ELSE t2.course_name END) AS course_name
            FROM
            (
                SELECT
                    t4.room_addr, t3.face_id, t3.pose_stat_time, t3.body_stat, t3.face_pose, t3.face_emotion
                FROM {0} t3 JOIN {1} t4
                ON t3.camera_id = t4.camera_id
            ) t1 LEFT OUTER JOIN
            (
                SELECT
                    room_addr, course_id, course_name, start_time, end_time
                FROM {2}
                WHERE weekday = dayofweek('{3}')
                GROUP BY room_addr, course_id, course_name, start_time, end_time
            ) t2 ON t1.room_addr = t2.room_addr AND cast(from_unixtime(t1.pose_stat_time,'%H:%i') as time) >= t2.start_time AND cast(from_unixtime(t1.pose_stat_time,'%H:%i') as time) <= t2.end_time
        '''.format(Config.INTERMEDIATE_TRACK_TABLE, Config.SCHOOL_CAMERA_ROOM_TABLE, Config.SCHOOL_STUDENT_COURSE_TABLE, day, Config.INTERMEDIATE_COURSE_TABLE)

        self.__db.insert(sql)
        self.__logger.info("Finish to update course_name")

        self.__logger.info("[Update course] add index")
        self.__db.execute("CREATE INDEX room_addr_index ON {0} (room_addr);".format(Config.INTERMEDIATE_COURSE_TABLE))
        self.__db.execute("CREATE INDEX face_id_index ON {0} (face_id);".format(Config.INTERMEDIATE_COURSE_TABLE))
        self.__db.execute("CREATE INDEX course_name_index ON {0} (course_name);".format(Config.INTERMEDIATE_COURSE_TABLE))

    def preprocess_aggregate(self, day):
        """ 预聚合信息
        """

        self.__logger.info("Try to pre-aggrate the data, then output results to the table {0}".format(Config.INTERMEDIATE_AGG_TABLE))
        sql = '''
            CREATE TABLE {1}
            SELECT
                room_addr, course_id, course_name, face_id, action, total, action_type, dt
            FROM (
                SELECT
                    room_addr, course_id, course_name, face_id, body_stat AS action, COUNT(*) AS total, {3} AS action_type, '{2}' AS dt
                FROM {0}
                WHERE body_stat != '-1'
                GROUP BY room_addr, course_id, course_name, face_id, body_stat
                UNION
                SELECT
                    room_addr, course_id, course_name, face_id, face_pose AS action, COUNT(*) AS total, {4} AS action_type, '{2}' AS dt
                FROM {0}
                WHERE face_pose != '-1'
                GROUP BY room_addr, course_id, course_name, face_id, face_pose
                UNION
                SELECT
                    room_addr, course_id, course_name, face_id, face_emotion AS action, COUNT(*) AS total, {5} AS action_type, '{2}' AS dt
                FROM {0}
                WHERE face_emotion != '-1'
                GROUP BY room_addr, course_id, course_name, face_id, face_emotion
            ) t
        '''.format(Config.INTERMEDIATE_COURSE_TABLE, Config.INTERMEDIATE_AGG_TABLE, day, Config.ACTION_TYPE['body_stat'], Config.ACTION_TYPE['face_pose'], Config.ACTION_TYPE['face_emotion'])
        self.__db.insert(sql)
        self.__logger.info("Finish to update student info")

        self.__logger.info("[pre-aggregation] add index")
        self.__db.execute("CREATE INDEX face_id_index ON {0} (face_id);".format(Config.INTERMEDIATE_AGG_TABLE))

    def update_student_info(self, day):
        """ 关联学生信息
        """

        self.__logger.info("Try to insert student info which includes colleage, grade, and class, then output results to the table {0}".format(Config.INTERMEDIATE_TABLE_TRAIN))
        sql = '''
            INSERT INTO {2}
            SELECT
                t1.room_addr, t1.course_id, t1.course_name, t2.college_name, t2.grade_name, t2.class_name, t1.face_id, t1.action, t1.total, t1.action_type, '{3}'
            FROM
            (
                SELECT * FROM {0}
            ) t1 JOIN
            (
                SELECT
                    student_number, college_name, grade_name, class_name
                FROM {1}
                WHERE weekday = dayofweek('{3}')
                GROUP BY student_number, college_name, grade_name, class_name
            ) t2 ON t1.face_id = t2.student_number
        '''.format(Config.INTERMEDIATE_AGG_TABLE, Config.SCHOOL_STUDENT_COURSE_TABLE, Config.INTERMEDIATE_TABLE_TRAIN, day)

        self.__db.insert(sql)
        self.__logger.info("Finish to update student info")


if __name__ == "__main__":
    configs = {
        'dbhost': '172.16.14.190',
        'multi': 0
    }

    processor = Preprocessor(configs)
    processor.preprocessor('2019-07-16')