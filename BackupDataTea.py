# !/usr/bin/python
# -*- coding: utf-8 -*-

import DbUtil
import Config
import Logger
from CommonUtil import CommonUtil


class BackupDataTea(object):
    """备份原始数据"""
    def __init__(self, configs):
        super(BackupDataTea, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD if configs['pwd'] is None else configs['pwd'], Config.INPUT_DB_DATABASE if configs['dbname'] is None else configs['dbname'], Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)

    def process(self):
        CommonUtil.verify()
        # self.__logger.info('开始备份教师行为数据，将数据从{0}备份到{1}.'.format(Config.TEACHER_RAW_DATA_TABLE, Config.TEACHER_RAW_DATA_TABLE_BAK))
        # sql = '''
        #     INSERT INTO {0} SELECT * FROM {1}
        # '''.format(Config.TEACHER_RAW_DATA_TABLE_BAK, Config.TEACHER_RAW_DATA_TABLE)
        # self.__db.insert(sql)
        self.__logger.info('开始将表{0}中的数据删除.'.format(Config.TEACHER_RAW_DATA_TABLE))
        sql = '''
            TRUNCATE TABLE {0}
        '''.format(Config.TEACHER_RAW_DATA_TABLE)
        self.__db.truncate(sql)
        self.__logger.info('备份数据结束')


if __name__ == "__main__":
    configs = {
        'dbhost': '172.16.14.190'
    }
    processor = BackupDataTea(configs)
    processor.process()
