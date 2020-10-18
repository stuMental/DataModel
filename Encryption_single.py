# !/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
from Cython.Build import cythonize

# Example call: sudo python Encryption.py build_ext
setup(ext_modules = cythonize(["Config.py"]))