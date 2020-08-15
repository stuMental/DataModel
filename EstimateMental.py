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
import CalcTeacherMetric
import CalcClassMetric
import AnalyzeGrade
import AnalyzeTeachingGrade
import CalcTeachingMetric
import datetime
import math
import time


class EstimateMental(object):
    """DataModel的主模块 以及是对应的入口文件"""
    def __init__(self, configs):
        super(EstimateMental, self).__init__()
        self.__logger = Logger.Logger(__name__)
        self.__preprocessor = Preprocessor.Preprocessor(configs)
        self.__poster = PostMetric.PostMetric(configs)
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE if configs['dbname'] is None else configs['dbname'], Config.INPUT_DB_CHARSET)
        self.__date = configs['date']
        self.__teaching = True if configs['teaching'] == 1 else False  # teaching=1 表示评估课堂的教学情况
        self.__teacher = True if configs['teaching'] == 2 else False  # teaching=2 表示基于S-T评估教师的教学情况
        if self.__teaching:  # 不识别学生情况下的教学效果评估
            self.__teaching_metric = CalcTeachingMetric.CalcTeachingMetric(configs)
            self.__teaching_analyzer = AnalyzeTeachingGrade.AnalyzeTeachingGrade(configs)
        elif self.__teacher:  # 基于S-T分析教师教学情况
            self.__teacher_metric = CalcTeacherMetric.CalcTeacherMetric(configs)
        else:  # 需要识别学生，基于学生的行为评估学生学习状态
            self.__metric = CalcMetric.CalcMetric(configs)
            self.__course = CalcCourseMetric.CalcCourseMetric(configs)
            self.__analyzer = AnalyzeGrade.AnalyzeGrade(configs)
            self.__interests = {}

    def estimate(self):
        """入口函数"""
        CommonUtil.verify()
        # 获取最新数据对应的日期
        times = CommonUtil.get_range_times()
        self.__logger.info("Current hour: {}".format(datetime.datetime.now().hour))
        diff_days = -1 if datetime.datetime.now().hour <= Config.DATETIME_THRESHOLD else 0
        estimate_date = CommonUtil.get_date_day(diff_days)

        # 是否执行指定日期的数据
        if self.__date != '-1':
            self.__logger.info("执行指定日期({})的数据".format(self.__date))
            estimate_date = self.__date
            start_date = CommonUtil.get_specific_date(self.__date)
            end_date = CommonUtil.get_specific_date(self.__date, 1)
            times['start_datetime'] = start_date.strftime("%Y-%m-%d")
            times['end_datetime'] = end_date.strftime("%Y-%m-%d")
            times['start_unixtime'] = int(time.mktime(start_date.timetuple()))
            times['end_unixtime'] = int(time.mktime(end_date.timetuple()))

        self.__logger.info("Begin to analyze the student data of {0}".format(estimate_date))
        self.__logger.info("Begin to preprocess data between {0} and {1}.".format(times['start_datetime'], times['end_datetime']))
        self.__preprocessor.preprocessor(estimate_date)

        if self.__teaching:
            self.__logger.info('在班级+科目的维度对教学效果进行评估')
            teaching_metrics = self.__teaching_metric.calculate_teaching_metrics(estimate_date)
            self.__logger.info('将分析结果存储到数据库中')
            self.__poster.post_teaching(teaching_metrics, estimate_date)
            teaching_analysis_metrics = self.__teaching_analyzer.Analysis(estimate_date)
            self.__poster.post_teaching_study_grade(teaching_analysis_metrics)
            self.__teaching_analyzer.analyze_teaching_scores(estimate_date)
        elif self.__teacher:
            self.__logger.info('基于S-T分析法评估教师的教学情况')
            emotions, behaviors, scores = self.__teacher_metric.calculate_teacher_metrics(estimate_date)
            self.__poster.post_teacher_emotions(emotions, estimate_date)
            self.__poster.post_teacher_behaviors(behaviors, estimate_date)
            self.__poster.post_teacher_scores(scores, estimate_date)
        else:
            # 评估学生
            # 获得学生基本信息
            students = self.get_students()

            # 先计算分科目的指标，因为兴趣需要基于这个数据计算
            self.__logger.info("Begin to compute and post daily course metrics")
            course_metrics = self.__course.calculate_course_metrics(times['start_unixtime'], times['end_unixtime'], estimate_date)
            students = self.__poster.post_course_metric(course_metrics, estimate_date, students)
            self.__logger.info("Finished to compute and post daily course metrics")
            self.__logger.info("Begin to compute and post daily metrics")
            metrics = self.__metric.calculate_daily_metrics(times['start_unixtime'], times['end_unixtime'], estimate_date)
            metrics = self.estimate_interest(times['end_datetime'], metrics)
            students = self.__poster.post(metrics, estimate_date, students)
            self.__logger.info("Finished to compute and post daily metrics")

            self.__logger.info("Begin to post Interest")
            students = self.__poster.post_interest_metric(self.__interests, estimate_date, students)
            self.__logger.info("Finished to post Interest")

            # 计算学生成绩与学习状态之间的四象限分析指标
            self.__logger.info("Begin to analyze and post Grade and Study_Status")
            analysis_metrics = self.__analyzer.Analysis(estimate_date)
            self.__poster.post_grade_study_metric(analysis_metrics, students)

            # 计算班级整体成绩与学习状态之间的四象限分析指标
            self.__logger.info("Begin to analyze and post Grade and Study status for class")
            class_metrics = self.__analyzer.class_analysis(estimate_date)
            self.__poster.post_teaching_study_grade(class_metrics)

        self.__logger.info("Finished to analyze and post")

    def count_interest(self, end_date):
        ''''''
        sql = '''
            SELECT
                CONCAT(college_name, grade_name, class_name) AS class_id, student_number, course_name, student_study_stat
            FROM {2}
            WHERE dt >= '{0}' AND dt < '{1}'
        '''.format(CommonUtil.get_specific_date(end_date, Config.LOOKBACKWINDOW), end_date, Config.OUTPUT_UI_COURSE_TABLE)

        res = {}
        for row in self.__db.select(sql):
            key = row[0].encode('utf-8')
            if key not in res:
                res[key] = {}

            subKey = row[1].encode('utf-8')
            if subKey not in res[key]:
                res[key][subKey] = {}

            ssKey = row[2].encode('utf-8')
            if ssKey not in res[key][subKey]:
                res[key][subKey][ssKey] = 0

            if row[3] == '0' or row[3] == '1': # 非常好 + 良好的总计天数
                res[key][subKey][ssKey] += 1
            else:
                continue
        self.__logger.debug(str(res))
        return res

    def count_course_interest_threshold(self, end_date):
        """ 不同的课程的上课天数是不一致的。
        """

        sql = '''
            SELECT
                class_id, course_name, COUNT(DISTINCT dt) as total
            FROM (
                SELECT
                    CONCAT(college_name, grade_name, class_name) AS class_id, course_name, dt
                FROM {2}
                WHERE dt >= '{0}' AND dt < '{1}'
            ) t
            GROUP BY class_id, course_name;
        '''.format(CommonUtil.get_specific_date(end_date, Config.LOOKBACKWINDOW), end_date, Config.OUTPUT_UI_COURSE_TABLE)

        res = {}
        for row in self.__db.select(sql):
            key = row[0].encode('utf-8')
            if key not in res:
                res[key] = {}

            course = row[1].encode('utf-8')
            res[key][course] = max(Config.INTEREST_THRESHOLD['STUDY_STATUS_DAYS_LOWER'], math.ceil(int(row[2]) * Config.INTEREST_THRESHOLD['STUDY_STATUS_DAYS_RATIO']))

        self.__logger.debug(str(res))
        return res

    def estimate_interest(self, end_date, metrics):
        ''''''
        self.__logger.info("Begin to compute student_interest")
        study_states = self.count_interest(end_date)
        course_thresholds = self.count_course_interest_threshold(end_date)
        for class_id, values in metrics.items():
            for face_id in values:
                if class_id in study_states and face_id in study_states[class_id]:
                    for course, value in study_states[class_id][face_id].items():
                        if class_id in course_thresholds and course in course_thresholds[class_id]:
                            if value >= course_thresholds[class_id][course]:
                                if student_interest not in metrics[class_id][face_id]:
                                    metrics[class_id][face_id]['student_interest'] = course
                                else:
                                    metrics[class_id][face_id]['student_interest'] += ',' + course

                                # Keep interest in a seperated table
                                if class_id not in self.__interests:
                                    self.__interests[class_id] = {}
                                if face_id not in self.__interests[class_id]:
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
                student_number, student_name, college_name, grade_name, class_name
            FROM {0}
            GROUP BY student_number, student_name, college_name, grade_name, class_name;
        '''.format(Config.SCHOOL_STUDENT_COURSE_TABLE)

        res = {}
        for row in self.__db.select(sql):
            key = row[0].encode('utf-8')
            if key not in res:
                res[key] = {}
            res[key]['student_name'] = row[1].encode('utf-8')
            res[key]['college_name'] = row[2].encode('utf-8')
            res[key]['grade_name'] = row[3].encode('utf-8')
            res[key]['class_name'] = row[4].encode('utf-8')

        self.__logger.debug(str(res))
        self.__logger.info("Done")
        return res