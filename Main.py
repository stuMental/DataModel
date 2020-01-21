# !/usr/bin/python
# -*- coding: utf-8 -*-

from EstimateMental import EstimateMental
from CommonUtil import CommonUtil

class Main(object):
    """Main class"""
    def __init__(self):
        super(Main, self).__init__()
        self.doer = EstimateMental(CommonUtil.parse_arguments())

    def executor(self):
        self.doer.estimate()

if __name__ == '__main__':
    obj = Main()
    obj.executor()