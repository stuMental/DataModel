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
        self.truncate_data(start_time, end_time, day)
        self.update_face_id(start_time, end_time)
        self.update_face_id_step2(start_time, end_time)
        # self.update_body_id(start_time, end_time)
        self.update_status(start_time, end_time)
        self.update_face_pose_state(start_time, end_time)
        # self.do_filter(start_time, end_time) TODO(xufeng)
        self.update_course(start_time, end_time)
        self.stat_attendance(start_time, end_time, day)

    def truncate_data(self, start_time, end_time, day):
        '''Truncate all data of intermediate tables'''
        self.__logger.info("Try to truncate all data of intermediate tables in {0}".format(Config.INPUT_DB_DATABASE))

        m_tables = [Config.INTERMEDIATE_TRACK_TABLE, Config.INTERMEDIATE_TABLE, Config.INTERMEDIATE_RES_TABLE]

        for table_name in m_tables:
            self.__logger.info("Begin to truncate {0}".format(table_name))
            sql = '''
                TRUNCATE TABLE {0}
            '''.format(table_name)
            self.__db.truncate(sql)
            self.__logger.info("End to truncate {0}".format(table_name))

        # 对于Config.INTERMEDIATE_TABLE_TRAIN，我们需要保留历史数据(半年) 便于计算人际关系和课堂兴趣
        self.__logger.info("Begin to delete unnecessary data for the table {0}.".format(Config.INTERMEDIATE_TABLE_TRAIN))
        sql = '''
            DELETE FROM {0} WHERE (pose_stat_time >= {1} AND pose_stat_time < {2}) OR (pose_stat_time < {3})
        '''.format(Config.INTERMEDIATE_TABLE_TRAIN, start_time, end_time, CommonUtil.get_specific_unixtime(start_time, Config.DATA_RESERVED_WINDOW))
        self.__db.delete(sql)
        self.__logger.info("End to delete unnecessary data for the table {0}.".format(Config.INTERMEDIATE_TABLE_TRAIN))

        # 删除学生出勤表中的数据
        self.__logger.info("Begin to delete unnecessary data from the table {0}.".format(Config.STUDENT_ATTENDANCE))
        sql = '''
            DELETE FROM {0} WHERE dt = '{1}'
        '''.format(Config.STUDENT_ATTENDANCE, day)
        self.__db.delete(sql)
        self.__logger.info("End to delete unnecessary data from the table {0}.".format(Config.STUDENT_ATTENDANCE))

        # 清空Config.SCHOOL_STUDENT_CLASS_TABLE中所有student_name中带有嘉宾符号的数据
        sql = '''
            DELETE FROM {0} WHERE student_name LIKE '%{1}%'
        '''.format(Config.SCHOOL_STUDENT_CLASS_TABLE, Config.PREFIX_GUEST)
        self.__db.delete(sql)
        self.__logger.info("End to delete all 嘉宾 records");
        self.__logger.info("End to truncate or delete all data of intermediate tables in {0}".format(Config.INPUT_DB_DATABASE))


    def update_face_id(self, start_time, end_time):
        ''' Update face_id accroding to face_track '''
        self.__logger.info("Try to update face_id based on face_track, then output results to the table {0}".format(Config.INTERMEDIATE_TRACK_TABLE))

    #TODO(xufeng):解决同一个track被识别为多个人的问题，目前是将这样的track直接舍弃
        sql = '''
            INSERT INTO {3}
            SELECT t1.camera_id, t1.frame_id, t1.body_id, t1.body_stat, t1.body_track, t2.face_id, t1.face_track, t1.face_pose, t1.face_pose_stat, t1.face_pose_stat_time, t1.face_emotion, t1.yawn, t1.unix_timestamp, t1.pose_stat_time
            FROM (
                SELECT *
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
                        SELECT camera_id, face_track, count(distinct face_id) as face_num
                        FROM {2}
                        WHERE face_id != 'unknown' AND face_track != 'unknown' AND pose_stat_time >= {0} AND pose_stat_time < {1}
                        GROUP BY camera_id, face_track
                    HAVING face_num = 1
                    )t22 ON t21.camera_id=t22.camera_id AND t21.face_track=t22.face_track
            )t2 ON t1.camera_id=t2.camera_id AND t1.face_track=t2.face_track
        '''.format(start_time, end_time, Config.RAW_INPUT_TABLE, Config.INTERMEDIATE_TRACK_TABLE)

        self.__db.insert(sql)
        self.__logger.info("[Step1] Finish to update face_id")

    def update_face_id_step2(self, start_time, end_time):
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

    #TODO(xufeng):解决同一个track被识别为多个人的问题，目前是将这样的track直接舍弃
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

    #将camera_id转化为class_id
    def update_status(self, start_time, end_time):
        ''' Update body_stat, face_pose and face_emotion by pose_stat_time '''
        self.__logger.info("Try to choose body_stat, face_pose, face_emotion, then output results to the table {0}".format(Config.INTERMEDIATE_TABLE))

        sql = '''
            INSERT INTO {2}
            SELECT class_id, face_id, pose_stat_time, face_pose_stat_time, MAX(body_stat) AS body_stat, MAX(face_pose) AS face_pose, MAX(face_emotion) AS face_emotion
            FROM (
                SELECT t2.class_id, t1.camera_id, t1.face_id, t1.pose_stat_time, t1.face_pose_stat_time, t1.body_stat, t1.face_pose, t1.face_emotion
                FROM (
                        SELECT camera_id, face_id, pose_stat_time, face_pose_stat_time, MAX(body_stat) AS body_stat, MAX(face_pose) AS face_pose, MAX(face_emotion) AS face_emotion
                        FROM {3}
                        WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND face_id != 'unknown'
                        GROUP BY camera_id, face_id, pose_stat_time, face_pose_stat_time
                )t1 JOIN (
                    SELECT camera_id, class_id
                    FROM {4}
                )t2 ON t1.camera_id=t2.camera_id
            )t3
            GROUP BY class_id, face_id, pose_stat_time, face_pose_stat_time # 有可能一个教室多个摄像头 所以需要再执行一次GROUP BY语句
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE, Config.INTERMEDIATE_TRACK_TABLE, Config.SCHOOL_CAMERA_CLASS_TABLE)

        self.__db.insert(sql)
        self.__logger.info("Finish to update")

    def update_face_pose_state(self, start_time, end_time):
        '''
            Judge if a face pose is normal based on all face pose data
            class_id stands for a classroom because each classroom has a different class_id
        '''
        self.__logger.info("Try to update face_pose_stat, then output results to the table {0}".format(Config.INTERMEDIATE_RES_TABLE))

        sql = '''
            INSERT INTO {3}
            SELECT t5.class_id, t5.face_id, t5.pose_stat_time, t5.body_stat, t5.face_pose, t5.face_emotion, 
                   (CASE WHEN t6.face_pose IS NULL THEN '1' ELSE '0' END) AS face_pose_stat
            FROM (
                SELECT class_id, face_id, pose_stat_time, face_pose_stat_time, body_stat, face_pose, face_emotion
                FROM {2}
                WHERE pose_stat_time >= {0} AND pose_stat_time < {1}
            )t5 LEFT OUTER JOIN (
                SELECT class_id, face_pose_stat_time, MIN(face_pose) AS face_pose
                FROM (
                SELECT t2.class_id, t2.face_pose_stat_time, t2.face_pose, t2.num
                FROM (
                    SELECT class_id, face_pose_stat_time, face_pose, COUNT(*) AS num
                    FROM {2}
                    WHERE face_pose != '-1' AND pose_stat_time >= {0} AND pose_stat_time < {1}
                    GROUP BY class_id, face_pose_stat_time, face_pose
                )t2 JOIN (
                    SELECT class_id, face_pose_stat_time, MAX(num) AS num
                    FROM (
                    SELECT class_id, face_pose_stat_time, face_pose, COUNT(*) AS num
                    FROM {2}
                    WHERE face_pose != '-1' AND pose_stat_time >= {0} AND pose_stat_time < {1}
                    GROUP BY class_id, face_pose_stat_time, face_pose
                    )t1 
                    GROUP BY class_id, face_pose_stat_time
                )t3
                ON t2.class_id=t3.class_id AND t2.face_pose_stat_time=t3.face_pose_stat_time AND t2.num=t3.num
                )t4
                GROUP BY class_id, face_pose_stat_time, num
            )t6
            ON t5.class_id=t6.class_id AND t5.face_pose_stat_time=t6.face_pose_stat_time AND t5.face_pose=t6.face_pose
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE, Config.INTERMEDIATE_RES_TABLE)

        self.__db.insert(sql)
        self.__logger.info('Finish update')

    def update_course(self, start_time, end_time):
        ''''''
        # 需要解决 不同的class_id在同一时间段对应不同的course_name
        self.__logger.info("Try to insert course according to class_id and timespan, then output results to the table {0}".format(Config.INTERMEDIATE_TABLE_TRAIN))

        sql = '''
            INSERT INTO {4}
            SELECT t1.class_id, t1.face_id, t1.pose_stat_time, t1.body_stat, t1.face_pose, t1.face_emotion, t1.face_pose_stat,
                   (CASE WHEN t2.course_name IS NULL THEN 'rest' ELSE t2.course_name END) AS course_name
            FROM
            (
                SELECT class_id, face_id, pose_stat_time, body_stat, face_pose, face_emotion, face_pose_stat
                    FROM {2}
                    WHERE pose_stat_time >= {0} AND pose_stat_time < {1}
            ) t1 LEFT OUTER JOIN
            (
                SELECT
                    t4.class_id, t3.course_name, t3.start_time, t3.end_time, t3.weekday
                FROM
                (
                    SELECT grade_name, class_name, course_name, start_time, end_time, weekday
                    FROM {3}
                ) t3 LEFT OUTER JOIN
                (
                    SELECT
                        DISTINCT class_id, class_name, grade_name
                    FROM {5}
                ) t4 ON t3.grade_name = t4.grade_name AND t3.class_name = t4.class_name
            ) t2 ON t1.class_id = t2.class_id AND cast(from_unixtime(t1.pose_stat_time,'%H:%i') as time) >= t2.start_time AND cast(from_unixtime(t1.pose_stat_time,'%H:%i') as time) <= t2.end_time AND dayofweek(from_unixtime(t1.pose_stat_time)) = t2.weekday
        '''.format(start_time, end_time, Config.INTERMEDIATE_RES_TABLE, Config.SCHOOL_COURSE_TABLE, Config.INTERMEDIATE_TABLE_TRAIN, Config.SCHOOL_CAMERA_CLASS_TABLE)

        self.__db.insert(sql)
        self.__logger.info("Finish to update course_name")

    def stat_attendance(self, start_time, end_time, day):
        self.__logger.info("Try to stat attendance, then output results to the table {0}".format(Config.STUDENT_ATTENDANCE))

        sql = '''
            INSERT INTO {6}
            SELECT t5.course_name, t5.class_name, t5.grade_name, t5.start_time, t5.end_time, t5.student_number, t5.student_name, '{7}'
            FROM (
                SELECT t1.course_name, t1.class_name, t1.grade_name, t1.start_time, t1.end_time, t1.weekday, t2.student_number, t2.student_name
                FROM (
                    SELECT course_name, class_name, grade_name, start_time, end_time, weekday
                    FROM {3}
                    WHERE dayofweek(from_unixtime({0})) = weekday
                    )t1 JOIN (
                    SELECT class_name, grade_name, student_number, student_name
                    FROM {4}
                )t2 ON t1.class_name=t2.class_name AND t1.grade_name=t2.grade_name
            )t5 LEFT JOIN (
                SELECT t3.face_id, t3.pose_stat_time, t4.class_name, t4.grade_name
                FROM (
                        SELECT class_id, face_id, pose_stat_time
                        FROM {2}
                        WHERE pose_stat_time >= {0} AND pose_stat_time < {1}
                    )t3 JOIN (
                    SELECT DISTINCT class_id, class_name, grade_name
                    FROM {5}
                )t4 ON t3.class_id=t4.class_id
            )t6 ON t5.student_number=t6.face_id AND cast(from_unixtime(t6.pose_stat_time,'%H:%i') as time) <= t5.end_time AND cast(from_unixtime(t6.pose_stat_time,'%H:%i') as time) >= t5.start_time AND dayofweek(from_unixtime(t6.pose_stat_time)) = t5.weekday AND t5.class_name=t6.class_name AND t5.grade_name=t6.grade_name
            WHERE t6.face_id IS NULL
        '''.format(start_time, end_time, Config.INTERMEDIATE_RES_TABLE, Config.SCHOOL_COURSE_TABLE, Config.SCHOOL_STUDENT_CLASS_TABLE, Config.SCHOOL_CAMERA_CLASS_TABLE, Config.STUDENT_ATTENDANCE, day)

        self.__db.insert(sql)
        self.__logger.info("Finish to stat_attendance")
