# !/usr/bin/python
# -*- coding: utf8 -*-

import DbUtil
import Config
from CommonUtil import CommonUtil
import Logger
import datetime

class PostMetric(object):
    """docsTry for PostMetric"""
    def __init__(self, configs):
        super(PostMetric, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD if configs['pwd'] is None else configs['pwd'], Config.INPUT_DB_DATABASE if configs['dbname'] is None else configs['dbname'], Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)
        self.__delimiter = '@'

    def post(self, datas, dt, students):
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
                    {0} (student_number, student_name, college_name, grade_name, class_name, student_relationship, student_emotion, student_mental_stat, student_study_stat, student_interest, dt) VALUES
            '''.format(Config.OUTPUT_UI_TABLE)

            valuesSql = ''
            for class_id, values in datas.items():
                for face_id, value in values.items():
                    if face_id in students:
                        if not first:
                            valuesSql += ','

                        valuesSql += '''
                            ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}')
                        '''.format(face_id, students[face_id]['student_name'], students[face_id]['college_name'], students[face_id]['grade_name'], students[face_id]['class_name'], self.get_valid_value(value, 'student_relationship'), self.get_valid_value(value, 'student_emotion'), self.get_valid_value(value, 'student_mental_stat'), self.get_valid_value(value, 'student_study_stat'), self.get_valid_value(value, 'student_interest'), dt)
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

        return students

    def post_course_metric(self, datas, dt, students):
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
                    {0} (student_number, student_name, college_name, grade_name, class_name, course_name, student_emotion, student_study_stat, student_mental_stat, dt) VALUES
            '''.format(Config.OUTPUT_UI_COURSE_TABLE)

            valuesSql = ''
            for class_id, raws in datas.items():
                for face_id, values in raws.items():
                    if face_id in students:
                        for course_name, course_value in values.items():
                            if not first:
                                valuesSql += ','

                            valuesSql +='''
                                ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}')
                            '''.format(face_id, students[face_id]['student_name'], students[face_id]['college_name'], students[face_id]['grade_name'], students[face_id]['class_name'], course_name, self.get_valid_value(course_value, 'student_emotion'), self.get_valid_value(course_value, 'student_study_stat'), self.get_valid_value(course_value, 'student_mental_stat'), dt)
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

        return students

    def post_interest_metric(self, datas, dt, students):
        ''''''
        self.__logger.info("Try to post metric for interest courses to UI database [{0}], and the table [{1}]".format(Config.INPUT_DB_DATABASE, Config.OUTPUT_UI_INTEREST_TABLE))
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
                    {0} (student_number, student_name, college_name, grade_name, class_name, student_interest, dt) VALUES
            '''.format(Config.OUTPUT_UI_INTEREST_TABLE)

            valuesSql = ''
            for class_id, raws in datas.items():
                for face_id, values in raws.items():
                    if face_id in students:
                        for course_name in values:
                            if not first:
                                valuesSql += ','

                            valuesSql +='''
                                ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')
                            '''.format(face_id, students[face_id]['student_name'], students[face_id]['college_name'], students[face_id]['grade_name'], students[face_id]['class_name'], course_name, dt)
                            first = False
                            count += 1

                            if count % Config.INSERT_BATCH_THRESHOLD == 0:
                                self.__logger.info("Try to insert {0} records to table {1}".format(Config.INSERT_BATCH_THRESHOLD, Config.OUTPUT_UI_INTEREST_TABLE))
                                self.__db.insert(sql + valuesSql)
                                valuesSql = ''
                                first = True

            if valuesSql != '':
                self.__db.insert(sql + valuesSql)
        self.__logger.info("Finished to post interest course metric data, total rows is {0}".format(count))

        return students

    def post_grade_study_metric(self, datas, students):
        ''''''
        self.__logger.info("Try to post metric for grade and study to UI database [{0}], and the table [{1}]".format(Config.INPUT_DB_DATABASE, Config.OUTPUT_UI_GRADE_STUDY_TABLE))
        count = 0
        if isinstance(datas, dict) and len(datas) > 0 and students:
            for item in datas.items():
                for dt in item[1].keys():
                    self.__logger.info("Begin to insert data on {0}".format(dt))
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
                            {0} (student_number, college_name, grade_name, class_name, course_name, grade_level, study_level, dt) VALUES
                    '''.format(Config.OUTPUT_UI_GRADE_STUDY_TABLE)

                    valuesSql = ''
                    for stu_id, values in item[1][dt].items():
                        if stu_id in students:
                            for row in values:
                                if not first:
                                    valuesSql += ','

                                valuesSql +='''
                                    ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')
                                '''.format(stu_id, students[stu_id]['college_name'], students[stu_id]['grade_name'], students[stu_id]['class_name'], row[0], row[1], row[2], dt)
                                first = False
                                count += 1

                                if count % Config.INSERT_BATCH_THRESHOLD == 0:
                                    self.__logger.info("Try to insert {0} records to table {1}".format(Config.INSERT_BATCH_THRESHOLD, Config.OUTPUT_UI_GRADE_STUDY_TABLE))
                                    self.__db.insert(sql + valuesSql)
                                    valuesSql = ''
                                    first = True

                    if valuesSql != '':
                        self.__db.insert(sql + valuesSql)
        self.__logger.info("Finished to post grade and study metric data, total rows is {0}".format(count))

    def post_teaching(self, data, dt):
        """ 将教学评估的数据存储到Mysql数据库中
        """

        self.__logger.info('Try to post teaching status to db.')
        self.post_teaching_student(data, dt)
        self.post_teaching_class(data, dt)
        self.__logger.info('End to post teaching status to db.')

    def post_teaching_student(self, data, dt):
        """ 将教学评估的数据存储到Mysql数据库中
        """

        self.__logger.info('Try to post teaching student status to db.')
        if data:
            sql = '''
                DELETE FROM {0} WHERE dt = '{1}'
            '''.format(Config.OUTPUT_TEACHING_CLASS_STUDENT, dt)
            self.__db.delete(sql)

            sql = '''
                INSERT INTO {0} (college_name, grade_name, class_name, course_name, action_status, rate, action_type, dt) VALUES
            '''.format(Config.OUTPUT_TEACHING_CLASS_STUDENT)

            for class_id, classes in data.items():
                result_sql = ''
                class_arr = class_id.split(self.__delimiter)
                for course, record in classes.items():
                    for key, values in record.items():
                        if key in ['face_emotion', 'mental', 'study']:
                            for action, score in values.items():
                                tmp_sql = ''
                                if result_sql:
                                    tmp_sql = ''',('{0}', '{1}', '{2}', '{3}', '{4}', {5}, {6}, '{7}')'''
                                else:
                                    tmp_sql = sql + '''('{0}', '{1}', '{2}', '{3}', '{4}', {5}, {6}, '{7}')'''

                                result_sql += tmp_sql.format(class_arr[0], class_arr[1], class_arr[2], course, action, score, Config.ACTION_TYPE[key], dt)

                self.__db.insert(result_sql)

    def post_teaching_class(self, data, dt):
        """ 将教学评估的数据存储到Mysql数据库中
        """

        self.__logger.info('Try to post teaching daily status to db.')
        if data:
            sql = '''
                DELETE FROM {0} WHERE dt = '{1}'
            '''.format(Config.OUTPUT_TEACHING_CLASS_DAILY, dt)
            self.__db.delete(sql)

            sql = '''
                INSERT INTO {0} (college_name, grade_name, class_name, course_name, class_positivity, class_interactivity, class_concentration, dt) VALUES
            '''.format(Config.OUTPUT_TEACHING_CLASS_DAILY)

            result_sql = ''
            for class_id, classes in data.items():
                class_arr = class_id.split(self.__delimiter)
                for course, record in classes.items():
                    tmp_sql = ''
                    if result_sql:
                        tmp_sql = ''',('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')'''
                    else:
                        tmp_sql = sql + '''('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')'''

                    result_sql += tmp_sql.format(class_arr[0], class_arr[1], class_arr[2], course, record['class_positivity'], record['class_interactivity'], record['class_concentration'], dt)

            self.__db.insert(result_sql)

    def post_teaching_study_grade(self, data):
        """ 将课堂的成绩和学习状态二元关系存储到数据表
        """
        if data:
            sql = '''
                INSERT INTO {0} (college_name, grade_name, class_name, course_name, grade_level, study_level, dt) VALUES
            '''.format(Config.OUTPUT_TEACHING_CLASS_GRADE_STUDY)

            result_sql = ''
            for class_id, dts in data.items():
                class_arr = class_id.split(self.__delimiter)
                for dt, records in dts.items():
                    del_sql = '''
                        DELETE FROM {0} WHERE dt = '{1}'
                    '''.format(Config.OUTPUT_TEACHING_CLASS_GRADE_STUDY, dt)
                    self.__db.delete(del_sql)
                    for course, scores in records.items():
                        tmp_sql = ''
                        if result_sql:
                            tmp_sql = ''',('{0}', '{1}', '{2}', '{3}', {4}, {5}, '{6}')'''
                        else:
                            tmp_sql = sql + '''('{0}', '{1}', '{2}', '{3}', {4}, {5}, '{6}')'''

                        result_sql += tmp_sql.format(class_arr[0], class_arr[1], class_arr[2], course, scores[0], scores[1], dt)

            self.__db.insert(result_sql)

    def post_teacher_emotions(self, data, dt):
        """ 将教师情绪储存到数据表
        """
        self.__logger.info('将教师情绪的结果存储到数据表')
        if data:
            sql = '''
                DELETE FROM {0} WHERE dt = '{1}'
            '''.format(Config.OUTPUT_UI_TEA_EMOTION_TABLE, dt)
            self.__db.delete(sql)

            sql = '''
                INSERT INTO {0} (teacher_id, teacher_name, college_name, grade_name, class_name, course_id, course_name, happy, normal, angry, dt) VALUES
            '''.format(Config.OUTPUT_UI_TEA_EMOTION_TABLE)
            result_sql = ''
            for teas in data.keys():
                tea_arrs = teas.split(self.__delimiter)
                for classes in data[teas].keys():
                    class_arrs = classes.split(self.__delimiter)
                    for courses, items in data[teas][classes].items():
                        course_arrs = courses.split(self.__delimiter)
                        tmp_sql = ''
                        if result_sql:
                            tmp_sql = ''',('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', {7}, {8}, {9}, '{10}')'''
                        else:
                            tmp_sql = sql + '''('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', {7}, {8}, {9}, '{10}')'''

                        result_sql += tmp_sql.format(tea_arrs[0], tea_arrs[1], class_arrs[0], class_arrs[1], class_arrs[2], course_arrs[0], course_arrs[1], items['happy'], items['normal'], items['angry'], dt)

            self.__db.insert(result_sql)

    def post_teacher_behaviors(self, data, dt):
        """ 将行为序列存储到数据表
        """
        self.__logger.info('将S-T行为序列的结果存储到数据表')
        if data:
            for table in [Config.OUTPUT_UI_TEA_BEHAVIOR_TABLE, Config.OUTPUT_UI_TEA_COURSE_TABLE]:
                sql = '''
                    DELETE FROM {0} WHERE dt = '{1}'
                '''.format(table, dt)
                self.__db.delete(sql)

            sql1 = '''
                INSERT INTO {0} (teacher_id, teacher_name, college_name, grade_name, class_name, course_id, course_name, action, type, unix_timestamp, dt) VALUES
            '''.format(Config.OUTPUT_UI_TEA_BEHAVIOR_TABLE)
            sql2 = '''
                INSERT INTO {0} (teacher_id, teacher_name, college_name, grade_name, class_name, course_id, course_name, rt, ch, dt) VALUES
            '''.format(Config.OUTPUT_UI_TEA_COURSE_TABLE)
            result_sql1 = ''
            result_sql2 = ''
            for teas in data.keys():
                tea_arrs = teas.split(self.__delimiter)
                for classes in data[teas].keys():
                    class_arrs = classes.split(self.__delimiter)
                    for courses, items in data[teas][classes].items():
                        course_arrs = courses.split(self.__delimiter)
                        tmp_sql2 = ''
                        if result_sql2:
                            tmp_sql2 = ''',('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', {7}, {8}, '{9}')'''
                        else:
                            tmp_sql2 = sql2 + '''('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', {7}, {8}, '{9}')'''

                        result_sql2 += tmp_sql2.format(tea_arrs[0], tea_arrs[1], class_arrs[0], class_arrs[1], class_arrs[2], course_arrs[0], course_arrs[1], items['scores'][0], items['scores'][1], dt)
                        for item in items['behaviors']:
                            arrs = item[1].split('-')
                            tmp_sql1 = ''
                            if result_sql1:
                                tmp_sql1 = ''',('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', {8}, {9}, '{10}')'''
                            else:
                                tmp_sql1 = sql1 + '''('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', {8}, {9}, '{10}')'''

                            result_sql1 += tmp_sql1.format(tea_arrs[0], tea_arrs[1], class_arrs[0], class_arrs[1], class_arrs[2], course_arrs[0], course_arrs[1], arrs[1], arrs[0], item[0], dt)

            self.__db.insert(result_sql1)
            self.__db.insert(result_sql2)

    def post_teacher_scores(self, data, dt):
        """ 将教学状态评估得分存储到数据表
        """
        self.__logger.info('将教学状态评估的结果存储到数据表')
        if data:
            sql = '''
                DELETE FROM {0} WHERE dt = '{1}'
            '''.format(Config.OUTPUT_UI_TEA_DAILY_TABLE, dt)
            self.__db.delete(sql)

            sql = '''
                INSERT INTO {0} (teacher_id, teacher_name, college_name, grade_name, class_name, course_id, course_name, score, emotion, behavior, ontime, dt) VALUES
            '''.format(Config.OUTPUT_UI_TEA_DAILY_TABLE)

            result_sql = ''
            for teas in data.keys():
                tea_arrs = teas.split(self.__delimiter)
                for classes in data[teas].keys():
                    class_arrs = classes.split(self.__delimiter)
                    for courses, items in data[teas][classes].items():
                        course_arrs = courses.split(self.__delimiter)
                        tmp_sql = ''
                        if result_sql:
                            tmp_sql = ''',('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', {7}, {8}, {9}, {10}, '{11}')'''
                        else:
                            tmp_sql = sql + '''('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', {7}, {8}, {9}, {10}, '{11}')'''

                        result_sql += tmp_sql.format(tea_arrs[0], tea_arrs[1], class_arrs[0], class_arrs[1], class_arrs[2], course_arrs[0], course_arrs[1], items['score'], items['emotion'], items['behavior'], items['ontime'], dt)

            self.__db.insert(result_sql)

    def get_valid_value(self, data, key):
        ''''''
        if isinstance(data, dict) and key in data:
            return data[key]
        else:
            return Config.STUDENT_STATUS_DEFAULT[key]  # 默认值

    def get_default_value(self, data):
        '''对于人际关系 无数据时设置正常（2）为默认值'''
        if data == '':
            return 2 # 正常
        else:
            return data

    def get_student_name(self, face_id, classes, class_id, dt):
        '''
            针对这次演示，如果学生信息表中无该face_id对应的数据 就以'嘉宾_'+face_id插入一条数据到学生信息表中
        '''
        self.__logger.debug("发现嘉宾数据，往数据表{0}中插入一条新数据。".format(Config.SCHOOL_STUDENT_CLASS_TABLE))
        data = face_id.split("_")
        student_name = Config.PREFIX_GUEST + self.get_time_from_unixtimestamp(float(data[0]) / 1000) + "_" + data[1]
        sql = '''
            INSERT INTO {0} (grade_name, class_name, student_number, student_name, dt) VALUES ('{1}', '{2}', '{3}', '{4}', '{5}');
        '''.format(Config.SCHOOL_STUDENT_CLASS_TABLE, classes[class_id][0], classes[class_id][1], face_id, student_name, dt)
        self.__db.insert(sql)
        self.__logger.debug("已插入一条嘉宾数据， 嘉宾ID是 {0}.".format(face_id))
        return student_name

    def get_time_from_unixtimestamp(self, timestamp):
        ''''''
        return datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
