import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.syncstep import SyncStep
from core.models import Service
from hpc.models import HpcService
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncHpcService(SyncStep):
    provides=[HpcService]
    requested_interval=0

    def fetch_pending(self):
        return HpcService.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def extract_slice_info(hpc_service):
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
        for slice in hpc_service.service.all():
            name = slice.name
            if not ("_" in name):
                continue

            if "coblitz" in name:
                slicenames["coblitz"] = name
                slicehosts["coblitz"] = [sliver.node.name for sliver in slice.slivers.all()]
            elif "cmi" in name:
                slicenames["cmi"] = name
                slicehosts["cmi"] = [sliver.node.name for sliver in slice.slivers.all()]

        base_hrn = None
        if "coblitz" in slicenames:
            base_hrn = slicenames["coblitz"].split("_")[0]

        mapping = {}
        mapping["base_hrn"] = base_hrn
        for (k,v) in slicenames.items():
            mapping["slice_" + k] = v
            mapping["service_" + k] = v.split("_",1)[1]
        for (k,v) in slicehosts.items()
            mapping["hostname_" + k] = v[0]
            mapping["hostnames_" + k] = ",".join(v)

        return mapping

    def write_slices_file(self, hpc_service):
        mapping = self.extract_slicenames(hpc_service)

        fn = "/tmp/slices"

        f = open(fn, "w")
        f.write("""
ENABLE_PLC=True
ENABLE_PS=False
BASE_HRN="%(base_hrn)"
RELEVANT_SERVICE_NAMES=['%(service_coblitz)', '%(service_dnsredir)', '%(service_dnsdemux)']
COBLITZ_SLICE_NAME="%(slice_coblitz)"
COBLITZ_SLICE_ID=1
COBLITZ_PS_SLICE_NAME="%(slice_coblitz)"
DNSREDIR_SLICE_NAME="%(slice_dnsredir)"
DNSREDIR_SLICE_ID=2
DNSREDIR_PS_SLICE_NAME="%(slice_dnsredir)"
DNSDEMUX_SLICE_NAME="%(slice_dnsdemux)"
DNSDEMUX_SLICE_ID=3
DNSDEMUX_PS_SLICE_NAME="%(slice_dnsdemux)"
CMI_URL="http://%(hostname_cmi)"
CMI_HTTP_PORT="8004"
CMI_HTTPS_PORT="8003"
PUPPET_MASTER_HOSTNAME="%(hostname_cmi)"
PUPPET_MASTER_PORT="8140"
""")

    def sync_record(self, hpc_service):
        logger.info("sync'ing hpc_service %s" % str(hpc_service))
        hpc_service.save()
