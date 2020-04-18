# !/usr/bin/python
# -*- coding: utf-8 -*-

from BackupData import BackupData
from CommonUtil import CommonUtil

class MainBK(object):
    """Main class"""
    def __init__(self):
        super(MainBK, self).__init__()
        self.doer = BackupData(CommonUtil.parse_arguments())

    def executor(self):
        self.doer.process()

if __name__ == '__main__':
    obj = MainBK()
    obj.executor()