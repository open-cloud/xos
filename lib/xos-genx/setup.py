#!/usr/bin/env python

from setuptools import setup

setup(name='XosGenX',
      version='1.0',
      description='XOS Generative Toolchain',
      author='Sapan Bhatia, Matteo Scandolo',
      author_email='sapan@onlab.us, teo@onlab.us',
      packages=['xosgenx'],
      scripts=['bin/xosgenx'],
      include_package_data=True,
     )