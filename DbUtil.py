# !/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import time
import datetime
import Logger

class DbUtil(object):
    """Define a util class for DB operation"""

    def __init__(self, hostname, user, password, database, charset):
        super(DbUtil, self).__init__()
        self.__logger = Logger.Logger(__name__)
        self.__db = MySQLdb.connect(hostname, user, password, database, charset=charset)
        self.__cursor = self.__db.cursor()

    def insert(self, query):
        self.execute(query)

    def select(self, query):
        self.__logger.debug(query)
        try:
            self.__cursor.execute(query)
            self.__logger.info("Impacted record count: {0}".format(self.__cursor.rowcount))
            return self.__cursor.fetchall()
        except Exception as e:
            self.__logger.warning('Fail to select data with the query. Message: ['+str(e)+']' +' ['+ query +']')
        finally:
            pass

    def update(self, query):
        self.execute(query)

    def delete(self, query):
        self.execute(query)
    
    def create(self, query):
        self.execute(query)

    def truncate(self, query):
        self.execute(query)

    def execute(self, query):
        self.__logger.debug(query)
        try:
            self.__cursor.execute(query)
            self.__db.commit()
            self.__logger.info("Impacted record count: {0}".format(self.__cursor.rowcount))
        except Exception as e:
            self.__db.rollback()
            self.__logger.warning('Fail to execute the query. Message: ['+str(e)+']' +' ['+ query +']')
        finally:
            pass

    def __del__(self):
        self.__db.close()
