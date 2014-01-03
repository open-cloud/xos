import os
import base64
import sys

if __name__ == '__main__':
    sys.path.append("/opt/planetstack")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")

from planetstack.config import Config
from core.models import Service
from hpc.models import HpcService
from requestrouter.models import RequestRouterService
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class HpcLibrary:
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

    def write_slices_file(self, hpc_service, rr_service):
        mapping = self.extract_slice_info(hpc_service)
        rr_mapping = self.extract_slice_info(rr_service)

        mapping.update(rr_mapping)

        print mapping

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

if __name__ == '__main__':
    hpc_service = HpcService.objects.get()
    rr_service = RequestRouterService.objects.get()
    lib = HpcLibrary()
    lib.write_slices_file(hpc_service, rr_service)


