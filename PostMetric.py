# !/usr/bin/python
# -*- coding: utf8 -*-

import DbUtil
import Config
from CommonUtil import CommonUtil
import Logger

class PostMetric(object):
    """docstring for PostMetric"""
    def __init__(self):
        super(PostMetric, self).__init__()
        self.__outputDB = DbUtil.DbUtil(Config.OUTPUT_DB_HOST, Config.OUTPUT_DB_USERNAME, Config.OUTPUT_DB_PASSWORD, Config.OUTPUT_DB_DATABASE, Config.OUTPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)

    def post(self, datas, dt):
        ''' Post data to UI database '''

        self.__logger.info("Try to post data to UI database [{0}], and the table [{1}].".format(Config.OUTPUT_DB_DATABASE, Config.OUTPUT_UI_TABLE))
        if isinstance(datas, dict):
            count = 0
            first = True
            sql = '''
                INSERT INTO
                    {0} (student_number, class_id, student_relationship, student_emotion, student_mental_stat, student_study_stat, student_interest, dt) VALUES 
            '''.format(Config.OUTPUT_UI_TABLE)

            valuesSql = ''

            for class_id, values in datas.items():
                for face_id, value in values.items():
                    if not first:
                        valuesSql += ','

                    valuesSql += '''
                        ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')
                    '''.format(face_id, class_id, self.get_valid_value(value, 'student_relationship'), self.get_valid_value(value, 'student_emotion'), self.get_valid_value(value, 'student_mental_stat'), self.get_valid_value(value, 'student_study_stat'), self.get_valid_value(value, 'student_interest'), dt)
                    first = False
                    count += 1
                    if count % Config.INSERT_BATCH_THRESHOLD == 0:
                        self.__logger.info("Tring to insert {0} records to table {1}".format(Config.INSERT_BATCH_THRESHOLD, Config.OUTPUT_UI_TABLE))
                        self.__outputDB.insert(sql + valuesSql)
                        valuesSql = ''
                        first = True

            if valuesSql != '':
                self.__outputDB.insert(sql + valuesSql)
        self.__logger.info("Finished to post data, total rows is {0}".format(count))

    def post_course_metric(self, datas, dt):
        ''''''

        self.__logger.info("Tring to post metric for courses to UI database [{0}], and the table [{1}]".format(Config.OUTPUT_DB_DATABASE, Config.OUTPUT_UI_COURSE_TABLE))
        if isinstance(datas, dict):
            count = 0
            first = True
            sql = '''
                INSERT INTO
                    {0} (student_number, class_id, course_name, student_study_stat, student_mental_stat, dt) VALUES 
            '''.format(Config.OUTPUT_UI_COURSE_TABLE)

            valuesSql = ''

            for class_id, raws in datas.items():
                for face_id, values in raws.items():
                    for course_name, course_value in values.items():
                        if not first:
                            valuesSql += ','

                        valuesSql +='''
                            ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')
                        '''.format(face_id, class_id, course_name, self.get_valid_value(course_value, 'student_study_stat'), self.get_valid_value(course_value, 'student_mental_stat'), dt)
                        first = False
                        count += 1

                        if count % Config.INSERT_BATCH_THRESHOLD == 0:
                            self.__logger.info("Tring to insert {0} records to table {1}".format(Config.INSERT_BATCH_THRESHOLD, Config.OUTPUT_UI_COURSE_TABLE))
                            self.__outputDB.insert(sql + valuesSql)
                            valuesSql = ''
                            first = True

            if valuesSql != '':
                self.__outputDB.insert(sql + valuesSql)
        self.__logger.info("Finished to post course metric data, total rows is {0}".format(count))

    def get_valid_value(self, data, key):
        ''''''
        if isinstance(data, dict) and data.has_key(key):
            return data[key]
        else:
            return ''