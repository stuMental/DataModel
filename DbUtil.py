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
        self.__logger = Logger(__name__)
        self.__db = MySQLdb.connect(hostname, user, password, database, charset=charset)
        self.__cursor = self.__db.cursor()

    def insert(self, query):
        self.execute(query)

    def select(self, query):
        try:
            self.__cursor.execute(query)
            return self.__cursor.fetchall()
        except Exception as e:
            self.__logger.warning('Fail to select data with the query. Message: ['+str(e)+']' +' ['+ query +']')
        finally:
            pass

    def update(self, query):
        self.execute(query)

    def delete(self, query):
        self.execute(query)
    
    def execute(self, query):
        try:
            self.__cursor.execute(query)
            self.__db.commit()
        except Exception as e:
            self.__db.rollback()
            self.__logger.warning('Fail to execute the query. Message: ['+str(e)+']' +' ['+ query +']')
        finally:
            pass

    def __del__(self):
        self.__db.close()