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

class EstimateMental(object):
    """docstring for EstimateMental"""
    def __init__(self):
        super(EstimateMental, self).__init__()
        self.__logger = Logger.Logger(__name__)
        self.__preprocessor = Preprocessor.Preprocessor()
        self.__metric = CalcMetric.CalcMetric()
        self.__poster = PostMetric.PostMetric()
        self.__course = CalcCourseMetric.CalcCourseMetric()
        self.__db = DbUtil.DbUtil(Config.OUTPUT_DB_HOST, Config.OUTPUT_DB_USERNAME, Config.OUTPUT_DB_PASSWORD, Config.OUTPUT_DB_DATABASE, Config.OUTPUT_DB_CHARSET)

    def estimate(self):
        times = CommonUtil.get_range_unixtime()
        self.__logger.info("Begin to preprocess data between {0} and {1}.".format(times['start_time'], times['end_time']))
        self.__preprocessor.preprocessor(times['start_time'], times['end_time'], CommonUtil.get_date_day())

        # 先计算分科目的指标，因为兴趣需要基于这个数据计算
        self.__logger.info("Begin to compute and post daily course metrics")
        course_metrics = self.__course.calculate_course_metrics(times['start_time'], times['end_time'])
        self.__logger.debug(str(course_metrics))
        self.__poster.post_course_metric(course_metrics, times['start_time'])
        self.__logger.info("Finished to compute and post daily course metrics")

        self.__logger.info("Begin to compute and post daily metrics")
        metrics = self.__metric.calculate_daily_metrics(times['start_time'], times['end_time'])
        metrics = self.estimate_interest(times['end_time'], metrics)
        self.__logger.debug(str(metrics))
        self.__poster.post(metrics, times['start_time'])
        self.__logger.info("Finished to compute and post daily metrics")

    def count_interest(self, end_time):
        ''''''
        sql = '''
            SELECT
                class_id, student_number, course_name, student_study_stat
            FROM {2}
            WHERE dt >= {0} AND dt <= {1}
        '''.format(CommonUtil.get_specific_unixtime(end_time, Config.LOOKBACKWINDOW), end_time, Config.OUTPUT_UI_COURSE_TABLE)

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

    def estimate_interest(self, end_time, metrics):
        ''''''
        self.__logger.info("Begin to compute student_interest")
        study_states = self.count_interest(end_time)
        for class_id, values in metrics.items():
            for face_id in values:
                if study_states.has_key(class_id) and study_states[class_id].has_key(face_id):
                    for course, value in study_states[class_id][face_id].items():
                        if value >= Config.INTEREST_THRESHOLD['STUDY_STATUS_DAYS']:
                            if not metrics[class_id][face_id].has_key('student_interest'):
                                metrics[class_id][face_id]['student_interest'] = course
                            else:
                                metrics[class_id][face_id]['student_interest'] += ',' + course

        self.__logger.info("Finished to compute student_interest")
        return metrics

if __name__ == '__main__':
    doer = EstimateMental()
    doer.estimate()