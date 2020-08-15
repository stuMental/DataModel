# !/usr/bin/python
# -*- coding: utf8 -*-
import Config
import json
import DbUtil
import Logger
from CommonUtil import CommonUtil

class CalcTeacherMetric(object):
    """评估教师的教学状态，包括S-T分析、教学情绪 """
    def __init__(self, configs):
        super(CalcTeacherMetric, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE if configs['dbname'] is None else configs['dbname'], Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)
        self.__delimiter = '@'

    def calculate_teacher_metrics(self, dt):
        """
            emotios
            return {
                '教师ID@教师名字1' => {
                    '学院@年级@班级1' => {
                        'course_name1' => {'happy' => value, 'normal' => value, 'angry' => value},
                        'course_name2' =>  {'happy' => value, 'normal' => value, 'angry' => value}
                    }
                }
            }

            behaviors
            return {
                '教师ID@教师名字1' => {
                    '学院@年级@班级1' => {
                        'course_name1' => {
                            'scores': (Rt_value, Ch_value),
                            'behaviors': [(unix_time1, action1), (unix_time2, action2), (unix_time3, action3)]
                        }
                    }
                }
            }

            scores
            return {
                '教师ID@教师名字1' => {
                    '学院@年级@班级1' => {
                        'course_name1' => {'score' => value, 'emotion' => value, 'behavior' => value, 'ontime' => value},
                        'course_name2' =>  {'score' => value, 'emotion' => value, 'behavior' => value, 'ontime' => value}
                    }
                }
            }
        """

        CommonUtil.verify()
        self.__logger.info("==== Try to compute teacher metrics ====")
        self.__logger.info("==== Begin to compute emotion ====")
        emotions = self.count_emotions(dt)
        self.__logger.info("==== End to compute emotion ====")

        self.__logger.info("==== Begin to compute S-T analysis ====")
        actions = self.count_behaviors(dt)
        behaviors = self.compute_teaching_behaviors(actions)
        self.__logger.info("==== End to compute S-T analysis ====")

        self.__logger.info("==== Begin to estimate teaching score ====")
        ontimes = self.count_ontimes(dt)
        scores = self.compute_teaching_score(emotions, behaviors, ontimes)
        self.__logger.info("==== End to estimate teaching score ====")

        return emotions, behaviors, scores

    def count_emotions(self, dt):
        """ 统计教师情绪数据
        """
        sql = '''
            SELECT
                CONCAT_WS('{2}', teacher_id, teacher_name) AS teacher, CONCAT_WS('{2}', college_name, grade_name, class_name) AS class_id, CONCAT_WS('{2}', course_id, course_name) AS course, face_emotion, total
            FROM {0}
            WHERE dt = '{1}'
            GROUP BY teacher, class_id, course, face_emotion
        '''.format(Config.INTERMEDIATE_TEACHER_EMOTION_TABLE, dt, self.__delimiter)

        res = {}
        for row in self.__db.select(sql):
            teacher = row[0].encode('utf-8')
            if teacher not in res:
                res[teacher] = {}

            class_id = row[1].encode('utf-8')
            if class_id not in res[teacher]:
                res[teacher][class_id] = {}

            course = row[2].encode('utf-8')
            if course not in res[teacher][class_id]:
                res[teacher][class_id][course] = {}

            emotion_id = row[3].encode('utf-8')
            total = int(row[4])
            if '0' == emotion_id:  # happy
                res[teacher][class_id][course]['happy'] = total
            elif '1' == emotion_id:  # normal
                res[teacher][class_id][course]['normal'] = total
            elif '2' == emotion_id:  # angry
                res[teacher][class_id][course]['angry'] = total
            else:
                self.__logger.warning('表情状态错误，仅限于(0,1,2)，但实际是{0}'.format(emotion_id))

        self.__logger.debug(str(res))
        return res

    def count_behaviors(self, dt):
        """ 统计学生、教师行为数据
            行为类别 0: 教师 1: 学生
        """
        sql = '''
            SELECT
                teacher, class_id, course, pose_stat_time, group_concat(behavior separator '{2}') AS behaviors
            FROM (
                SELECT
                    CONCAT_WS('{2}', teacher_id, teacher_name) AS teacher, CONCAT_WS('{2}', college_name, grade_name, class_name) AS class_id, CONCAT_WS('{2}', course_id, course_name) AS course, pose_stat_time, CONCAT_WS('-', '1', behavior) AS behavior
                FROM {0}
                WHERE dt = '{3}'
                UNION
                SELECT
                    CONCAT_WS('{2}', teacher_id, teacher_name) AS teacher, CONCAT_WS('{2}', college_name, grade_name, class_name) AS class_id, CONCAT_WS('{2}', course_id, course_name) AS course, pose_stat_time, CONCAT_WS('-', '0', behavior) AS behavior
                FROM {1}
                WHERE dt = '{3}'
            ) t1
            GROUP BY teacher, class_id, course, pose_stat_time
            ORDER BY pose_stat_time ASC
        '''.format(Config.INTERMEDIATE_TEACHER_STUDENT_BEHAVIOR_TABLE, Config.INTERMEDIATE_TEACHER_BEHAVIOR_TABLE, self.__delimiter, dt)

        res = {}
        for row in self.__db.select(sql):
            teacher = row[0].encode('utf-8')
            if teacher not in res:
                res[teacher] = {}

            class_id = row[1].encode('utf-8')
            if class_id not in res[teacher]:
                res[teacher][class_id] = {}

            course = row[2].encode('utf-8')
            if course not in res[teacher][class_id]:
                res[teacher][class_id][course] = []

            unix_time = int(row[3])
            behaviors = row[4].encode('utf-8')
            res[teacher][class_id][course].append([unix_time, behaviors])

        self.__logger.debug(str(res))
        return res

    def compute_teaching_behaviors(self, behaviors):
        """ 处理教师与学生的行为序列
        """
        result = {}
        for teacher in behaviors.keys():
            if teacher not in result:
                result[teacher] = {}
            for class_id in behaviors[teacher].keys():
                if class_id not in result[teacher]:
                    result[teacher][class_id] = {}
                for course, actions in behaviors[teacher][class_id].items():
                    if course not in result[teacher][class_id]:
                        result[teacher][class_id][course] = {'scores': None, 'behaviors': []}

                    is_speak = False
                    for row in actions:  # row = (unix_time, behaviors)
                        ans = None
                        arr = row[1].split(self.__delimiter)
                        if 1 == len(arr):
                            ans = row
                        elif 2 == len(arr):  # 同一个时刻有两个行为，第一个是学生，第二个是教师
                            if Config.STUDENT_BEHAVIORS[3] in arr[0]:  # 学生行为：其他，直接采纳教师行为
                                ans = [row[0], arr[1]]
                            elif Config.TEACHER_BEHAVIORS[3] in arr[1]:  # 教师行为：其他，采纳学生行为
                                ans = [row[0], arr[0]]
                            elif Config.STUDENT_BEHAVIORS[0] in arr[0]:  # 学生行为：发言，直接采纳学生行为
                                ans = [row[0], arr[0]]
                            else:  # 兜底措施，直接采纳教师行为
                                ans = [row[0], arr[1]]
                        else:
                            self.__logger.warning('同一时刻的行为动作最多只有2个，目前是{0}'.format(len(arr)))

                        result[teacher][class_id][course]['behaviors'].append(ans)
                        if Config.STUDENT_BEHAVIORS[0] in ans[1] and not is_speak:
                            if len(result[teacher][class_id][course]['behaviors']) >= 2:
                                result[teacher][class_id][course]['behaviors'][-2][1] = '0-问答'  # 将 [发言] 前的行为修改为 [问答]
                            is_speak = True

                        if Config.STUDENT_BEHAVIORS[0] not in ans[1] and is_speak:
                            result[teacher][class_id][course]['behaviors'][-1][1] = '0-问答'  # 将 [发言] 后的行为修改为 [问答]
                            is_speak = False

        # 计算S-T分析中Rt和Ch的得分
        for teacher in result.keys():
            for class_id in result[teacher].keys():
                for course, actions in result[teacher][class_id].items():
                    prev_type = '0' if '0' in actions['behaviors'][0][1] else '1'
                    teacher_cnt = 1 if prev_type == '0' else 0
                    exchange_cnt = 0
                    for row in actions['behaviors'][1:]:
                        if '0' in row[1]:
                            teacher_cnt += 1
                        if prev_type not in row[1]:
                            exchange_cnt += 1
                            prev_type = '0' if '0' in row[1] else '1'

                    total = float(len(actions['behaviors']))
                    result[teacher][class_id][course]['scores'] = (teacher_cnt / total, exchange_cnt / total)  # Rt, Ch得分

        self.__logger.debug(str(result))
        return result

    def count_ontimes(self, dt):
        """ 获取教师上课是否守时情况
        """
        sql = '''
            SELECT
                CONCAT_WS('{2}', teacher_id, teacher_name) AS teacher, CONCAT_WS('{2}', college_name, grade_name, class_name) AS class_id, CONCAT_WS('{2}', course_id, course_name) AS course, ontime
            FROM {0}
            WHERE dt = '{1}'
        '''.format(Config.INTERMEDIATE_TEACHER_ONTIME_TABLE, dt, self.__delimiter)

        res = {}
        for row in self.__db.select(sql):
            teacher = row[0].encode('utf-8')
            if teacher not in res:
                res[teacher] = {}

            class_id = row[1].encode('utf-8')
            if class_id not in res[teacher]:
                res[teacher][class_id] = {}

            course = row[2].encode('utf-8')
            if course not in res[teacher][class_id]:
                res[teacher][class_id][course] = []

            ontime = int(row[3])
            res[teacher][class_id][course].append(ontime)

        self.__logger.debug(str(res))
        return res

    def compute_teaching_score(self, emotions, behaviors, ontimes):
        """ 根据教师情绪、动作和是否准时衡量教师的教学状态。
        """
        result = {}
        for teacher in emotions.keys():
            if teacher not in result:
                result[teacher] = {}
            for class_id in emotions[teacher].keys():
                if class_id not in result[teacher]:
                    result[teacher][class_id] = {}
                for course, rows in emotions[teacher][class_id].items():
                    if course not in result[teacher][class_id]:
                         result[teacher][class_id][course] = {}

                    result[teacher][class_id][course]['emotion'] = self.__compute_emotion_score(rows)
                    if teacher in ontimes and class_id in ontimes[teacher] and course in ontimes[teacher][class_id]:
                        result[teacher][class_id][course]['ontime'] = self.__compute_ontime_score(ontimes[teacher][class_id][course])
                    else:
                        result[teacher][class_id][course]['ontime'] = Config.TEACHER_ESTIMATE_DEFAULT

                    if teacher in behaviors and class_id in behaviors[teacher] and course in behaviors[teacher][class_id]:
                        result[teacher][class_id][course]['behavior'] = self.__compute_behavior_score(behaviors[teacher][class_id][course]['behaviors'])
                    else:
                        result[teacher][class_id][course]['behavior'] = Config.TEACHER_ESTIMATE_DEFAULT

                    result[teacher][class_id][course]['score'] = self.__compute_final_score(value = CommonUtil.get_score_by_triangle([result[teacher][class_id][course]['emotion'], result[teacher][class_id][course]['ontime'], result[teacher][class_id][course]['behavior']]))

        return result

    def __compute_emotion_score(self, rows):
        """ 计算教学情绪得分
        """

        happy_cnt = self.__get_value('happy', rows)
        normal_cnt = self.__get_value('normal', rows)
        angry_cnt = self.__get_value('angry', rows)

        emotion_total = float(happy_cnt + normal_cnt + angry_cnt)
        normal_cnt = normal_cnt if happy_cnt / emotion_total >= Config.TEACHER_HAPPY_THRESHOLD else normal_cnt * Config.TEACHER_NORMAL_WEIGHT

        return (happy_cnt + normal_cnt) / emotion_total

    def __compute_ontime_score(self, rows):
        """ 计算教学是否准时的得分
        """

        total = float(len(rows))  # 总得课堂数
        ontime_cnt = sum(rows)  # 对1的所有元素求和。即教师准时到的课堂数
        return ontime_cnt / total

    def __compute_behavior_score(self, rows):
        """ 计算教学行为的得分
        """

        behaviors = set([row[1] for row in rows if '0' in row[1]])  # 提取教师的行为
        total = float(len(behaviors))
        return total / len(Config.TEACHER_BEHAVIORS)

    def __compute_final_score(self, value):
        """ 计算综合得分
        """

        return CommonUtil.sigmoid(x=value, alpha=3.0)  # 当分布为[0.6, 0.6, 0.6]，score的值应该是0.6。因此计算得到alpha的值应该为3。

    def __get_value(self, key, arrs):
        """ 获取非None值
        """

        if key in arrs and arrs[key] is not None:
            return arrs[key]

        return 0
