# !/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import time
import json
import Config
from Logger import Logger


class Client(object):
    def __init__(self, configs):
        self.__dbhost = configs['dbhost']
        self.__logger = Logger(__name__)

    def receive(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.__dbhost, Config.SOCKET_PORT))
        while True:
            try:
                data = json.loads(client.recv(Config.SOCKET_SIZE).decode('utf-8'))
                print data
            except socket.error as msg:
                self.__logger.info('接受信息失败, 错误信息是{}'.format(msg))
            # finally:
            #     client.close()

        client.close()


if __name__ == "__main__":
    configs = {
        'dbhost': '127.0.0.1'
    }
    doer = Client(configs)
    doer.receive()
