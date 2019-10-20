# !/usr/bin/python
# -*- coding: utf-8 -*-
import Config
import DbUtil
import Logger
import MetricUtil

class CalcCourseMetric(object):
    """docsTry for CalcCourseMetric"""
    def __init__(self, configs):
        super(CalcCourseMetric, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__utils = MetricUtil.MetricUtil()
        self.__logger = Logger.Logger(__name__)

    def calculate_course_metrics(self, start_time, end_time):
        """
            Calculate 2 metrics, including student_emotion, student_study_stat and student_mental_stat for each course for each student.
            return {
                'class_id1' => {
                    'face_id1' => {
                        'course_name1' => {'student_emotion' => value, student_study_stat' => value, 'student_mental_stat' => value}, 
                        'course_name2' => {'student_emotion' => value, student_study_stat' => value, 'student_mental_stat' => value}
                    },
                    'face_id2' => {
                        'course_name1' => {'student_emotion' => value, 'student_study_stat' => value, 'student_mental_stat' => value}, 
                        'course_name2' => {'student_emotion' => value, 'student_study_stat' => value, 'student_mental_stat' => value}
                    }
                },
                'class_id2' => {
                    'face_id1' => {
                        'course_name1' => {'student_emotion' => value, 'student_study_stat' => value, 'student_mental_stat' => value}, 
                        'course_name2' => {'student_emotion' => value, 'student_study_stat' => value, 'student_mental_stat' => value}
                    },
                    'face_id2' => {
                        'course_name1' => {'student_emotion' => value, 'student_study_stat' => value, 'student_mental_stat' => value}, 
                        'course_name2' => {'student_emotion' => value, 'student_study_stat' => value, 'student_mental_stat' => value}
                    }
                }
            }
        """

        # Compute the count of each basic metric
        self.__logger.info("Try to compute course basic metrics")
        body_stat_count = self.count_body_stat(start_time, end_time)
        emotion_count = self.count_face_emotion(start_time, end_time)
        face_pose_count = self.count_face_pose(start_time, end_time)
        self.__logger.info("Finished to compte course basic metrics")

        self.__logger.info("Try to comput the course metrics")
        metrics = {}

        # Calculate student emotion based on emotion
        self.__logger.info("Begin to compute student_emotion")
        for class_id, raws in emotion_count.items():
            for course_name, values in raws.items():
                emotion_thresholds = self.__utils.calculate_emotion_threshold(emotion_count[class_id][course_name])
                for face_id, value in values.items():
                    if not metrics.has_key(class_id):
                        metrics[class_id] = {}

                    if not metrics[class_id].has_key(face_id):
                        metrics[class_id][face_id] = {}

                    if not metrics[class_id][face_id].has_key(course_name):
                        metrics[class_id][face_id][course_name] = {}

                    metrics[class_id][face_id][course_name]['student_emotion'] = self.__utils.estimate_emotion(value, emotion_thresholds)

        # Calculate student mental status based on body_stat and emotion
        self.__logger.info("Begin to compute student_mental_stat")
        for class_id, raws in body_stat_count.items():
            for course_name, values in raws.items():
                body_stat_thresholds = self.__utils.calculate_mental_threshold(body_stat_count[class_id][course_name])
                for face_id, value in values.items():
                    if not metrics.has_key(class_id):
                        metrics[class_id] = {}

                    if not metrics[class_id].has_key(face_id):
                        metrics[class_id][face_id] = {}

                    if not metrics[class_id][face_id].has_key(course_name):
                        metrics[class_id][face_id][course_name] = {}

                    metrics[class_id][face_id][course_name]['student_mental_stat'] = self.__utils.estimate_mental_stat(metrics[class_id][face_id][course_name], value, body_stat_thresholds)

        # Calculate student study status based on student mental and face_pose
        # Calculate threshold
        self.__logger.info("Begin to compute student_study_stat")
        for class_id, raws in face_pose_count.items():
            for course_name, values in raws.items():
                study_stat_thresholds = self.__utils.calculate_study_threshold(face_pose_count[class_id][course_name])
                for face_id, value in values.items():
                    if not metrics.has_key(class_id):
                        metrics[class_id] = {}
                    
                    if not metrics[class_id].has_key(face_id):
                        metrics[class_id][face_id] = {}
                    
                    if not metrics[class_id][face_id].has_key(course_name):
                        metrics[class_id][face_id][course_name] = {}

                    metrics[class_id][face_id][course_name]['student_study_stat'] = self.__utils.estimate_study_stat(metrics[class_id][face_id][course_name], value, study_stat_thresholds)

        self.__logger.debug(str(metrics))
        self.__logger.info("Finished to compute the course metrics")

        return metrics

    def count_body_stat(self, start_time, end_time):
        ''''''
        self.__logger.info("Begin to count by body_stat")
        sql = '''
            SELECT
                class_id, course_name, face_id, body_stat, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND body_stat != '-1' AND face_id != 'unknown' AND course_name != 'rest'
            GROUP BY class_id, course_name, face_id, body_stat
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN)

        res = {} # {'course_name' => {'face_id1' => values, 'face_id2' => values}}
        count = 0
        for row in self.__db.select(sql):
            count += 1
            key = row[0].encode('utf-8')
            if not res.has_key(key):
                res[key] = {}
            subKey = row[1].encode('utf-8')
            if not res[key].has_key(subKey):
                res[key][subKey] = {}

            ssKey = row[2].encode('utf-8')
            if not res[key][subKey].has_key(ssKey):
                res[key][subKey][ssKey] = {}

            if row[3] == '0': # 正常
                res[key][subKey][ssKey]['body_stat_normal'] = row[4]
            elif row[3] == '1': # 站立
                res[key][subKey][ssKey]['body_stat_standup'] = row[4]
            elif row[3] == '2': # 举手
                res[key][subKey][ssKey]['body_stat_handup'] = row[4]
            elif row[3] == '3': # 睡觉
                res[key][subKey][ssKey]['body_stat_sleep'] = row[4]
            elif row[3] == '4': # 手托着听课
                res[key][subKey][ssKey]['body_stat_sttk'] = row[4]
            elif row[3] == '5': # 趴着听课
                res[key][subKey][ssKey]['body_stat_pztk'] = row[4]
            else:
                continue
        self.__logger.debug("count_body_stat: " + str(res))
        self.__logger.info("Finished to count face_pose, and get total {0} records.".format(count))

        return res

    def count_face_emotion(self, start_time, end_time):
        ''''''
        self.__logger.info("Begin to count by face_emotion")
        sql = '''
            SELECT
                class_id, course_name, face_id, face_emotion, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND face_emotion != '-1' AND face_id != 'unknown' AND course_name != 'rest'
            GROUP BY class_id, course_name, face_id, face_emotion
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN)

        res = {}
        count = 0
        for row in self.__db.select(sql):
            count += 1
            key = row[0].encode('utf-8')
            if not res.has_key(key):
                res[key] = {}

            subKey = row[1].encode('utf-8')
            if not res[key].has_key(subKey):
                res[key][subKey] = {}

            ssKey = row[2].encode('utf-8')
            if not res[key][subKey].has_key(ssKey):
                res[key][subKey][ssKey] = {}

            if row[3] == '0': # 正常
                res[key][subKey][ssKey]['emotion_normal'] = row[4]
            elif row[3] == '1': # 开心
                res[key][subKey][ssKey]['emotion_happy'] = row[4]
            elif row[3] == '2': # 低落
                res[key][subKey][ssKey]['emotion_low'] = row[4]
            else:
                continue
        self.__logger.debug("count_face_emotion: " + str(res))
        self.__logger.info("Finished to count face_pose, and get total {0} records.".format(count))

        return res

    def count_face_pose(self, start_time, end_time):
        ''' Compute the count of face pose based on face_id level '''
        # TODO 考虑如何利用face_pose_stat
        self.__logger.info("Begin to count by face_pose")
        sql = '''
            SELECT
                class_id, course_name, face_id, face_pose, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND face_pose != '-1' AND face_id != 'unknown' AND course_name != 'rest'
            GROUP BY class_id, course_name, face_id, face_pose
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN)

        res = {}
        count = 0
        for row in self.__db.select(sql):
            count += 1
            key = row[0].encode('utf-8')
            if not res.has_key(key):
                res[key] = {}

            subKey = row[1].encode('utf-8')
            if not res[key].has_key(subKey):
                res[key][subKey] = {}

            ssKey = row[2].encode('utf-8')
            if not res[key][subKey].has_key(ssKey):
                res[key][subKey][ssKey] = {}

            if row[3] == '0': # 平视
                res[key][subKey][ssKey]['face_pose_normal'] = row[4]
            elif row[3] == '1': # 左顾右盼
                res[key][subKey][ssKey]['face_pose_around'] = row[4]
            elif row[3] == '2': # 低头
                res[key][subKey][ssKey]['face_pose_low'] = row[4]
            else:
                continue
        self.__logger.debug("count_face_pose: " + str(res))
        self.__logger.info("Finished to count face_pose, and get total {0} records.".format(count))

        return res