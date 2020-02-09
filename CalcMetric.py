# !/usr/bin/python
# -*- coding: utf-8 -*-
import Config
import DbUtil
import Logger
import math
from CommonUtil import CommonUtil
import MetricUtil

class CalcMetric(object):
    """docsTry for CalcMetric"""
    def __init__(self, configs):
        super(CalcMetric, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__util = MetricUtil.MetricUtil()
        self.__logger = Logger.Logger(__name__)

    def calculate_daily_metrics(self, start_time, end_time, day):
        """
            Calculate 4 metrics, including student_emotion, student_study_stat, student_relationship, and student_mental_stat.
            return {
                'class_id1' => {
                    'face_id1' => {'student_emotion' => value, 'student_study_stat' => value, 'student_relationship' => value, 'student_mental_stat' => value},
                    'face_id2' => {'student_emotion' => value, 'student_study_stat' => value, 'student_relationship' => value, 'student_mental_stat' => value}
                },
                'class_id2' => {
                    'face_id1' => {'student_emotion' => value, 'student_study_stat' => value, 'student_relationship' => value, 'student_mental_stat' => value},
                    'face_id2' => {'student_emotion' => value, 'student_study_stat' => value, 'student_relationship' => value, 'student_mental_stat' => value}
                },
            }

            基于学院-年级-班级信息作为class_id
        """

        # Compute the count of each basic metric
        self.__logger.info("Try to compute basic metrics")
        body_stat_count = self.count_body_stat(day)
        emotion_count = self.count_face_emotion(day)
        face_pose_count = self.count_face_pose(day)
        self.__logger.info("Finished to compte basic metrics")

        self.__logger.info("Try to comput the high-level metrics")
        metrics = {}

        # Calculate student emotion based on emotions
        # Calculate threshold
        self.__logger.info("Begin to compute student_emotion")
        for class_id, values in emotion_count.items():
            emotion_thresholds = self.__util.calculate_emotion_threshold(emotion_count[class_id])
            for face_id in values:
                if not metrics.has_key(class_id):
                    metrics[class_id] = {}
                if not metrics[class_id].has_key(face_id):
                    metrics[class_id][face_id] = {}
                metrics[class_id][face_id]['student_emotion'] = self.__util.estimate_emotion(emotion_count[class_id][face_id], emotion_thresholds)

        # Calculate student mental status based on body_stat and emotion
        self.__logger.info("Begin to compute student_mental_stat")
        for class_id, values in metrics.items():
            body_stat_thresholds = self.__util.calculate_mental_threshold(body_stat_count[class_id])
            if body_stat_count.has_key(class_id):
                for face_id in values:
                    if body_stat_count[class_id].has_key(face_id):
                        metrics[class_id][face_id]['student_mental_stat'] = self.__util.estimate_mental_stat(metrics[class_id][face_id], body_stat_count[class_id][face_id], body_stat_thresholds)

        # Calculate student study status based on student mental and face_pose
        # Calculate threshold
        self.__logger.info("Begin to compute student_study_stat")
        for class_id, values in metrics.items():
            if face_pose_count.has_key(class_id):
                study_stat_thresholds = self.__util.calculate_study_threshold(face_pose_count[class_id])
                for face_id in values:
                    if face_pose_count[class_id].has_key(face_id):
                        metrics[class_id][face_id]['student_study_stat'] = self.__util.estimate_study_stat(metrics[class_id][face_id], face_pose_count[class_id][face_id], study_stat_thresholds)

        # Calculate student relationship based on emotions, facePoses
        # Calculate threshold
        self.__logger.info("Begin to compute student_relationship")
        emotion_count = self.count_face_emotion(day, True)
        face_pose_count = self.count_face_pose(day, True)
        for class_id, values in metrics.items():
            if emotion_count.has_key(class_id) and face_pose_count.has_key(class_id):
                relationship_thresholds = self.calculate_relationship_threshold(emotion_count[class_id], face_pose_count[class_id])
                for face_id in values:
                    if emotion_count[class_id].has_key(face_id) and face_pose_count[class_id].has_key(face_id):
                        metrics[class_id][face_id]['student_relationship'] = self.estimate_relationship(metrics[class_id][face_id], emotion_count[class_id][face_id], face_pose_count[class_id][face_id], relationship_thresholds)

        self.__logger.debug(str(metrics))
        self.__logger.info("Finished to compute high-level metrics")

        return metrics

    def calculate_relationship_threshold(self, emotions, face_poses):
        ''''''
        smiles = []
        for key, value in emotions.items():
            if value.has_key('emotion_happy'):
                smiles.append(value['emotion_happy'])

        arounds = []
        lows = []
        for key, value in face_poses.items():
            if value.has_key('face_pose_around'):
                arounds.append(value['face_pose_around'])
            if value.has_key('face_pose_low'):
                lows.append(value['face_pose_low'])

        thresholds = {}
        smile_len = len(smiles)
        around_len = len(arounds)
        low_len = len(lows)
        if low_len != 0:
            # face_pose 低头
            lows.sort(reverse=True)
            self.__logger.debug(str(lows))
            thresholds['solitary_low'] = lows[self.__util.threshold_index(int(math.floor(low_len * Config.RELATIONSHIP_THRESHOLD_SOLITARY['FACE_POSE_LOW'])))]
        if around_len != 0:
            # face_pose 左顾右盼
            arounds.sort(reverse=True)
            self.__logger.debug(str(arounds))
            thresholds['great_around'] = arounds[self.__util.threshold_index(int(math.floor(around_len * Config.RELATIONSHIP_THRESHOLD_GREAT['FACE_POSE_AROUND'])))]
            thresholds['good_around'] = arounds[self.__util.threshold_index(int(math.floor(around_len * Config.RELATIONSHIP_THRESHOLD_GOOD['FACE_POSE_AROUND'])))]
        if smile_len != 0:
            # emotion 微笑
            smiles.sort(reverse=True)
            self.__logger.debug(str(smiles))
            thresholds['solitary_smile'] = smiles[self.__util.threshold_index(int(math.floor(smile_len * Config.RELATIONSHIP_THRESHOLD_SOLITARY['EMOTION_SMILE'])))]
            thresholds['great_smile'] = smiles[self.__util.threshold_index(int(math.floor(smile_len * Config.RELATIONSHIP_THRESHOLD_GREAT['EMOTION_SMILE'])))]
            thresholds['good_smile'] = smiles[self.__util.threshold_index(int(math.floor(smile_len * Config.RELATIONSHIP_THRESHOLD_GOOD['EMOTION_SMILE'])))]

        self.__logger.debug("Relation Thresholds: " + str(thresholds))
        return thresholds

    def count_body_stat(self, day):
        ''''''
        self.__logger.info("Begin to count by body_stat")
        sql = '''
            SELECT
                CONCAT(college_name, grade_name, class_name) AS class_id, face_id, action, SUM(total) AS total
            FROM {1}
            WHERE dt = '{0}' AND action_type = {2}
            GROUP BY class_id, face_id, action
        '''.format(day, Config.INTERMEDIATE_TABLE_TRAIN, Config.ACTION_TYPE['body_stat'])

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

            cnt = float(row[3])
            if row[2] == '0': # 正常
                res[key][subKey]['body_stat_normal'] = cnt
            elif row[2] == '1': # 站立
                res[key][subKey]['body_stat_standup'] = cnt
            elif row[2] == '2': # 举手
                res[key][subKey]['body_stat_handup'] = cnt
            elif row[2] == '3': # 睡觉
                res[key][subKey]['body_stat_sleep'] = cnt
            elif row[2] == '4': # 手托着听课
                res[key][subKey]['body_stat_sttk'] = cnt
            elif row[2] == '5': # 趴着听课
                res[key][subKey]['body_stat_pztk'] = cnt
            else:
                continue
        self.__logger.debug("count_body_stat: " + str(res))

        self.__logger.info("Finished to count body_stat, and get total {0} records.".format(count))
        return res

    def count_face_emotion(self, day, is_lookback=False):
        ''''''
        self.__logger.info("Begin to count by face_emotion")
        sql = ''
        if is_lookback:
            sql = '''
                SELECT
                    class_id, face_id, action, COUNT(*) AS total
                FROM (
                    SELECT
                        CONCAT(t1.college_name, t1.grade_name, t1.class_name) AS class_id, t1.face_id, t1.action
                    FROM {2} t1
                    WHERE t1.dt >= '{0}' AND t1.dt <= '{1}' AND action_type = {4} AND t1.course_name = 'rest' AND t1.face_id in
                    (
                        SELECT
                            t2.face_id
                        FROM
                        (
                            SELECT
                                face_id, COUNT(*) AS num
                            FROM {2}
                            WHERE dt >= '{0}' AND dt <= '{1}' AND course_name = 'rest'
                            GROUP BY face_id
                            HAVING num >= {3}
                        ) t2
                    )
                ) tt
                GROUP BY class_id, face_id, action
            '''.format(day, CommonUtil.get_date_day(Config.LOOKBACKWINDOW), Config.INTERMEDIATE_TABLE_TRAIN, Config.DETECTED_LOWEST_LIMIT, Config.ACTION_TYPE['face_emotion'])
        else:
            sql = '''
                SELECT
                    CONCAT(college_name, grade_name, class_name) AS class_id, face_id, action, SUM(total) AS total
                FROM {1}
                WHERE dt = '{0}' AND action_type = {2}
                GROUP BY class_id, face_id, action
            '''.format(day, Config.INTERMEDIATE_TABLE_TRAIN, Config.ACTION_TYPE['face_emotion'])

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

            cnt = float(row[3])
            if row[2] == '0': # 正常
                res[key][subKey]['emotion_normal'] = cnt
            elif row[2] == '1': # 开心
                res[key][subKey]['emotion_happy'] = cnt
            elif row[2] == '2': # 低落
                res[key][subKey]['emotion_low'] = cnt
            else:
                continue
        self.__logger.debug("count_face_emotion: " + str(res))

        self.__logger.info("Finished to count face_emotion, and get total {0} records.".format(count))
        return res

    def count_face_pose(self, day, is_lookback = False):
        ''' Compute the count of face pose based on face_id level '''
        # TODO 如何将face_pose_stat考虑到指标计算中
        self.__logger.info("Begin to count by face_pose")
        sql = ''
        if is_lookback:
            sql = '''
                SELECT
                    class_id, face_id, action, COUNT(*) AS total
                FROM (
                    SELECT
                        CONCAT(t1.college_name, t1.grade_name, t1.class_name) AS class_id, t1.face_id, t1.action
                    FROM {2} t1
                    WHERE t1.dt >= '{0}' AND t1.dt <= '{1}' AND t1.course_name = 'rest' AND t1.action_type = {4} AND t1.face_id in
                    (
                        SELECT
                            t2.face_id
                        FROM
                        (
                            SELECT
                                face_id, COUNT(*) AS num
                            FROM {2}
                            WHERE dt >= '{0}' AND dt <= '{1}' AND course_name = 'rest'
                            GROUP BY face_id
                            HAVING num >= {3}
                        ) t2
                    )
                ) tt
                GROUP BY class_id, face_id, action
            '''.format(day, CommonUtil.get_date_day(Config.LOOKBACKWINDOW), Config.INTERMEDIATE_TABLE_TRAIN, Config.DETECTED_LOWEST_LIMIT, Config.ACTION_TYPE['face_pose'])
        else:
            sql = '''
                SELECT
                    CONCAT(college_name, grade_name, class_name) AS class_id, face_id, action, COUNT(*) AS total
                FROM {1}
                WHERE dt = '{0}' AND action_type = {2} AND course_name != 'rest'
                GROUP BY class_id, face_id, action
            '''.format(day, Config.INTERMEDIATE_TABLE_TRAIN, Config.ACTION_TYPE['face_pose'])

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

            cnt = float(row[3])
            if row[2] == '0': # 平视
                res[key][subKey]['face_pose_normal'] = cnt
            elif row[2] == '1': # 左顾右盼
                res[key][subKey]['face_pose_around'] = cnt
            elif row[2] == '2': # 低头
                res[key][subKey]['face_pose_low'] = cnt
            else:
                continue
        self.__logger.debug("count_face_pose: " + str(res))

        self.__logger.info("Finished to count face_pose, and get total {0} records.".format(count))
        return res

    def estimate_relationship(self, metrics, emotions, face_poses, thresholds):
        ''' Estimate the relationship based on threshold and top k'''
        self.__logger.debug("Emotions: " + str(emotions))
        self.__logger.debug("Face_poses: " + str(face_poses))
        self.__logger.debug("Thresholds: " + str(thresholds))
        if metrics.has_key('student_emotion') and metrics['student_emotion'] == Config.RELATIONSHIP_THRESHOLD_SOLITARY['EMOTION_STATUS']\
        and emotions.has_key('emotion_happy') and thresholds.has_key('solitary_smile') and (emotions['emotion_happy'] <= thresholds['solitary_smile'])\
        and face_poses.has_key('face_pose_low') and thresholds.has_key('solitary_low') and (face_poses['face_pose_low'] >= thresholds['solitary_low']): # 人际关系 -- 孤僻
            return 3
        elif metrics.has_key('student_emotion') and metrics['student_emotion'] == Config.RELATIONSHIP_THRESHOLD_GREAT['EMOTION_STATUS']\
        and emotions.has_key('emotion_happy') and thresholds.has_key('great_smile') and (emotions['emotion_happy'] >= thresholds['great_smile'])\
        and face_poses.has_key('face_pose_around') and thresholds.has_key('great_around') and (face_poses['face_pose_around'] >= thresholds['great_around']): # 人际关系 -- 非常好
            return 0
        elif metrics.has_key('student_emotion') and metrics['student_emotion'] in Config.RELATIONSHIP_THRESHOLD_GOOD['EMOTION_STATUS']\
        and emotions.has_key('emotion_happy') and thresholds.has_key('good_smile') and (emotions['emotion_happy'] >= thresholds['good_smile'])\
        and face_poses.has_key('face_pose_around') and thresholds.has_key('good_around') and (face_poses['face_pose_around'] >= thresholds['good_around']): # 人际关系 -- 良好
            return 1
        else: # 人际关系 -- 正常
            return 2