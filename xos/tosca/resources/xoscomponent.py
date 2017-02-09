from xosresource import XOSResource
from core.models import XOSComponent, XOSComponentLink, XOSComponentVolume, XOSComponentVolumeContainer


class XOSXOSComponent(XOSResource):
    provides = "tosca.nodes.Component"
    xos_model = XOSComponent
    copyin_props = ["name", "image", "command", "ports", "extra"]


class XOSXOSComponentLink(XOSResource):
    provides = "tosca.nodes.ComponentLink"
    xos_model = XOSComponentLink
    copyin_props = ["container", "alias", "kind"]
    name_field = "container"

    def get_xos_args(self, throw_exception=True):
        args = super(XOSXOSComponentLink, self).get_xos_args()

        component_name = self.get_requirement("tosca.relationships.LinkOfComponent", throw_exception=throw_exception)
        if component_name:
            args["component"] = self.get_xos_object(XOSComponent, throw_exception=throw_exception, name=component_name)

        return args


class XOSXOSComponentVolume(XOSResource):
    provides = "tosca.nodes.ComponentVolume"
    xos_model = XOSComponentVolume
    copyin_props = ["host_path", "read_only"]
    name_field = "container_path"

    def get_xos_args(self, throw_exception=True):
        args = super(XOSXOSComponentVolume, self).get_xos_args()

        component_name = self.get_requirement("tosca.relationships.VolumeOfComponent", throw_exception=throw_exception)
        if component_name:
            args["component"] = self.get_xos_object(XOSComponent, throw_exception=throw_exception, name=component_name)

        return args


class XOSXOSComponentVolumeContainer(XOSResource):
    provides = "tosca.nodes.ComponentVolumeContainer"
    xos_model = XOSComponentVolumeContainer
    copyin_props = ["name", "container"]
    name_field = "name"

    def get_xos_args(self, throw_exception=True):
        args = super(XOSXOSComponentVolumeContainer, self).get_xos_args()

        component_name = self.get_requirement("tosca.relationships.VolumeContainerOfComponent", throw_exception=throw_exception)
        if component_name:
            args["component"] = self.get_xos_object(XOSComponent, throw_exception=throw_exception, name=component_name)

        return args