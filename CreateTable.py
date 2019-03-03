# !/usr/bin/python
# -*- coding: utf-8 -*-

import DbUtil
import Config
import Logger

class CreateTable(object):
    """docsTry for Preprocessor"""
    def __init__(self):
        super(CreateTable, self).__init__()
        self.__db = DbUtil.DbUtil(Config.INPUT_DB_HOST, Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)

    def create_database(self):
        self.__logger.info("Create raw data tables in the database {0}".format(Config.INPUT_DB_DATABASE))

        sql='''
            CREATE DATABASE {0} DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
        '''.format(Config.INPUT_DB_DATABASE)
        self.__db.create(sql)

        self.__logger.info("Create raw data tables in the database {0}".format(Config.INPUT_DB_DATABASE))

    def create_table(self):
        # 在raw数据库中创建数据表
        self.__logger.info("Create raw data tables in the database {0}".format(Config.INPUT_DB_DATABASE))

        sql='''
            CREATE TABLE {0} (
                id int not null auto_increment,
                camera_id char(20),
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
                pose_stat_time char(20),
                primary key(id)
            )engine=innodb default charset=utf8
        '''.format(Config.RAW_INPUT_TABLE)
        self.__db.create(sql)

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
                class_id char(20),
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
                class_id char(20) not null,
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
                class_id char(20) not null,
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

        sql = '''
            CREATE TABLE {0} (
                grade_name char(20),
                class_name char(20),
                class_id char(20),
                student_number char(20),
                student_name char(20),
                dt char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.SCHOOL_STUDENT_CLASS_TABLE)
        self.__db.create(sql)

        sql = '''
            CREATE TABLE {0} (
                camera_id char(20),
                camera_addr char(20),
                class_id char(20),
                class_name char(20),
                grade_name char(20),
                dt char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.SCHOOL_CAMERA_CLASS_TABLE)
        self.__db.create(sql)

        sql = '''
            CREATE TABLE {0} (
                id int not null auto_increment,
                course_id char(20),
                course_name char(20),
                tea_id char(20),
                tea_name char(20),
                class_name char(20),
                grade_name char(20),
                start_time char(20),
                end_time char(20),
                dt char(20),
                primary key(id)
            )engine=innodb default charset=utf8
        '''.format(Config.SCHOOL_COURSE_TABLE)
        self.__db.create(sql)

        sql = '''
            CREATE TABLE {0} (
                student_number char(20),
                student_name char(20),
                grade_name char(20),
                class_name char(20),
                course_id char(20),
                course_name char(20),
                score float,
                dt char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.SCHOOL_PERFORMANCE_TABLE)
        self.__db.create(sql)

        sql = '''
            CREATE TABLE {0} (
                student_number char(20),
                student_name char(20),
                award_type char(20),
                award_level char(20),
                award_name char(20),
                dt char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.SCHOOL_AWARD_TABLE)
        self.__db.create(sql)
        self.__logger.info("Finished to create table")

        # 在UI数据库中创建数据表
        self.__logger.info("Create tables in output UI database {0}".format(Config.INPUT_DB_DATABASE))
        sql = '''
            CREATE TABLE {0} (
                student_number char(20) not null,
                student_name char(20),
                class_id char(20),
                grade_name char(20),
                class_name char(20),
                student_relationship char(10),
                student_emotion char(10),
                student_mental_stat char(10),
                student_study_stat char(10),
                student_interest char(255),
                dt char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.OUTPUT_UI_TABLE)
        self.__db.create(sql)

        sql = '''
            CREATE TABLE {0} (
                student_number char(20) not null,
                student_name char(20),
                class_id char(20),
                grade_name char(20),
                class_name char(20),
                course_name char(20),
                student_mental_stat char(10),
                student_study_stat char(10),
                dt char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.OUTPUT_UI_COURSE_TABLE)
        self.__db.create(sql)

        sql = '''
            CREATE TABLE {0} (
                student_number char(20) not null,
                student_name char(20),
                class_id char(20),
                grade_name char(20),
                class_name char(20),
                study_interest char(20),
                dt char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.OUTPUT_UI_INTEREST_TABLE)
        self.__db.create(sql)

        sql = '''
            CREATE TABLE {0} (
                student_number char(20) not null,
                course_name char(20),
                grade_level char(10),
                study_level char(10),
                dt char(20)
            )engine=innodb default charset=utf8
        '''.format(Config.OUTPUT_UI_GRADE_STUDY_TABLE)
        self.__db.create(sql)

        sql='''
            CREATE TABLE {0} (
                course_name char(20),
                class_name char(20),
                grade_name char(20),
                start_time char(20),
                end_time char(20),
                student_number char(20),
                student_name char(20),
                dt char(20)
        )engine=innodb default charset=utf8
        '''.format(Config.STUDENT_ATTENDANCE)
        self.__db.create(sql)

        self.__logger.info("Finished to create tables for UI")

    def create_index(self):
        self.__logger.info("Create index on the table")
        sql = '''
            CREATE INDEX pose_stat_time_index ON {0} (pose_stat_time);
            CREATE INDEX pose_stat_time_index ON {1} (pose_stat_time);
            CREATE INDEX pose_stat_time_index ON {2} (pose_stat_time);
            CREATE INDEX pose_stat_time_index ON {3} (pose_stat_time);
            CREATE INDEX pose_stat_time_index ON {4} (pose_stat_time);
        '''.format(Config.RAW_INPUT_TABLE, Config.INTERMEDIATE_TRACK_TABLE, Config.INTERMEDIATE_TABLE, Config.INTERMEDIATE_RES_TABLE, Config.INTERMEDIATE_TABLE_TRAIN)
        self.__db.create(sql)
        self.__logger.info("Finished to create index")

        self.__logger.info("Try to create index for UI tables")
        sql = '''
            CREATE INDEX dt_index ON {0} (dt);
            CREATE INDEX dt_index ON {1} (dt);
            CREATE INDEX dt_index ON {2} (dt);
            CREATE INDEX dt_index ON {3} (dt);
            CREATE INDEX dt_index ON {4} (dt);
        '''.format(Config.OUTPUT_UI_TABLE, Config.OUTPUT_UI_COURSE_TABLE, Config.OUTPUT_UI_INTEREST_TABLE, Config.OUTPUT_UI_GRADE_STUDY_TABLE, Config.STUDENT_ATTENDANCE)
        self.__db.create(sql)
        self.__logger.info("Finished create index")

if __name__ == '__main__':
    doer = CreateTable()
    # doer.create_database()
    doer.create_table()
    doer.create_index()