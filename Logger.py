# !/usr/bin/python
# -*- coding: utf8 -*-

import os
import sys
import Config
import logging
import datetime


class Logger(object):
    """docsTry for Logger"""
    def __init__(self, class_name):
        super(Logger, self).__init__()
        self.__filename = ''.join([self.__dir(), '/Log_', datetime.date.today().strftime('%Y_%m_%d'), '.txt'])
        logging.basicConfig(level = Config.LOGGER_LEVEL, filename = self.__filename, filemode = 'a', format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # logging.basicConfig(level=Config.LOGGER_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.__logger = logging.getLogger(class_name)

    def __dir(self):
        """ 创建logs目录
        """

        dir_path, file_name = os.path.split(os.path.abspath(sys.argv[0]))
        log_path = dir_path + '/logs'
        while (not os.path.exists(log_path)):
            print ('Trying to create log path: {}'.format(log_path))
            os.mkdir(log_path)

        print ('Log path: {}'.format(log_path))
        return log_path

    def fatal(self, message):
        self.__logger.fatal(message)

    def critical(self, message):
        self.__logger.critical(message)

    def error(self, message):
        self.__logger.error(message)

    def warning(self, message):
        self.__logger.warning(message)

    def info(self, message):
        self.__logger.info(message)

    def debug(self, message):
        self.__logger.debug(message)
