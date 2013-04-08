from distutils.core import setup
from glob import glob

setup(name='plstackapi',
      version='0.1',
      description='PlanetStack API',
      packages=['plstackapi', 'plstackapi/planetstack', 'plstackapi/planetstack/views', 'plstackapi/planetatack/api', 'plstackapi/openstack' ,'plstackapi/util', 'plstackapi/importer', 'plstackapi/importer/plclassic'],
      scripts=['plstackapi/plstackapi-debug-server.py'],
      data_files=[
        ('/etc/planetstack/', ['config/plstackapi_config']),
        ('/opt/planetstack/', glob('plstackapi/planetstack/*')),
        ])
