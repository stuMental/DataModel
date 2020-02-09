# !/usr/bin/python
# -*- coding: utf-8 -*-

from Attendance import Attendance
from CommonUtil import CommonUtil


class Main(object):
    """Main class for attendance"""
    def __init__(self):
        super(Main, self).__init__()
        self.doer = Attendance(CommonUtil.parse_arguments())

    def executor(self):
        self.doer.process(CommonUtil.get_date_day())

if __name__ == '__main__':
    obj = Main()
    obj.executor()