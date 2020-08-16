# !/usr/bin/python
# -*- coding: utf8 -*-
import Config
import json
import DbUtil
import Logger
from CommonUtil import CommonUtil

class CalcTeachingMetric(object):
    """评估教学效果，学生的情绪、精神状态和学习状态等，班级的积极性、互动性和专注度。"""
    def __init__(self, configs):
        super(CalcTeachingMetric, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE if configs['dbname'] is None else configs['dbname'], Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)
        self.__delimiter = '@'

    def calculate_teaching_metrics(self, dt):
        """
            班级+科目的形式评估教学效果
            return {
                '学院@年级@班级1' => {
                    'course_name1' => {'face_emotion' => value, 'mental' => value, 'study' => value, 'class_positivity' => value, 'class_interactivity' => value, 'class_concentration' => value},
                    'course_name2' =>  {'face_emotion' => value, 'mental' => value, 'study' => value, 'class_positivity' => value, 'class_interactivity' => value, 'class_concentration' => value}
                },
                '学院@年级@班级2' => {
                    'course_name1' =>  {'face_emotion' => value, 'mental' => value, 'study' => value, 'class_positivity' => value, 'class_interactivity' => value, 'class_concentration' => value},
                    'course_name2' =>  {'face_emotion' => value, 'mental' => value, 'study' => value, 'class_positivity' => value, 'class_interactivity' => value, 'class_concentration' => value}
                }
            }
        """

        CommonUtil.verify()
        self.__logger.info("==== Try to compute teaching metrics ====")
        actions = self.count_action(dt)
        metrics = {}
        self.__logger.info("Begin to compute face_emotion, mental, study of teaching")
        for action_key in Config.ACTION_TYPE.keys():
            if action_key in ('face_emotion', 'mental', 'study') and Config.ACTION_TYPE[action_key] in actions:
                for class_id, records in actions[Config.ACTION_TYPE[action_key]].items():
                    for course_name, values in records.items():
                        if class_id not in metrics:
                            metrics[class_id] = {}
                        if course_name not  in metrics[class_id]:
                            metrics[class_id][course_name] = {}
                        metrics[class_id][course_name][action_key] = self.teaching_normalize(values)

        self.__logger.info("Begin to compute class_positivity of teaching")
        for class_id, courses in metrics.items():
            for course_name, values in courses.items():
                if Config.ACTION_TYPE['body_stat'] in actions and class_id in actions[Config.ACTION_TYPE['body_stat']] and course_name in actions[Config.ACTION_TYPE['body_stat']][class_id]:
                    metrics[class_id][course_name]['class_positivity'] = self.estimate_class_positivity(actions[Config.ACTION_TYPE['body_stat']][class_id][course_name], metrics[class_id][course_name]['face_emotion'])
                else:
                    metrics[class_id][course_name]['class_positivity'] = 1  # 正常

        self.__logger.info("Begin to compute class_interactivity of teaching")
        for class_id, courses in metrics.items():
            for course_name, values in courses.items():
                if class_id in actions[Config.ACTION_TYPE['body_stat']] and course_name in actions[Config.ACTION_TYPE['body_stat']][class_id] \
                    and class_id in actions[Config.ACTION_TYPE['face_pose']] and course_name in actions[Config.ACTION_TYPE['face_pose']][class_id]:
                    metrics[class_id][course_name]['class_interactivity'] = self.estimate_class_interactivity(actions[Config.ACTION_TYPE['body_stat']][class_id][course_name], actions[Config.ACTION_TYPE['face_pose']][class_id][course_name], metrics[class_id][course_name]['face_emotion'])
                else:
                    metrics[class_id][course_name]['class_interactivity'] = 2  # 正常

        self.__logger.info("Begin to compute class_concentration of teaching")
        for class_id, courses in metrics.items():
            for course_name, values in courses.items():
                if class_id in actions[Config.ACTION_TYPE['body_stat']] and course_name in actions[Config.ACTION_TYPE['body_stat']][class_id] \
                    and class_id in actions[Config.ACTION_TYPE['face_pose']] and course_name in actions[Config.ACTION_TYPE['face_pose']][class_id]:
                    metrics[class_id][course_name]['class_concentration'] = self.estimate_class_concentration(actions[Config.ACTION_TYPE['body_stat']][class_id][course_name], actions[Config.ACTION_TYPE['face_pose']][class_id][course_name], metrics[class_id][course_name]['mental'], metrics[class_id][course_name]['study'])
                else:
                    metrics[class_id][course_name]['class_concentration'] = 1  # 正常
        self.__logger.debug(json.dumps(metrics))
        self.__logger.info("End to compute metrics for teaching.")

        return metrics

    def count_action(self, dt):
        """ 计算各个动作状态的数据
        """
        sql = '''
            SELECT
                action_type, CONCAT_WS('{2}', college_name, grade_name, class_name) AS class_id, course_name, action, SUM(total) AS total
            FROM {1}
            WHERE dt = '{0}'
            GROUP BY action_type, class_id, course_name, action
        '''.format(dt, Config.INTERMEDIATE_TEACHING_AGG_TABLE, self.__delimiter)

        res = {}
        for row in self.__db.select(sql):
            action_type = int(row[0])
            if action_type not in res:
                res[action_type] = {}

            class_id = row[1]
            if class_id not in res[action_type]:
                res[action_type][class_id] = {}

            course_name = row[2]
            if course_name not in res[action_type][class_id]:
                res[action_type][class_id][course_name] = {}

            action = row[3]
            res[action_type][class_id][course_name][action] = float(row[4])

        self.__logger.debug('Teaching action status: ' + json.dumps(res))
        return res

    def teaching_normalize(self, data):
        """ 将数据归一化
        """

        total = sum(data.values())
        result = {}
        for key in data.keys():
            result[key] = data[key] / total

        return result

    def estimate_class_positivity(self, body_stats, emotions):
        """ 评估班级的积极性
        """

        body_stat_total = sum(body_stats.values())
        total = 0.0
        if '1' in body_stats:
            total += body_stats['1']
        if '2' in body_stats:
            total += body_stats['2']

        if '2' in emotions and emotions['2'] >= Config.TEACHING_POSITIVITY_BAD['emotion'] and total / body_stat_total <= Config.TEACHING_POSITIVITY_BAD['body_stat']:  # 不佳
            return 2
        elif '0' in emotions and emotions['0'] >= Config.TEACHING_POSITIVITY_GOOD['emotion'] and total / body_stat_total >= Config.TEACHING_POSITIVITY_GOOD['body_stat']:  # 积极
            return 0
        else:  # 正常
            return 1

    def estimate_class_interactivity(self, body_stats, face_poses, emotions):
        """ 评估班级的互动性
        """

        body_stat_total = sum(body_stats.values())
        face_pose_total = sum(face_poses.values())
        face_pose_normal = face_poses['0'] if '0' in face_poses else 0.0
        face_pose_around = face_poses['1'] if '1' in face_poses else 0.0
        body_stat_handup = body_stats['1'] if '1' in body_stats else 0.0
        body_stat_standup = body_stats['2'] if '2' in body_stats else 0.0

        if '1' in emotions and emotions['1'] >= Config.TEACHING_INTERACTIVITY_BAD['emotion'] and (face_pose_normal / face_pose_total >= Config.TEACHING_INTERACTIVITY_BAD['face_pose_normal'] or face_pose_around / face_pose_total <= Config.TEACHING_INTERACTIVITY_BAD['face_pose_around'] or (body_stat_handup + body_stat_standup) / body_stat_total <= Config.TEACHING_INTERACTIVITY_BAD['body_stat']):  # 不佳
            return 3
        elif '0' in emotions and emotions['0'] >= Config.TEACHING_INTERACTIVITY_GREAT['emotion'] and (face_pose_around / face_pose_total >= Config.TEACHING_INTERACTIVITY_GREAT['face_pose_around'] or (body_stat_handup + body_stat_standup) / body_stat_total >= Config.TEACHING_INTERACTIVITY_GREAT['body_stat']):  # 非常好
            return 0
        elif '0' in emotions and emotions['0'] >= Config.TEACHING_INTERACTIVITY_GOOD['emotion'] and (face_pose_around / face_pose_total >= Config.TEACHING_INTERACTIVITY_GOOD['face_pose_around'] or (body_stat_handup + body_stat_standup) / body_stat_total >= Config.TEACHING_INTERACTIVITY_GOOD['body_stat']):  # 良好
            return 1
        else:
            return 2

    def estimate_class_concentration(self, body_stats, face_poses, mentals, studies):
        """ 评估班级的专注度
        """

        body_stat_total = sum(body_stats.values())
        face_pose_total = sum(face_poses.values())
        face_pose_normal = face_poses['0'] if '0' in face_poses else 0.0
        face_pose_around = face_poses['1'] if '1' in face_poses else 0.0
        face_pose_low = face_poses['2'] if '2' in face_poses else 0.0
        body_stat_handup = body_stats['1'] if '1' in body_stats else 0.0
        body_stat_standup = body_stats['2'] if '2' in body_stats else 0.0
        body_stat_sleep = body_stats['3'] if '3' in body_stats else 0.0
        body_stat_stjtk = body_stats['4'] if '4' in body_stats else 0.0
        body_stat_pztk = body_stats['5'] if '5' in body_stats else 0.0
        study_great = studies['0'] if '0' in studies else 0.0
        study_good = studies['1'] if '1' in studies else 0.0

        if '2' in mentals and mentals['2'] >= Config.TEACHING_CONCENTRATION_LOW['mental'] and '3' in studies and studies['3'] >= Config.TEACHING_CONCENTRATION_LOW['study'] and ((face_pose_around + face_pose_low) / face_pose_total >= Config.TEACHING_CONCENTRATION_LOW['face_pose'] or (body_stat_sleep + body_stat_stjtk + body_stat_pztk) / body_stat_total >= Config.TEACHING_CONCENTRATION_LOW['body_stat']):  # 低
            return 2
        elif '0' in mentals and mentals['0'] >= Config.TEACHING_CONCENTRATION_HIGH['mental'] and (study_great + study_good) >= Config.TEACHING_CONCENTRATION_HIGH['study'] and (face_pose_normal / face_pose_total >= Config.TEACHING_CONCENTRATION_HIGH['face_pose'] or (body_stat_handup + body_stat_standup) / body_stat_total >= Config.TEACHING_CONCENTRATION_HIGH['body_stat']):  # 高
            return 0
        else:  # 正常
            return 1