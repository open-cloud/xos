#!/usr/bin/env python

from distutils.core import setup

setup(name='XosConfig',
      version='1.0',
      description='XOS Config Library',
      author='Matteo Scandolo',
      author_email='teo@onlab.us',
      packages=['xosconfig'],
      data_files=[
            ('.', ['xosconfig/config-schema.yaml'])
      ]
     )