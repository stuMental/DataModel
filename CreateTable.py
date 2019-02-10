# !/usr/bin/python
# -*- coding: utf-8 -*-

import DbUtil
import Config
import Logger

class CreateTable(object):
    """docstring for Preprocessor"""
    def __init__(self):
        super(CreateTable, self).__init__()
        self.__db = DbUtil.DbUtil(Config.INPUT_DB_HOST, Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__outputDB = DbUtil.DbUtil(Config.OUTPUT_DB_HOST, Config.OUTPUT_DB_USERNAME, Config.OUTPUT_DB_PASSWORD, Config.OUTPUT_DB_DATABASE, Config.OUTPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)


    def create_table(self):
        # 在raw数据库中创建数据表
        self.__logger.info("Create tables in the database {0}".format(Config.INPUT_DB_DATABASE))
        sql='''
            CREATE TABLE {0} (
                camera_id char(20) not null,
                frame_id char(20),
                body_id char(20),
                body_stat char(10),
                body_track char(20),
                face_id char(20),
                face_track char(20),
                face_pose char(10),
                face_pose_stat char(10),
                face_pose_stat_time char(10),
                face_emotion char(10),
                yawn char(10),
                unix_timestamp char(20),
                pose_stat_time char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.INTERMEDIATE_TRACK_TABLE)
        self.__db.create(sql)


        sql='''
            CREATE TABLE {0} (
                camera_id char(20) not null,
                face_id char(20),
                pose_stat_time char(20),
                face_pose_stat_time char(20),
                body_stat char(10),
                face_pose char(10),
                face_emotion char(10)
            )engine=innodb default charset=utf8
        '''.format(Config.INTERMEDIATE_TABLE)
        self.__db.create(sql)

        sql='''
            CREATE TABLE {0} (
                camera_id char(20) not null,
                face_id char(20),
                pose_stat_time char(20),
                body_stat char(10),
                face_pose char(10),
                face_emotion char(10),
                face_pose_stat char(10)
            )engine=innodb default charset=utf8
        '''.format(Config.INTERMEDIATE_RES_TABLE)
        self.__db.create(sql)

        sql='''
            CREATE TABLE {0} (
                camera_id char(20) not null,
                face_id char(20),
                pose_stat_time char(20),
                body_stat char(10),
                face_pose char(10),
                face_emotion char(10),
                face_pose_stat char(10),
                course_name char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.INTERMEDIATE_TABLE_TRAIN)
        self.__db.create(sql)

        sql='''
            CREATE TABLE {0} (
                course_name char(20),
                start_time char(20),
                end_time char(20),
                ds char(10)
        )engine=innodb default charset=utf8
        '''.format(Config.COURSE_INFO)
        self.__db.create(sql)
        self.__logger.info("Done")

        # 在UI数据库中创建数据表
        self.__logger.info("Create tables in output UI database {0}".format(Config.OUTPUT_DB_DATABASE))
        sql = '''
            CREATE TABLE {0} (
                student_number char(20) not null,
                class_id char(20),
                student_relationship char(10),
                student_emotion char(10),
                student_mental_stat char(10),
                student_study_stat char(10),
                student_interest char(255),
                dt char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.OUTPUT_UI_TABLE)
        self.__outputDB.create(sql)

        sql = '''
            CREATE TABLE {0} (
                student_number char(20) not null,
                class_id char(20),
                course_name char(20),
                student_mental_stat char(10),
                student_study_stat char(10),
                dt char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.OUTPUT_UI_COURSE_TABLE)
        self.__outputDB.create(sql)
        self.__logger.info("Done")