import os
import base64
import string
import sys
import xmlrpclib

if __name__ == '__main__':
    sys.path.append("/opt/planetstack")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")

from planetstack.config import Config
from core.models import Service
from hpc.models import HpcService
from requestrouter.models import RequestRouterService
from util.logger import Logger, logging

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

    def extract_slice_info(self, service):
        """ Produce a dict that describes the slices for the CMI

            slice_coblitz = <name of coblitz slice>
            service_coblitz = <name of coblitz service>
            hostname_coblitz = <name of first coblitz slice>
            hostnames_coblitz = <name_of_first_cob_slice>,<name_of_second_cob_slice>,...

            slice_cmi = <name of cmi slice>
            ...
        """

        slicenames = {}
        slicehosts = {}
        for slice in service.service.all():
            name = slice.name
            if not ("_" in name):
                continue

            if "coblitz" in name:
                slicenames["coblitz"] = name
                slicehosts["coblitz"] = [sliver.node.name for sliver in slice.slivers.all()]
            elif "cmi" in name:
                slicenames["cmi"] = name
                slicehosts["cmi"] = [sliver.node.name for sliver in slice.slivers.all()]
            elif "dnsredir" in name:
                slicenames["dnsredir"] = name
                slicehosts["dnsredir"] = [sliver.node.name for sliver in slice.slivers.all()]
            elif "dnsdemux" in name:
                slicenames["dnsdemux"] = name
                slicehosts["dnsdemux"] = [sliver.node.name for sliver in slice.slivers.all()]

        base_hrn = None
        if "coblitz" in slicenames:
            base_hrn = slicenames["coblitz"].split("_")[0]

        mapping = {}
        mapping["base_hrn"] = base_hrn
        for (k,v) in slicenames.items():
            mapping["slice_" + k] = v
            mapping["service_" + k] = v.split("_",1)[1]
        for (k,v) in slicehosts.items():
            mapping["hostname_" + k] = v[0]
            mapping["hostnames_" + k] = ",".join(v)

        return mapping

    def get_cmi_hostname(self, hpc_service=None):
        if (hpc_service is None):
            hpc_service = HpcService.objects.get()

        slice_info = self.extract_slice_info(hpc_service)
        return slice_info["hostname_cmi"]

    def write_slices_file(self, hpc_service=None, rr_service=None):
        if (hpc_service is None):
            hpc_service = HpcService.objects.get()

        if (rr_service is None):
            rr_service = RequestRouterService.objects.get()

        mapping = self.extract_slice_info(hpc_service)
        rr_mapping = self.extract_slice_info(rr_service)

        mapping.update(rr_mapping)

        fn = "/tmp/slices"

        f = open(fn, "w")
        f.write("""
ENABLE_PLC=True
ENABLE_PS=False
BASE_HRN="%(base_hrn)s"
RELEVANT_SERVICE_NAMES=['%(service_coblitz)s', '%(service_dnsredir)s', '%(service_dnsdemux)s']
COBLITZ_SLICE_NAME="%(slice_coblitz)s"
COBLITZ_SLICE_ID=1
COBLITZ_PS_SLICE_NAME="%(slice_coblitz)s"
DNSREDIR_SLICE_NAME="%(slice_dnsredir)s"
DNSREDIR_SLICE_ID=2
DNSREDIR_PS_SLICE_NAME="%(slice_dnsredir)s"
DNSDEMUX_SLICE_NAME="%(slice_dnsdemux)s"
DNSDEMUX_SLICE_ID=3
DNSDEMUX_PS_SLICE_NAME="%(slice_dnsdemux)s"
CMI_URL="http://%(hostname_cmi)s"
CMI_HTTP_PORT="8004"
CMI_HTTPS_PORT="8003"
PUPPET_MASTER_HOSTNAME="%(hostname_cmi)s"
PUPPET_MASTER_PORT="8140"
""" % mapping)

    @property
    def client(self):
        if self._client is None:
            self._client = CmiClient(self.get_cmi_hostname())
        return self._client

if __name__ == '__main__':
    print "testing write_slices_file"
    lib = HpcLibrary()
    lib.write_slices_file()

    print "testing API connection"
    lib.client.cob.GetNewObjects()
    lib.client.onev.ListAll("CDN")




