#!/usr/bin/env python
import argparse
import imp
import inspect
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
sys.path.append("/opt/xos")
from xos.config import Config, DEFAULT_CONFIG_FN, XOS_DIR
from xos.logger import Logger, logging
from synchronizers.base.syncstep import SyncStep

try:
    from django import setup as django_setup # django 1.7
except:
    django_setup = False

logger = Logger(level=logging.INFO)

class XOSConsistencyCheck:
	def __init__(self):
                self.sync_steps = []
		self.load_sync_step_modules()

	def load_sync_step_modules(self, step_dir=None):
		if step_dir is None:
			if hasattr(Config(), "observer_steps_dir"):
				step_dir = Config().observer_steps_dir
			else:
				step_dir = XOS_DIR+"/observer/steps"

		for fn in os.listdir(step_dir):
			pathname = os.path.join(step_dir,fn)
			if os.path.isfile(pathname) and fn.endswith(".py") and (fn!="__init__.py"):
				module = imp.load_source(fn[:-3],pathname)
				for classname in dir(module):
					c = getattr(module, classname, None)

					# make sure 'c' is a descendent of SyncStep and has a
					# provides field (this eliminates the abstract base classes
					# since they don't have a provides)

					if inspect.isclass(c) and issubclass(c, SyncStep) and hasattr(c,"provides") and (c not in self.sync_steps):
						self.sync_steps.append(c)
		logger.info('loaded sync steps: %s' % ",".join([x.__name__ for x in self.sync_steps]))

        def run(self):
            updated = True
            while updated:
                updated = False

                for step in self.sync_steps:
                    if hasattr(step, "consistency_check"):
                        updated = updated or step(driver=None).consistency_check()

                if updated:
                    logger.info('re-running consistency checks because something changed')

def main():
    if not "-C" in sys.argv:
        print >> sys.stderr, "You probably wanted to use -C " + XOS_DIR + "/hpc_observer/hpc_observer_config"

    # Generate command line parser
    parser = argparse.ArgumentParser(usage='%(prog)s [options]')
    # smbaker: util/config.py parses sys.argv[] directly to get config file name; include the option here to avoid
    #   throwing unrecognized argument exceptions
    parser.add_argument('-C', '--config', dest='config_file', action='store', default=DEFAULT_CONFIG_FN,
                        help='Name of config file.')
    args = parser.parse_args()

    if django_setup: # 1.7
        django_setup()

    cc = XOSConsistencyCheck()
    cc.run()

if __name__ == '__main__':
    main()

