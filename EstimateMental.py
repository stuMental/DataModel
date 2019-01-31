# !/usr/bin/python
# -*- coding: utf8 -*-

import CommonUtil
import CalcMetric
import PostMetric
import Preprocessor
import Logger
import Config
import DbUtil

class EstimateMental(object):
    """docstring for EstimateMental"""
    def __init__(self):
        super(EstimateMental, self).__init__()
        self.__logger = Logger(__name__)
        self.__preprocessor = Preprocessor()
        self.__metric = CalcMetric()
        self.__poster = PostMetric()
        self.__db = DbUtil(Config.OUTPUT_DB_HOST, Config.OUTPUT_DB_USERNAME, Config.OUTPUT_DB_PASSWORD, Config.OUTPUT_DB_DATABASE, Config.OUTPUT_DB_CHARSET)

    def estimate(self):
        times = CommonUtil.get_time_range()
        self.__logger.info("Begin to preprocess data between {0} and {1}.".format(times['start_time'], times['end_time']))
        self.__preprocessor.preprocessor(times['start_time'], times['end_time'])
        self.__logger.info("Finished to preprocess.")

        self.__logger.info("Begin to compute metrics")
        metrics = self.__metric.calculate_metrics(times['start_time'], times['end_time'])
        self.__logger.info("Finished to compute metrics, such as study_state, emotion, mental, relationship.")

        self.__logger.info("Begin to compute interest metric")
        metrics = self.estimate_interest(times['end_time'], metrics)
        self.__logger.info("Finished to compute interest metric.")

        self.__logger.info("Begin to post results to UI Database")
        self.__poster.Post(metrics)
        self.__logger.info("Finished to process data between {0} and {1}.".format(times['start_time'], times['end_time']))

    def count_interest(self, end_time):
        ''''''
        sql = '''
            SELECT
                student_number, course_name, student_study_stat
            FROM {2}
            WHERE ds >= {0} AND ds <= {1}
        '''.format(CommonUtil.get_specific_time(end_time, Config.LOOKBACKWINDOW), end_time, Config.OUTPUT_UI_COURSE_TABLE)

        res = {}
        for row in self.__db.select(sql):
            if not res.has_key(row[0]):
                res[row[0]] = {}

            if not res[row[0]].has_key(row[1]):
                res[row[0]][row[1]] = 0

            if row[2] == 0 or row[2] == 1: # 非常好 + 良好的总计天数
                res[row[0]][row[1]] += 1
            else:
                continue

            return res

    def estimate_interest(self, end_time, metrics):
        ''''''
        study_states = self.count_interest(end_time)
        for key, value in metrics.items():
            if study_states.has_key(key):
                for course, value in study_states[key].items():
                    if value >= Config.INTEREST_THRESHOLD:
                        if not metrics[key].has_key('student_interest'):
                            metrics[key]['student_interest'] = course
                        else:
                            metrics[key]['student_interest'] += ',' + course

        return metrics


if __name__ == '__main__':
    doer = EstimateMental()
    doer.estimate()