# !/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
from Cython.Build import cythonize

# Example call: sudo python Encryption.py build_ext
setup(ext_modules = cythonize(["AnalyzeGrade.py","CalcCourseMetric.py","CalcMetric.py","ClassAPI.py","CommonUtil.py","Config.py","EstimateMental.py","MetricUtil.py","PostMetric.py","Preprocessor.py", "CalcClassMetric.py", "CalcTeacherMetric.py", "AnalyzeTeachingGrade.py", "Attendance.py", "BackupData.py", "CalcTeachingMetric.py", "RTCount.py"]))