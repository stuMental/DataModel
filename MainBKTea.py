# !/usr/bin/python
# -*- coding: utf-8 -*-

from BackupDataTea import BackupDataTea
from CommonUtil import CommonUtil


class MainBKTea(object):
    """Main class"""
    def __init__(self):
        super(MainBKTea, self).__init__()
        self.doer = BackupDataTea(CommonUtil.parse_arguments())

    def executor(self):
        self.doer.process()


if __name__ == '__main__':
    obj = MainBKTea()
    obj.executor()
