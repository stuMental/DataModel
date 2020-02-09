# !/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import json
import time
import Config
from Logger import Logger
import threading


class Server(object):
    def __init__(self, configs):
        self.__logger = Logger(__name__)
        self.__dbhost = configs['dbhost']
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((configs['dbhost'], Config.SOCKET_PORT))
        self.__server.listen(5)
        # self.__db = DbUtil(configs['dbhost'], Config.INPUT_DB_USERNAME, Config.INPUT_DB_PASSWORD, Config.INPUT_DB_DATABASE, Config.INPUT_DB_CHARSET)

    def __get_data(self):

        unixtimestamp = int(time.time())
        sql = '''
            select
                addr,
                max(num) as num
            from {0}
            where pose_stat_time < {1} and pose_stat_time > {2}
            group by addr
        '''.format(Config.SOCKET_TABLE, unixtimestamp, unixtimestamp - Config.SOCKET_WAIT)

        result = {}
        # for row in self.__db.select(sql):
        #     pass

        return result

    def __get_test_data(self):

        data = {
            'time': '2020-01-26 22:10:00',
            'data': [
                {
                    'room_addr': '教七101',
                    'total': 35
                },
                {
                    'room_addr': '教七102',
                    'total': 35
                },
                {
                    'room_addr': '教七103',
                    'total': 35
                },
                {
                    'room_addr': '教七104',
                    'total': 35
                },
                {
                    'room_addr': '教七105',
                    'total': 35
                },
                {
                    'room_addr': '教七106',
                    'total': 35
                },
                {
                    'room_addr': '教七107',
                    'total': 35
                },
                {
                    'room_addr': '教七108',
                    'total': 35
                },
                {
                    'room_addr': '教七109',
                    'total': 35
                },
                {
                    'room_addr': '教七110',
                    'total': 35
                },
                {
                    'room_addr': '教七111',
                    'total': 35
                },
                {
                    'room_addr': '教七112',
                    'total': 35
                },
                {
                    'room_addr': '教七113',
                    'total': 35
                },
                {
                    'room_addr': '教七114',
                    'total': 35
                }
            ]
        }

        return data

    def start(self):
        conn, addr = self.__server.accept()
        while True:
            try:
                self.__logger.info('已连接，地址是:{}'.format(addr))
                self.__logger.info('开始发送信息')
                message = json.dumps(self.__get_test_data()).encode('utf-8')
                conn.sendall(message)
                self.__logger.info('已发送')
            except socket.error as msg:
                self.__logger.info('发送失败, 错误信息: {}'.format(msg))
                conn.close()
                exit(0)

            time.sleep(Config.SOCKET_WAIT)

        # 关闭
        conn.close()
        exit(0)


if __name__ == "__main__":
    configs = {
        'dbhost': '127.0.0.1'
    }

    doer = Server(configs)
    while True:
        t = threading.Thread(target=doer.start)
        t.start()
