# !/usr/bin/python
# -*- coding: utf-8 -*-

import DbUtil
import Config
import Logger
import ClassAPI

class Preprocessor(object):
    """docstring for Preprocessor"""
    def __init__(self):
        super(Preprocessor, self).__init__()
        self.__db = DBUtil(Config.INPUT_DB_HOST, Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger(__name__)

    def preprocessor(self, start_time, end_time):
        self.update_status(start_time, end_time)
        self.update_face_id(start_time, end_time)
        self.update_body_id(start_time, end_time)
        self.update_face_pose_state(start_time, end_time)
        self.do_filter(start_time, end_time)
        self.update_course(start_time, end_time)

    def update_face_pose_state(self, start_time, end_time):
        '''
            Judge if a face pose is normal based on all face pose data
            camera_id stands for a classroom because each classroom has a different camera_id
        '''
        self.__logger.info("Tring to update face_pose_stat")

        sql = '''
            SELECT
                camera_id, face_pose_stat_time, face_pose, num * 1.0 / total AS ratio
            FROM
            (
                (
                    SELECT 
                        camera_id, face_pose_stat_time, face_pose, COUNT(*) AS num
                    FROM {2}
                    WHERE face_pose != '-1' AND pose_stat_time >= {0} AND pose_stat_time <= {1}
                    GROUP BY camera_id, face_pose_stat_time, face_pose
                ) AS t1
                LEFT OUTER JOIN
                (
                    SELECT
                        camera_id, face_pose_stat_time, COUNT(*) AS total
                    FROM {2}
                    WHERE face_pose != '-1' AND pose_stat_time >= {0} AND pose_stat_time <= {1}
                    GROUP BY camera_id, face_pose_stat_time
                ) AS t2
                ON t1.camera_id = t2.camera_id AND t1.face_pose_stat_time = t2.face_pose_stat_time
            )
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE)

        count = 0
        for row in self.__db.select(sql):
            updateSql = '''
                UPDATE {4}
                SET face_pose_stat = {0}
                WHERE camera_id = {1} AND face_pose_stat_time = {2} AND face_pose = {3}
            '''.format(self.get_face_pose_stat(row[3]), row[0], row[1], row[2], Config.INTERMEDIATE_TABLE)
            self.__db.update(updateSql)
            count += 1

        self.__logger.info('Finish to update {0} records'.format(count))

    def update_face_id(self, start_time, end_time):
        ''' Update face_id accroding to face_track '''
        self.__logger.info("Tring to update face_id based on face_track")

        sql = '''
            SELECT
                camera_id, face_track, face_id, COUNT(*) AS total
            FROM {2}
            WHERE face_id != 'unknown' AND face_track != 'unknown' AND pose_stat_time >= {0} AND pose_stat_time <= {1}
            GROUP BY camera_id, face_track, face_id
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE)

        results = self.__db.select(sql)

        # Only need to update face_id if the face_track has one more face_id
        sql = '''
            SELECT
                camera_id, face_track, COUNT(*) AS face_num
            FROM {2}
            WHERE face_track != 'unknown' AND face_id != 'unknown' AND pose_stat_time >= {0} AND pose_stat_time <= {1}
            GROUP BY camera_id, face_track, face_id
            HAVING face_num > 1
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE)

        # TODO: optimize get_id_with_max_value to calcute this once
        count = 0
        for row in self.__db.select(sql):
            sql = '''
                UPDATE {5}
                SET face_id = {0}
                WHERE camera_id = {1} AND face_track = {2} AND pose_stat_time >= {3} AND pose_stat_time <= {4}
            '''.format(self.get_id_with_max_value(results, row), row[0], row[1],start_time, end_time, Config.INTERMEDIATE_TABLE)
            self.__db.update(sql)
            count += 1

        self.__logger("Finish to update face_id {0} records".format(count))

    def update_body_id(self, start_time, end_time):
        ''' Update body_id accroding to body_track '''
        self.__logger.info("Tring to udpate body_id based on body_track")

        sql = '''
            SELECT
                camera_id, body_track, body_id, COUNT(*) AS total
            FROM {2}
            WHERE body_id != 'unknown' AND body_track != 'unknown' AND pose_stat_time >= {0} AND pose_stat_time <= {1}
            GROUP BY camera_id, body_track, body_id
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE)

        results = self.__db.select(sql)

        sql = '''
            SELECT
                camera_id, body_track, COUNT(*) AS body_num
            FROM {2}
            WHERE body_track != 'unknown' AND body_id != 'unknown' AND pose_stat_time >= {0} AND pose_stat_time <= {1}
            GROUP BY camera_id, body_track, body_id
            HAVING body_num > 1
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE)

        count = 0
        for row in self.__db.select(sql):
            sql = '''
                UPDATE {5}
                SET body_id = {0}
                WHERE camera_id = {1} AND body_track = {2} AND pose_stat_time >= {3} AND pose_stat_time <= {4}
            '''.format(self.get_id_with_max_value(results, row), row[0], row[1], start_time, end_time, Config.INTERMEDIATE_TABLE)
            self.__db.update(sql)
            count += 1

        self.__logger.info("Finish to update {0} records".format(count))

    def update_status(self, start_time, end_time):
        ''' Update body_stat, face_pose and face_emotion by pose_stat_time '''
        self.__logger.info("Tring to choose body_stat, face_pose, face_emotion")

        sql = '''
            INSERT INTO {2} SELECT
                t2.camera_id, f2.frame_id, t2.body_id, t1.body_stat, t2.body_track, t1.face_id, t2.face_track, t1.face_pose, t2.face_pose_stat, t2.face_pose_stat_time, t1.face_emotion, t2.yawn, t2.unix_timestamp, t1.pose_stat_time
            FROM
            (
                (    
                    SELECT
                        face_id, pose_stat_time, MAX(body_stat) AS body_stat, MAX(face_pose) AS face_pose, MAX(face_emotion) AS face_emotion
                    FROM {3}
                    WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_id != 'unknown'
                    GROUP BY face_id, pose_stat_time
                ) AS t1
                LEFT OUTER JOIN
                (
                    SELECT * FROM WHERE {3} WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_id != 'unknown'
                ) AS t2
                ON t1.face_id = t2.face_id AND t1.pose_stat_time = t2.pose_stat_time
            )
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE, Config.RAW_INPUT_TABLE)

        self.__db.insert(sql)

        self.__logger.info("Finish to update")

    def do_filter(self, start_time, end_time):
        ''''''
        self.__logger.info("Tring to filter some records under the number limit")

        sql = '''
            SELECT
                face_id, COUNT(*) AS num
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time <= {1}
            GROUP BY face_id
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE)

        res = self.get_available_face_id(self.__db.select(sql))

        count = 0
        for face_id in res:
            sql = '''
                INSERT INTO {4}
                SELECT * FROM {3} WHERE face_id = {2} AND pose_stat_time >= {0} AND pose_stat_time <= {1}
            '''.format(start_time, end_time, face_id, Config.INTERMEDIATE_TABLE, Config.INTERMEDIATE_TABLE_TRAIN)
            self.__db.insert(sql)
            count += 1

        self.__logger.info("Finish to choose {0} records of face_id".format(count))

    def update_course(self, start_time, end_time):
        ''''''
        self.__logger.info("Tring to insert course according to camera_id and timespan")

        sql = '''
            SELECT
                camera_id, unix_timestamp
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time <= {1}
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN)

        for row in self.__db.select(sql):
            updateSql = '''
                UPDATE {3}
                SET course_name = {2}
                WHERE unix_timestamp = {0} AND camera_id = {1}
            '''.format(row[1], row[0], ClassAPI.get_course_name(row[0], row[1])[0], Config.INTERMEDIATE_TABLE_TRAIN)
            self.__db.update(updateSql)

        self.__logger.info("Finish to update course_name")

    def get_status(self, overall_data, row):
        ''''''
        for r in overall_data:
            if r[0] == row[0] and r[1] == row[1] and r[2] == row[2]:
                return 1 if r[3] >= 0.5 else 0

    def get_face_pose_stat(self, ratio):
        ''''''
        if ratio < Config.FACE_POSE_STAT_ABNORMAL:
            return 1
        else:
            return 0

    def get_id_with_max_value(self, data, row):
        ''' TODO: optimized by calcute this once '''
        maxValue = 0
        res = '-1' # means 'unknown'
        for r in data:
            if r[0] == row[0] and r[1] == row[1] and maxValue < r[3]:
                res = r[2]
                maxValue = r[3]

        return res

    def get_available_face_id(self, data):
        face_ids = []
        num = 0
        for row in data:
            num += row[1]

        average = float(num) / len(data)

        for row in data:
            if row[1] >= average:
                face_ids.append(row[0])

        return face_ids