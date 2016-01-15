import os
import base64
import string
import sys
import xmlrpclib

if __name__ == '__main__':
    sys.path.append("/opt/xos")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")

from xos.config import Config
from core.models import Service
from services.hpc.models import HpcService
from services.requestrouter.models import RequestRouterService
from xos.logger import Logger, logging

logger = Logger(level=logging.INFO)

class APIHelper:
    def __init__(self, proxy, auth, method=None):
        self.proxy = proxy
        self.auth = auth
        self.method = method

    def __getattr__(self, name):
        if name.startswith("_"):
            return getattr(self, name)
        else:
            return APIHelper(self.proxy, self.auth, name)

    def __call__(self, *args):
        method = getattr(self.proxy, self.method)
        return method(self.auth, *args)

class CmiClient:
    def __init__(self, hostname, port=8003, username="apiuser", password="apiuser"):
        self.connect_api(hostname, port, username, password)

    def connect_api(self, hostname, port=8003, username="apiuser", password="apiuser"):
        #print "https://%s:%d/COAPI/" % (hostname, port)
        cob = xmlrpclib.ServerProxy("https://%s:%d/COAPI/" % (hostname, port), allow_none=True)
        cob_auth = {}
        cob_auth["Username"] = username
        cob_auth["AuthString"] = password
        cob_auth["AuthMethod"] = "password"

        onev = xmlrpclib.ServerProxy("https://%s:%d/ONEV_API/" % (hostname, port), allow_none=True)
        onev_auth = {}
        onev_auth["Username"] = username
        onev_auth["AuthString"] = password
        onev_auth["AuthMethod"] = "password"

        self.cob = APIHelper(cob, cob_auth)
        self.onev = APIHelper(onev, onev_auth)

class HpcLibrary:
    def __init__(self):
        self._client = None

    def make_account_name(self, x):
        x=x.lower()
        y = ""
        for c in x:
            if (c in (string.lowercase + string.digits)):
                y = y + c
        return y[:20]

    def get_hpc_service(self):
        hpc_service_name = getattr(Config(), "observer_hpc_service", None)
        if hpc_service_name:
            hpc_service = HpcService.objects.filter(name = hpc_service_name)
        else:
            hpc_service = HpcService.objects.all()

        if not hpc_service:
            if hpc_service_name:
                raise Exception("No HPC Service with name %s" % hpc_service_name)
            else:
                raise Exception("No HPC Services")
        hpc_service = hpc_service[0]

        return hpc_service

    def get_cmi_hostname(self, hpc_service=None):
        if getattr(Config(),"observer_cmi_hostname",None):
            return getattr(Config(),"observer_cmi_hostname")

        if (hpc_service is None):
            hpc_service = self.get_hpc_service()

        if hpc_service.cmi_hostname:
            return hpc_service.cmi_hostname

        try:
            slices = hpc_service.slices.all()
        except:
            # deal with buggy data model
            slices = hpc_service.service.all()

        for slice in slices:
            if slice.name.endswith("cmi"):
                for instance in slice.instances.all():
                    if instance.node:
                         return instance.node.name

        raise Exception("Failed to find a CMI instance")

    @property
    def client(self):
        if self._client is None:
            self._client = CmiClient(self.get_cmi_hostname())
        return self._client

if __name__ == '__main__':
    import django
    django.setup()

    lib = HpcLibrary()

    print "testing API connection to", lib.get_cmi_hostname()
    lib.client.cob.GetNewObjects()
    lib.client.onev.ListAll("CDN")




