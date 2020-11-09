# !/usr/bin/python
# -*- coding: utf-8 -*-

from RTCount import RTCount
from CommonUtil import CommonUtil


class Main(object):
    """Main class for real time to count people"""
    def __init__(self):
        super(Main, self).__init__()
        self.doer = RTCount(CommonUtil.parse_arguments())

    def executor(self):
        self.doer.process()

if __name__ == '__main__':
    obj = Main()
    obj.executor()
