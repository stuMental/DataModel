# !/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time

class CommonUtil(object):
    """Define some common functions"""
    def __init__(self):
        super(CommonUtil, self).__init__()

    @staticmethod  
    def get_truncate_time(interval):
        ''''''
        now = datetime.datetime.now()
        unix = time.mktime(now.timetuple())
        return datetime.datetime.fromtimestamp(unix - unix % interval)

    @staticmethod
    def get_time_range():
        ''''''
        res = {}
        res['start_time'] = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
        res['end_time'] =datetime.date.today().strftime("%Y-%m-%d")

        return res

    @staticmethod
    def get_range_unixtime():
        ''''''
        res = {}
        start_time = (datetime.date.today() + datetime.timedelta(days=-1))
        end_time =datetime.date.today()

        res['start_time'] = time.mktime(start_time.timetuple())
        res['end_time'] = time.mktime(end_time.timetuple())

        # For test
        # res['start_time'] = 1549882797
        # res['end_time'] = 1549882797

        return res

    @staticmethod
    def get_current_time():
        ''''''
        return str(datetime.datetime.now())

    @staticmethod
    def get_specific_unixtime(str_time, days = 0):
        ''''''
        dt = datetime.datetime.fromtimestamp(str_time)
        ans = dt.date() + datetime.timedelta(days)
        return int(time.mktime(ans.timetuple()))

    @staticmethod
    def get_date_day(days = 0):
        ''''''
        return (datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y%m%d")