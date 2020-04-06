# !/usr/bin/python
# -*- coding: utf-8 -*-

import Config
import DbUtil
import Logger
import math
from CommonUtil import CommonUtil

class AnalyzeTeachingGrade(object):
    """Analyze grade with course ans study_status for class"""
    def __init__(self, configs):
        super(AnalyzeTeachingGrade, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)
        self.__delimiter = '@'

    def Analysis(self, dt):
        ''''''
        CommonUtil.verify()
        self.__logger.info("Begin to analyze grade and study_status for class")
        dates = self.get_calc_dates(dt)
        if not dates:
            self.__logger.info("No dates that needs to be computed")
            return {}

        metrics = {}
        for dt in dates:
            class_id = self.__delimiter.join(dt[:-1])
            self.__logger.debug("class_id: {0}, Date: {1}".format(class_id, dt[3]))
            if class_id not in metrics:
                metrics[class_id] = {}
            metrics[class_id][dt[3]] = {}
            grade_levels = self.get_course_grade_level(dt)
            study_levels = self.get_course_study_status(CommonUtil.get_specific_date(dt[3], Config.ANALYSIS_LOOKBACKWINDOW) , dt)
            for course_name, score in study_levels.items():
                    if course_name not in Config.FILTER_COURSES and grade_levels.has_key(course_name):
                        metrics[class_id][dt[3]][course_name] = [grade_levels[course_name], score]

        self.__logger.debug(str(metrics))
        self.__logger.info("Finished to analyze grade and study_status")
        return metrics

    def get_calc_dates(self, dt):
        """"""
        self.__logger.info("Try to get all dates to compute grade and study_status")
        sql = '''
            SELECT
                DISTINCT college_name, grade_name, class_name, dt
            FROM {0}
            WHERE dt <= '{1}' and CONCAT(college_name, grade_name, class_name, dt) NOT IN (SELECT DISTINCT CONCAT(college_name, grade_name, class_name, dt) FROM {2})
        '''.format(Config.SCHOOL_PERFORMANCE_TABLE, dt, Config.OUTPUT_TEACHING_CLASS_GRADE_STUDY)

        res = []
        for row in self.__db.select(sql):
            res.append([row[0].encode('utf-8'), row[1].encode('utf-8'), row[2].encode('utf-8'), str(row[3])])

        self.__logger.info("Need to compute dates: {}".format(res))

        return res

    def get_course_grade_level(self, dt):
        ''' 科目平均分可以作为原点，高于平均分认为是正向的，低于平均分是负向的。
        '''
        self.__logger.info("Try to get all course_names from {0} on {1}".format(Config.SCHOOL_PERFORMANCE_TABLE, dt))
        sql = '''
            SELECT
                course_name,
                ROUND((score - 60.0) / IF(score <= 60.0, 60.0, 40.0), 2) AS grade_level
            FROM (
                SELECT
                    course_name, AVG(score) AS score
                FROM {1}
                WHERE dt = '{0}' AND college_name = '{2}' AND grade_name = '{3}' AND class_name = '{4}'
                GROUP BY course_name
            ) tmp
        '''.format(dt[3], Config.SCHOOL_PERFORMANCE_TABLE, dt[0], dt[1], dt[2])

        res = {}
        for row in self.__db.select(sql):
            course = row[0].encode('utf-8')
            if not res.has_key(course):
                res[course] = {}

            res[course] = float(row[1])

        self.__logger.debug("Get_course_grade_level: " + str(res))
        return res

    def get_course_study_status(self, start_time, dt):
        ''''''
        self.__logger.info("Try to get all study_status from {0} between {1} and {2}".format(Config.OUTPUT_UI_COURSE_TABLE, start_time, dt[3]))
        self.__logger.info("Begin to compute study level for all student, and all course")
        sql = '''
            SELECT
                course_name,
                ROUND((score - 0.6) / IF(score <= 0.6, 0.6, 0.4), 2) AS study_level
            FROM (
                SELECT
                    course_name, AVG(score) AS score
                FROM (
                    SELECT
                        dt, course_name, SUM(rate) AS score
                    FROM {2}
                    WHERE action_type = 5 and action_status != '3' AND dt >= '{0}' AND dt < '{1}' AND college_name = '{3}' AND grade_name = '{4}' AND class_name = '{5}'
                    GROUP BY dt, course_name
                ) tmp
                GROUP BY course_name
            ) t
        '''.format(start_time, dt[3], Config.OUTPUT_TEACHING_CLASS_STUDENT, dt[0], dt[1], dt[2])

        res = {}
        for row in self.__db.select(sql):
            course = row[0].encode('utf-8')
            if not res.has_key(course):
                res[course] = {}

            res[course] = float(row[1])

        self.__logger.debug("Get_course_study_status: " + str(res))
        return res


    def analyze_teaching_scores(self, dt):
        """ 计算教学效果综合得分
        """

        sql = '''
            DELETE FROM {0} WHERE dt = '{1}'
        '''.format(Config.OUTPUT_TEACHING_CLASS_SCORES, dt)
        self.__db.delete(sql)

        sql = '''
            INSERT INTO {0}
            SELECT t2.college_name, t2.grade_name, t2.class_name, NULL AS course_id, t2.course_name, t6.student_study_score, t2.student_emotion_score, t4.student_mental_score, t11.class_concentration_score, t11.class_interactivity_score, t11.class_positivity_score, NULL AS teacher_attitude_score, NULL AS teacher_emotion_score, NULL AS teacher_ethics_score, '{1}' AS dt
            FROM (
                SELECT
                    college_name, grade_name, class_name, course_name, ROUND(AVG(score), 2)AS student_emotion_score
                FROM (
                    SELECT
                        dt, college_name, grade_name, class_name, course_name, SUM(rate) AS score
                    FROM {3}
                    WHERE dt >= '{2}' AND dt <= '{1}' AND action_type = 3 AND action_status != '2'
                    GROUP BY dt, college_name, grade_name, class_name, course_name
                ) t1
                GROUP BY college_name, grade_name, class_name, course_name
            ) t2 JOIN (
                SELECT
                    college_name, grade_name, class_name, course_name, ROUND(AVG(score), 2) AS student_mental_score
                FROM (
                    SELECT
                        dt, college_name, grade_name, class_name, course_name, SUM(rate) AS score
                    FROM {3}
                    WHERE dt >= '{2}' AND dt <= '{1}' AND action_type = 4 AND action_status != '2'
                    GROUP BY dt, college_name, grade_name, class_name, course_name
                ) t3
                GROUP BY college_name, grade_name, class_name, course_name
            ) t4 ON t2.college_name = t4.college_name AND t2.grade_name = t4.grade_name AND t2.class_name = t4.class_name AND t2.course_name = t4.course_name
            JOIN (
                SELECT
                    college_name, grade_name, class_name, course_name, ROUND(AVG(score), 2) AS student_study_score
                FROM (
                    SELECT
                        dt, college_name, grade_name, class_name, course_name, SUM(rate) AS score
                    FROM {3}
                    WHERE dt >= '{2}' AND dt <= '{1}' AND action_type = 5 AND action_status != '3'
                    GROUP BY dt, college_name, grade_name, class_name, course_name
                ) t5
                GROUP BY college_name, grade_name, class_name, course_name
            ) t6 ON t2.college_name = t6.college_name AND t2.grade_name = t6.grade_name AND t2.class_name = t6.class_name AND t2.course_name = t6.course_name
            JOIN (
                SELECT
                    t7.college_name, t7.grade_name, t7.class_name, t7.course_name, ROUND(t8.total / t7.total, 2) AS class_positivity_score, ROUND(t9.total / t7.total, 2) AS class_interactivity_score, ROUND(t10.total / t7.total, 2) AS class_concentration_score
                FROM (
                    SELECT
                        college_name, grade_name, class_name, course_name, COUNT(DISTINCT dt) AS total
                    FROM {4}
                    WHERE dt >= '{2}' AND dt <= '{1}'
                    GROUP BY college_name, grade_name, class_name, course_name
                ) t7 JOIN (
                    SELECT
                        college_name, grade_name, class_name, course_name, SUM(IF(class_positivity != '1', 1, {5})) AS total
                    FROM {4}
                    WHERE class_positivity != '2' AND dt >= '{2}' AND dt <= '{1}'
                    GROUP BY college_name, grade_name, class_name, course_name
                ) t8 ON t7.college_name = t8.college_name AND t7.grade_name = t8.grade_name AND t7.class_name = t8.class_name AND t7.course_name = t8.course_name
                JOIN (
                    SELECT
                        college_name, grade_name, class_name, course_name, SUM(IF(class_interactivity != '2', 1, {5})) AS total
                    FROM {4}
                    WHERE class_interactivity != '3' AND dt >= '{2}' AND dt <= '{1}'
                    GROUP BY college_name, grade_name, class_name, course_name
                ) t9 ON t7.college_name = t9.college_name AND t7.grade_name = t9.grade_name AND t7.class_name = t9.class_name AND t7.course_name = t9.course_name
                JOIN (
                    SELECT
                        college_name, grade_name, class_name, course_name, SUM(IF(class_concentration != '1', 1, {5})) AS total
                    FROM {4}
                    WHERE class_concentration != '2' AND dt >= '{2}' AND dt <= '{1}'
                    GROUP BY college_name, grade_name, class_name, course_name
                ) t10 ON t7.college_name = t10.college_name AND t7.grade_name = t10.grade_name AND t7.class_name = t10.class_name AND t7.course_name = t10.course_name
            ) t11 ON t2.college_name = t11.college_name AND t2.grade_name = t11.grade_name AND t2.class_name = t11.class_name AND t2.course_name = t11.course_name
        '''.format(Config.OUTPUT_TEACHING_CLASS_SCORES, dt, CommonUtil.get_specific_date(dt, Config.ANALYSIS_LOOKBACKWINDOW), Config.OUTPUT_TEACHING_CLASS_STUDENT, Config.OUTPUT_TEACHING_CLASS_DAILY, Config.TEACHING_NORMAL_WEIGHT)
        self.__db.insert(sql)