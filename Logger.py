# !/usr/bin/python
# -*- coding: utf8 -*-

import Config
import logging

class Logger(object):
    """docstring for Logger"""
    def __init__(self, class_name):
        super(Logger, self).__init__()
        logging.basicConfig(level = Config.LOGGER_LEVEL, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(class_name)

    def fatal(self, message):
        self.logger.fatal(message)

    def critical(slef, message):
        self.logger.critical(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)