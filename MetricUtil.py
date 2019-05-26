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

    def threshold_index(self, index):
        if index < 0:
            return 0;

        return index if index == 0 else index - 1

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
            deleteNumber = int(math.floor(arounds_len * Config.STUDY_THREHOLD_BAD['FACE_POSE_PERCENTAGE']))
            deleteNumber = 1 if deleteNumber == 0 else deleteNumber # 避免deleteNumber等于0
            self.__logger.debug("DeleteNumber of face_pose_around: " + str(deleteNumber))
            around_data = arounds[deleteNumber:-deleteNumber]
            thresholds['study_bad_around_count'] = math.floor(np.mean(around_data) + 5 * np.std(around_data, ddof=1))
            thresholds['study_bad_around_count'] = 0 if np.isnan(thresholds['study_bad_around_count']) else thresholds['study_bad_around_count']

        lows_len = len(lows)
        if lows_len != 0:
            lows.sort(reverse=True)
            self.__logger.debug(str(lows))
            thresholds['study_bad_low'] = arounds[self.threshold_index(int(math.floor(arounds_len * Config.STUDY_THREHOLD_BAD['FACE_POSE_LOW'])))]
            deleteNumber = int(math.floor(lows_len * Config.STUDY_THREHOLD_BAD['FACE_POSE_PERCENTAGE']))
            deleteNumber = 1 if deleteNumber == 0 else deleteNumber # 避免deleteNumber等于0
            self.__logger.debug("DeleteNumber of face_pose_low: " + str(deleteNumber))
            low_data = lows[deleteNumber:-deleteNumber]
            thresholds['study_bad_low_count'] = math.floor(np.mean(low_data) + 5 * np.std(low_data, ddof=1))
            thresholds['study_bad_low_count'] = 0 if np.isnan(thresholds['study_bad_low_count']) else thresholds['study_bad_low_count']

        self.__logger.debug("Study Thresholds: " + str(thresholds))

        return thresholds

    def estimate_study_stat(self, mentals, face_poses, thresholds):
        ''''''
        self.__logger.debug("Mentals: " + str(mentals))
        self.__logger.debug("Face_pose: " + str(face_poses))
        self.__logger.debug("Thresholds: " + str(thresholds))

        # 去动态阈值和固定阈值中最大值，作为最后的阈值
        low_count_threshold = max(thresholds['study_bad_low_count'], Config.STUDY_THREHOLD_BAD['FACE_POSE_LOW_CNT'])
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

    def estimate_mental_stat(self, emotions, body_stats):
        ''''''
        self.__logger.debug("Emotion: " + str(emotions))
        self.__logger.debug("Body_Stat: " + str(body_stats))
        if ((emotions.has_key('emotion_happy') and emotions['emotion_happy'] <= Config.MENTAL_THRESHOLD_TIRED['EMOTION_SMILE']) \
            or (emotions.has_key('emotion_low') and emotions['emotion_low'] >= Config.MENTAL_THRESHOLD_TIRED['EMOTION_LOW'])) \
        and ((body_stats.has_key('body_stat_sttk') and body_stats['body_stat_sttk'] >= Config.MENTAL_THRESHOLD_TIRED['BODY_STAT']) \
        or (body_stats.has_key('body_stat_pztk') and body_stats['body_stat_pztk'] >= Config.MENTAL_THRESHOLD_TIRED['BODY_STAT'])): # 精神状态 -- 疲惫
            return 2
        elif (emotions.has_key('emotion_happy') and emotions['emotion_happy'] >= Config.MENTAL_THRESHOLD_POSITIVE['EMOTION_SMILE']) \
        and ((body_stats.has_key('body_stat_standup') and body_stats['body_stat_standup'] >= Config.MENTAL_THRESHOLD_POSITIVE['BODY_STAT']) \
        or (body_stats.has_key('body_stat_handup') and body_stats['body_stat_handup'] >= Config.MENTAL_THRESHOLD_POSITIVE['BODY_STAT'])): # 精神状态 -- 积极
            return 0
        else: # 正常
            return 1