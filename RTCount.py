# !/usr/bin/python
# -*- coding: utf-8 -*-

import time
import DbUtil
import Config
import Logger
from CommonUtil import CommonUtil


class RTCount(object):
    """实时统计教室的人数情况"""
    def __init__(self, configs):
        super(RTCount, self).__init__()
        self.__db = DbUtil.DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)
        self.__logger = Logger.Logger(__name__)

    def process(self):
        CommonUtil.verify()
        self.__logger.info("Try to real time the number of students for each teaching room, then output results to the table {0}".format(Config.REAL_TIME_PEOPLE_TABLE))
        unixtimestamp = int(time.time())
        self.__process_people_count(unixtimestamp)
        self.__process_history(unixtimestamp)
        self.__logger.info('Done')

    def __process_people_count(self, timestamp):
        """ 每隔固定时间间隔处理数据
        """

        # self.__logger.info('Delete all data in table {0} for the time {1}'.format(Config.REAL_TIME_PEOPLE_TABLE_RTL, timestamp))
        # sql = '''
        #     TRUNCATE TABLE {0}
        # '''.format(Config.REAL_TIME_PEOPLE_TABLE_RTL)
        # self.__db.delete(sql)
        sql = '''
            SELECT t4.room_id, t4.room_addr, IF(t5.total IS NULL, 0, t5.total) AS total, {0} AS unix_timestamp, FROM_UNIXTIME({0}) AS dt
            FROM {4} t4 LEFT OUTER JOIN (
                SELECT t3.room_id, t3.room_addr, MAX(t3.total) AS total
                FROM (
                    SELECT t2.room_id, t2.room_addr, t1.frame_id, COUNT(*) AS total
                    FROM (
                        SELECT
                            camera_id, frame_id
                        FROM {2}
                        WHERE pose_stat_time >= {1} AND pose_stat_time <= {0}
                    ) t1 JOIN {3} t2
                    ON t1.camera_id = t2.camera_id
                    GROUP BY t2.room_id, t2.room_addr, t1.frame_id
                ) t3
                GROUP BY t3.room_id, t3.room_addr
            ) t5 ON t4.room_id = t5.room_id AND t4.room_addr = t5.room_addr
        '''.format(timestamp, timestamp - Config.REAL_TIME_INTERVAL, Config.RAW_INPUT_TABLE, Config.SCHOOL_CAMERA_ROOM_TABLE, Config.SCHOOL_CAMERA_ROOM_TABLE)
        for record in self.__db.select(sql):
            sql = '''
                INSERT INTO {0} (room_id, room_addr, total, unix_timestamp, dt) VALUES({1}, '{2}', {3}, {4}, '{5}') ON DUPLICATE KEY UPDATE total = {3}, unix_timestamp ={4}, dt = '{5}'
            '''.format(Config.REAL_TIME_PEOPLE_TABLE_RTL, record[0], record[1].encode('utf-8'), record[2], record[3], record[4])
            self.__db.insert(sql)
        self.__logger.info("Finish to compute real time the number of students for each teaching room.")

    def __process_history(self, timestamp):
        """ 备份历史数据
        """

        self.__logger.info('Delete all data in table {0} for the time {1}'.format(Config.REAL_TIME_PEOPLE_TABLE, timestamp))
        sql = '''
            DELETE a FROM {0} a WHERE unix_timestamp = {1}
        '''.format(Config.REAL_TIME_PEOPLE_TABLE, timestamp)
        self.__db.delete(sql)

        sql = '''
            INSERT INTO {0} SELECT * FROM {1}
        '''.format(Config.REAL_TIME_PEOPLE_TABLE, Config.REAL_TIME_PEOPLE_TABLE_RTL)
        self.__db.insert(sql)
        self.__logger.info("Finish to back up data.")


if __name__ == "__main__":
    configs = {
        'dbhost': '127.0.0.1'
    }
    processor = RTCount(configs)
    processor.process()