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
    def get_range_times():
        ''''''
        res = {}
        start_time = (datetime.date.today() + datetime.timedelta(days=-1))
        end_time =datetime.date.today()

        res['start_datetime'] = start_time.strftime("%Y-%m-%d")
        res['end_datetime'] = end_time.strftime("%Y-%m-%d")
        res['start_unixtime'] = int(time.mktime(start_time.timetuple()))
        res['end_unixtime'] = int(time.mktime(end_time.timetuple()))

        # For test
        # res['start_datetime'] = '2019-03-02'
        # res['end_datetime'] = '2019-03-03'
        # res['start_unixtime'] = 257993581
        # res['end_unixtime'] = 257993610

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
    def get_specific_date(str_date, days = 0):
        ''''''
        dt = datetime.datetime.strptime(str_date, "%Y-%m-%d")
        return dt.date() + datetime.timedelta(days)

    @staticmethod
    def get_date_day(days = 0):
        ''''''
        return (datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        # For test
        # return '2019-03-03'