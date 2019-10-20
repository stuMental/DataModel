# !/usr/bin/python
# -*- coding: utf8 -*-
import Config
import DbUtil
import Logger
import MetricUtil

class CalcTeacherMetric(object):
	"""计算教师报表相关的指标，比如教师情绪、师德修养和教学态度等。"""
	def __init__(self, configs):
		super(CalcTeacherMetric, self).__init__()
		self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__utils = MetricUtil.MetricUtil()
        self.__logger = Logger.Logger(__name__)

    def calculate_teacher_metrics(self, start_time, end_time):
    	'''
    		以天为单位，计算教师在情绪，修养和态度等方面的表现请款.
    		return {
				'teacher_id1' => {'teacher_emotion' => value, 'teacher_ethics' => value, 'teacher_attitude' => value},
                'teacher_id2' => {'teacher_emotion' => value, 'teacher_ethics' => value, 'teacher_attitude' => value}
    		}
    	'''

        self.__logger.info("==== Try to compute teacher metrics ====")
        emotion_count = self.count_emotin(start_time, end_time)
        body_stat_count = self.count_body_stat(start_time, end_time)
        activity_count = self.count_activity(start_time, end_time)
        clothes_count = self.count_clothes(start_time, end_time)
        ontime_count = self.count_ontime(start_time, end_time)
        
        self.__logger.info("Begin to compute teacher high-level metrics")
        metrics = {}

        self.__logger.info("Begin to compute teacher_emotion metric")
        emotion_thresholds = self.__utils.calculate_teacher_emotion_threshold(emotion_count)
        for face_id, values in emotion_count.items():
            if not metrics.has_key(face_id):
                metrics[face_id] = {}
            metrics[face_id]['teacher_emotion'] = self.__utils.estimate_teacher_emotion(values, emotion_thresholds)

        self.__logger.info("Begin to compute teacher_ethics metric")
        for face_id, values in metrics.items():
            metrics[face_id]['teacher_ethics'] = self.estimate_teacher_ethics(values['teacher_emotion'], clothes_count)

        self.__logger.info("Begin to compute teacher_attitude metric")
        for face_id, values in metrics.items():
            metrics[face_id]['teacher_attitude'] = self.__utils.estimate_teacher_attitude(values['teacher_emotion'], values['teacher_ethics'], ontime_count, body_stat_count, activity_count)

        self.__logger.debug(str(metrics))
        self.__logger.info("End to compute teacher metrics")

        return metrics

    def count_emotin(self, start_time, end_time):
        '''统计教师表情的情况'''
        sql = '''
            SELECT
                face_id, face_emotion, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND face_emotion != '-1' AND face_id != 'unknown'
            GROUP BY face_id, face_emotion
        '''.format(start_time, end_time, Config.INTERMEDIATE_TEACHER_TABLE_TRAIN)

        res = {}
        count = 0
        for row in self.__db.select(sql):
            count += 1
            key = row[0].encode('utf-8')
            if not res.has_key(key):
                res[key] = {}

            if row[1] == '0': # 开心
                res[key]['emotion_happy'] = row[2]
            elif row[1] == '1': # 正常
                res[key]['emotion_normal'] = row[2]
            elif row[1] == '2': # 低落
                res[key]['emotion_low'] = row[2]
            elif row[1] == '3': # 愤怒
                res[key]['emotion_angry'] = row[2]
            else:
                continue
        self.__logger.debug("teacher count_face_emotion: " + str(res))

        self.__logger.info("Finished to count teacher face_emotion, and get total {0} records.".format(count))
        return res

    def count_body_stat(self, start_time, end_time):
        '''统计教师身体姿态的情况'''
        sql = '''
            SELECT
                face_id, body_stat, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND body_stat != '-1' AND face_id != 'unknown'
            GROUP BY face_id, body_stat
        '''.format(start_time, end_time, Config.INTERMEDIATE_TEACHER_TABLE_TRAIN)

        res = {}
        count = 0
        for row in self.__db.select(sql):
            count += 1
            key = row[0].encode('utf-8')
            if not res.has_key(key):
                res[key] = {}

            if row[1] == '0': # 正常
                res[key]['body_stat_normal'] = row[2]
            elif row[1] == '1': # 站着讲课
                res[key]['body_stat_stand'] = row[2]
            elif row[1] == '2': # 面向学生
                res[key]['body_stat_facing_student'] = row[2]
            elif row[1] == '3': # 坐着讲课
                res[key]['body_stat_sit'] = row[2]
            elif row[1] == '4': # 背对学生
                res[key]['body_stat_back_student'] = row[2]
            else:
                continue
        self.__logger.debug("teacher count_body_stat: " + str(res))

        self.__logger.info("Finished to count teacher body_stat, and get total {0} records.".format(count))
        return res

    def count_activity(self, start_time, end_time):
        '''统计教师活动的情况'''
        sql = '''
            SELECT
                face_id, activity_stat, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND activity_stat != '-1' AND face_id != 'unknown'
            GROUP BY face_id, activity_stat
        '''.format(start_time, end_time, Config.INTERMEDIATE_TEACHER_TABLE_TRAIN)

        res = {}
        count = 0
        for row in self.__db.select(sql):
            count += 1
            key = row[0].encode('utf-8')
            if not res.has_key(key):
                res[key] = {}

            if row[1] == '0': # 正常
                res[key]['activity_stat_normal'] = row[2]
            elif row[1] == '1': # 板书
                res[key]['activity_stat_write'] = row[2]
            elif row[1] == '2': # 演示
                res[key]['activity_stat_present'] = row[2]
            elif row[1] == '3': # 巡视
                res[key]['activity_stat_lookover'] = row[2]
            elif row[1] == '4': # 辅导学生
                res[key]['activity_stat_coach'] = row[2]
            else:
                continue
        self.__logger.debug("teacher count_activity_stat: " + str(res))

        self.__logger.info("Finished to count teacher activity_stat, and get total {0} records.".format(count))
        return res

    def count_clothes(self, start_time, end_time):
        '''统计教师衣着的情况'''
        sql = '''
            SELECT
                face_id, clothes_stat, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND clothes_stat != '-1' AND face_id != 'unknown'
            GROUP BY face_id, clothes_stat
        '''.format(start_time, end_time, Config.INTERMEDIATE_TEACHER_TABLE_TRAIN)

        res = {}
        count = 0
        for row in self.__db.select(sql):
            count += 1
            key = row[0].encode('utf-8')
            if not res.has_key(key):
                res[key] = {}

            if row[1] == '0': # 正常
                res[key]['activity_stat_normal'] = row[2]
            elif row[1] == '1': # 不正常
                res[key]['activity_stat_abnormal'] = row[2]
            else:
                continue
        self.__logger.debug("teacher count_clothes_stat: " + str(res))

        self.__logger.info("Finished to count teacher clothes_stat, and get total {0} records.".format(count))
        return res

    def count_ontime(self, start_time, end_time):
        '''统计教师是否准时上课的情况'''
        sql = '''
            SELECT
                face_id, ontime, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time < {1}
            GROUP BY face_id, ontime
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_ONTIME)

        res = {}
        count = 0
        for row in self.__db.select(sql):
            count += 1
            key = row[0].encode('utf-8')
            if not res.has_key(key):
                res[key] = {}

            if row[1] == '0': # 准时
                res[key]['ontime_normal'] = row[2]
            elif row[1] == '1': # 迟到
                res[key]['ontime_late'] = row[2]
            else:
                continue
        self.__logger.debug("teacher count_ontime: " + str(res))

        self.__logger.info("Finished to count teacher ontime, and get total {0} records.".format(count))
        return res

    def estimate_teacher_ethics(self, emotion, clothes):
        pass