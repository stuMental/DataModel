# !/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time
import Config
import argparse

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

        now = datetime.datetime.now()
        start_days = 0
        end_days = 0
        if (now.hour <= Config.DATETIME_THRESHOLD): # 小于每天16时 表示当天的数据还没有完全产生 所以需要跑前一天的数据
            start_days = -1
            end_days = 0
        else: # 当天数据已经产生 可以跑当天的数据
            start_days = 0
            end_days = 1

        start_time = (datetime.date.today() + datetime.timedelta(days=start_days))
        end_time = (datetime.date.today() + datetime.timedelta(days=end_days))

        res['start_datetime'] = start_time.strftime("%Y-%m-%d")
        res['end_datetime'] = end_time.strftime("%Y-%m-%d")
        res['start_unixtime'] = int(time.mktime(start_time.timetuple()))
        res['end_unixtime'] = int(time.mktime(end_time.timetuple()))

        # For test
        # res['start_datetime'] = '2019-05-08'
        # res['end_datetime'] = '2019-05-09'
        # res['start_unixtime'] = 1557244800
        # res['end_unixtime'] = 1557331200

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
        # return '2019-05-08'
    
    '''
    解析命令行参数
    '''
    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser()
        parser.add_argument('--dbhost', type=str, help='database host ip')
        # parser.add_argument('--dbuser', type=str, help='database username')
        # parser.add_argument('--dbpassword', type=str, help='database user password')
        # parser.add_argument('--dbname', type=str, help='database name')
        
        args = parser.parse_args()
        if not args.dbhost:
            print "请在执行命令的时候传递正确格式的参数，比如: sudo python Main.py --dbhost xx"
            raise Exception("Please add necessary parameters (such as sudo python Main.py --dbhost xx) in the command line.")
        
        configs = {}
        configs['dbhost'] = args.dbhost

        return configs