import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate
import pdb

from services.mcord.models import MCORDService

from service import XOSService

class XOSMCORDService(XOSService):
    provides = "tosca.nodes.MCORDService"
    xos_model = MCORDService
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key",
                    "private_key_fn", "versionNumber",
                    ]

