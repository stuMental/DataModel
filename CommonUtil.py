# !/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time
import Config
import argparse
import uuid
import math
import hashlib
from AuthService import DoAuth


class CommonUtil(object):
    """Define some common functions"""
    def __init__(self):
        super(CommonUtil, self).__init__()

    @staticmethod
    def get_truncate_time(interval):
        """ 对当前时间按照固定的时间周期进行截断
        """

        now = datetime.datetime.now()
        unix = time.mktime(now.timetuple())
        return datetime.datetime.fromtimestamp(unix - unix % interval)

    @staticmethod
    def get_truncate_unix_timstamp(unix, interval):
        """ 对以秒为单位的时间戳进行固定周期interval的截断
        """

        return unix - unix % interval

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

    @staticmethod
    def get_mac_addr():
        """ 获取mac地址
        """

        return uuid.UUID(int = uuid.getnode()).hex[-12:].lower()

    @staticmethod
    def verify():
        """ 验证权限
        """

        if CommonUtil.get_mac_addr() != Config.MAC_ADDRESS:
            exit(-1)

        return True

    # @staticmethod
    # def verify():
    #     """ 验证权限
    #     """

    #     if not DoAuth.auth():
    #         exit(-1)

    @staticmethod
    def parse_arguments():
        '''
        解析命令行参数
        '''
        parser = argparse.ArgumentParser()
        parser.add_argument('--dbhost', type=str, help='Database host ip')
        parser.add_argument('--teaching', type=int, help='0: Don\'t estimate, 1: Estimate teaching status, 2: Estimate teacher status based on S-T analysis', default=0)
        parser.add_argument('--date', type=str, help='date yyyy-mm-dd', default='-1')
        parser.add_argument('--dbname', type=str, help='Database name', default=None)
        parser.add_argument('--pwd', type=str, help='Input the password', default=None)

        args = parser.parse_args()
        if not args.dbhost:
            print ("Please add necessary parameters, eg. --dbhost ip_address")
            raise Exception("Please add necessary parameters (eg. --dbhost ip_address) in the command line.")

        configs = {}
        configs['dbhost'] = args.dbhost
        configs['teaching'] = args.teaching
        configs['date'] = args.date
        configs['dbname'] = args.dbname
        configs['pwd'] = args.pwd

        return configs

    @staticmethod
    def get_score_by_triangle(edges):
        """ 用三角形计算图形的面积
        """
        length = len(edges)
        if length <= 2:
            return 0.0

        sin_value = 2 * math.pi / length
        score = 0.0
        for i in range(0, length):
            a = edges[i]
            b = edges[0] if i == length - 1 else edges[i + 1]
            score += 0.5 * a * b * math.sin(sin_value)

        return score

    @staticmethod
    def sigmoid(x, alpha=1, base=math.e):
        """ 求sigmoid函数值
        """

        return 2 / (1 + math.pow(base, -x * alpha)) - 1
