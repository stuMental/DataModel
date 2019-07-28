# !/usr/bin/python
# -*- coding: utf-8 -*-
import Config
import math
import Logger
import numpy as np

class MetricUtil(object):
    """docsTry for MetricUtil"""
    def __init__(self):
        super(MetricUtil, self).__init__()
        self.__logger = Logger.Logger(__name__)
        self.__MINVALUE =  -2147483648 # The min value of INT.
        self.__MAXVALUE = 2147483647 # The max value of INT

    def get_min_value(self):
        return self.__MINVALUE

    def get_max_value(self):
        return self.__MAXVALUE

    def threshold_index(self, index):
        if index < 0:
            return 0;

        return index if index == 0 else index - 1

    def DynamicThreshold(self, data, percentage = 0.2, is_upper = True):
        '''
            Method: Average_Value + 5 * Standard Deviation
            percentage: 去掉高低各该百分比的数据，默认值是20%
            is_upper: True将返回上界阈值，False将返回下界阈值
        '''
        multi_fact = 5;
        if not is_upper:
            multi_fact = -5

        deleteNumber = int(math.floor(len(data) * percentage))
        deleteNumber = 1 if deleteNumber == 0 else deleteNumber # 避免deleteNumber等于0
        self.__logger.debug("DeleteNumber of face_pose_around: " + str(deleteNumber))
        calc_data = data[deleteNumber:-deleteNumber]
        if len(calc_data) != 0:
            result = math.floor(np.mean(calc_data) + multi_fact * np.std(calc_data, ddof=1))
            if np.isnan(result):
                result = self.__MINVALUE if is_upper else self.__MAXVALUE
        else:
            result = self.__MINVALUE if is_upper else self.__MAXVALUE

        return result

    def calculate_study_threshold(self, data):
        ''''''
        normals = []
        arounds = []
        lows = []
        for key, value in data.items():
            if value.has_key('face_pose_normal'):
                normals.append(value['face_pose_normal'])
            if value.has_key('face_pose_around'):
                arounds.append(value['face_pose_around'])
            if value.has_key('face_pose_low'):
                lows.append(value['face_pose_low'])

        normal_len = len(normals)
        thresholds = {}
        if normal_len != 0:
            normals.sort(reverse=True)
            self.__logger.debug(str(normals))
            # 不佳
            thresholds['study_bad'] = normals[self.threshold_index(int(math.floor(normal_len * Config.STUDY_THREHOLD_BAD['FACE_POSE_NORMAL'])))]
            # 非常好
            thresholds['study_great'] = normals[self.threshold_index(int(math.floor(normal_len * Config.STUDY_THREHOLD_GREAT['FACE_POSE_NORMAL'])))]
            # 良好
            thresholds['study_good'] = normals[self.threshold_index(int(math.floor(normal_len * Config.STUDY_THREHOLD_GOOD['FACE_POSE_NORMAL'])))]

        arounds_len = len(arounds)
        if arounds_len != 0:
            arounds.sort(reverse=True)
            self.__logger.debug(str(arounds))
            thresholds['study_bad_around'] = arounds[self.threshold_index(int(math.floor(arounds_len * Config.STUDY_THREHOLD_BAD['FACE_POSE_AROUND'])))]
            thresholds['study_bad_around_count'] = self.DynamicThreshold(arounds, Config.DYNAMIC_DELETE_PERCENTAGE, is_upper=True)

        lows_len = len(lows)
        if lows_len != 0:
            lows.sort(reverse=True)
            self.__logger.debug(str(lows))
            thresholds['study_bad_low'] = lows[self.threshold_index(int(math.floor(arounds_len * Config.STUDY_THREHOLD_BAD['FACE_POSE_LOW'])))]
            thresholds['study_bad_low_count'] = self.DynamicThreshold(lows, Config.DYNAMIC_DELETE_PERCENTAGE, is_upper=True)

        self.__logger.debug("Study Thresholds: " + str(thresholds))

        return thresholds

    def calculate_emotion_threshold(self, data):
        ''''''
        res_happy = []
        res_low = []
        for key, value in data.items():
            if value.has_key('emotion_happy'):
                res_happy.append(value['emotion_happy'])
            if value.has_key('emotion_low'):
                res_low.append(value['emotion_low'])

        thresholds = {}
        if len(res_low) != 0:
            # 低落
            res_low.sort(reverse=True)
            self.__logger.debug(str(res_low))
            thresholds['emotion_low'] = res_low[self.threshold_index(int(math.floor(len(res_low) * Config.EMOTION_THRESHOLD_LOW['SAD_RATIO'])))]
            thresholds['emotion_low_count'] = self.DynamicThreshold(res_low, Config.DYNAMIC_DELETE_PERCENTAGE, is_upper=True)

        if len(res_happy) != 0:
            # 开心
            res_happy.sort(reverse=True)
            self.__logger.debug(str(res_happy))
            thresholds['emotion_happy'] = res_happy[self.threshold_index(int(math.floor(len(res_happy) * Config.EMOTION_THRESHOLD_HAPPY['SMILE_RATIO'])))]
            thresholds['emotion_happy_count'] = self.DynamicThreshold(res_happy, Config.DYNAMIC_DELETE_PERCENTAGE, is_upper=True)

        self.__logger.debug("Emotion threshold: " + str(thresholds))
        return thresholds

    def calculate_mental_threshold(self, data):
        body_stat_sttk = []
        body_stat_pztk = []
        body_stat_standup = []
        body_stat_handup = []
        for key, value in data.items():
            if value.has_key('body_stat_sttk'):
                body_stat_sttk.append(value['body_stat_sttk'])
            if value.has_key('body_stat_pztk'):
                body_stat_pztk.append(value['body_stat_pztk'])
            if value.has_key('body_stat_standup'):
                body_stat_standup.append(value['body_stat_standup'])
            if value.has_key('body_stat_handup'):
                body_stat_handup.append(value['body_stat_handup'])

        thresholds = {}
        if len(body_stat_sttk) != 0:
            # 手托头听课
            body_stat_sttk.sort(reverse=True)
            self.__logger.debug(str(body_stat_sttk))
            thresholds['body_stat_sttk_count'] = self.DynamicThreshold(body_stat_sttk, Config.DYNAMIC_DELETE_PERCENTAGE, is_upper=True)

        if len(body_stat_pztk) != 0:
            # 手托头听课
            body_stat_pztk.sort(reverse=True)
            self.__logger.debug(str(body_stat_pztk))
            thresholds['body_stat_pztk_count'] = self.DynamicThreshold(body_stat_pztk, Config.DYNAMIC_DELETE_PERCENTAGE, is_upper=True)

        if len(body_stat_standup) != 0:
            # 手托头听课
            body_stat_standup.sort(reverse=True)
            self.__logger.debug(str(body_stat_standup))
            thresholds['body_stat_standup_count'] = self.DynamicThreshold(body_stat_standup, Config.DYNAMIC_DELETE_PERCENTAGE, is_upper=True)

        if len(body_stat_handup) != 0:
            # 手托头听课
            body_stat_handup.sort(reverse=True)
            self.__logger.debug(str(body_stat_handup))
            thresholds['body_stat_handup_count'] = self.DynamicThreshold(body_stat_handup, Config.DYNAMIC_DELETE_PERCENTAGE, is_upper=True)

        self.__logger.debug("Emotion threshold: " + str(thresholds))
        return thresholds

    def estimate_study_stat(self, mentals, face_poses, thresholds):
        ''''''
        self.__logger.debug("Mentals: " + str(mentals))
        self.__logger.debug("Face_pose: " + str(face_poses))
        self.__logger.debug("Thresholds: " + str(thresholds))

        # 去动态阈值和固定阈值中最大值，作为最后的阈值
        low_count_threshold = Config.STUDY_THREHOLD_BAD['FACE_POSE_LOW_CNT']
        if thresholds.has_key('study_bad_low_count'):
            low_count_threshold = max(thresholds['study_bad_low_count'], Config.STUDY_THREHOLD_BAD['FACE_POSE_LOW_CNT'])

        around_count_threshold = Config.STUDY_THREHOLD_BAD['FACE_POSE_AROUND_CNT']
        if thresholds.has_key('study_bad_around_count'):
            around_count_threshold = max(thresholds['study_bad_around_count'], Config.STUDY_THREHOLD_BAD['FACE_POSE_AROUND_CNT'])

        self.__logger.debug("low_count_threshold: {0}, around_count_threshold: {1}.".format(low_count_threshold, around_count_threshold))

        if (mentals.has_key('student_mental_stat') and (mentals['student_mental_stat'] == Config.STUDY_THREHOLD_BAD['MENTAL'])\
        and face_poses.has_key('face_pose_normal') and thresholds.has_key('study_bad') and (face_poses['face_pose_normal'] <= thresholds['study_bad'])) \
        or (face_poses.has_key('face_pose_around') and thresholds.has_key('study_bad_around') and (face_poses['face_pose_around'] >= thresholds['study_bad_around']) and (face_poses['face_pose_around'] >= around_count_threshold))\
        or (face_poses.has_key('face_pose_low') and thresholds.has_key('study_bad_low') and (face_poses['face_pose_low'] >= thresholds['study_bad_low']) and (face_poses['face_pose_low'] >= low_count_threshold)): # 学习状态 -- 不佳
            return 3
        elif mentals.has_key('student_mental_stat') and (mentals['student_mental_stat'] == Config.STUDY_THREHOLD_GREAT['MENTAL'])\
        and face_poses.has_key('face_pose_normal') and thresholds.has_key('study_great') and (face_poses['face_pose_normal'] >= thresholds['study_great']) and (face_poses['face_pose_normal'] >= Config.STUDY_THREHOLD_GREAT['FACE_POSE_NORMAL_CNT']): # 学习状态 -- 非常好
            return 0
        elif mentals.has_key('student_mental_stat') and (mentals['student_mental_stat'] in Config.STUDY_THREHOLD_GOOD['MENTAL'])\
        and face_poses.has_key('face_pose_normal') and thresholds.has_key('study_good') and (face_poses['face_pose_normal'] >= thresholds['study_good']) and (face_poses['face_pose_normal'] >= Config.STUDY_THREHOLD_GOOD['FACE_POSE_NORMAL_CNT']): # 学习状态 -- 良好
            return 1
        else: # 学习状态 -- 正常
            return 2

    def estimate_mental_stat(self, emotions, body_stats, thresholds):
        ''''''
        self.__logger.debug("Emotion: " + str(emotions))
        self.__logger.debug("Body_Stat: " + str(body_stats))

        body_stat_sttk_threshold = Config.MENTAL_THRESHOLD_TIRED['BODY_STAT']
        body_stat_pztk_threshold = Config.MENTAL_THRESHOLD_TIRED['BODY_STAT']
        body_stat_standup_threshold = Config.MENTAL_THRESHOLD_POSITIVE['BODY_STAT']
        body_stat_handup_threshold = Config.MENTAL_THRESHOLD_POSITIVE['BODY_STAT']
        if thresholds.has_key('body_stat_sttk_count'):
            body_stat_sttk_threshold = max(body_stat_sttk_threshold, thresholds['body_stat_sttk_count'])
        if thresholds.has_key('body_body_stat_pztk'):
            body_stat_pztk_threshold = max(body_stat_pztk_threshold, thresholds['body_stat_pztk_count'])
        if thresholds.has_key('body_stat_standup_count'):
            body_stat_standup_threshold = max(body_stat_standup_threshold, thresholds['body_stat_standup_count'])
        if thresholds.has_key('body_stat_handup_count'):
            body_stat_handup_threshold = max(body_stat_handup_threshold, thresholds['body_stat_handup_count'])
        self.__logger.debug("body_stat_sttk_threshold: {0}, body_stat_pztk_threshold: {1}, body_stat_standup_threshold: {2}, body_stat_handup_threshold: {3}.".format(body_stat_sttk_threshold, body_stat_pztk_threshold, body_stat_standup_threshold, body_stat_handup_threshold))

        if (emotions.has_key('student_emotion') and emotions['student_emotion'] == Config.MENTAL_THRESHOLD_TIRED['EMOTION_STATUS']) \
        and ((body_stats.has_key('body_stat_sttk') and body_stats['body_stat_sttk'] >= body_stat_sttk_threshold) \
        or (body_stats.has_key('body_stat_pztk') and body_stats['body_stat_pztk'] >= body_stat_pztk_threshold)): # 精神状态 -- 疲惫
            return 2
        elif (emotions.has_key('student_emotion') and emotions['student_emotion'] == Config.MENTAL_THRESHOLD_POSITIVE['EMOTION_STATUS']) \
        and ((body_stats.has_key('body_stat_standup') and body_stats['body_stat_standup'] >= body_stat_standup_threshold) \
        or (body_stats.has_key('body_stat_handup') and body_stats['body_stat_handup'] >= body_stat_handup_threshold)): # 精神状态 -- 积极
            return 0
        else: # 正常
            return 1

    def estimate_emotion(self, emotions, thresholds):
        ''''''
        self.__logger.debug("Emotions: " + str(emotions))
        self.__logger.debug("Thresholds: " + str(thresholds))
        emotion_low_cnt_threshold = Config.EMOTION_THRESHOLD_LOW['SAD_FREQUENCY']
        emotion_happy_cnt_threshold = Config.EMOTION_THRESHOLD_HAPPY['SMILE_FREQUENCY']
        if thresholds.has_key('emotion_low_count'):
            emotion_low_cnt_threshold = max(thresholds['emotion_low_count'], emotion_low_cnt_threshold)
        if thresholds.has_key('emotion_happy_count'):
            emotion_happy_cnt_threshold = max(thresholds['emotion_happy_count'], emotion_happy_cnt_threshold)
        self.__logger.debug("emotion_low_cnt_threshold: {0}, emotion_happy_cnt_threshold: {1}.".format(emotion_low_cnt_threshold, emotion_happy_cnt_threshold))

        if emotions.has_key('emotion_low') and thresholds.has_key('emotion_low') and (emotions['emotion_low'] >= emotion_low_cnt_threshold) and (emotions['emotion_low'] >= thresholds['emotion_low']): # 情绪 -- 低落
            return 2
        elif emotions.has_key('emotion_happy') and thresholds.has_key('emotion_happy') and (emotions['emotion_happy'] >= emotion_happy_cnt_threshold) and (emotions['emotion_happy'] >= thresholds['emotion_happy']): # 情绪 -- 开心
            return 0
        else: # 情绪 -- 正常
            return 1