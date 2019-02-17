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
    def __init__(self):
        super(CalcMetric, self).__init__()
        self.__db = DbUtil.DbUtil(Config.INPUT_DB_HOST, Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__util = MetricUtil.MetricUtil()
        self.__logger = Logger.Logger(__name__)

    def calculate_daily_metrics(self, start_time, end_time):
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
        """

        # Compute the count of each basic metric
        self.__logger.info("Try to compute basic metrics")
        body_stat_count = self.count_body_stat(start_time, end_time)
        emotion_count = self.count_face_emotion(start_time, end_time)
        face_pose_count = self.count_face_pose(start_time, end_time)
        self.__logger.info("Finished to compte basic metrics")

        self.__logger.info("Try to comput the high-level metrics")
        metrics = {}

        # Calculate student mental status based on body_stat and emotion
        self.__logger.info("Begin to compute student_mental_stat")
        for class_id, values in emotion_count.items():
            if body_stat_count.has_key(class_id):
                for face_id, value in values.items():
                    if not metrics.has_key(class_id):
                        metrics[class_id] = {}
                    if not metrics[class_id].has_key(face_id):
                        metrics[class_id][face_id] = {}
                    metrics[class_id][face_id]['student_mental_stat'] = self.__util.estimate_mental_stat(value, body_stat_count[class_id][face_id])

        # Calculate student study status based on student mental and face_pose
        # Calculate threshold
        self.__logger.info("Begin to compute student_study_stat")
        for class_id, values in metrics.items():
            if face_pose_count.has_key(class_id):
                study_stat_thresholds = self.__util.calculate_study_threshold(face_pose_count[class_id])
                for face_id in values:
                    if face_pose_count[class_id].has_key(face_id):
                        metrics[class_id][face_id]['student_study_stat'] = self.__util.estimate_study_stat(metrics[class_id][face_id], face_pose_count[class_id][face_id], study_stat_thresholds)

        # Calculate student emotion based on emotions
        # Calculate threshold
        self.__logger.info("Begin to compute student_emotion")
        for class_id, values in metrics.items():
            if emotion_count.has_key(class_id):
                emotion_thresholds = self.calculate_emotion_threshold(emotion_count[class_id])
                for face_id in values:
                    if emotion_count[class_id].has_key(face_id):
                        metrics[class_id][face_id]['student_emotion'] = self.estimate_emotion(emotion_count[class_id][face_id], emotion_thresholds)

        # Calculate student relationship based on emotions, facePoses
        # Calculate threshold
        self.__logger.info("Begin to compute student_relationship")
        emotion_count = self.count_face_emotion(CommonUtil.get_specific_unixtime(end_time, Config.LOOKBACKWINDOW), end_time, True)
        face_pose_count = self.count_face_pose(CommonUtil.get_specific_unixtime(end_time, Config.LOOKBACKWINDOW), end_time, True)
        for class_id, values in metrics.items():
            if emotion_count.has_key(class_id) and face_pose_count.has_key(class_id):
                relationship_thresholds = self.calculate_relationship_threshold(emotion_count[class_id], face_pose_count[class_id])
                for face_id in values:
                    if emotion_count[class_id].has_key(face_id) and face_pose_count[class_id].has_key(face_id):
                        metrics[class_id][face_id]['student_relationship'] = self.estimate_relationship(emotion_count[class_id][face_id], face_pose_count[class_id][face_id], relationship_thresholds)

        self.__logger.debug(str(metrics))
        self.__logger.info("Finished to compute high-level metrics")

        return metrics

    def calculate_emotion_threshold(self, data):
        ''''''
        res_happy = []
        for key, value in data.items():
            if value.has_key('emotion_happy'):
                res_happy.append(value['emotion_happy'])

        res_low = []
        for key, value in data.items():
            if value.has_key('emotion_low'):
                res_low.append(value['emotion_low'])

        thresholds = {}
        if len(res_low) != 0:
            # 低落
            res_low.sort(reverse=True)
            self.__logger.debug(str(res_low))
            thresholds['emotion_low'] = res_low[int(math.floor(len(res_low) * Config.EMOTION_THRESHOLD_LOW['SAD_RATIO']))]
        if len(res_happy) != 0:
            # 开心
            res_happy.sort(reverse=True)
            self.__logger.debug(str(res_happy))
            thresholds['emotion_happy'] = res_happy[int(math.floor(len(res_happy) * Config.EMOTION_THRESHOLD_HAPPY['SMILE_RATIO']))]

        return thresholds

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
            thresholds['solitary_low'] = lows[int(math.floor(low_len * Config.RELATIONSHIP_THRESHOLD_SOLITARY['FACE_POSE_LOW']))]
        if around_len != 0:
            # face_pose 左顾右盼
            arounds.sort(reverse=True)
            self.__logger.debug(str(arounds))
            thresholds['great_around'] = arounds[int(math.floor(around_len * Config.RELATIONSHIP_THRESHOLD_GREAT['FACE_POSE_AROUND']))]
            thresholds['good_around'] = arounds[int(math.floor(around_len * Config.RELATIONSHIP_THRESHOLD_GOOD['FACE_POSE_AROUND']))]
        if smile_len != 0:
            # emotion 微笑
            smiles.sort(reverse=True)
            self.__logger.debug(str(smiles))
            thresholds['solitary_smile'] = smiles[int(math.floor(smile_len * Config.RELATIONSHIP_THRESHOLD_SOLITARY['EMOTION_SMILE']))]
            thresholds['great_smile'] = smiles[int(math.floor(smile_len * Config.RELATIONSHIP_THRESHOLD_GREAT['EMOTION_SMILE']))]
            thresholds['good_smile'] = smiles[int(math.floor(smile_len * Config.RELATIONSHIP_THRESHOLD_GOOD['EMOTION_SMILE']))]

        return thresholds

    def count_body_stat(self, start_time, end_time):
        ''''''
        self.__logger.info("Begin to count by body_stat")
        sql = '''
            SELECT
                class_id, face_id, body_stat, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND body_stat != '-1' AND face_id != 'unknown' AND course_name != 'rest'
            GROUP BY class_id, face_id, body_stat
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

            if row[2] == '0': # 正常
                res[key][subKey]['body_stat_normal'] = row[3]
            elif row[2] == '1': # 站立
                res[key][subKey]['body_stat_standup'] = row[3]
            elif row[2] == '2': # 举手
                res[key][subKey]['body_stat_handup'] = row[3]
            elif row[2] == '3': # 睡觉
                res[key][subKey]['body_stat_sleep'] = row[3]
            elif row[2] == '4': # 手托着听课
                res[key][subKey]['body_stat_sttk'] = row[3]
            elif row[2] == '5': # 趴着听课
                res[key][subKey]['body_stat_pztk'] = row[3]
            else:
                continue
        self.__logger.debug("count_body_stat: " + str(res))

        self.__logger.info("Finished to count body_stat, and get total {0} records.".format(count))
        return res

    def count_face_emotion(self, start_time, end_time, is_lookback=False):
        ''''''
        self.__logger.info("Begin to count by face_emotion")
        sql = ''
        if is_lookback:
            sql = '''
                SELECT
                    t1.class_id, t1.face_id, t1.face_emotion, COUNT(*) AS total
                FROM {2} t1
                WHERE t1.pose_stat_time >= {0} AND t1.pose_stat_time <= {1} AND t1.face_emotion != '-1' AND t1.course_name = 'rest' AND t1.face_id in
                (
                    SELECT
                        t2.face_id
                    FROM
                    (
                        SELECT
                            face_id, COUNT(*) AS num
                        FROM {2}
                        WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_id != 'unknown' AND course_name = 'rest'
                        GROUP BY face_id
                        HAVING num >= {3}
                    ) t2
                )
                GROUP BY t1.class_id, t1.face_id, t1.face_emotion
            '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN, Config.DETECTED_LOWEST_LIMIT)
        else:
            sql = '''
                SELECT
                    class_id, face_id, face_emotion, COUNT(*) AS total
                FROM {2}
                WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_emotion != '-1' AND face_id != 'unknown' AND course_name != 'rest'
                GROUP BY class_id, face_id, face_emotion
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

            if row[2] == '0': # 正常
                res[key][subKey]['emotion_normal'] = row[3]
            elif row[2] == '1': # 开心
                res[key][subKey]['emotion_happy'] = row[3]
            elif row[2] == '2': # 低落
                res[key][subKey]['emotion_low'] = row[3]
            else:
                continue
        self.__logger.debug("count_face_emotion: " + str(res))

        self.__logger.info("Finished to count face_emotion, and get total {0} records.".format(count))
        return res

    def count_face_pose(self, start_time, end_time, is_lookback = False):
        ''' Compute the count of face pose based on face_id level '''
        # TODO 如何将face_pose_stat考虑到指标计算中
        self.__logger.info("Begin to count by face_pose")
        sql = ''
        if is_lookback:
            sql = '''
                SELECT
                    t1.class_id, t1.face_id, t1.face_pose, COUNT(*) AS total
                FROM {2} t1
                WHERE t1.pose_stat_time >= {0} AND t1.pose_stat_time <= {1} AND t1.course_name = 'rest' AND t1.face_pose != '-1' AND t1.face_id in
                (
                    SELECT
                        t2.face_id
                    FROM
                    (
                        SELECT
                            face_id, COUNT(*) AS num
                        FROM {2}
                        WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_id != 'unknown' AND course_name = 'rest'
                        GROUP BY face_id
                        HAVING num >= {3}
                    ) t2
                )
                GROUP BY t1.class_id, t1.face_id, t1.face_pose
            '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN, Config.DETECTED_LOWEST_LIMIT)
        else:
            sql = '''
                SELECT
                    class_id, face_id, face_pose, COUNT(*) AS total
                FROM {2}
                WHERE pose_stat_time >= {0} AND pose_stat_time <= {1} AND face_pose != '-1' AND face_id != 'unknown' AND course_name != 'rest'
                GROUP BY class_id, face_id, face_pose
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

            if row[2] == '0': # 平视
                res[key][subKey]['face_pose_normal'] = row[3]
            elif row[2] == '1': # 左顾右盼
                res[key][subKey]['face_pose_around'] = row[3]
            elif row[2] == '2': # 低头
                res[key][subKey]['face_pose_low'] = row[3]
            else:
                continue
        self.__logger.debug("count_face_pose: " + str(res))

        self.__logger.info("Finished to count face_pose, and get total {0} records.".format(count))
        return res

    def estimate_relationship(self, emotions, face_poses, thresholds):
        ''' Estimate the relationship based on threshold and top k'''
        self.__logger.debug("Emotions: " + str(emotions))
        self.__logger.debug("Face_poses: " + str(face_poses))
        self.__logger.debug("Thresholds: " + str(thresholds))
        if emotions.has_key('emotion_happy') and thresholds.has_key('solitary_smile') and (emotions['emotion_happy'] <= thresholds['solitary_smile'])\
        and face_poses.has_key('face_pose_low') and thresholds.has_key('solitary_low') and (face_poses['face_pose_low'] >= thresholds['solitary_low']): # 人际关系 -- 孤僻
            return 3
        elif emotions.has_key('emotion_happy') and thresholds.has_key('great_smile') and (emotions['emotion_happy'] >= thresholds['great_smile'])\
        and face_poses.has_key('face_pose_around') and thresholds.has_key('great_around') and (face_poses['face_pose_around'] >= thresholds['great_around']): # 人际关系 -- 非常好
            return 0
        elif emotions.has_key('emotion_happy') and thresholds.has_key('good_smile') and (emotions['emotion_happy'] >= thresholds['good_smile'])\
        and face_poses.has_key('face_pose_around') and thresholds.has_key('good_around') and (face_poses['face_pose_around'] >= thresholds['good_around']): # 人际关系 -- 良好
            return 1
        else: # 人际关系 -- 正常
            return 2

    def estimate_emotion(self, emotions, thresholds):
        ''''''
        self.__logger.debug("Emotions: " + str(emotions))
        self.__logger.debug("Thresholds: " + str(thresholds))
        if emotions.has_key('emotion_low') and thresholds.has_key('emotion_low') and (emotions['emotion_low'] >= Config.EMOTION_THRESHOLD_LOW['SAD_FREQUENCY']) and (emotions['emotion_low'] >= thresholds['emotion_low']): # 情绪 -- 低落
            return 2
        elif emotions.has_key('emotion_happy') and thresholds.has_key('emotion_happy') and (emotions['emotion_happy'] >= Config.EMOTION_THRESHOLD_HAPPY['SMILE_FREQUENCY']) and (emotions['emotion_happy'] >= thresholds['emotion_happy']): # 情绪 -- 开心
            return 0
        else: # 情绪 -- 正常
            return 1