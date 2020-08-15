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
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE if configs['dbname'] is None else configs['dbname'], Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)
        self.__teaching = True if configs['teaching'] == 1 else False  # teaching=1 表示评估课堂的教学情况
        self.__teacher = True if configs['teaching'] == 2 else False  # teaching=2 表示基于S-T评估教师的教学情况

    def preprocessor(self, day):
        CommonUtil.verify()
        if self.__teaching:
            self.__logger.info('教学效果评估--预处理数据')
            self.truncate_teaching_data(day)
            self.update_teaching_mental()
            self.update_teaching_study()
            self.update_teaching_data(day)
            self.preprocess_aggregate_teaching(day)
        elif self.__teacher:
            self.__logger.info('基于S-T评估教师教学情况')
            self.truncate_teacher_data(day)
            self.filter_student_for_teacher(day)
            self.process_student_actions(day)
            self.update_teacher_course(day)
            self.process_teacher_ontime(day)
            self.process_teacher_emotion(day)
            self.process_teacher_behavior(day)
        else:
            self.__logger.info('基于学生评估教学状态--预处理数据')
            self.truncate_data(day)
            self.update_face_id()
            self.update_course(day)
            self.preprocess_aggregate(day)
            self.update_student_info(day)

    def truncate_data(self, day):
        '''Truncate all data of intermediate tables'''
        self.__logger.info("Try to truncate all data of intermediate tables in {0}".format(Config.INPUT_DB_DATABASE))
        tmp_tables = [Config.INTERMEDIATE_TRACK_TABLE, Config.INTERMEDIATE_COURSE_TABLE, Config.INTERMEDIATE_AGG_TABLE]
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
        self.__db.execute("CREATE INDEX course_id_index ON {0} (course_id);".format(Config.INTERMEDIATE_COURSE_TABLE))

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

    def truncate_teaching_data(self, day):
        '''Truncate all data of intermediate teaching tables'''
        # 对于Config.INTERMEDIATE_TEACHING_TABLE(半年) 便于计算人际关系和课堂兴趣
        self.__logger.info("Try to delete teaching data in {0}".format(Config.INPUT_DB_DATABASE))
        del_tables = [Config.INTERMEDIATE_TEACHING_MENTAL_TABLE, Config.INTERMEDIATE_TEACHING_STUDY_TABLE, Config.INTERMEDIATE_TEACHING_TABLE]
        for table in del_tables:
            self.__logger.info('Begin to drop table {0}'.format(table))
            sql = '''
                DROP TABLE {0}
            '''.format(table)
            self.__db.delete(sql)

        sql = '''
            DELETE a FROM {0} a WHERE dt = '{1}' OR dt < '{2}'
        '''.format(Config.INTERMEDIATE_TEACHING_AGG_TABLE, day, CommonUtil.get_specific_date(day, Config.DATA_RESERVED_WINDOW))
        self.__db.delete(sql)
        self.__logger.info("End to delete teaching data in {0}.".format(Config.INPUT_DB_DATABASE))

    def update_teaching_mental(self):
        """ 评估每条记录的精神状态
        """

        self.__logger.info("Process teaching data, then output results to the table {0}".format(Config.INTERMEDIATE_TEACHING_MENTAL_TABLE))
        sql = '''
            CREATE TABLE {1}
            SELECT
                camera_id, pose_stat_time, body_stat, face_pose,
                case
                    WHEN face_emotion = '0' THEN '1'
                    WHEN face_emotion = '1' THEN '0'
                ELSE face_emotion
                END AS face_emotion,
                CASE
                    WHEN face_emotion IN ('2', '-1') AND body_stat IN ('3', '4', '5') THEN '2'
                    WHEN face_emotion IN ('1', '-1') AND body_stat IN ('1', '2') THEN '0'
                ELSE '1'
                END AS mental
            FROM {0}
            WHERE face_emotion != '-1' OR face_pose != '-1' OR body_stat != '-1'
        '''.format(Config.RAW_INPUT_TABLE, Config.INTERMEDIATE_TEACHING_MENTAL_TABLE)

        self.__db.insert(sql)
        self.__logger.info("Finish to update teaching mental")

    def update_teaching_study(self):
        """ 评估每条记录的学习状态
        """

        self.__logger.info("Process teaching data, then output results to the table {0}".format(Config.INTERMEDIATE_TEACHING_STUDY_TABLE))
        sql = '''
            CREATE TABLE {1}
            SELECT
                camera_id, pose_stat_time, body_stat, face_pose, face_emotion, mental,
                CASE
                    WHEN mental = '2' AND face_pose IN ('1', '2') THEN '3'
                    WHEN mental = '0' AND face_pose = '0' THEN '0'
                    WHEN mental IN ('0', '1') AND face_pose = '0' THEN '1'
                ELSE '2'
                END AS study
            FROM {0}
        '''.format(Config.INTERMEDIATE_TEACHING_MENTAL_TABLE, Config.INTERMEDIATE_TEACHING_STUDY_TABLE)

        self.__db.insert(sql)
        self.__logger.info("Finish to update teaching study")

        self.__logger.info("[Update teaching] add index")
        self.__db.execute("CREATE INDEX camera_id_name_index ON {0} (camera_id);".format(Config.INTERMEDIATE_TEACHING_STUDY_TABLE))

    def update_teaching_data(self, day):
        """ 关联课程信息
        """

        self.__logger.info("Process teaching data, then output results to the table {0}".format(Config.INTERMEDIATE_TEACHING_TABLE))
        sql = '''
            CREATE TABLE {3}
            SELECT
                t2.college_name, t2.grade_name, t2.class_name, t1.body_stat, t1.face_pose, t1.face_emotion, t1.mental, t1.study, t2.course_id, t2.course_name
            FROM
            (
                SELECT
                    t4.room_addr, t3.pose_stat_time, t3.body_stat, t3.face_pose, t3.face_emotion, t3.mental, t3.study
                FROM {0} t3 JOIN {1} t4
                ON t3.camera_id = t4.camera_id
            ) t1 JOIN
            (
                SELECT
                    room_addr, college_name, grade_name, class_name, course_id, course_name, start_time, end_time
                FROM {2}
                WHERE weekday = dayofweek('{4}')
                GROUP BY room_addr, college_name, grade_name, class_name, course_id, course_name, start_time, end_time
            ) t2 ON t1.room_addr = t2.room_addr AND cast(from_unixtime(t1.pose_stat_time,'%H:%i') as time) >= t2.start_time AND cast(from_unixtime(t1.pose_stat_time,'%H:%i') as time) <= t2.end_time
        '''.format(Config.INTERMEDIATE_TEACHING_STUDY_TABLE, Config.SCHOOL_CAMERA_ROOM_TABLE, Config.SCHOOL_STUDENT_COURSE_TABLE, Config.INTERMEDIATE_TEACHING_TABLE, day, Config.TEACHING_INTERVAL)

        self.__db.insert(sql)
        self.__logger.info("Finish to update student info")

        self.__logger.info("[Update teaching] add index")
        self.__db.execute("CREATE INDEX college_name_index ON {0} (college_name);".format(Config.INTERMEDIATE_TEACHING_TABLE))
        self.__db.execute("CREATE INDEX grade_name_index ON {0} (grade_name);".format(Config.INTERMEDIATE_TEACHING_TABLE))
        self.__db.execute("CREATE INDEX class_name_index ON {0} (class_name);".format(Config.INTERMEDIATE_TEACHING_TABLE))

    def preprocess_aggregate_teaching(self, day):
        """ 每隔固定周期聚合数据
        """

        self.__logger.info("Try to pre-aggrate the data, then output results to the table {0}".format(Config.INTERMEDIATE_TEACHING_AGG_TABLE))
        sql = '''
            INSERT INTO {1}
            SELECT
                college_name, grade_name, class_name, course_id, course_name, action, total, action_type, dt
            FROM (
                SELECT
                    college_name, grade_name, class_name, course_id, course_name, body_stat AS action, COUNT(*) AS total, {3} AS action_type, '{2}' AS dt
                FROM {0}
                WHERE body_stat != '-1'
                GROUP BY college_name, grade_name, class_name, course_id, course_name, body_stat
                UNION
                SELECT
                    college_name, grade_name, class_name, course_id, course_name, face_pose AS action, COUNT(*) AS total, {4} AS action_type, '{2}' AS dt
                FROM {0}
                WHERE face_pose != '-1'
                GROUP BY college_name, grade_name, class_name, course_id, course_name, face_pose
                UNION
                SELECT
                    college_name, grade_name, class_name, course_id, course_name, face_emotion AS action, COUNT(*) AS total, {5} AS action_type, '{2}' AS dt
                FROM {0}
                WHERE face_emotion != '-1'
                GROUP BY college_name, grade_name, class_name, course_id, course_name, face_emotion
                UNION
                SELECT
                    college_name, grade_name, class_name, course_id, course_name, mental AS action, COUNT(*) AS total, {6} AS action_type, '{2}' AS dt
                FROM {0}
                GROUP BY college_name, grade_name, class_name, course_id, course_name, mental
                UNION
                SELECT
                    college_name, grade_name, class_name, course_id, course_name, study AS action, COUNT(*) AS total, {7} AS action_type, '{2}' AS dt
                FROM {0}
                GROUP BY college_name, grade_name, class_name, course_id, course_name, study
            ) t
        '''.format(Config.INTERMEDIATE_TEACHING_TABLE, Config.INTERMEDIATE_TEACHING_AGG_TABLE, day, Config.ACTION_TYPE['body_stat'], Config.ACTION_TYPE['face_pose'], Config.ACTION_TYPE['face_emotion'], Config.ACTION_TYPE['mental'], Config.ACTION_TYPE['study'])
        self.__db.insert(sql)
        self.__logger.info("Finish to preprocess aggregate teaching data")

    def truncate_teacher_data(self, day):
        """ 清除教师教学情况的临时表
        """
        self.__logger.info("Truncate all data for teacher in database {0}".format(Config.INPUT_DB_DATABASE))
        tables = [Config.INTERMEDIATE_TEACHER_STUDENT_TABLE, Config.INTERMEDIATE_TEACHER_COURSE_TABLE, Config.INTERMEDIATE_TEACHER_BEHAVIOR_TABLE, Config.INTERMEDIATE_TEACHER_STUDENT_BEHAVIOR_TABLE, Config.INTERMEDIATE_TEACHER_EMOTION_TABLE, Config.INTERMEDIATE_TEACHER_ONTIME_TABLE]
        for table in tables:
            sql = '''
                DROP TABLE {0}
            '''.format(table)
            self.__db.truncate(sql)

        self.__logger.info("Done to truncate or delete data")

    def filter_student_for_teacher(self, day):
        """ 预处理学生数据、关联课程信息
        """

        self.__logger.info("filter student data for teacher")
        sql = '''
            CREATE TABLE {0}
            SELECT
                t4.college_name, t4.grade_name, t4.class_name, t4.course_id, t4.course_name, t4.teacher_id, t4.teacher_name, t3.body_stat AS body_stat, t3.face_pose, t3.pose_stat_time - t3.pose_stat_time % {5} AS pose_stat_time
            FROM (
                SELECT
                    t2.room_addr, t1.body_stat, t1.face_pose, t1.pose_stat_time
                FROM (
                    SELECT
                        camera_id, body_stat, face_pose, pose_stat_time
                    FROM {1}
                    WHERE body_stat IN ('1', '2') OR face_pose IN ('0', '1', '2')
                ) t1 JOIN {2} t2 ON t1.camera_id = t2.camera_id
            ) t3 JOIN (
                SELECT
                    room_addr, college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, start_time, end_time
                FROM {3}
                WHERE weekday = dayofweek('{4}')
                GROUP BY room_addr, college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, start_time, end_time
            ) t4 ON t3.room_addr = t4.room_addr AND cast(from_unixtime(t3.pose_stat_time,'%H:%i') as time) >= t4.start_time AND cast(from_unixtime(t3.pose_stat_time,'%H:%i') as time) <= t4.end_time
        '''.format(Config.INTERMEDIATE_TEACHER_STUDENT_TABLE, Config.RAW_INPUT_TABLE, Config.SCHOOL_CAMERA_ROOM_TABLE, Config.SCHOOL_STUDENT_COURSE_TABLE, day, Config.TEACHER_INTERVAL)
        self.__db.insert(sql)
        self.__logger.info("Finish to filter student data for teacher")

        self.__logger.info("To add index")
        self.__db.execute("CREATE INDEX college_name_index ON {0} (college_name);".format(Config.INTERMEDIATE_TEACHER_STUDENT_TABLE))
        self.__db.execute("CREATE INDEX grade_name_index ON {0} (grade_name);".format(Config.INTERMEDIATE_TEACHER_STUDENT_TABLE))
        self.__db.execute("CREATE INDEX class_name_index ON {0} (class_name);".format(Config.INTERMEDIATE_TEACHER_STUDENT_TABLE))

    def process_student_actions(self, day):
        """ 处理学生的行为动作序列
        """
        self.__logger.info("Process student actions for teacher")
        sql = '''
            CREATE TABLE {0}
            SELECT
                college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time,
                CASE
                    WHEN body_stat_cnt >= {9} THEN '{5}'
                    WHEN face_pose_cnt1 / total >= {2} THEN '{6}'
                    WHEN face_pose_cnt2 / total >= {3} THEN '{7}'
                ELSE '{8}'
                END AS behavior,
                '{4}' AS dt
            FROM (
                SELECT
                    t3.college_name, t3.grade_name, t3.class_name, t3.course_id, t3.course_name, t3.teacher_id, t3.teacher_name, t3.pose_stat_time,
                    MAX(CASE WHEN t4.body_stat IS NOT NULL THEN t4.body_stat_cnt ELSE 0 END) AS body_stat_cnt,
                    MAX(CASE WHEN t3.face_pose IS NOT NULL AND t3.face_pose = '1' THEN t3.face_pose_cnt ELSE 0 END) AS face_pose_cnt1,
                    MAX(CASE WHEN t3.face_pose IS NOT NULL AND t3.face_pose = '2' THEN t3.face_pose_cnt ELSE 0 END) AS face_pose_cnt2,
                    MAX(total) AS total
                FROM (
                    SELECT
                        t1.college_name, t1.grade_name, t1.class_name, t1.course_id, t1.course_name, t1.teacher_id, t1.teacher_name, t1.pose_stat_time, t1.total, t2.face_pose, t2.face_pose_cnt
                    FROM (
                        SELECT
                            college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time, COUNT(*) AS total
                        FROM {1}
                        GROUP BY college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time
                    ) t1 LEFT OUTER JOIN (
                        SELECT
                            college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time, face_pose, COUNT(*) AS face_pose_cnt
                        FROM {1}
                        WHERE face_pose IN ('1', '2')
                        GROUP BY college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time, face_pose
                    ) t2 ON t1.college_name = t2.college_name AND t1.grade_name = t2.grade_name AND t1.class_name = t2.class_name AND t1.course_id = t2.course_id AND t1.course_name = t2.course_name AND t1.teacher_id = t2.teacher_id AND t1.teacher_name = t2.teacher_name AND t1.pose_stat_time = t2.pose_stat_time
                ) t3 LEFT OUTER JOIN (
                    SELECT
                        college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time, body_stat, COUNT(*) AS body_stat_cnt
                    FROM (
                        SELECT
                            college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time, '1' AS body_stat
                        FROM {1}
                        WHERE body_stat IN ('1', '2')
                    ) tmp
                    GROUP BY college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time, body_stat
                ) t4 ON t3.college_name = t4.college_name AND t3.grade_name = t4.grade_name AND t3.class_name = t4.class_name AND t3.course_id = t4.course_id AND t3.course_name = t4.course_name AND t3.teacher_id = t4.teacher_id AND t3.teacher_name = t4.teacher_name AND t3.pose_stat_time = t4.pose_stat_time
                GROUP BY t3.college_name, t3.grade_name, t3.class_name, t3.course_id, t3.course_name, t3.teacher_id, t3.teacher_name, t3.pose_stat_time
            ) tmp2
        '''.format(Config.INTERMEDIATE_TEACHER_STUDENT_BEHAVIOR_TABLE, Config.INTERMEDIATE_TEACHER_STUDENT_TABLE, Config.TEACHER_STUDENT_DISCUSSION, Config.TEACHER_STUDENT_THINK, day, Config.STUDENT_BEHAVIORS[0], Config.STUDENT_BEHAVIORS[1], Config.STUDENT_BEHAVIORS[2], Config.STUDENT_BEHAVIORS[3], Config.TEACHER_STUDENT_SPEAK)
        self.__db.insert(sql)
        self.__logger.info("Finish to process behavior of student for teacher")

        self.__logger.info("To add index")
        self.__db.execute("CREATE INDEX college_name_index ON {0} (college_name);".format(Config.INTERMEDIATE_TEACHER_STUDENT_BEHAVIOR_TABLE))
        self.__db.execute("CREATE INDEX grade_name_index ON {0} (grade_name);".format(Config.INTERMEDIATE_TEACHER_STUDENT_BEHAVIOR_TABLE))
        self.__db.execute("CREATE INDEX class_name_index ON {0} (class_name);".format(Config.INTERMEDIATE_TEACHER_STUDENT_BEHAVIOR_TABLE))

    def update_teacher_course(self, day):
        """ 处理教师数据，关联课程信息
        """
        self.__logger.info("To add course info for teacher")
        sql = '''
            CREATE TABLE {0}
            SELECT
                t4.college_name, t4.grade_name, t4.class_name, t4.course_id, t4.course_name, t4.teacher_id, t4.teacher_name, t3.face_id, t3.body_stat, t3.face_emotion, t3.unix_timestamp - t3.unix_timestamp % {5} AS pose_stat_time, cast(from_unixtime(t3.unix_timestamp,'%H:%i') as time) AS u_time, t4.start_time
            FROM (
                SELECT
                    t2.room_addr, t1.body_stat, t1.face_emotion, t1.unix_timestamp, t1.face_id
                FROM (
                    SELECT
                        camera_id, face_id, body_stat, face_emotion, unix_timestamp
                    FROM {1}
                    WHERE dt = '{4}'
                ) t1 JOIN {2} t2 ON t1.camera_id = t2.camera_id
            ) t3 JOIN (
                SELECT
                    room_addr, college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, start_time, end_time
                FROM {3}
                WHERE weekday = dayofweek('{4}')
                GROUP BY room_addr, college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, start_time, end_time
            ) t4 ON t3.room_addr = t4.room_addr AND cast(from_unixtime(t3.unix_timestamp,'%H:%i') as time) >= t4.start_time AND cast(from_unixtime(t3.unix_timestamp,'%H:%i') as time) <= t4.end_time
        '''.format(Config.INTERMEDIATE_TEACHER_COURSE_TABLE, Config.TEACHER_RAW_DATA_TABLE, Config.SCHOOL_CAMERA_ROOM_TABLE, Config.SCHOOL_STUDENT_COURSE_TABLE, day, Config.TEACHER_INTERVAL)
        self.__db.insert(sql)
        self.__logger.info("Finish to add course data for teacher")

        self.__logger.info("To add index")
        self.__db.execute("CREATE INDEX college_name_index ON {0} (college_name);".format(Config.INTERMEDIATE_TEACHER_COURSE_TABLE))
        self.__db.execute("CREATE INDEX grade_name_index ON {0} (grade_name);".format(Config.INTERMEDIATE_TEACHER_COURSE_TABLE))
        self.__db.execute("CREATE INDEX class_name_index ON {0} (class_name);".format(Config.INTERMEDIATE_TEACHER_COURSE_TABLE))

    def process_teacher_ontime(self, day):
        """ 判定教师是否准时上课
            标准：教师是否在课堂5分钟内被识别
        """
        self.__logger.info("Judge if the teacher begins to take course on time")
        sql = '''
            CREATE TABLE {0}
            SELECT
                college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, start_time,
                CASE
                    WHEN total > 0 THEN 1
                ELSE 0
                END AS ontime,
                '{3}' AS dt
            FROM (
                SELECT
                    college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, start_time, COUNT(*) AS total
                FROM {1}
                WHERE face_id != 'unknown' AND u_time >= start_time AND u_time <= DATE_FORMAT(ADDTIME(start_time, '{2}'), '%H:%i')
                GROUP BY college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, start_time
            ) t1
        '''.format(Config.INTERMEDIATE_TEACHER_ONTIME_TABLE, Config.INTERMEDIATE_TEACHER_COURSE_TABLE, Config.TEACHER_ONTIME, day)
        self.__db.insert(sql)
        self.__logger.info("Finish to judge ontime for teacher")

    def process_teacher_emotion(self, day):
        """ 处理教师的表情数据
        """
        self.__logger.info("Compute the emotion of teacher")
        sql = '''
            CREATE TABLE {0}
            SELECT
                college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, face_emotion, COUNT(*) AS total, '{2}' AS dt
            FROM {1}
            WHERE face_emotion != '-1'
            GROUP BY college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, face_emotion
        '''.format(Config.INTERMEDIATE_TEACHER_EMOTION_TABLE, Config.INTERMEDIATE_TEACHER_COURSE_TABLE, day)
        self.__db.insert(sql)
        self.__logger.info("Finish to compute the emotion of teacher")

    def process_teacher_behavior(self, day):
        """ 处理教师的行为数据
        """
        self.__logger.info("Process behaviors of teacher")
        sql = '''
            CREATE TABLE {0}
            SELECT college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time,
            CASE
                WHEN behavior1 != 0 AND GREATEST(behavior1, behavior2, behavior3) = behavior1 THEN '{3}'
                WHEN behavior2 != 0 AND GREATEST(behavior1, behavior2, behavior3) = behavior2 THEN '{4}'
                WHEN behavior3 != 0 AND GREATEST(behavior1, behavior2, behavior3) = behavior3 THEN '{5}'
            ELSE '{6}'
            END AS behavior,
            '{2}' AS dt
            FROM (
                SELECT college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time,
                    MAX(CASE WHEN body_stat = '0' THEN total ELSE 0 END) AS behavior0,
                    MAX(CASE WHEN body_stat = '1' THEN total ELSE 0 END) AS behavior1,
                    MAX(CASE WHEN body_stat = '2' THEN total ELSE 0 END) AS behavior2,
                    MAX(CASE WHEN body_stat = '3' THEN total ELSE 0 END) AS behavior3
                FROM (
                    SELECT
                        college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time, body_stat, COUNT(*) AS total
                    FROM {1}
                    GROUP BY college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time, body_stat
                ) t1
                GROUP BY college_name, grade_name, class_name, course_id, course_name, teacher_id, teacher_name, pose_stat_time
            ) t2
        '''.format(Config.INTERMEDIATE_TEACHER_BEHAVIOR_TABLE, Config.INTERMEDIATE_TEACHER_COURSE_TABLE, day, Config.TEACHER_BEHAVIORS[0], Config.TEACHER_BEHAVIORS[1], Config.TEACHER_BEHAVIORS[2], Config.TEACHER_BEHAVIORS[3])
        self.__db.insert(sql)
        self.__logger.info("Finish to process behavior of teacher")

        self.__logger.info("To add index")
        self.__db.execute("CREATE INDEX college_name_index ON {0} (college_name);".format(Config.INTERMEDIATE_TEACHER_BEHAVIOR_TABLE))
        self.__db.execute("CREATE INDEX grade_name_index ON {0} (grade_name);".format(Config.INTERMEDIATE_TEACHER_BEHAVIOR_TABLE))
        self.__db.execute("CREATE INDEX class_name_index ON {0} (class_name);".format(Config.INTERMEDIATE_TEACHER_BEHAVIOR_TABLE))


if __name__ == "__main__":
    configs = {
        'dbhost': '172.16.14.190',
        'teaching': 2
    }

    processor = Preprocessor(configs)
    processor.preprocessor('2020-07-07')