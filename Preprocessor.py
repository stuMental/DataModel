# !/usr/bin/python
# -*- coding: utf-8 -*-

import DbUtil
import Config
import Logger
from CommonUtil import CommonUtil

class Preprocessor(object):
    """docsTry for Preprocessor"""
    def __init__(self, configs):
        super(Preprocessor, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)

    def preprocessor(self, start_time, end_time, day):
        CommonUtil.verify()
        self.truncate_data(start_time, end_time, day)
        self.update_face_id(start_time, end_time)
        self.update_status(start_time, end_time)
        self.update_course(start_time, end_time, day)
        self.update_student_info(start_time, end_time, day)
        self.stat_attendance(start_time, end_time, day)
        self.stat_exist_attendance(day)

    def truncate_data(self, start_time, end_time, day):
        '''Truncate all data of intermediate tables'''
        self.__logger.info("Try to truncate all data of intermediate tables in {0}".format(Config.INPUT_DB_DATABASE))

        self.__logger.info('Begin to delete raw log for the table {0}'.format(Config.RAW_INPUT_TABLE))
        sql = '''
            DELETE a FROM {0} a WHERE pose_stat_time < {1}
        '''.format(Config.RAW_INPUT_TABLE, CommonUtil.get_specific_unixtime(start_time, Config.DATA_RESERVED_RAW_WINDOW))
        self.__db.delete(sql)
        self.__logger.info("Deleted raw log for the table {0}".format(Config.RAW_INPUT_TABLE))

        logs = [Config.INTERMEDIATE_TRACK_TABLE, Config.INTERMEDIATE_TABLE, Config.INTERMEDIATE_COURSE_TABLE]
        for table_name in logs:
            self.__logger.info("Begin to drop {0}".format(table_name))
            sql = '''
                DROP TABLE {0}
            '''.format(table_name)
            self.__db.truncate(sql)
            self.__logger.info("End to drop {0}".format(table_name))

        # 对于Config.INTERMEDIATE_TABLE_TRAIN，我们需要保留历史数据(半年) 便于计算人际关系和课堂兴趣
        self.__logger.info("Begin to delete unnecessary data for the table {0}.".format(Config.INTERMEDIATE_TABLE_TRAIN))
        sql = '''
            DELETE a FROM {0} a WHERE (pose_stat_time >= {1} AND pose_stat_time < {2}) OR (pose_stat_time < {3})
        '''.format(Config.INTERMEDIATE_TABLE_TRAIN, start_time, end_time, CommonUtil.get_specific_unixtime(start_time, Config.DATA_RESERVED_WINDOW))
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

    def update_face_id(self, start_time, end_time):
        ''' Update face_id accroding to face_track '''
        self.__logger.info("Try to update face_id based on face_track, then output results to the table {0}".format(Config.INTERMEDIATE_TRACK_TABLE))

        # TODO(xufeng):解决同一个track被识别为多个人的问题，目前是将这样的track直接舍弃
        sql = '''
            CREATE TABLE {3}
            SELECT
                t1.camera_id, t1.body_stat, t2.face_id, t1.face_track, t1.face_pose, t1.face_emotion, t1.pose_stat_time
            FROM (
                SELECT camera_id, body_stat, face_track, face_pose, face_emotion, pose_stat_time
                FROM {2}
                    WHERE face_track != 'unknown' AND pose_stat_time >= {0} AND pose_stat_time < {1}
                )t1 JOIN (
                    SELECT t21.camera_id, t21.face_track, t21.face_id
                    FROM (
                        SELECT camera_id, face_track, face_id
                        FROM {2}
                        WHERE face_id != 'unknown' AND face_track != 'unknown' AND pose_stat_time >= {0} AND pose_stat_time < {1}
                        GROUP BY camera_id, face_track, face_id
                    )t21 JOIN (
                        SELECT camera_id, face_track, count(DISTINCT face_id) as face_num
                        FROM {2}
                        WHERE face_id != 'unknown' AND face_track != 'unknown' AND pose_stat_time >= {0} AND pose_stat_time < {1}
                        GROUP BY camera_id, face_track
                    HAVING face_num = 1
                    )t22 ON t21.camera_id=t22.camera_id AND t21.face_track=t22.face_track
            )t2 ON t1.camera_id=t2.camera_id AND t1.face_track=t2.face_track
        '''.format(start_time, end_time, Config.RAW_INPUT_TABLE, Config.INTERMEDIATE_TRACK_TABLE)

        self.__db.insert(sql)
        self.__logger.info("[Step1] Finish to update face_id")

        self.__logger.info("[Update face_id] add index")
        self.__db.execute("CREATE INDEX pose_stat_time_index ON {0} (pose_stat_time);".format(Config.INTERMEDIATE_TRACK_TABLE))
        self.__db.execute("CREATE INDEX camera_id_index ON {0} (camera_id);".format(Config.INTERMEDIATE_TRACK_TABLE))
        self.__db.execute("CREATE INDEX face_id_index ON {0} (face_id);".format(Config.INTERMEDIATE_TRACK_TABLE))

    def update_face_id_guest(self, start_time, end_time):
        '''
            用face_track去更新对应的face_id
            针对嘉宾的特殊处理
        '''
        self.__logger.info("[Step2] Begin to update face_id with face_track.")
        sql = '''
            INSERT INTO {3}
            SELECT t1.camera_id, t1.frame_id, t1.body_id, t1.body_stat, t1.body_track, t1.face_track AS face_id, t1.face_track, t1.face_pose, t1.face_pose_stat, t1.face_pose_stat_time, t1.face_emotion, t1.yawn, t1.unix_timestamp, t1.pose_stat_time
            FROM
            (
                SELECT * FROM {2}
                WHERE face_track != 'unknown' AND face_id = 'unknown' and pose_stat_time >= {0} and pose_stat_time < {1}
            ) t1 JOIN (
                SELECT t21.camera_id, t21.face_track FROM
                (
                    SELECT camera_id, face_track FROM {2}
                    WHERE face_track != 'unknown' AND face_id = 'unknown' and pose_stat_time >= {0} and pose_stat_time < {1}
                ) t21 LEFT OUTER JOIN (
                    SELECT camera_id, face_track FROM {3}
                    GROUP BY camera_id, face_track
                ) t22 ON t21.camera_id = t22.camera_id AND t21.face_track = t22.face_track
                WHERE t22.face_track IS NULL
                GROUP BY camera_id, face_track
                HAVING COUNT(*) >= {4}
            ) t2 ON t1.camera_id = t2.camera_id AND t1.face_track = t2.face_track
        '''.format(start_time, end_time, Config.RAW_INPUT_TABLE, Config.INTERMEDIATE_TRACK_TABLE, Config.FACETRACK_MININUM_LIMITATION)
        self.__db.insert(sql)
        self.__logger.info("[Step2] Finish to update face_id with face_track.")

    def update_body_id(self, start_time, end_time):
        ''' Update body_id accroding to body_track '''
        self.__logger.info("Try to udpate body_id based on body_track")

        # TODO(xufeng):解决同一个track被识别为多个人的问题，目前是将这样的track直接舍弃
        sql = '''
            INSERT INTO {3}
            SELECT t1.camera_id, t1.frame_id, t1.body_id, t1.body_stat, t1.body_track, t2.face_id, t1.face_track, t1.face_pose, t1.face_pose_stat, t1.face_pose_stat_time, t1.face_emotion, t1.yawn, t1.unix_timestamp, t1.pose_stat_time
            FROM (
                SELECT *
                FROM {2}
                    WHERE body_track != 'unknown' AND pose_stat_time >= {0} AND pose_stat_time < {1}
                )t1 JOIN (
                    SELECT camera_id, body_track, face_id, count(*) as face_num
                    FROM {2}
                    WHERE face_id != 'unknown' AND body_track != 'unknown' AND pose_stat_time >= {0} AND pose_stat_time < {1}
                    GROUP BY camera_id, body_track, face_id
                HAVING face_num = 1
            )t2 ON t1.camera_id=t2.camera_id AND t1.body_track=t2.body_track
        '''.format(start_time, end_time, Config.RAW_INPUT_TABLE, Config.INTERMEDIATE_TRACK_TABLE)

        self.__db.insert(sql)
        self.__logger("Finish to update body_id")

    # 将camera_id转化为room_addr
    def update_status(self, start_time, end_time):
        ''' Update body_stat, face_pose and face_emotion by pose_stat_time '''
        self.__logger.info("Try to choose body_stat, face_pose, face_emotion, then output results to the table {0}".format(Config.INTERMEDIATE_TABLE))

        sql = '''
            CREATE TABLE {2}
            SELECT
                room_addr, face_id, pose_stat_time, MAX(body_stat) AS body_stat, MAX(face_pose) AS face_pose, MAX(face_emotion) AS face_emotion
            FROM (
                SELECT t2.room_addr, t1.camera_id, t1.face_id, t1.pose_stat_time, t1.body_stat, t1.face_pose, t1.face_emotion
                FROM (
                        SELECT camera_id, face_id, pose_stat_time, MAX(body_stat) AS body_stat, MAX(face_pose) AS face_pose, MAX(face_emotion) AS face_emotion
                        FROM {3}
                        WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND face_id != 'unknown'
                        GROUP BY camera_id, face_id, pose_stat_time
                )t1 JOIN (
                    SELECT camera_id, room_id, room_addr
                    FROM {4}
                )t2 ON t1.camera_id=t2.camera_id
            )t3
            GROUP BY room_addr, face_id, pose_stat_time # 有可能一个教室多个摄像头 所以需要再执行一次GROUP BY语句
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE, Config.INTERMEDIATE_TRACK_TABLE, Config.SCHOOL_CAMERA_ROOM_TABLE)

        self.__db.insert(sql)
        self.__logger.info("Finish to update")

        self.__logger.info("[Update status] add index")
        self.__db.execute("CREATE INDEX pose_stat_time_index ON {0} (pose_stat_time);".format(Config.INTERMEDIATE_TABLE))
        self.__db.execute("CREATE INDEX room_addr_index ON {0} (room_addr);".format(Config.INTERMEDIATE_TABLE))

    def update_face_pose_state(self, start_time, end_time):
        '''
            Judge if a face pose is normal based on all face pose data
            room_addr stands for a classroom
        '''
        self.__logger.info("Try to update face_pose_stat, then output results to the table {0}".format(Config.INTERMEDIATE_RES_TABLE))

        sql = '''
            INSERT INTO {3}
            SELECT t5.room_addr, t5.face_id, t5.pose_stat_time, t5.body_stat, t5.face_pose, t5.face_emotion,
                   (CASE WHEN t6.face_pose IS NULL THEN '1' ELSE '0' END) AS face_pose_stat
            FROM (
                SELECT room_addr, face_id, pose_stat_time, face_pose_stat_time, body_stat, face_pose, face_emotion
                FROM {2}
                WHERE pose_stat_time >= {0} AND pose_stat_time < {1}
            )t5 LEFT OUTER JOIN (
                SELECT room_addr, face_pose_stat_time, MIN(face_pose) AS face_pose
                FROM (
                SELECT t2.room_addr, t2.face_pose_stat_time, t2.face_pose, t2.num
                FROM (
                    SELECT room_addr, face_pose_stat_time, face_pose, COUNT(*) AS num
                    FROM {2}
                    WHERE face_pose != '-1' AND pose_stat_time >= {0} AND pose_stat_time < {1}
                    GROUP BY room_addr, face_pose_stat_time, face_pose
                )t2 JOIN (
                    SELECT room_addr, face_pose_stat_time, MAX(num) AS num
                    FROM (
                    SELECT room_addr, face_pose_stat_time, face_pose, COUNT(*) AS num
                    FROM {2}
                    WHERE face_pose != '-1' AND pose_stat_time >= {0} AND pose_stat_time < {1}
                    GROUP BY room_addr, face_pose_stat_time, face_pose
                    )t1
                    GROUP BY room_addr, face_pose_stat_time
                )t3
                ON t2.room_addr=t3.room_addr AND t2.face_pose_stat_time=t3.face_pose_stat_time AND t2.num=t3.num
                )t4
                GROUP BY room_addr, face_pose_stat_time, num
            )t6
            ON t5.room_addr=t6.room_addr AND t5.face_pose_stat_time=t6.face_pose_stat_time AND t5.face_pose=t6.face_pose
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE, Config.INTERMEDIATE_RES_TABLE)

        self.__db.insert(sql)
        self.__logger.info('Finish update')

    def update_course(self, start_time, end_time, day):
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
                    room_addr, face_id, pose_stat_time, body_stat, face_pose, face_emotion
                FROM {2}
                WHERE pose_stat_time >= {0} AND pose_stat_time < {1}
            ) t1 LEFT OUTER JOIN
            (
                SELECT
                    room_addr, course_id, course_name, start_time, end_time
                FROM {3}
                WHERE weekday = dayofweek('{5}')
                GROUP BY room_addr, course_id, course_name, start_time, end_time
            ) t2 ON t1.room_addr = t2.room_addr AND cast(from_unixtime(t1.pose_stat_time,'%H:%i') as time) >= t2.start_time AND cast(from_unixtime(t1.pose_stat_time,'%H:%i') as time) <= t2.end_time
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE, Config.SCHOOL_STUDENT_COURSE_TABLE, Config.INTERMEDIATE_COURSE_TABLE, day)

        self.__db.insert(sql)
        self.__logger.info("Finish to update course_name")

        self.__logger.info("[Update course] add index")
        self.__db.execute("CREATE INDEX pose_stat_time_index ON {0} (pose_stat_time);".format(Config.INTERMEDIATE_COURSE_TABLE))
        self.__db.execute("CREATE INDEX face_id_index ON {0} (face_id);".format(Config.INTERMEDIATE_COURSE_TABLE))

    def update_student_info(self, start_time, end_time, day):
        """ 关联学生信息
        """

        self.__logger.info("Try to insert student info which includes colleage, grade, and class, then output results to the table {0}".format(Config.INTERMEDIATE_TABLE_TRAIN))

        sql = '''
            INSERT INTO {4}
            SELECT
                t1.room_addr, t1.face_id, t1.pose_stat_time, t1.body_stat, t1.face_pose, t1.face_emotion, t1.course_id, t1.course_name, t2.college_name, t2.grade_name, t2.class_name
            FROM
            (
                SELECT * FROM {2}
                WHERE pose_stat_time >= {0} AND pose_stat_time < {1}
            ) t1 JOIN
            (
                SELECT
                    student_number, college_name, grade_name, class_name
                FROM {3}
                WHERE weekday = dayofweek('{5}')
                GROUP BY student_number, college_name, grade_name, class_name
            ) t2 ON t1.face_id = t2.student_number
        '''.format(start_time, end_time, Config.INTERMEDIATE_COURSE_TABLE, Config.SCHOOL_STUDENT_COURSE_TABLE, Config.INTERMEDIATE_TABLE_TRAIN, day)

        self.__db.insert(sql)
        self.__logger.info("Finish to update student info")

    def stat_attendance(self, start_time, end_time, day):
        self.__logger.info("Try to stat attendance, then output results to the table {0}".format(Config.STUDENT_ATTENDANCE))

        sql = '''
            INSERT INTO {4}
            SELECT t5.room_addr, t5.course_id, t5.course_name, t5.college_name, t5.class_name, t5.grade_name, t5.start_time, t5.end_time, t5.student_number, t5.student_name, t5.teacher_id, t5.teacher_name, '{5}'
            FROM (
                SELECT
                    room_addr, course_id, course_name, college_name, class_name, grade_name, start_time, end_time, student_number, student_name, teacher_id, teacher_name
                FROM {3}
                WHERE weekday = dayofweek('{5}')
            )t5 LEFT JOIN (
                SELECT room_addr, face_id, pose_stat_time
                FROM {2}
                WHERE pose_stat_time >= {0} AND pose_stat_time < {1}
            )t6 ON t5.student_number=t6.face_id AND cast(from_unixtime(t6.pose_stat_time,'%H:%i') as time) <= t5.end_time AND cast(from_unixtime(t6.pose_stat_time,'%H:%i') as time) >= t5.start_time AND t5.room_addr = t6.room_addr
            WHERE t6.face_id IS NULL
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN, Config.SCHOOL_STUDENT_COURSE_TABLE, Config.STUDENT_ATTENDANCE, day)

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
