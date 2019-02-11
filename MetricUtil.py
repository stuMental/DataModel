# !/usr/bin/python
# -*- coding: utf-8 -*-
import Config
import math
import Logger

class MetricUtil(object):
    """docstring for MetricUtil"""
    def __init__(self):
        super(MetricUtil, self).__init__()
        self.__logger = Logger.Logger(__name__)

    def calculate_study_threshold(self, data):
        ''''''
        res = []
        for key, value in data.items():
            if value.has_key('face_pose_normal'):
                res.append(value['face_pose_normal'])

        length = len(res)
        threshold = {}
        if length != 0:
            res.sort(reverse=True)
            self.__logger.debug(str(res))
            # 不佳
            threshold['study_bad'] = res[int(math.floor(length * Config.STUDY_THREHOLD_BAD['FACE_POSE_NORMAL']))]
            # 非常好
            threshold['study_great'] = res[int(math.floor(length * Config.STUDY_THREHOLD_GREAT['FACE_POSE_NORMAL']))]
            # 良好
            threshold['study_good'] = res[int(math.floor(length * Config.STUDY_THREHOLD_GOOD['FACE_POSE_NORMAL']))]

        return threshold

    def estimate_study_stat(self, mentals, face_poses, thresholds):
        ''''''
        self.__logger.debug("Mentals: " + str(mentals))
        self.__logger.debug("Face_pose: " + str(face_poses))
        self.__logger.debug("Thresholds: " + str(thresholds))
        if mentals.has_key('student_mental_stat') and (mentals['student_mental_stat'] == Config.STUDY_THREHOLD_BAD['MENTAL'])\
        and face_poses.has_key('face_pose_normal') and thresholds.has_key('study_bad') and (face_poses['face_pose_normal'] <= thresholds['study_bad']): # 学习状态 -- 不佳
            return 3
        elif mentals.has_key('student_mental_stat') and (mentals['student_mental_stat'] == Config.STUDY_THREHOLD_GREAT['MENTAL'])\
        and face_poses.has_key('face_pose_normal') and thresholds.has_key('study_great') and (face_poses['face_pose_normal'] >= thresholds['study_great']): # 学习状态 -- 非常好
            return 0
        elif mentals.has_key('student_mental_stat') and (mentals['student_mental_stat'] in Config.STUDY_THREHOLD_GOOD['MENTAL'])\
        and face_poses.has_key('face_pose_normal') and thresholds.has_key('study_good') and (face_poses['face_pose_normal'] >= thresholds['study_good']): # 学习状态 -- 良好
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