import os
import sys
import time

import django
xos_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/..')
sys.path.append(xos_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")

from reaper import ReaperThread
from grpc_server import XOSGrpcServer, restart_chameleon

from xos.logger import Logger, logging
logger = Logger(level=logging.DEBUG)


if __name__ == '__main__':

    django.setup()

    reaper = ReaperThread()
    reaper.start()

    server = XOSGrpcServer().start()

    restart_chameleon()

    logger.info("Core_main entering wait loop")

    _ONE_DAY_IN_SECONDS = 60 * 60 * 24
    try:
        while 1:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop()
        reaper.stop()

