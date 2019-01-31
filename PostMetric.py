# !/usr/bin/python
# -*- coding: utf8 -*-

import DbUtil
import Config
import CommonUtil
import Logger

class PostMetric(object):
    """docstring for PostMetric"""
    def __init__(self):
        super(PostMetric, self).__init__()
        self.__outputDB = DbUtil(Config.OUTPUT_DB_HOST, Config.OUTPUT_DB_USERNAME, Config.OUTPUT_DB_PASSWORD, Config.OUTPUT_DB_DATABASE, Config.OUTPUT_DB_CHARSET)
        self.__logger = Logger(__name__)

    def Post(self, datas):
        ''' Post data to UI database '''

        self.__logger.info("Try to post data to UI database [{0}], and the table [{1}].".format(Config.OUTPUT_DB_DATABASE, Config.OUTPUT_UI_TABLE))
        if isinstance(datas, dict):
            count = 0
            for key, value in datas.items():
                sql = '''
                    INSERT INTO
                        {6} (student_number, student_relationship, student_emotion, student_mental_stat, student_study_stat, ds)
                    VALUES ({0}, {1}, {2}, {3}, {4}, {5})
                '''.format(key, value['student_relationship'], value['student_emotion'], value['student_mental_stat'], value['student_study_stat'], CommonUtil.get_current_time(), Config.OUTPUT_UI_TABLE)

                self.__outputDB.insert(sql)
                count += 1
        self.__logger.info("Finished to post data, total rows is {0}".fromat(count))