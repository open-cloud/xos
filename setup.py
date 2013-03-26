from distutils.core import setup
from glob import glob

setup(name='plstackapi',
      version='0.1',
      description='PlanetStack API',
      packages=['plstackapi', 'plstackapi/core', 'plstackapi/planetstack'],
      scripts=[],
      data_files=[])
