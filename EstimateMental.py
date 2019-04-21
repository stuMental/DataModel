# !/usr/bin/python
# -*- coding: utf8 -*-

from CommonUtil import CommonUtil
import CalcMetric
import PostMetric
import Preprocessor
import Logger
import Config
import DbUtil
import CalcCourseMetric
import AnalyzeGrade
import datetime

class EstimateMental(object):
    """DataModel的主模块 以及是对应的入口文件"""
    def __init__(self):
        super(EstimateMental, self).__init__()
        self.__logger = Logger.Logger(__name__)
        self.__preprocessor = Preprocessor.Preprocessor()
        self.__metric = CalcMetric.CalcMetric()
        self.__poster = PostMetric.PostMetric()
        self.__course = CalcCourseMetric.CalcCourseMetric()
        self.__analyzer = AnalyzeGrade.AnalyzeGrade()
        self.__db = DbUtil.DbUtil(Config.INPUT_DB_HOST, Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__interests = {}

    def estimate(self):
        times = CommonUtil.get_range_times()
        diff_days = -1 if datetime.datetime.now().hour <= Config.DATETIME_THRESHOLD else 0
        estimate_date = CommonUtil.get_date_day(diff_days)
        self.__logger.info("Begin to analyze the student data of {0}".format(estimate_date))
        self.__logger.info("Begin to preprocess data between {0} and {1}.".format(times['start_datetime'], times['end_datetime']))
        self.__preprocessor.preprocessor(times['start_unixtime'], times['end_unixtime'], estimate_date)

        # 获得学生信息和班级信息
        students = self.get_students()
        classes = self.get_classes()

        # 先计算分科目的指标，因为兴趣需要基于这个数据计算
        self.__logger.info("Begin to compute and post daily course metrics")
        course_metrics = self.__course.calculate_course_metrics(times['start_unixtime'], times['end_unixtime'])
        self.__poster.post_course_metric(course_metrics, estimate_date, students, classes)
        self.__logger.info("Finished to compute and post daily course metrics")

        self.__logger.info("Begin to compute and post daily metrics")
        metrics = self.__metric.calculate_daily_metrics(times['start_unixtime'], times['end_unixtime'])
        metrics = self.estimate_interest(times['end_datetime'], metrics)
        self.__poster.post(metrics, estimate_date, students, classes)
        self.__logger.info("Finished to compute and post daily metrics")

        self.__logger.info("Begin to post Interest")
        self.__poster.post_interest_metric(self.__interests, estimate_date, students, classes)
        self.__logger.info("Finished to post Interest")

        # 计算成绩与学习状态之间的四象限分析指标
        self.__logger.info("Begin to analyze and post Grade and Study_Status")
        analysis_metrics = self.__analyzer.Analysis(times['start_datetime'], times['end_datetime'])
        self.__poster.post_grade_study_metric(analysis_metrics, estimate_date)
        self.__logger.info("Finished to analyze and post")

    def count_interest(self, end_date):
        ''''''
        sql = '''
            SELECT
                class_id, student_number, course_name, student_study_stat
            FROM {2}
            WHERE dt >= '{0}' AND dt < '{1}'
        '''.format(CommonUtil.get_specific_date(end_date, Config.LOOKBACKWINDOW), end_date, Config.OUTPUT_UI_COURSE_TABLE)

        res = {}
        for row in self.__db.select(sql):
            key = row[0].encode('utf-8')
            if not res.has_key(key):
                res[key] = {}

            subKey = row[1].encode('utf-8')
            if not res[key].has_key(subKey):
                res[key][subKey] = {}

            ssKey = row[2].encode('utf-8')
            if not res[key][subKey].has_key(ssKey):
                res[key][subKey][ssKey] = 0

            if row[3] == '0' or row[3] == '1': # 非常好 + 良好的总计天数
                res[key][subKey][ssKey] += 1
            else:
                continue
        self.__logger.debug(str(res))
        return res

    def estimate_interest(self, end_date, metrics):
        ''''''
        self.__logger.info("Begin to compute student_interest")
        study_states = self.count_interest(end_date)
        for class_id, values in metrics.items():
            for face_id in values:
                if study_states.has_key(class_id) and study_states[class_id].has_key(face_id):
                    for course, value in study_states[class_id][face_id].items():
                        if value >= Config.INTEREST_THRESHOLD['STUDY_STATUS_DAYS']:
                            if not metrics[class_id][face_id].has_key('student_interest'):
                                metrics[class_id][face_id]['student_interest'] = course
                            else:
                                metrics[class_id][face_id]['student_interest'] += ',' + course

                            # Keep interest in a seperated table
                            if not self.__interests.has_key(class_id):
                                self.__interests[class_id] = {}
                            if not self.__interests[class_id].has_key(face_id):
                                self.__interests[class_id][face_id] = []
                            self.__interests[class_id][face_id].append(course)

        self.__logger.debug(str(self.__interests))
        self.__logger.info("Finished to compute student_interest")
        return metrics

    def get_students(self):
        ''''''
        self.__logger.info("Get all students")
        sql = '''
            SELECT
                DISTINCT student_number, student_name
            FROM {0}
        '''.format(Config.SCHOOL_STUDENT_CLASS_TABLE)

        res = {}
        for row in self.__db.select(sql):
            key = row[0].encode('utf-8')
            if not res.has_key(key):
                res[key] = ''
            res[key] = row[1]

        self.__logger.info("Done")
        return res

    def  get_classes(self):
        ''''''
        self.__logger.info("Get all classes")
        sql = '''
            SELECT
                DISTINCT class_id, grade_name, class_name
            FROM {0}
        '''.format(Config.SCHOOL_CAMERA_CLASS_TABLE)

        res = {}
        for row in self.__db.select(sql):
            key = row[0].encode('utf-8')
            if not res.has_key(key):
                res[key] = ''
            res[key] = [row[1], row[2]]

        self.__logger.info("Done")
        return res

if __name__ == '__main__':
    doer = EstimateMental()
    doer.estimate()