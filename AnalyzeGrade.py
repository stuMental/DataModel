# !/usr/bin/python
# -*- coding: utf-8 -*-

import Config
import DbUtil
import Logger
import math
from CommonUtil import CommonUtil

class AnalyzeGrade(object):
    """Analyze grade with course ans study_status"""
    def __init__(self, configs):
        super(AnalyzeGrade, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)
        self.__delimiter = '@'

    def Analysis(self, dt):
        ''''''
        self.__logger.info("Begin to analyze grade and study_status")
        dates = self.get_calc_dates(dt)
        if not dates:
            self.__logger.info("No dates that needs to be computed")
            return {}

        metrics = {}
        for dt in dates:
            class_id = ''.join(dt[:-1])
            self.__logger.debug("class_id: {}".format(class_id))
            if class_id not in metrics:
                metrics[class_id] = {}
            metrics[class_id][dt[3]] = {}
            grade_levels = self.get_course_grade_level(dt)
            study_levels = self.get_course_study_status(CommonUtil.get_specific_date(dt[3], Config.ANALYSIS_LOOKBACKWINDOW) , dt)

            for stu, courses in study_levels.items():
                for course_name, value in courses.items():
                    if course_name not in Config.FILTER_COURSES and grade_levels.has_key(stu) and grade_levels[stu].has_key(course_name):
                        if not metrics[class_id][dt[3]].has_key(stu):
                            metrics[class_id][dt[3]][stu] = []

                        metrics[class_id][dt[3]][stu].append([course_name, grade_levels[stu][course_name], value])

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
        '''.format(Config.SCHOOL_PERFORMANCE_TABLE, dt, Config.OUTPUT_UI_GRADE_STUDY_TABLE)

        res = []
        for row in self.__db.select(sql):
            res.append([row[0].encode('utf-8'), row[1].encode('utf-8'), row[2].encode('utf-8'), str(row[3])])

        self.__logger.info("Need to compute dates: {}".format(res))

        return res

    def get_course_grade_level(self, dt):
        ''''''
        self.__logger.info("Try to get all course_names from {0} on {1}".format(Config.SCHOOL_PERFORMANCE_TABLE, dt))
        sql = '''
            SELECT
               t0.student_number, t0.course_name, ROUND(1.0 * (t0.score - t3.avg_score) / (IF(t0.score <= t3.avg_score, t3.avg_score, t3.high_score)), 2) AS grade_level
            FROM
            (
                SELECT
                    college_name, grade_name, class_name, student_number, course_name, score
                FROM {1}
                WHERE dt = '{0}' AND college_name = '{2}' AND grade_name = '{3}' AND class_name = '{4}'
            ) t0 JOIN
            (
                SELECT
                    t1.college_name, t1.grade_name, t1.class_name, t1.course_name, t1.avg_score, t2.max_score, (t2.max_score - t1.avg_score) AS high_score
                FROM
                (
                    (
                        SELECT
                            college_name, grade_name, class_name, course_name, AVG(score) AS avg_score
                        FROM {1}
                        WHERE dt = '{0}' AND college_name = '{2}' AND grade_name = '{3}' AND class_name = '{4}'
                        GROUP BY college_name, grade_name, class_name, course_name
                    ) t1 JOIN
                    (
                        SELECT
                            college_name, grade_name, course_name, MAX(score) AS max_score
                        FROM {1}
                        WHERE dt = '{0}' AND college_name = '{2}' AND grade_name = '{3}'
                        GROUP BY college_name, grade_name, course_name
                    ) t2 ON t1.grade_name = t2.grade_name AND t1.course_name = t2.course_name
                )
            ) t3 ON t0.college_name = t3.college_name AND t0.grade_name = t3.grade_name AND t0.class_name = t3.class_name AND t0.course_name = t3.course_name;
        '''.format(dt[3], Config.SCHOOL_PERFORMANCE_TABLE, dt[0], dt[1], dt[2])

        res = {}
        for row in self.__db.select(sql):
            stu_id = row[0].encode('utf-8')
            if not res.has_key(stu_id):
                res[stu_id] = {}

            course_id = row[1].encode('utf-8')
            if not res[stu_id].has_key(course_id):
                res[stu_id][course_id] = 0
            res[stu_id][course_id] = row[2]

        self.__logger.debug("get_course_grade_level: " + str(res))
        self.__logger.info("Done")
        return res

    def get_course_study_status(self, start_time, dt):
        ''''''
        self.__logger.info("Try to get all study_status from {0} between {1} and {2}".format(Config.OUTPUT_UI_COURSE_TABLE, start_time, dt[3]))
        self.__logger.info("Begin to compute study level for all student, and all course")
        sql = '''
            SELECT
                t1.student_number, t1.course_name, ROUND(1.0 * (t1.num - t2.threshold) / IF(t1.num <= t2.threshold, t2.threshold, t2.total - t2.threshold), 2) AS study_level
            FROM (
                SELECT
                    college_name, grade_name, class_name, student_number, course_name, count(*) AS total, SUM(IF(student_study_stat != '3', 1, 0)) AS num
                FROM {2}
                WHERE dt >= '{0}' AND dt < '{1}' AND college_name = '{4}' AND grade_name = '{5}' AND class_name = '{6}'
                GROUP BY college_name, grade_name, class_name, student_number, course_name
            ) t1 JOIN (
                SELECT
                    college_name, grade_name, course_name, count(DISTINCT dt) AS total, GREATEST(1, floor(count(DISTINCT dt) * {3})) AS threshold
                FROM {2}
                WHERE dt >= '{0}' AND dt < '{1}' AND college_name = '{4}' AND grade_name = '{5}'
                GROUP BY college_name, grade_name, course_name
            ) t2 ON t1.course_name = t2.course_name AND t1.college_name = t2.college_name AND t1.grade_name AND t2.grade_name AND t1.total >= t2.total * {7};
        '''.format(start_time, dt[3], Config.OUTPUT_UI_COURSE_TABLE, Config.ANALYSIS_STUDY_STAT_THRESHOLD, dt[0], dt[1], dt[2], Config.ANALYSIS_STUDY_STAT_COURSE_THRESHOLD)

        res = {}
        for row in self.__db.select(sql):
            stu_id = row[0].encode('utf-8')
            if not res.has_key(stu_id):
                res[stu_id] = {}

            course_id = row[1].encode('utf-8')
            if not res[stu_id].has_key(course_id):
                res[stu_id][course_id] = 0
            res[stu_id][course_id] = row[2]

        self.__logger.debug("get_course_study_status: " + str(res))
        self.__logger.info("Done")
        return res