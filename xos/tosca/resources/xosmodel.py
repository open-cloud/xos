from xosresource import XOSResource
from core.models import XOS, XOSVolume


class XOSXOS(XOSResource):
    provides = "tosca.nodes.XOS"
    xos_model = XOS
    copyin_props = [
        "ui_port", "bootstrap_ui_port", "docker_project_name", "db_container_name", "redis_container_name",
        "enable_build", "frontend_only", "source_ui_image", "extra_hosts", "no_start", "no_build",
        "dest_ui_image", "cert_chain_name",
    ]


class XOSVolume(XOSResource):
    provides = "tosca.nodes.XOSVolume"
    xos_model = XOSVolume
    copyin_props = ["host_path", "read_only"]
    name_field = "container_path"

    def get_xos_args(self, throw_exception=True):
        args = super(XOSVolume, self).get_xos_args()

        xos_name = self.get_requirement("tosca.relationships.UsedByXOS", throw_exception=throw_exception)
        if xos_name:
            args["xos"] = self.get_xos_object(XOS, throw_exception=throw_exception, name=xos_name)

        return args
