# !/usr/bin/python
# -*- coding: utf8 -*-

import DbUtil
import Config
from CommonUtil import CommonUtil
import Logger

class PostMetric(object):
    """docsTry for PostMetric"""
    def __init__(self, configs):
        super(PostMetric, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)

    def post(self, datas, dt, students, classes):
        ''' Post data to UI database '''
        self.__logger.info("Try to post data to UI database [{0}], and the table [{1}].".format(Config.INPUT_DB_DATABASE, Config.OUTPUT_UI_TABLE))
        count = 0
        if isinstance(datas, dict) and len(datas) > 0:
            # 如果表中已经存在dt对应的数据，应先删除
            self.__logger.info("Delete data of date {0} in the table {1}.".format(dt, Config.OUTPUT_UI_TABLE))
            sql = '''
                DELETE FROM {0} WHERE dt = '{1}'
            '''.format(Config.OUTPUT_UI_TABLE, dt)
            self.__db.delete(sql)
            self.__logger.info("Done")

            # 插入dt对应的最新的计算结果
            first = True
            sql = '''
                INSERT INTO
                    {0} (student_number, class_id, student_relationship, student_emotion, student_mental_stat, student_study_stat, student_interest, dt, student_name, grade_name, class_name) VALUES 
            '''.format(Config.OUTPUT_UI_TABLE)

            valuesSql = ''

            for class_id, values in datas.items():
                for face_id, value in values.items():
                    if not first:
                        valuesSql += ','

                    valuesSql += '''
                        ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}')
                    '''.format(face_id, class_id, self.get_default_value(self.get_valid_value(value, 'student_relationship')), self.get_valid_value(value, 'student_emotion'), self.get_valid_value(value, 'student_mental_stat'), self.get_valid_value(value, 'student_study_stat'), self.get_valid_value(value, 'student_interest'), dt, students[face_id].encode('utf-8'), classes[class_id][0].encode('utf-8'), classes[class_id][1].encode('utf-8'))
                    first = False
                    count += 1
                    if count % Config.INSERT_BATCH_THRESHOLD == 0:
                        self.__logger.info("Try to insert {0} records to table {1}".format(Config.INSERT_BATCH_THRESHOLD, Config.OUTPUT_UI_TABLE))
                        self.__db.insert(sql + valuesSql)
                        valuesSql = ''
                        first = True

            if valuesSql != '':
                self.__db.insert(sql + valuesSql)
        self.__logger.info("Finished to post data, total rows is {0}".format(count))

    def post_course_metric(self, datas, dt, students, classes):
        ''''''
        self.__logger.info("Try to post metric for courses to UI database [{0}], and the table [{1}]".format(Config.INPUT_DB_DATABASE, Config.OUTPUT_UI_COURSE_TABLE))
        count = 0
        if isinstance(datas, dict) and len(datas) > 0:
            # 如果表中已经存在dt对应的数据，应先删除
            self.__logger.info("Delete data of date {0} in the table {1}.".format(dt, Config.OUTPUT_UI_COURSE_TABLE))
            sql = '''
                DELETE FROM {0} WHERE dt = '{1}'
            '''.format(Config.OUTPUT_UI_COURSE_TABLE, dt)
            self.__db.delete(sql)
            self.__logger.info("Done")

            # 插入dt对应的最新的计算结果
            first = True
            sql = '''
                INSERT INTO
                    {0} (student_number, class_id, course_name, student_study_stat, student_mental_stat, dt, student_name, grade_name, class_name) VALUES 
            '''.format(Config.OUTPUT_UI_COURSE_TABLE)

            valuesSql = ''

            for class_id, raws in datas.items():
                for face_id, values in raws.items():
                    for course_name, course_value in values.items():
                        if not first:
                            valuesSql += ','

                        valuesSql +='''
                            ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')
                        '''.format(face_id, class_id, course_name, self.get_valid_value(course_value, 'student_study_stat'), self.get_valid_value(course_value, 'student_mental_stat'), dt, students[face_id].encode('utf-8'), classes[class_id][0].encode('utf-8'), classes[class_id][1].encode('utf-8'))
                        first = False
                        count += 1

                        if count % Config.INSERT_BATCH_THRESHOLD == 0:
                            self.__logger.info("Try to insert {0} records to table {1}".format(Config.INSERT_BATCH_THRESHOLD, Config.OUTPUT_UI_COURSE_TABLE))
                            self.__db.insert(sql + valuesSql)
                            valuesSql = ''
                            first = True

            if valuesSql != '':
                self.__db.insert(sql + valuesSql)
        self.__logger.info("Finished to post course metric data, total rows is {0}".format(count))

    def post_interest_metric(self, datas, dt, students, classes):
        ''''''
        self.__logger.info("Try to post metric for courses to UI database [{0}], and the table [{1}]".format(Config.INPUT_DB_DATABASE, Config.OUTPUT_UI_INTEREST_TABLE))
        count = 0
        if isinstance(datas, dict) and len(datas) > 0:
            # 如果表中已经存在dt对应的数据，应先删除
            self.__logger.info("Delete data of date {0} in the table {1}.".format(dt, Config.OUTPUT_UI_INTEREST_TABLE))
            sql = '''
                DELETE FROM {0} WHERE dt = '{1}'
            '''.format(Config.OUTPUT_UI_INTEREST_TABLE, dt)
            self.__db.delete(sql)
            self.__logger.info("Done")

            # 插入dt对应的最新的计算结果
            first = True
            sql = '''
                INSERT INTO
                    {0} (student_number, class_id, student_interest, dt, student_name, grade_name, class_name) VALUES 
            '''.format(Config.OUTPUT_UI_INTEREST_TABLE)

            valuesSql = ''

            for class_id, raws in datas.items():
                for face_id, values in raws.items():
                    for course_name in values:
                        if not first:
                            valuesSql += ','

                        valuesSql +='''
                            ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')
                        '''.format(face_id, class_id, course_name, dt, students[face_id].encode('utf-8'), classes[class_id][0].encode('utf-8'), classes[class_id][1].encode('utf-8'))
                        first = False
                        count += 1

                        if count % Config.INSERT_BATCH_THRESHOLD == 0:
                            self.__logger.info("Try to insert {0} records to table {1}".format(Config.INSERT_BATCH_THRESHOLD, Config.OUTPUT_UI_INTEREST_TABLE))
                            self.__db.insert(sql + valuesSql)
                            valuesSql = ''
                            first = True

            if valuesSql != '':
                self.__db.insert(sql + valuesSql)
        self.__logger.info("Finished to post course metric data, total rows is {0}".format(count))

    def post_grade_study_metric(self, datas, dt):
        ''''''
        self.__logger.info("Try to post metric for courses to UI database [{0}], and the table [{1}]".format(Config.INPUT_DB_DATABASE, Config.OUTPUT_UI_GRADE_STUDY_TABLE))
        count = 0
        if isinstance(datas, dict) and len(datas) > 0:
            # 如果表中已经存在dt对应的数据，应先删除
            self.__logger.info("Delete data of date {0} in the table {1}.".format(dt, Config.OUTPUT_UI_GRADE_STUDY_TABLE))
            sql = '''
                DELETE FROM {0} WHERE dt = '{1}'
            '''.format(Config.OUTPUT_UI_GRADE_STUDY_TABLE, dt)
            self.__db.delete(sql)
            self.__logger.info("Done")

            # 插入dt对应的最新的计算结果
            first = True
            sql = '''
                INSERT INTO
                    {0} (student_number, course_name, grade_level, study_level, dt) VALUES 
            '''.format(Config.OUTPUT_UI_GRADE_STUDY_TABLE)

            valuesSql = ''

            for stu_id, values in datas.items():
                for row in values:
                    if not first:
                        valuesSql += ','

                    valuesSql +='''
                        ('{0}', '{1}', '{2}', '{3}', '{4}')
                    '''.format(stu_id, row[0], row[1], row[2], dt)
                    first = False
                    count += 1

                    if count % Config.INSERT_BATCH_THRESHOLD == 0:
                        self.__logger.info("Try to insert {0} records to table {1}".format(Config.INSERT_BATCH_THRESHOLD, Config.OUTPUT_UI_GRADE_STUDY_TABLE))
                        self.__db.insert(sql + valuesSql)
                        valuesSql = ''
                        first = True

            if valuesSql != '':
                self.__db.insert(sql + valuesSql)
        self.__logger.info("Finished to post course metric data, total rows is {0}".format(count))

    def get_valid_value(self, data, key):
        ''''''
        if isinstance(data, dict) and data.has_key(key):
            return data[key]
        else:
            return ''

    def get_default_value(self, data):
        '''对于人际关系 无数据时设置正常（2）为默认值'''
        if data == '':
            return 2 # 正常