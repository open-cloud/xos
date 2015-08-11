import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Slice,Sliver,User,Flavor,Node,Image
from nodeselect import XOSNodeSelector
from imageselect import XOSImageSelector
from flavorselect import XOSFlavorSelector

from xosresource import XOSResource

class XOSCompute(XOSResource):
    provides = "tosca.nodes.Compute"
    xos_model = Sliver

    def select_compute_node(self, user, v, hostname=None):
        mem_size = v.get_property_value("mem_size")
        num_cpus = v.get_property_value("num_cpus")
        disk_size = v.get_property_value("disk_size")

        flavor = XOSFlavorSelector(user, mem_size=mem_size, num_cpus=num_cpus, disk_size=disk_size).get_flavor()

        compute_node = XOSNodeSelector(user, mem_size=mem_size, num_cpus=num_cpus, disk_size=disk_size, hostname=hostname).get_nodes(1)[0]

        return (compute_node, flavor)

    def select_image(self, user, v):
        distribution = v.get_property_value("distribution")
        version = v.get_property_value("version")
        type = v.get_property_value("type")
        architecture = v.get_property_value("architecture")

        return XOSImageSelector(user, distribution=distribution, version=version, type=type, architecture=architecture).get_image()

    def get_xos_args(self, name=None, index=None):
        nodetemplate = self.nodetemplate

        if not name:
            name = nodetemplate.name

        host=None
        flavor=None
        image=None

        sliceName = self.get_requirement("tosca.relationships.MemberOfSlice", throw_exception=True)
        slice = self.get_xos_object(Slice, name=sliceName)

        # locate it one the same host as some other sliver
        colocate_host = None
        colocate_sliver_name = self.get_requirement("tosca.relationships.SameHost")
        if index is not None:
            colocate_sliver_name = "%s-%d" % (colocate_sliver_name, index)
        colocate_slivers = Sliver.objects.filter(name=colocate_sliver_name)
        if colocate_slivers:
            colocate_host = colocate_slivers[0].node.name
            self.info("colocating on %s" % colocate_host)

        capabilities = nodetemplate.get_capabilities()
        for (k,v) in capabilities.items():
            if (k=="host"):
                (compute_node, flavor) = self.select_compute_node(self.user, v, hostname=colocate_host)
            elif (k=="os"):
                image = self.select_image(self.user, v)

        if not compute_node:
            raise Exception("Failed to pick a host")
        if not image:
            raise Exception("Failed to pick an image")
        if not flavor:
            raise Exception("Failed to pick a flavor")

        return {"name": name,
                "image": image,
                "slice": slice,
                "flavor": flavor,
                "node": compute_node,
                "deployment": compute_node.site_deployment.deployment}

    def create(self, name = None):
        xos_args = self.get_xos_args(name=name)
        sliver = Sliver(**xos_args)
        sliver.caller = self.user
        sliver.save()

        self.info("Created Sliver '%s' on node '%s' using flavor '%s' and image '%s'" %
                  (str(sliver), str(sliver.node), str(sliver.flavor), str(sliver.image)))

    def create_or_update(self):
        scalable = self.get_scalable()
        if scalable:
            default_instances = scalable.get("default_instances",1)
            for i in range(0, default_instances):
                name = "%s-%d" % (self.nodetemplate.name, i)
                existing_slivers = Sliver.objects.filter(name=name, index=i)
                if existing_slivers:
                    self.info("%s %s already exists" % (self.xos_model.__name__, name))
                    self.update(existing_slivers[0])
                else:
                    self.create(name)
        else:
            super(XOSCompute,self).create_or_update()

    def get_existing_objs(self):
        scalable = self.get_scalable()
        if scalable:
            existing_slivers = []
            max_instances = scalable.get("max_instances",1)
            for i in range(0, max_instances):
                name = "%s-%d" % (self.nodetemplate.name, i)
                existing_slivers = existing_slivers + list(Sliver.objects.filter(name=name))
            return existing_slivers
        else:
            return super(XOSCompute,self).get_existing_objs()

