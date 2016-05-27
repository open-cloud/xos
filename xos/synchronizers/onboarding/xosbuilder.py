import os
import base64
import string
import sys
import xmlrpclib

if __name__ == '__main__':
    sys.path.append("/opt/xos")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")

from xos.config import Config
from core.models import Service, ServiceController, ServiceControllerResource
from xos.logger import Logger, logging

logger = Logger(level=logging.INFO)

class XOSBuilder(object):
    def __init__(self):
        self.source_image = "xosproject/xos"
