from xosresource import XOSResource
from core.models import XOS


class XOSXOS(XOSResource):
    provides = "tosca.nodes.XOS"
    xos_model = XOS
    obsolete_props = [
        "ui_port", "bootstrap_ui_port", "docker_project_name", "db_container_name", "redis_container_name",
        "enable_build", "frontend_only", "source_ui_image", "extra_hosts", "no_start", "no_build",
        "dest_ui_image", "cert_chain_name",
    ]

