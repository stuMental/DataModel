# !/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

class CommonUtil(object):
    """Define some common functions"""
    def __init__(self, interval):
        super(CommonUtil, self).__init__()
        self.__interval = interval

    @staticmethod  
    def get_truncate_time(self):
        ''''''
        now = datetime.datetime.now()
        unix = time.mktime(now.timetuple())
        return datetime.datetime.fromtimestamp(unix - unix % self.__interval)

    @staticmethod
    def get_time_range(self):
        ''''''
        res = {}
        res['start_time'] = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
        res['end_time'] =datetime.date.today().strftime("%Y-%m-%d")

        return res

    @staticmethod
    def get_current_time(self):
        ''''''
        return str(datetime.datetime.now())

    @staticmethod
    def get_specific_time(self, str_time, days = 0):
        ''''''
        dt = datetime.datetime.strptime(str_time, "%Y-%m-%d")
        ans = dt.date() + datetime.timedelta(days)
        return ans.strftime("%Y-%m-%d")
