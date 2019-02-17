# !/usr/bin/python
# -*- coding: utf8 -*-

import Config
import logging

class Logger(object):
    """docsTry for Logger"""
    def __init__(self, class_name):
        super(Logger, self).__init__()
        logging.basicConfig(level = Config.LOGGER_LEVEL, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.__logger = logging.getLogger(class_name)

    def fatal(self, message):
        self.__logger.fatal(message)

    def critical(slef, message):
        self.__logger.critical(message)

    def error(self, message):
        self.__logger.error(message)

    def warning(self, message):
        self.__logger.warning(message)

    def info(self, message):
        self.__logger.info(message)

    def debug(self, message):
        self.__logger.debug(message)