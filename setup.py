from distutils.core import setup
from glob import glob

setup(name='plstackapi',
      version='0.1',
      description='PlanetStack API',
      packages=['plstackapi', 'plstackapi/core', 'plstackapi/planetstack'],
      scripts=['plstackapi/plstackapi-debug-server.py'],
      data_files=[
        ('/etc/planetstack/', ['config/plstackapi_config']),
        ])
