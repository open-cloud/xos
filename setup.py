import os
import shutil 
from distutils.core import setup

def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(src).st_mtime - os.stat(dst).st_mtime > 1:
                shutil.copy2(s, d)

setup(name='planetstack',
      version='0.1',
      description='PlanetStack',
      scripts=['planetstack/planetstack-backend.py'],
      data_files=[
        ('/etc/planetstack/', ['planetstack/plstackapi_config']),
        ('/lib/systemd/system/', ['planetstack/redhat/planetstack-backend.service']),
        ])

copytree('planetstack/', '/opt/planetstack')
