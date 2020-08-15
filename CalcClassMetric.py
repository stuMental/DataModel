# !/usr/bin/python
# -*- coding: utf8 -*-
import Config
import DbUtil
import Logger
import MetricUtil
from CommonUtil import CommonUtil

class CalcClassMetric(object):
    """计算教师报表相关的指标，比如教师情绪、师德修养和教学态度等。"""
    def __init__(self, configs):
        super(CalcClassMetric, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE if configs['dbname'] is None else configs['dbname'], Config.INPUT_DB_CHARSET)
        self.__utils = MetricUtil.MetricUtil()
        self.__logger = Logger.Logger(__name__)

    def calculate_class_metrics(self, start_time, end_time, estimate_day):
        '''
            以天为单位，评估课堂的教学情况。

            课堂：评估课堂的积极性、专注度和互动性
            return {
                'class_id1' => {
                    'course_id1' => {'class_positivity' => value, 'class_interactivity' => value, 'class_concentration' => value},
                    'course_id2' => {'class_positivity' => value, 'class_interactivity' => value, 'class_concentration' => value}
                    },
                'class_id1' => {
                    'course_id1' => {'class_positivity' => value, 'class_interactivity' => value, 'class_concentration' => value},
                    'course_id2' => {'class_positivity' => value, 'class_interactivity' => value, 'class_concentration' => value}
                    }
            }
        '''
        CommonUtil.verify()
        self.__logger.info("==== Try to compute class metrics ====")
        student_emotions = self.get_student_emotion(estimate_day)
        student_mentals = self.get_student_mental_stat(estimate_day)
        student_studies = self.get_student_study_stat(estimate_day)
        teacher_emotions = self.get_teacher_emotion(estimate_day)
        teacher_attitudes = self.get_teacher_attitude(estimate_day)

        teacher_body_stat_count = self.count_teacher_body_stat(start_time, end_time)
        student_body_stat_count = self.count_student_body_stat()(start_time, end_time)
        student_face_pose_count = self.count_sutdent_face_pose(start_time, end_time)

        self.__logger.info("Begin to compute class high-level metrics")
        metrics = {}

        self.__logger.info("Begin to compute class_positivity metric")
        for class_id, rows in student_emotions.items():
            for course, records in rows.items():
                if class_id in teacher_emotions and course in teacher_emotions[class_id] \
                    and class_id in student_body_stat_count and course in student_body_stat_count[class_id] \
                    and class_id in teacher_body_stat_count and course in teacher_body_stat_count[class_id]:
                    if class_id not in metrics:
                        metrics[class_id] = {}

                    if course not in metrics[class_id]:
                        metrics[class_id][course] = {}

                    metrics[class_id][course]['class_positivity'] = self.estimate_class_positivity(teacher_emotions[class_id][course], teacher_body_stat_count[class_id][course], student_emotions[class_id][course], student_body_stat_count[class_id][course])

        self.__logger.info("Begin to compute class_concentration metric")
        for class_id, values in metrics.items():
            for course, records in values.items():
                if class_id in student_mentals and course in student_mentals[class_id] \
                    and class_id in student_studies and course in student_studies[class_id] \
                    and class_id in student_face_pose_count and course in student_face_pose_count[class_id] \
                    and class_id in student_body_stat_count and course in student_body_stat_count[class_id] \
                    and class_id in teacher_attitudes and course in teacher_attitudes[class_id]:

                    metrics[class_id][course]['class_concentration'] = self.estimate_class_concentration(student_mentals[class_id][course], student_studies[class_id][course], student_face_pose_count[class_id][course], student_body_stat_count[class_id][course], teacher_attitudes[class_id][course])

        self.__logger.info("Begin to compute class_interactivity metric")
        for class_id, values in metrics.items():
            for course, records in values.items():
                if class_id in student_face_pose_count and course in student_face_pose_count[class_id] \
                    and class_id in student_body_stat_count and course in student_body_stat_count[class_id] \
                    and class_id in teacher_body_stat_count and course in teacher_body_stat_count[class_id]:

                    metrics[class_id][course]['class_interactivity'] = self.estimate_class_interactivity(student_face_pose_count[class_id][course], student_body_stat_count[class_id][course], teacher_body_stat_count[class_id][course])

        self.__logger.debug(str(metrics))
        self.__logger.info("End to compute teacher metrics")

        return metrics

    def get_teacher_emotion(self, estimate_day):
        """"""
        sql = '''
            SELECT
                class_id, course_name, teacher_emotion
            FROM {0}
            WHERE dt = '{1}';
        '''.format(Config.OUTPUT_UI_TEA_COURSE_TABLE, estimate_day)

        res = {}
        for row in self.__db.select(sql):
            if row[0] not in res:
                res[row[0]] ={}

            course_name = row[1].encode('utf-8')
            if course_name not in res[row[0]]:
                res[row[0]][course_name] = None

            res[row[0]][course_name] = row[2]

        self.__logger.debug('Teacher emotion: ' + str(res))

        return res

    def get_teacher_attitude(self, estimate_day):
        """"""
        sql = '''
            SELECT
                class_id, course_name, teacher_attitude
            FROM {0}
            WHERE dt = '{1}';
        '''.format(Config.OUTPUT_UI_TEA_COURSE_TABLE, estimate_day)

        res = {}
        for row in self.__db.select(sql):
            if row[0] not in res:
                res[row[0]] ={}

            course_name = row[1].encode('utf-8')
            if course_name not in res[row[0]]:
                res[row[0]][course_name] = None

            res[row[0]][course_name] = row[2]

        self.__logger.debug('Teacher attitude: ' + str(res))

        return res

    def get_student_emotion(self, estimate_day):
        """"""
        sql = '''
            SELECT
                class_id, course_name, student_emotion
            FROM {0}
            WHERE dt = '{1}';
        '''.format(Config.OUTPUT_UI_COURSE_TABLE, estimate_day)

        res = {}
        for row in self.__db.select(sql):
            if row[0] not in res:
                res[row[0]] ={}

            course_name = row[1].encode('utf-8')
            if row[0] not in res[row[0]]:
                res[row[0]][course_name] = []

            res[row[0]][course_name].append(row[2])

        self.__logger.debug('Student emotion: ' + str(res))

        return res

    def get_student_mental_stat(self, estimate_day):
        """"""
        sql = '''
            SELECT
                class_id, course_name, student_mental_stat
            FROM {0}
            WHERE dt = '{1}';
        '''.format(Config.OUTPUT_UI_COURSE_TABLE, estimate_day)

        res = {}
        for row in self.__db.select(sql):
            if row[0] not in res:
                res[row[0]] ={}

            course_name = row[1].encode('utf-8')
            if course_name not in res[row[0]]:
                res[row[0]][course_name] = []

            res[row[0]][course_name].append(row[2])

        self.__logger.debug('Student mental: ' + str(res))

        return res

    def get_student_study_stat(self, estimate_day):
        """"""
        sql = '''
            SELECT
                class_id, course_name, student_study_stat
            FROM {0}
            WHERE dt = '{1}';
        '''.format(Config.OUTPUT_UI_COURSE_TABLE, estimate_day)

        res = {}
        for row in self.__db.select(sql):
            if row[0] not in res:
                res[row[0]] ={}

            course_name = row[1].encode('utf-8')
            if course_name not in res[row[0]]:
                res[row[0]][course_name] = []

            res[row[0]][course_name].append(row[2])

        self.__logger.debug('Student study: ' + str(res))

        return res

    def count_teacher_body_stat(self, start_time, end_time):
        """"""
        '''统计教师身体姿态的情况'''
        sql = '''
            SELECT
                class_id, course_name, body_stat, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND body_stat != '-1' AND course_name != 'rest'
            GROUP BY class_id, course_name, body_stat
        '''.format(start_time, end_time, Config.INTERMEDIATE_TEACHER_TABLE_TRAIN)

        res = {}
        count = 0
        for row in self.__db.select(sql):
            count += 1
            key = row[0].encode('utf-8')
            if key not in res:
                res[key] = {}

            course_name = row[1].encode('utf-8')
            if course_name not in res[key]:
                res[key][course_name] = {}

            if row[2] == '0': # 正常
                res[key][course_name]['body_stat_normal'] = row[3]
            elif row[2] == '1': # 站着讲课
                res[key][course_name]['body_stat_stand'] = row[3]
            elif row[2] == '2': # 面向学生
                res[key][course_name]['body_stat_facing_student'] = row[3]
            elif row[2] == '3': # 坐着讲课
                res[key][course_name]['body_stat_sit'] = row[3]
            elif row[2] == '4': # 背对学生
                res[key][course_name]['body_stat_back_student'] = row[3]
            else:
                continue
        self.__logger.debug("teacher count_body_stat: " + str(res))

        self.__logger.info("Finished to count teacher body_stat, and get total {0} records.".format(count))
        return res

    def count_student_body_stat(self, start_time, end_time):
        ''''''
        self.__logger.info("Begin to count by body_stat")
        sql = '''
            SELECT
                class_id, course_name, body_stat, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND body_stat != '-1' AND course_name != 'rest'
            GROUP BY class_id, course_name, body_stat
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN)

        res = {} # {'course_name' => {'face_id1' => values, 'face_id2' => values}}
        count = 0
        for row in self.__db.select(sql):
            count += 1
            key = row[0].encode('utf-8')
            if key not in res:
                res[key] = {}
            subKey = row[1].encode('utf-8')
            if subKey not in res[key]:
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
        self.__logger.info("Finished to count face_pose, and get total {0} records.".format(count))

        return res

    def count_sutdent_face_pose(self, start_time, end_time):
        ''' Compute the count of face pose based on face_id level '''
        # TODO 考虑如何利用face_pose_stat
        self.__logger.info("Begin to count by face_pose")
        sql = '''
            SELECT
                class_id, course_name, face_pose, COUNT(*) AS total
            FROM {2}
            WHERE pose_stat_time >= {0} AND pose_stat_time < {1} AND face_pose != '-1' AND  course_name != 'rest'
            GROUP BY class_id, course_name, face_pose
        '''.format(start_time, end_time, Config.INTERMEDIATE_TABLE_TRAIN)

        res = {}
        count = 0
        for row in self.__db.select(sql):
            count += 1
            key = row[0].encode('utf-8')
            if key not in res:
                res[key] = {}

            subKey = row[1].encode('utf-8')
            if subKey not in res[key]:
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

    def estimate_class_positivity(self, teacher_emotion, teacher_body_stats, student_emotions, student_body_stats):
        emotion_total = float(sum([v for k, v in student_emotions.items()]))
        tea_body_total = float(sum([v for k, v in teacher_body_stats.items()]))
        stu_body_total = float(sum([v for k, v in student_body_stats.items()]))

        if teacher_emotion in Config.CLASS_POSITIVITY_BAD_THRESHOLD['TEACHER_EMOTION'] and student_emotions['2'] / emotion_total > Config.CLASS_POSITIVITY_BAD_THRESHOLD['STUDENT_EMOTION_LOW'] and (student_body_stats['1'] + student_body_stats['2']) / stu_body_total < Config.CLASS_POSITIVITY_BAD_THRESHOLD['STUDENT_HAND_STAND'] and (teacher_body_stats['1'] + teacher_body_stats['2']) / tea_body_total < Config.CLASS_POSITIVITY_BAD_THRESHOLD['FACING_STUDENT_TIME']:  # 不佳
            return 2
        elif teacher_emotion in Config.CLASS_POSITIVITY_GREAT_THRESHOLD['TEACHER_EMOTION'] and student_emotions['0'] / emotion_total > Config.CLASS_POSITIVITY_GREAT_THRESHOLD['STUDENT_EMOTION_HAPPY'] and (student_body_stats['1'] + student_body_stats['2']) / stu_body_total > Config.CLASS_POSITIVITY_GREAT_THRESHOLD['STUDENT_HAND_STAND'] and (teacher_body_stats['1'] + teacher_body_stats['2']) / tea_body_total > Config.CLASS_POSITIVITY_GREAT_THRESHOLD['FACING_STUDENT_TIME']:  # 积极
            return 0
        else:  # 正常
            return 1

    def estimate_class_concentration(self, student_mentals, student_studies, student_poses, student_body_stats, teacher_attitude):
        mental_total = float(sum([v for k, v in student_mentals.items()]))
        study_total = float(sum([v for k, v in student_studies.items()]))
        stu_pose_total = float(sum([v for k, v in student_poses.items()]))
        stu_body_total = float(sum([v for k, v in student_body_stats.items()]))

        if teacher_attitude in Config.CLASS_CONCENTRATION_LOW_THRESHOLD['TEACHER_ATTRITUDE'] and student_mentals['2'] / mental_total > Config.CLASS_CONCENTRATION_LOW_THRESHOLD['STUDENT_METAL'] and student_studies['3'] / study_total > Config.CLASS_CONCENTRATION_LOW_THRESHOLD['STUDENT_STUDY'] and (student_poses['1'] + student_poses['2']) / stu_pose_total > Config.CLASS_CONCENTRATION_LOW_THRESHOLD['STUDENT_HEAD_POSE'] and (student_body_stats['4'] + student_body_stats['4']) / stu_body_total > Config.CLASS_CONCENTRATION_LOW_THRESHOLD['STUDENT_TZTK_PZTK']:  # 低
            return 2
        if teacher_attitude in Config.CLASS_CONCENTRATION_LOW_THRESHOLD['TEACHER_ATTRITUDE'] and student_mentals['0'] / mental_total > Config.CLASS_CONCENTRATION_LOW_THRESHOLD['STUDENT_METAL'] and (student_studies['0'] + student_studies['1']) / study_total > Config.CLASS_CONCENTRATION_LOW_THRESHOLD['STUDENT_STUDY'] and student_poses['0'] / stu_pose_total > Config.CLASS_CONCENTRATION_LOW_THRESHOLD['STUDENT_HEAD_POSE'] and (student_body_stats['1'] + student_body_stats['2']) / stu_body_total > Config.CLASS_CONCENTRATION_LOW_THRESHOLD['STUDENT_HAND_STAND']:  # 高
            return 0
        else:  # 低
            return 1

    def estimate_class_interactivity(self, student_poses, student_body_stats, teacher_body_stats):
        stu_pose_total = float(sum([v for k, v in student_poses.items()]))
        stu_body_total = float(sum([v for k, v in student_body_stats.items()]))
        tea_body_total = float(sum([v for k, v in teacher_body_stats.items()]))

        if teacher_body_stats['2'] / tea_body_total < Config.CLASS_INTERACTIVITY_BAD_THRESHOLD['FACING_STUDENT_TIME'] and student_poses['0'] / stu_pose_total < Config.CLASS_INTERACTIVITY_BAD_THRESHOLD['STUDENT_HEAD_POSE'] and student_poses['1'] / stu_pose_total < Config.CLASS_INTERACTIVITY_BAD_THRESHOLD['HEAD_POSE_AROUND']:  # 不佳
            return 3
        if teacher_body_stats['2'] / tea_body_total > Config.CLASS_INTERACTIVITY_GREAT_THRESHOLD['FACING_STUDENT_TIME'] and student_poses['1'] / stu_pose_total > Config.CLASS_INTERACTIVITY_GREAT_THRESHOLD['HEAD_POSE_AROUND'] and (student_body_stats['1'] + student_body_stats['2']) / stu_body_total > Config.CLASS_INTERACTIVITY_GREAT_THRESHOLD['STUDENT_HAND_STAND']:  # 非常好
            return 0
        if teacher_body_stats['2'] / tea_body_total > Config.CLASS_INTERACTIVITY_GOOD_THRESHOLD['FACING_STUDENT_TIME'] and student_poses['1'] / stu_pose_total > Config.CLASS_INTERACTIVITY_GOOD_THRESHOLD['HEAD_POSE_AROUND'] and (student_body_stats['1'] + student_body_stats['2']) / stu_body_total > Config.CLASS_INTERACTIVITY_GOOD_THRESHOLD['STUDENT_HAND_STAND']:  # 良好
            return 1
        else:  # 正常
            return 2

