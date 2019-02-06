# !/usr/bin/python
# -*- coding: utf-8 -*-
import Config
import DbUtil
import Logger
import math
import CommonUtil
import MetricUtil

class CalcMetric(object):
    """docstring for CalcMetric"""
    def __init__(self):
        super(CalcMetric, self).__init__()
        self.__db = DbUtil.DbUtil(Config.INPUT_DB_HOST, Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__util = MetricUtil.MetricUtil()
        self.__logger = Logger.Logger(__name__)

    def calculate_daily_metrics(self, start_time, end_time):
        """
            Calculate 4 metrics, including student_emotion, student_study_stat, student_relationship, and student_mental_stat.
            return {
                'face_id1' => {'student_emotion' => value, 'student_study_stat' => value, 'student_relationship' => value, 'student_mental_stat' => value}, 
                'face_id2' => {'student_emotion' => value, 'student_study_stat' => value, 'student_relationship' => value, 'student_mental_stat' => value}
            }
        """

        # Compute the count of each basic metric
        self.__logger.info("Tring to compute basic metrics")
        body_stat_count = self.count_body_stat(start_time, end_time)
        emotion_count = self.count_face_emotion(start_time, end_time)
        face_pose_count = self.count_face_pose(start_time, end_time)
        self.__logger.info("Finished to compte basic metrcis")


        self.__logger.info("Tring to comput the high-level metrics")
        metrcis = {}
        # Calculate student mental status based on body_stat and emotion
        for key, value in emotion_count.items():
            if body_stat_count.has_key(key):
                if not metrcis.has_key(key):
                    metrcis[key] = {}
                metrcis[key]['student_mental_stat'] = self.__util.estimate_mental_stat(value, body_stat_count[key])

        # Calculate student study status based on student mental and face_pose
        # Calculate threshold
        study_stat_thresholds = self.__util.calculate_study_threshold(face_pose_count)
        for key in metrcis:
            if face_pose_count.has_key(key):
                metrcis[key]['student_study_stat'] = self.__util.estimate_study_stat(metrcis[key], face_pose_count[key], study_stat_thresholds)

        # Calculate student emotion based on emotions
        # Calculate threshold
        emotion_thresholds = self.calculate_emotion_threshold(emotion_count)
        for key in metrcis:
            if emotion_count.has_key(key):
                metrcis[key]['student_emotion'] = self.estimate_emotion(emotion_count[key], emotion_thresholds)

        # Calculate student relationship based on emotions, facePoses
        # Calculate threshold
        relationship_thresholds = self.calculate_relationship_threshold(emotion_count, face_pose_count)
        emotion_count = self.count_face_emotion(CommonUtil.get_specific_time(end_time, Config.LOOKBACKWINDOW), end_time, True)
        face_pose_count = self.count_face_pose(CommonUtil.get_specific_time(end_time, Config.LOOKBACKWINDOW), end_time, True)
        for key in metrcis:
            if emotion_count.has_key(key) and face_pose_count.has_key(key):
                metrcis[key]['student_relationship'] = self.estimate_relationship(emotion_count[key], face_pose_count[key], relationship_thresholds)
        self.__logger.info("Finished to compute high-level metrics")

        return metrcis

    def calculate_emotion_threshold(self, data):
        ''''''
        res_happy = []
        for key, value in data.items():
            res_happy.append(value['emotion_happy'])
        res_happy.sort(reverse=True)

        res_low = []
        for key, value in data.items():
            res_low.append(value['emotion_low'])
        res_low.sort(reverse=True)

        length = len(data)
        thresholds = {}
        # 低落
        thresholds['emotion_low'] = res_low[math.floor(length * Config.EMOTION_THRESHOLD_LOW['SAD_RATIO'])]
        # 开心
        thresholds['emotion_happy'] = res_happy[math.floor(length * Config.EMOTION_THRESHOLD_HAPPY['SMILE_RATIO'])]

        return thresholds

    def calculate_relationship_threshold(self, emotions, face_poses):
        ''''''
        smiles = []
        for key, value in emotions.items():
            smiles.append(value['emotion_happy'])
        smiles.sort(reverse=True)

        arounds = []
        lows = []
        for key, value in face_poses.items():
            arounds.append(value['face_pose_around'])
            lows.append(value['face_pose_low'])
        arounds.sort(reverse=True)
        lows.sort(reverse=True)

        thresholds = {}
        smile_len = len(smiles)
        around_len = len(arounds)
        low_len = len(lows)
        # face_pose 低头
        thresholds['solitary_low'] = lows[math.floor(low_len * Config.RELATIONSHIP_THRESHOLD_SOLITARY['FACE_POSE_LOW'])]
        # face_pose 左顾右盼
        thresholds['great_around'] = smiles[math.floor(smile_len * Config.RELATIONSHIP_THRESHOLD_GREAT['FACE_POSE_AROUND'])]
        thresholds['good_around'] = smiles[math.floor(smile_len * Config.RELATIONSHIP_THRESHOLD_GOOD['FACE_POSE_AROUND'])]
        # emotion 微笑
        thresholds['solitary_smile'] = smiles[math.floor(smile_len * Config.RELATIONSHIP_THRESHOLD_SOLITARY['EMOTION_SMILE'])]
        thresholds['great_smile'] = smiles[math.floor(smile_len * Config.RELATIONSHIP_THRESHOLD_GREAT['EMOTION_SMILE'])]
        thresholds['good_smile'] = smiles[math.floor(smile_len * Config.RELATIONSHIP_THRESHOLD_GOOD['EMOTION_SMILE'])]

        return thresholds

    def count_body_stat(self, start_time, end_time):
        ''''''
        sql = '''
            SELECT
                face_id, body_stat, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND body_stat != -1 AND face_id != 'unknown'
            GROUP BY face_id, body_stat
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN)

        res = {}
        for row in self.__db.select(sql):
            if not res.has_key(row[0]):
                res[row[0]] = {}

            if row[1] == 0: # 正常
                res[row[0]]['body_stat_normal'] = row[2]
            elif row[1] == 1: # 站立
                res[row[0]]['body_stat_standup'] = row[2]
            elif row[1] == 2: # 举手
                res[row[0]]['body_stat_handup'] = row[2]
            elif row[1] == 3: # 睡觉
                res[row[0]]['body_stat_sleep'] = row[2]
            elif row[1] == 4: # 手托着听课
                res[row[0]]['body_stat_sttk'] = row[2]
            elif row[1] == 5: # 趴着听课
                res[row[0]]['body_stat_pztk'] = row[2]
            else:
                continue

        return res

    def count_face_emotion(self, start_time, end_time, is_lookback=False):
        ''''''
        sql = ''
        if is_lookback:
            sql = '''
                SELECT
                    face_id, face_emotion, COUNT(*) AS total
                FROM {2}
                WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_id in
                (
                    SELECT
                        face_id
                    FROM
                    (
                        SELECT
                            face_id, COUNT(*) AS num
                        FROM {2}
                        WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_id != 'unknown'
                        HAVING num >= {3}
                    )
                )
                GROUP BY face_id, face_emotion
            '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN, Config.DETECTED_LOWEST_LIMIT)
        else:
            sql = '''
                SELECT
                    face_id, face_emotion, COUNT(*) AS total
                FROM {2}
                WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_emotion != -1 AND face_id != 'unknown'
                GROUP BY face_id, face_emotion
            '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN)

        res = {}
        for row in self.__db.select(sql):
            if not res.has_key(row[0]):
                res[row[0]] = {}

            if row[1] == 0: # 正常
                res[row[0]]['emotion_normal'] = row[2]
            elif row[1] == 1: # 开心
                res[row[0]]['emotion_happy'] = row[2]
            elif row[1] == 2: # 低落
                res[row[0]]['emotion_low'] = row[2]
            else:
                continue

        return res

    def count_face_pose(self, start_time, end_time, is_lookback = False):
        ''' Compute the count of face pose based on face_id level '''
        sql = ''
        if is_lookback:
            sql = '''
                SELECT
                    face_id, face_pose, COUNT(*) AS total
                FROM {2}
                WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_id in
                (
                    SELECT
                        face_id
                    FROM
                    (
                        SELECT
                            face_id, COUNT(*) AS num
                        FROM {2}
                        WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_id != 'unknown'
                        HAVING num >= {3}
                    )
                )
                GROUP BY face_id, face_pose
            '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN, Config.DETECTED_LOWEST_LIMIT)
        else:
            sql = '''
                SELECT
                    face_id, face_pose, COUNT(*) AS total
                FROM {2}
                WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_pose != -1 AND face_pose_stat == 0 AND face_id != 'unknown'
                GROUP BY face_id, face_pose
            '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN)

        res = {}
        for row in self.__db.select(sql):
            if not res.has_key(row[0]):
                res[row[0]] = {}

            if row[1] == 0: # 平视
                res[row[0]]['face_pose_normal'] = row[2]
            elif row[1] == 1: # 左顾右盼
                res[row[0]]['face_pose_around'] = row[2]
            elif row[1] == 2: # 低头
                res[row[0]]['face_pose_low'] = row[2]
            else:
                continue

        return res

    def estimate_relationship(self, emotions, face_poses, thresholds):
        ''' Estimate the relationship based on threshold and top k'''
        if emotions['emotion_happy'] < thresholds['solitary_smile'] and face_poses['face_pose_low'] > thresholds['solitary_low']: # 人际关系 -- 孤僻
            return 3
        elif emotions['emotion_happy'] > thresholds['great_smile']  and face_poses['face_pose_around'] > thresholds['great_around']: # 人际关系 -- 非常好
            return 0
        elif emotions['emotion_happy'] > thresholds['good_smile'] and face_poses['face_pose_around'] > thresholds['good_around']: # 人际关系 -- 良好
            return 1
        else: # 人际关系 -- 正常
            return 2

    def estimate_emotion(self, emotions, thresholds):
        ''''''
        if emotions['emotion_low'] > Config.EMOTION_THRESHOLD_LOW['SAD_FREQUENCY'] and emotions['emotion_low'] > thresholds['emotion_low']: # 情绪 -- 低落
            return 2
        elif emotions['emotion_happy'] > Config.EMOTION_THRESHOLD_HAPPY['SMILE_FREQUENCY'] and emotions['emotion_happy'] > thresholds['emotion_happy']: # 情绪 -- 开心
            return 0
        else: # 情绪 -- 正常
            return 1